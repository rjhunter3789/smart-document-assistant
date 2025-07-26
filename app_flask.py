#!/usr/bin/env python3
"""
Flask app for iOS Shortcuts compatibility
Returns plain text and JSON responses
"""
from flask import Flask, request, jsonify
import os
import json
from search_engine import search_local_docs

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)