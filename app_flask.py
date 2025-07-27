#!/usr/bin/env python3
"""
Flask app with Google Drive integration and Claude AI summarization
Searches documents and provides intelligent summaries
"""
from flask import Flask, request, jsonify
import os
import json
import io
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import fitz  # PyMuPDF
from docx import Document as DocxDoc
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI (API key from environment)
openai_client = None
api_key = os.environ.get('OPENAI_API_KEY')
if api_key:
    print(f"OpenAI API key found: {api_key[:10]}...")
    try:
        openai_client = OpenAI(api_key=api_key)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
else:
    print("No OPENAI_API_KEY found in environment")

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
PARENT_FOLDER_ID = "1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6"  # WMA RAG folder

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

def search_google_drive(query, service):
    """Search for files in Google Drive within WMA RAG folder"""
    if not service:
        return []
    
    results = []
    
    try:
        # Get all subfolders
        all_folders = get_subfolders(service, PARENT_FOLDER_ID)
        folder_ids = [PARENT_FOLDER_ID] + all_folders
        
        # Build query to search in main folder and all subfolders
        folder_query = " or ".join([f"'{fid}' in parents" for fid in folder_ids[:10]])
        search_query = f"(name contains '{query}' or fullText contains '{query}') and trashed = false and ({folder_query})"
        
        response = service.files().list(
            q=search_query,
            fields="files(id, name, mimeType, modifiedTime)",
            pageSize=5
        ).execute()
        
        files = response.get('files', [])
        
        for file in files[:3]:  # Process first 3 files
            content = extract_text_from_drive_file(file['id'], file['mimeType'], service)
            if content and query.lower() in content.lower():
                results.append({
                    'filename': file['name'],
                    'content': content[:2000],  # First 2000 chars for AI context
                    'full_content': content  # Keep full content for detailed analysis
                })
                
    except Exception as e:
        print(f"Drive search error: {e}")
    
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
                simple_results.append(f"From {doc['filename']}: {snippet}")
        return "\n\n---\n\n".join(simple_results) if simple_results else f"No information found about '{query}'."
    
    # Prepare context for Claude
    context = f"You are a helpful assistant searching documents for information about: {query}\n\n"
    context += "Here are the relevant documents:\n\n"
    
    for i, doc in enumerate(documents[:3], 1):
        context += f"Document {i} - {doc['filename']}:\n{doc['content']}\n\n"
    
    # Create prompt for Claude
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
            model="gpt-4o-mini",  # Fast and affordable
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

def search_all_sources(query):
    """Search both local files and Google Drive, then AI summarize"""
    all_documents = []
    
    # Search local files
    local_results = search_local_docs(query)
    all_documents.extend(local_results)
    
    # Search Google Drive if authenticated
    service = authenticate_gdrive()
    if service:
        drive_results = search_google_drive(query, service)
        all_documents.extend(drive_results)
    
    if not all_documents:
        return f"No information found about '{query}' in documents."
    
    # Use AI to summarize findings
    return ai_summarize(query, all_documents)

@app.route('/')
def home():
    """Simple HTML interface for browser testing"""
    return '''
    <html>
        <head>
            <title>Smart Document Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                input { width: 400px; padding: 10px; font-size: 16px; }
                button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .status { margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            </style>
        </head>
        <body>
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

@app.route('/search')
def search():
    """Browser-friendly search endpoint"""
    query = request.args.get('q', '')
    if not query:
        return '<p>Please provide a search query</p>'
    
    answer = search_all_sources(query)
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
            <div class="answer">
                {answer.replace(chr(10), '<br>')}
            </div>
            <p><a href="/">Ask another question</a></p>
        </body>
    </html>
    '''

@app.route('/api/search')
def api_search():
    """API endpoint - returns JSON or plain text"""
    query = request.args.get('q', '')
    if not query:
        return 'Please provide a search query', 400
    
    answer = search_all_sources(query)
    
    # For iOS Shortcuts - return plain text
    if request.headers.get('User-Agent', '').startswith('Shortcuts'):
        return answer
    
    # For other API clients - return JSON
    return jsonify({
        'query': query,
        'answer': answer,
        'ai_enabled': bool(openai_client)
    })

@app.route('/api/search/text')
def api_search_text():
    """Pure text endpoint for iOS - no JSON, just text"""
    query = request.args.get('q', '')
    if not query:
        return 'Please provide a search query'
    
    answer = search_all_sources(query)
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
        'ai_model': 'gpt-4o-mini' if openai_client else None
    })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask with Google Drive and AI integration on port {port}")
    print(f"AI enabled: {bool(openai_client)}")
    print(f"VERSION: 3.3.2-OpenAI")
    app.run(host='0.0.0.0', port=port)