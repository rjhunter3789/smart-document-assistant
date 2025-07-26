#!/usr/bin/env python3
"""
Dead simple HTTP server for iOS Shortcuts
Returns ONLY plain text, no HTML wrapping
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote
import os
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def search_docs(self, query):
        """Search documents"""
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
                                index = content.lower().find(query.lower())
                                start = max(0, index - 100)
                                end = min(len(content), index + 200)
                                snippet = content[start:end].strip()
                                results.append(f"From {filename}: {snippet}")
                    except:
                        pass
        
        if results:
            return " ".join(results[:2])
        return f"No information found about {query}"
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'q' in params:
            query = unquote(params['q'][0])
            response = self.search_docs(query)
            
            # Send plain text response
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            # Simple HTML for browser
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = """
            <h1>Smart Document Assistant</h1>
            <p>Add ?q=yourquery to search</p>
            <p>Example: ?q=Jeff</p>
            """
            self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Server running on port {port}")
    server.serve_forever()