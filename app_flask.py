#!/usr/bin/env python3
"""
Flask app for iOS Shortcuts compatibility
Returns plain text and JSON responses
"""
from flask import Flask, request, jsonify
import os
import json

# Simple document search function
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
    
    if results:
        return "\n\n".join(results)
    else:
        return f"No information found about '{query}' in local documents."

app = Flask(__name__)

@app.route('/')
def home():
    """Simple HTML interface for browser testing"""
    return '''
    <html>
        <head><title>Smart Document Assistant</title></head>
        <body>
            <h1>Smart Document Assistant</h1>
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Ask a question..." size="50">
                <button type="submit">Search</button>
            </form>
            <p>Or use the API: /api/search?q=your+question</p>
        </body>
    </html>
    '''

@app.route('/search')
def search():
    """Browser-friendly search endpoint"""
    query = request.args.get('q', '')
    if not query:
        return '<p>Please provide a search query</p>'
    
    answer = search_local_docs(query)
    return f'''
    <html>
        <body>
            <h2>Question: {query}</h2>
            <p>{answer}</p>
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
    
    answer = search_local_docs(query)
    
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
    
    answer = search_local_docs(query)
    return answer, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port)