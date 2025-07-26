"""
Ultra-simple text-only response for iOS Shortcuts
Returns ONLY plain text, no HTML at all
"""
import os
from urllib.parse import unquote

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
        return f"No information found about '{query}'. Try: Jeff, WMA, Ford, dealership"

# FastAPI-style response
if __name__ == "__main__":
    import sys
    import streamlit as st
    
    # Try to get query parameter
    query = None
    
    # Method 1: From query params
    try:
        params = st.experimental_get_query_params()
        if "q" in params:
            query = unquote(params["q"][0])
    except:
        pass
    
    # If we have a query, return ONLY the text response
    if query:
        answer = search_local_docs(query)
        # Clear everything and show only text
        st.text(answer)
        st.stop()  # Stop rendering anything else
    else:
        # Normal web interface
        st.title("Smart Document Assistant")
        st.write("Add ?q=your+question to the URL")