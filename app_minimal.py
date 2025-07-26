"""
Minimal Streamlit app that works with iOS Shortcuts
"""
import streamlit as st
import os
from urllib.parse import unquote

# Hide all Streamlit UI elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp > header {display: none;}
</style>
"""

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
        return f"No information found about '{query}'. Try: Jeff, WMA, Ford, dealership"

# Get query parameter
try:
    params = st.experimental_get_query_params()
    query = params.get("q", [""])[0]
    if query:
        query = unquote(query)
except:
    query = ""

if query:
    # Hide all UI and show only text
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    answer = search_local_docs(query)
    # Use container for clean output
    container = st.container()
    with container:
        st.text(answer)  # Plain text for iOS
else:
    # Normal interface
    st.title("Smart Document Assistant")
    st.write("Add ?q=your+question to the URL")