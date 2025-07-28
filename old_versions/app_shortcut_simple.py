"""
Simple URL parameter handler for Shortcuts
Returns PLAIN TEXT instead of HTML when ?q= parameter is present
"""
import streamlit as st
from datetime import datetime
import os

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
        return " ".join(results[:2])  # Return first 2 results
    else:
        return f"No specific information found about '{query}' in the documents. Please try a different search term."

# Get query parameter using multiple methods for compatibility
voice_query = ""

# Try new Streamlit API first
try:
    voice_query = st.query_params.get("q", "")
except:
    # Fall back to old API
    try:
        query_params = st.experimental_get_query_params()
        voice_query = query_params.get("q", [""])[0]
    except:
        pass

# URL decode if needed
if voice_query:
    from urllib.parse import unquote
    voice_query = unquote(voice_query)

if voice_query:
    # For URL parameters, search docs and return plain text
    answer = search_local_docs(voice_query)
    
    # Display as plain text for Shortcuts to speak
    # Using st.text() for pure text output
    st.text(answer)
    
    # Add a minimal separator and query info
    st.text("---")
    st.text(f"Query: {voice_query}")
else:
    # Normal web interface
    st.title("Smart Document Assistant v3.1.1")
    st.write("Add ?q=your+question to the URL to get a response")
    
    # Show available documents
    if os.path.exists("app/docs"):
        st.write("Available documents:")
        for f in os.listdir("app/docs"):
            if f.endswith('.txt'):
                st.write(f"- {f}")