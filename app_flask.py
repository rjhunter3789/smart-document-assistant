#!/usr/bin/env python3
"""
Flask app with Google Drive integration for iOS Shortcuts
Searches both local files and Google Drive documents
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

app = Flask(__name__)

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
PARENT_FOLDER_ID = "1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6"  # From existing code

def get_google_credentials():
    """Get Google credentials from environment variables or file"""
    # First try environment variables (for Railway)
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
    
    # Try loading from credentials.json file
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
            
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def search_google_drive(query, service):
    """Search for files in Google Drive"""
    if not service:
        return []
    
    results = []
    try:
        # Search for files containing the query in name or content
        search_query = f"(name contains '{query}' or fullText contains '{query}') and trashed = false"
        
        response = service.files().list(
            q=search_query,
            fields="files(id, name, mimeType, modifiedTime)",
            pageSize=10
        ).execute()
        
        files = response.get('files', [])
        
        for file in files:
            # Get file content based on type
            content = extract_text_from_drive_file(file['id'], file['mimeType'], service)
            if content and query.lower() in content.lower():
                # Extract relevant snippet
                index = content.lower().find(query.lower())
                start = max(0, index - 100)
                end = min(len(content), index + 200)
                snippet = content[start:end].strip()
                results.append(f"From Drive - {file['name']}: ...{snippet}...")
                
    except Exception as e:
        print(f"Drive search error: {e}")
    
    return results

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

def search_local_docs(query):
    """Search through local documents in app/docs folder"""
    docs_path = "app/docs"
    results = []
    
    if os.path.exists(docs_path):
        for filename in os.listdir(docs_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(docs_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            # Extract relevant snippet
                            index = content.lower().find(query.lower())
                            start = max(0, index - 100)
                            end = min(len(content), index + 200)
                            snippet = content[start:end].strip()
                            results.append(f"From {filename}: ...{snippet}...")
                except:
                    pass
    
    return results

def search_all_sources(query):
    """Search both local files and Google Drive"""
    results = []
    
    # Search local files
    local_results = search_local_docs(query)
    results.extend(local_results)
    
    # Search Google Drive if authenticated
    service = authenticate_gdrive()
    if service:
        drive_results = search_google_drive(query, service)
        results.extend(drive_results)
    else:
        results.append("Note: Google Drive not connected. Searching local files only.")
    
    if not results:
        return f"No information found about '{query}' in documents."
    
    return "\n\n".join(results)

@app.route('/')
def home():
    """Simple HTML interface for browser testing"""
    return '''
    <html>
        <head><title>Smart Document Assistant</title></head>
        <body>
            <h1>Smart Document Assistant with Google Drive</h1>
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Ask a question..." size="50">
                <button type="submit">Search</button>
            </form>
            <p>API Endpoints:</p>
            <ul>
                <li>/api/search?q=your+question - JSON response</li>
                <li>/api/search/text?q=your+question - Plain text for iOS</li>
                <li>/api/status - Check Google Drive connection</li>
            </ul>
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
        <body>
            <h2>Question: {query}</h2>
            <pre>{answer}</pre>
            <a href="/">Ask another question</a>
        </body>
    </html>
    '''

@app.route('/api/search')
def api_search():
    """iOS-friendly API endpoint - returns plain text"""
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
        'answer': answer
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
    """Check Google Drive connection status"""
    service = authenticate_gdrive()
    if service:
        try:
            # Try to list one file to verify connection
            service.files().list(pageSize=1).execute()
            return jsonify({
                'google_drive': 'connected',
                'status': 'ok'
            })
        except:
            return jsonify({
                'google_drive': 'error',
                'status': 'authentication failed'
            })
    else:
        return jsonify({
            'google_drive': 'not configured',
            'status': 'credentials missing'
        })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask with Google Drive integration on port {port}")
    app.run(host='0.0.0.0', port=port)