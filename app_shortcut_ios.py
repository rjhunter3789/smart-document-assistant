"""
Smart Document Assistant - iOS Shortcut Optimized
Minimal HTML output for better iOS Shortcuts compatibility
"""
import streamlit as st
import os
from urllib.parse import unquote

# Minimal page config
st.set_page_config(page_title="Document Assistant", layout="centered")

def search_local_docs(query):
    """Search through local documents"""
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
                            results.append(f"From {filename}: ...{snippet}...")
                except:
                    pass
    
    if results:
        return " ".join(results[:2])
    else:
        return f"No information found about '{query}'. Try another search term."

# Get query parameter - try multiple methods
voice_query = ""

# Method 1: New API
try:
    voice_query = st.query_params.get("q", "")
except:
    pass

# Method 2: Old API
if not voice_query:
    try:
        params = st.experimental_get_query_params()
        voice_query = params.get("q", [""])[0]
    except:
        pass

# URL decode
if voice_query:
    voice_query = unquote(voice_query)

# If we have a query, show minimal response
if voice_query:
    # Search for answer
    answer = search_local_docs(voice_query)
    
    # Ultra-minimal output for iOS
    st.write(f"**Question:** {voice_query}")
    st.write(f"**Answer:** {answer}")
    
else:
    # Regular interface
    st.title("Document Assistant")
    st.write("Add ?q=your+question to search")
    
    # Test form
    with st.form("search"):
        query = st.text_input("Test a search:")
        if st.form_submit_button("Search"):
            if query:
                answer = search_local_docs(query)
                st.write(f"**Result:** {answer}")