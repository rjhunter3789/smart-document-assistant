#!/usr/bin/env python3
"""
Flask app with Google Drive integration, OpenAI GPT-4o-mini, and User Authentication
Searches documents and provides intelligent AI summaries with user-specific folder prioritization
Version: 4.0.0-Authentication
"""
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import io
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import fitz  # PyMuPDF
from docx import Document as DocxDoc
import openai
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize OpenAI (API key from environment)
openai_client = None
api_key = os.environ.get('OPENAI_API_KEY')

# Workaround for Railway's proxy injection issue
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
              'NO_PROXY', 'no_proxy', 'ALL_PROXY', 'all_proxy']
saved_proxies = {}
for var in proxy_vars:
    if var in os.environ:
        saved_proxies[var] = os.environ.pop(var)

if api_key:
    try:
        import httpx
        custom_http_client = httpx.Client(
            trust_env=False,
            timeout=httpx.Timeout(60.0)
        )
        openai_client = OpenAI(
            api_key=api_key,
            http_client=custom_http_client
        )
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        openai_client = None

# Restore proxy variables
for var, value in saved_proxies.items():
    os.environ[var] = value

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
PARENT_FOLDER_ID = "1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6"  # WMA RAG folder

# Load user folder configuration
SEARCH_CONFIG = {}
try:
    with open('search_config.json', 'r') as f:
        SEARCH_CONFIG = json.load(f)
except Exception as e:
    print(f"Could not load search_config.json: {e}")
    SEARCH_CONFIG = {
        'user_folders': {},
        'default_team_folder': '1INF091UIAoK87SIVzN4MpeUERyAyO-w4',
        'search_weights': {'user_folder': 2.0, 'team_folder': 1.0},
        'users': {}
    }

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username
        self.is_admin = username.lower() == 'jeff'

@login_manager.user_loader
def load_user(username):
    if username in SEARCH_CONFIG.get('users', {}):
        return User(username)
    return None

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return 'Unauthorized', 403
        return f(*args, **kwargs)
    return decorated_function

def get_google_credentials():
    """Get Google credentials from environment variables or file"""
    if os.environ.get('GOOGLE_CLIENT_ID'):
        creds_dict = {
            "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
            "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
            "refresh_token": os.environ.get('GOOGLE_REFRESH_TOKEN'),
            "token": os.environ.get('GOOGLE_TOKEN'),
            "token_uri": "https://oauth2.googleapis.com/token",
            "type": "authorized_user"
        }
        return Credentials.from_authorized_user_info(creds_dict, SCOPES)
    
    creds_file = 'credentials.json'
    if os.path.exists(creds_file):
        with open(creds_file, 'r') as f:
            creds_dict = json.load(f)
        return Credentials.from_authorized_user_info(creds_dict, SCOPES)
    
    return None

def authenticate_gdrive():
    """Authenticate and return Google Drive service"""
    try:
        creds = get_google_credentials()
        if not creds:
            return None
            
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def get_subfolders(service, parent_folder_id):
    """Get all subfolders within a parent folder"""
    folders = []
    try:
        query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        response = service.files().list(
            q=query,
            fields="files(id, name)",
            pageSize=100
        ).execute()
        
        for folder in response.get('files', []):
            folders.append(folder['id'])
            
    except Exception as e:
        print(f"Error getting subfolders: {e}")
    
    return folders

def extract_text_from_drive_file(file_id, mime_type, service):
    """Extract text content from a Google Drive file"""
    try:
        # Handle Google Docs
        if mime_type == 'application/vnd.google-apps.document':
            result = service.files().export(
                fileId=file_id,
                mimeType='text/plain'
            ).execute()
            return result.decode('utf-8')
        
        # Handle other files - download and extract
        request = service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        
        # Extract text based on file type
        if mime_type == 'application/pdf':
            pdf_document = fitz.open(stream=file_buffer.read(), filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
            return text
            
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            doc = DocxDoc(file_buffer)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
        elif mime_type == 'text/plain':
            return file_buffer.read().decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"Error extracting text from {file_id}: {e}")
    
    return ""

def search_google_drive(query, service, user=None):
    """Search for files in Google Drive with user-specific prioritization"""
    if not service:
        return []
    
    results = []
    
    try:
        # Determine folders to search
        folders_to_search = []
        
        # Add user-specific folder if user is provided
        # Normalize username for case-insensitive lookup
        user_folder_id = None
        if user:
            for folder_user, folder_id in SEARCH_CONFIG.get('user_folders', {}).items():
                if folder_user.lower() == user.lower():
                    user_folder_id = folder_id
                    user = folder_user  # Use correct case
                    break
        
        if user_folder_id:
            user_subfolders = get_subfolders(service, user_folder_id)
            user_folder_ids = [user_folder_id] + user_subfolders
            folders_to_search.append({
                'folder_ids': user_folder_ids,
                'weight': SEARCH_CONFIG['search_weights']['user_folder'],
                'source': f"{user}'s folder"
            })
        
        # Add team folder
        team_folder_id = SEARCH_CONFIG.get('default_team_folder', PARENT_FOLDER_ID)
        team_subfolders = get_subfolders(service, team_folder_id)
        team_folder_ids = [team_folder_id] + team_subfolders
        folders_to_search.append({
            'folder_ids': team_folder_ids,
            'weight': SEARCH_CONFIG['search_weights']['team_folder'],
            'source': "WMA Team folder"
        })
        
        # Search each folder group
        for folder_group in folders_to_search:
            folder_ids = folder_group['folder_ids'][:10]  # Limit to 10 folders per group
            folder_query = " or ".join([f"'{fid}' in parents" for fid in folder_ids])
            search_query = f"(name contains '{query}' or fullText contains '{query}') and trashed = false and ({folder_query})"
            
            response = service.files().list(
                q=search_query,
                fields="files(id, name, mimeType, modifiedTime)",
                pageSize=5
            ).execute()
            
            files = response.get('files', [])
            
            for file in files[:3]:  # Process first 3 files per folder group
                content = extract_text_from_drive_file(file['id'], file['mimeType'], service)
                if content and query.lower() in content.lower():
                    results.append({
                        'filename': file['name'],
                        'content': content[:2000],  # First 2000 chars for AI context
                        'full_content': content,  # Keep full content for detailed analysis
                        'weight': folder_group['weight'],
                        'source': folder_group['source']
                    })
                
    except Exception as e:
        print(f"Drive search error: {e}")
    
    # Sort results by weight (user folder results first)
    results.sort(key=lambda x: x.get('weight', 1.0), reverse=True)
    
    return results

def search_local_docs(query):
    """Search through local documents in app/docs folder"""
    docs_path = "app/docs"
    results = []
    
    # List of system files to exclude from search results
    system_files = ['WMA_AI_Agent_System_Prompt.txt', 'WMA_AI_Agent_System_Prompt.docx']
    
    if os.path.exists(docs_path):
        for filename in os.listdir(docs_path):
            # Skip system prompt files
            if filename in system_files:
                continue
            
            filepath = os.path.join(docs_path, filename)
            content = ""
            
            try:
                if filename.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                elif filename.endswith('.pdf'):
                    pdf_document = fitz.open(filepath)
                    for page in pdf_document:
                        content += page.get_text()
                    pdf_document.close()
                    
                elif filename.endswith('.docx'):
                    doc = DocxDoc(filepath)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                
                # Search for query in content
                if content and query.lower() in content.lower():
                    results.append({
                        'filename': filename,
                        'content': content[:2000],
                        'full_content': content
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return results

def get_system_prompt():
    """Load the WMA AI Agent system prompt for context"""
    system_prompt_path = "app/docs/WMA_AI_Agent_System_Prompt.txt"
    try:
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return ""

def ai_summarize(query, documents):
    """Use OpenAI GPT to intelligently summarize search results"""
    if not openai_client or not documents:
        # Fallback to simple extraction if no AI available
        simple_results = []
        for doc in documents:
            content = doc['content']
            index = content.lower().find(query.lower())
            if index != -1:
                start = max(0, index - 150)
                end = min(len(content), index + 150)
                snippet = content[start:end].strip()
                source_info = f" (from {doc.get('source', 'documents')})" if 'source' in doc else ""
                simple_results.append(f"From {doc['filename']}{source_info}: {snippet}")
        return "\n\n---\n\n".join(simple_results) if simple_results else f"No information found about '{query}'."
    
    # Prepare context for AI
    context = f"You are a helpful assistant searching documents for information about: {query}\n\n"
    context += "Here are the relevant documents:\n\n"
    
    for i, doc in enumerate(documents[:5], 1):  # Process up to 5 documents
        source_info = f" (from {doc.get('source', 'documents')})" if 'source' in doc else ""
        context += f"Document {i} - {doc['filename']}{source_info}:\n{doc['content']}\n\n"
    
    # Create prompt based on query type
    action_words = ['review', 'summarize', 'analyze', 'explain', 'describe', 'list', 'overview',
                   'what\'s new', 'what is new', 'whats new', 'latest', 'recent', 'update on',
                   'tell me about', 'give me', 'show me', 'find', 'look up', 'check on']
    query_lower = query.lower()
    is_action_query = any(word in query_lower for word in action_words)
    
    if is_action_query:
        # Special handling for action/command requests
        prompt = f"""The user asked: "{query}"
        
Please provide a helpful response based on the documents:
- If they want recent/latest info, focus on the most current information
- If they want a summary/review, provide key points and takeaways
- If they want an update, highlight what's new or changed
- Focus on answering their actual intent, not defining terms
- Keep the response clear, concise, and actionable
- Use natural language suitable for voice output"""
    else:
        prompt = f"""Based on the documents provided, please give a clear, concise answer to this query: "{query}"

Instructions:
- Synthesize information from all relevant documents
- Be specific and include key facts
- If quoting directly, mention which document it's from
- Keep the response under 300 words
- Focus on answering the user's specific question
- Use natural language suitable for text-to-speech"""

    try:
        # Get system prompt for additional context
        system_prompt = get_system_prompt()
        
        # Enhance system message with WMA context if available
        system_message = "You are a helpful document analysis assistant."
        if system_prompt:
            system_message = f"""You are the WMA AI Agent helping Jeff and his team analyze dealership documents. 
{system_prompt[:500]}...

Focus on providing clear, actionable insights from the documents provided."""
        
        # Combine context and prompt for OpenAI
        full_prompt = context + "\n" + prompt
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI summarization error: {e}")
        # Fallback to simple extraction
        return "\n\n---\n\n".join([f"From {doc['filename']}: {doc['content'][:300]}..." for doc in documents])

def search_all_sources(query, user=None):
    """Search both local files and Google Drive with user prioritization, then AI summarize"""
    all_documents = []
    
    # Search local files
    local_results = search_local_docs(query)
    all_documents.extend(local_results)
    
    # Search Google Drive if authenticated
    service = authenticate_gdrive()
    if service:
        drive_results = search_google_drive(query, service, user)
        all_documents.extend(drive_results)
    
    if not all_documents:
        return f"No information found about '{query}' in documents."
    
    # Use AI to summarize findings
    return ai_summarize(query, all_documents)

# HTML Templates
LOGIN_TEMPLATE = '''
<html>
    <head>
        <title>Smart Document Assistant - Login</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
            h1 { color: #333; text-align: center; }
            form { background: #f0f0f0; padding: 30px; border-radius: 5px; }
            input { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .error { color: red; text-align: center; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Smart Document Assistant</h1>
        <form method="post">
            <h2>Login</h2>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            <input type="text" name="username" placeholder="Username" required autofocus>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </body>
</html>
'''

HOME_TEMPLATE = '''
<html>
    <head>
        <title>Smart Document Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .user-info { float: right; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            .user-info a { color: #007bff; text-decoration: none; margin-left: 10px; }
            input { width: 400px; padding: 10px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .status { margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            .clear { clear: both; }
        </style>
    </head>
    <body>
        <div class="user-info">
            Welcome, {{ current_user.username }}
            {% if current_user.is_admin %}
            | <a href="/admin">Admin Panel</a>
            {% endif %}
            | <a href="/logout">Logout</a>
        </div>
        <div class="clear"></div>
        <h1>Smart Document Assistant with AI</h1>
        <form action="/search" method="get">
            <input type="text" name="q" placeholder="Ask a question..." required>
            <button type="submit">Search</button>
        </form>
        <div class="status">
            <p><strong>Status:</strong></p>
            <ul>
                <li>Google Drive: <span id="drive-status">Checking...</span></li>
                <li>AI (OpenAI GPT-4o-mini): <span id="ai-status">Checking...</span></li>
            </ul>
        </div>
        <script>
            fetch('/api/status').then(r => r.json()).then(data => {
                document.getElementById('drive-status').textContent = data.google_drive || 'Not configured';
                document.getElementById('ai-status').textContent = data.ai_enabled ? 'GPT Connected' : 'Not configured';
            });
        </script>
    </body>
</html>
'''

ADMIN_TEMPLATE = '''
<html>
    <head>
        <title>Admin Panel - Smart Document Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .back { float: right; color: #007bff; text-decoration: none; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background: #f0f0f0; }
            .add-user, .change-password { background: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0; }
            input, select { padding: 8px; margin: 5px; }
            button { padding: 8px 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .delete { background: #dc3545; }
            .delete:hover { background: #c82333; }
            .message { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .info { background: #d1ecf1; color: #0c5460; }
            .password-display { background: #fff3cd; color: #856404; padding: 10px; margin: 10px 0; border-radius: 5px; font-family: monospace; font-size: 16px; }
        </style>
    </head>
    <body>
        <a href="/" class="back">← Back to Search</a>
        <h1>Admin Panel</h1>
        
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        
        {% if new_password %}
        <div class="message info">
            <strong>Password changed successfully!</strong><br>
            User: {{ password_username }}<br>
            <div class="password-display">
                New Password: {{ new_password }}
            </div>
            <em>Please save this password. It will not be shown again.</em>
        </div>
        {% endif %}
        
        <div class="add-user">
            <h2>Add New User</h2>
            <form method="post" action="/admin/add-user">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="text" name="folder_id" placeholder="Google Drive Folder ID (optional)">
                <button type="submit">Add User</button>
            </form>
        </div>
        
        <div class="change-password">
            <h2>Change Password</h2>
            <form method="post" action="/admin/change-password">
                <select name="username" required>
                    <option value="">Select user...</option>
                    {% for username in users %}
                    <option value="{{ username }}">{{ username }}{% if username == 'Jeff' %} (Admin){% endif %}</option>
                    {% endfor %}
                </select>
                <input type="password" name="new_password" placeholder="New Password" required>
                <button type="submit">Change Password</button>
            </form>
        </div>
        
        <h2>Current Users</h2>
        <table>
            <tr>
                <th>Username</th>
                <th>Has Folder</th>
                <th>Actions</th>
            </tr>
            {% for username in users %}
            <tr>
                <td>{{ username }}</td>
                <td>{{ 'Yes' if username in user_folders else 'No' }}</td>
                <td>
                    {% if username != 'Jeff' %}
                    <form method="post" action="/admin/delete-user" style="display: inline;">
                        <input type="hidden" name="username" value="{{ username }}">
                        <button type="submit" class="delete" onclick="return confirm('Delete user {{ username }}?')">Delete</button>
                    </form>
                    {% else %}
                    <em>Admin</em>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = SEARCH_CONFIG.get('users', {})
        if username in users:
            stored_password = users[username]['password']
            
            # Handle placeholder passwords for initial setup
            if stored_password.startswith('NEEDS_REHASH:'):
                expected_password = stored_password.replace('NEEDS_REHASH:', '')
                if password == expected_password:
                    # Update with proper hash
                    users[username]['password'] = generate_password_hash(password)
                    try:
                        with open('search_config.json', 'w') as f:
                            json.dump(SEARCH_CONFIG, f, indent=2)
                    except:
                        pass
                    
                    user = User(username)
                    login_user(user, remember=True)
                    session.permanent = True
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('home'))
            elif check_password_hash(stored_password, password):
                user = User(username)
                login_user(user, remember=True)
                session.permanent = True
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid username or password')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    """Logout the user"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """Main search interface - requires login"""
    return render_template_string(HOME_TEMPLATE)

@app.route('/search')
@login_required
def search():
    """Browser-friendly search endpoint"""
    query = request.args.get('q', '')
    if not query:
        return '<p>Please provide a search query</p>'
    
    # Always search using the logged-in user's folder
    answer = search_all_sources(query, current_user.username)
    return f'''
    <html>
        <head>
            <title>Search Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .answer {{ background: #f0f0f0; padding: 20px; border-radius: 5px; line-height: 1.6; }}
                a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h2>Question: {query}</h2>
            <p><em>Searching {current_user.username}'s documents and WMA Team folder...</em></p>
            <div class="answer">
                {answer.replace(chr(10), '<br>')}
            </div>
            <p><a href="/">Ask another question</a></p>
        </body>
    </html>
    '''

@app.route('/admin')
@admin_required
def admin():
    """Admin panel for managing users"""
    users = list(SEARCH_CONFIG.get('users', {}).keys())
    user_folders = SEARCH_CONFIG.get('user_folders', {})
    
    message = request.args.get('message')
    message_type = request.args.get('message_type', 'success')
    new_password = request.args.get('new_password')
    password_username = request.args.get('password_username')
    
    return render_template_string(ADMIN_TEMPLATE, 
                                users=users, 
                                user_folders=user_folders,
                                message=message,
                                message_type=message_type,
                                new_password=new_password,
                                password_username=password_username)

@app.route('/admin/add-user', methods=['POST'])
@admin_required
def add_user():
    """Add a new user"""
    global SEARCH_CONFIG
    
    username = request.form.get('username')
    password = request.form.get('password')
    folder_id = request.form.get('folder_id')
    
    if not username or not password:
        return redirect(url_for('admin', message='Username and password required', message_type='error'))
    
    # Load current config
    config = SEARCH_CONFIG.copy()
    
    # Add user with hashed password
    if 'users' not in config:
        config['users'] = {}
    
    config['users'][username] = {
        'password': generate_password_hash(password)
    }
    
    # Add folder mapping if provided
    if folder_id:
        if 'user_folders' not in config:
            config['user_folders'] = {}
        config['user_folders'][username] = folder_id
    
    # Save config
    try:
        with open('search_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update global config
        SEARCH_CONFIG = config
        
        # Redirect with the plain password to display it once
        from urllib.parse import urlencode
        params = {
            'message': f'User {username} added successfully',
            'new_password': password,
            'password_username': username
        }
        return redirect(url_for('admin') + '?' + urlencode(params))
    except Exception as e:
        return redirect(url_for('admin', message=f'Error saving config: {e}', message_type='error'))

@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def delete_user():
    """Delete a user"""
    global SEARCH_CONFIG
    
    username = request.form.get('username')
    
    if username == 'Jeff':
        return redirect(url_for('admin', message='Cannot delete admin user', message_type='error'))
    
    # Load current config
    config = SEARCH_CONFIG.copy()
    
    # Remove user
    if username in config.get('users', {}):
        del config['users'][username]
    
    # Remove folder mapping
    if username in config.get('user_folders', {}):
        del config['user_folders'][username]
    
    # Save config
    try:
        with open('search_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update global config
        SEARCH_CONFIG = config
        
        return redirect(url_for('admin', message=f'User {username} deleted'))
    except Exception as e:
        return redirect(url_for('admin', message=f'Error saving config: {e}', message_type='error'))

@app.route('/admin/change-password', methods=['POST'])
@admin_required
def change_password():
    """Change a user password"""
    global SEARCH_CONFIG
    
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    
    if not username or not new_password:
        return redirect(url_for('admin', message='Username and new password required', message_type='error'))
    
    # Load current config
    config = SEARCH_CONFIG.copy()
    
    # Check if user exists
    if username not in config.get('users', {}):
        return redirect(url_for('admin', message=f'User {username} not found', message_type='error'))
    
    # Update password with hash
    config['users'][username]['password'] = generate_password_hash(new_password)
    
    # Save config
    try:
        with open('search_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update global config
        SEARCH_CONFIG = config
        
        # Redirect with the plain password to display it once
        from urllib.parse import urlencode
        params = {
            'message': f'Password changed for {username}',
            'new_password': new_password,
            'password_username': username
        }
        return redirect(url_for('admin') + '?' + urlencode(params))
    except Exception as e:
        return redirect(url_for('admin', message=f'Error saving config: {e}', message_type='error'))

# API Endpoints - maintain backward compatibility
@app.route('/api/search')
def api_search():
    """API endpoint - supports both authenticated and user parameter"""
    query = request.args.get('q', '')
    user = request.args.get('user', '')
    
    if not query:
        return 'Please provide a search query', 400
    
    # If authenticated via web, use current user
    if current_user.is_authenticated:
        user = current_user.username
    # Otherwise, use the user parameter (for iOS shortcuts)
    elif not user:
        return 'User parameter required for API access', 401
    
    answer = search_all_sources(query, user)
    
    # For iOS Shortcuts - return plain text
    if request.headers.get('User-Agent', '').startswith('Shortcuts'):
        return answer
    
    # For other API clients - return JSON
    return jsonify({
        'query': query,
        'user': user,
        'answer': answer,
        'ai_enabled': bool(openai_client)
    })

@app.route('/api/search/text')
@app.route('/api/search/text/<username>')
def api_search_text(username=None):
    """Pure text endpoint for iOS - no JSON, just text"""
    query = request.args.get('q', '')
    user = username or request.args.get('user', '')  # Try URL path first, then parameter
    
    # Debug logging
    print(f"API Search Text - Query: '{query}', User: '{user}', Username from path: '{username}'")
    print(f"Full URL: {request.url}")
    print(f"All args: {dict(request.args)}")
    
    if not query:
        return 'Please provide a search query'
    
    # For API access, user parameter is sufficient (iOS Shortcuts compatibility)
    if not user and not current_user.is_authenticated:
        return 'User parameter required for API access'
    
    # Use authenticated user if logged in, otherwise use parameter
    if current_user.is_authenticated:
        user = current_user.username
    
    # Validate the user exists (check both user_folders and users)
    valid_users = list(SEARCH_CONFIG.get('user_folders', {}).keys())
    valid_users.extend(list(SEARCH_CONFIG.get('users', {}).keys()))
    
    # Make comparison case-insensitive and normalize username
    user_found = False
    for valid_user in valid_users:
        if user.lower() == valid_user.lower():
            user = valid_user  # Use the correct case from config
            user_found = True
            break
    
    if not user_found:
        return f'Unknown user: {user}. Valid users: {", ".join(sorted(set(valid_users)))}'
    
    answer = search_all_sources(query, user)
    return answer, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/status')
def api_status():
    """Check Google Drive and AI connection status"""
    service = authenticate_gdrive()
    drive_status = 'not configured'
    
    if service:
        try:
            service.files().list(pageSize=1).execute()
            drive_status = 'connected'
        except:
            drive_status = 'authentication failed'
    
    return jsonify({
        'google_drive': drive_status,
        'ai_enabled': bool(openai_client),
        'ai_model': 'gpt-4o-mini' if openai_client else None,
        'authenticated': current_user.is_authenticated,
        'user': current_user.username if current_user.is_authenticated else None
    })

@app.route('/api/users')
def api_users():
    """Get list of available users for search filtering"""
    users = list(SEARCH_CONFIG.get('user_folders', {}).keys())
    users = [u for u in users if u != 'WMA Team']
    users.sort()
    return jsonify({
        'users': users,
        'total': len(users)
    })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return 'OK', 200

@app.route('/voice')
def voice_search():
    """Alternative endpoint for iOS with user parameter first"""
    user = request.args.get('user', '')
    query = request.args.get('q', '')
    
    print(f"Voice Search - User: '{user}', Query: '{query}'")
    
    if not query:
        return 'Please provide a search query'
    
    if not user:
        return 'User parameter required'
    
    # Validate and normalize username
    user_found = False
    for valid_user in list(SEARCH_CONFIG.get('users', {}).keys()):
        if user.lower() == valid_user.lower():
            user = valid_user
            user_found = True
            break
    
    if not user_found:
        return f'Unknown user: {user}'
    
    answer = search_all_sources(query, user)
    return answer, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    # Initialize default admin user if no users exist
    if not SEARCH_CONFIG.get('users'):
        print("No users found. Creating default admin user...")
        SEARCH_CONFIG['users'] = {
            'Jeff': {
                'password': generate_password_hash('changeme')  # Default password
            }
        }
        try:
            with open('search_config.json', 'w') as f:
                json.dump(SEARCH_CONFIG, f, indent=2)
            print("Default admin user created: Jeff (password: changeme)")
            print("IMPORTANT: Change the password after first login!")
        except Exception as e:
            print(f"Could not save default user: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask with Authentication on port {port}")
    print(f"AI enabled: {bool(openai_client)}")
    print(f"VERSION: 4.0.0-Authentication")
    app.run(host='0.0.0.0', port=port)