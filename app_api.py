"""
Pure API endpoint for iOS Shortcuts - no Streamlit
Returns only plain text
"""
from flask import Flask, request, Response
import os

app = Flask(__name__)

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
        return " ".join(results[:2])  # Return first 2 results
    else:
        return f"No information found about '{query}'. Try asking about Jeff, WMA, Ford, or dealerships."

@app.route('/')
def home():
    query = request.args.get('q', '')
    
    if query:
        # Return plain text response for shortcuts
        answer = search_local_docs(query)
        return Response(answer, mimetype='text/plain')
    else:
        # Return simple HTML for browser
        return """
        <h1>Smart Document Assistant API</h1>
        <p>Add ?q=your+question to the URL to get a response</p>
        <p>Example: ?q=Jeff</p>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)