"""
Smart Document Assistant - iOS Shortcut Debug Version
Enhanced URL parameter handling and debugging for iOS Shortcuts
"""
import streamlit as st
from datetime import datetime
import os
import json
from urllib.parse import unquote, parse_qs
import sys

# Configure page
st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon="🎙️",
    layout="centered"
)

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

def get_query_parameter():
    """Get query parameter using multiple methods for compatibility"""
    voice_query = None
    debug_info = []
    
    # Method 1: New Streamlit API
    try:
        if hasattr(st, 'query_params'):
            params = st.query_params
            voice_query = params.get("q", "")
            debug_info.append(f"Method 1 (new API): {voice_query}")
    except Exception as e:
        debug_info.append(f"Method 1 failed: {str(e)}")
    
    # Method 2: Old Streamlit API
    if not voice_query:
        try:
            if hasattr(st, 'experimental_get_query_params'):
                params = st.experimental_get_query_params()
                voice_query = params.get("q", [""])[0] if "q" in params else ""
                debug_info.append(f"Method 2 (old API): {voice_query}")
        except Exception as e:
            debug_info.append(f"Method 2 failed: {str(e)}")
    
    # Method 3: Session state (if passed from another page)
    if not voice_query:
        try:
            voice_query = st.session_state.get('voice_query', '')
            if voice_query:
                debug_info.append(f"Method 3 (session): {voice_query}")
        except Exception as e:
            debug_info.append(f"Method 3 failed: {str(e)}")
    
    # URL decode the query
    if voice_query:
        try:
            voice_query = unquote(voice_query)
            debug_info.append(f"URL decoded: {voice_query}")
        except:
            pass
    
    return voice_query, debug_info

# Get query parameter
voice_query, debug_info = get_query_parameter()

# Check if we're in shortcut mode (has query parameter)
if voice_query:
    # Minimal response for iOS Shortcuts
    answer = search_local_docs(voice_query)
    
    # For iOS Shortcuts, we want the simplest possible response
    # Using markdown with minimal formatting
    st.markdown(f"""
### Question: {voice_query}

{answer}
""")
    
    # Add debug info in an expander (won't show in Quick Look)
    with st.expander("Debug Information", expanded=False):
        st.write("Query received:", voice_query)
        st.write("Debug steps:")
        for info in debug_info:
            st.write(f"- {info}")
        st.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    # Normal web interface
    st.title("🎙️ Smart Document Assistant")
    st.markdown("### Debug Version for iOS Shortcuts")
    
    # Show status
    st.info("No query parameter detected. Add ?q=your+question to the URL")
    
    # Debug information
    with st.expander("🔍 Debug Information", expanded=True):
        st.write("**Current URL Parameters:**")
        
        # Try to get all parameters
        try:
            if hasattr(st, 'query_params'):
                all_params = dict(st.query_params)
                st.json(all_params)
            elif hasattr(st, 'experimental_get_query_params'):
                all_params = st.experimental_get_query_params()
                st.json(all_params)
            else:
                st.write("No query parameter API available")
        except Exception as e:
            st.error(f"Error getting parameters: {str(e)}")
        
        st.write("**Debug steps attempted:**")
        for info in debug_info:
            st.write(f"- {info}")
    
    # Test section
    st.markdown("---")
    st.markdown("### 🧪 Test URLs")
    
    base_url = "https://web-production-5c94.up.railway.app"
    
    # Show clickable test links
    test_queries = [
        "test",
        "Jeff",
        "sales report",
        "Q2 summary"
    ]
    
    st.write("Click these links to test:")
    for query in test_queries:
        encoded_query = query.replace(" ", "%20")
        url = f"{base_url}?q={encoded_query}"
        st.markdown(f"- [{query}]({url})")
    
    # Manual test form
    st.markdown("---")
    st.markdown("### ⌨️ Manual Test")
    
    with st.form("test_form"):
        test_query = st.text_input("Enter test query:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Test with Redirect"):
                if test_query:
                    # Set query params and rerun
                    if hasattr(st, 'query_params'):
                        st.query_params["q"] = test_query
                    st.rerun()
        
        with col2:
            if st.form_submit_button("Generate URL"):
                if test_query:
                    encoded = test_query.replace(" ", "%20")
                    st.code(f"{base_url}?q={encoded}")
    
    # iOS Shortcut Setup
    st.markdown("---")
    st.markdown("### 📱 iOS Shortcut Setup")
    
    with st.expander("Detailed Instructions"):
        st.markdown("""
        **Method 1: Simple URL**
        1. Open Shortcuts app
        2. Create new shortcut
        3. Add action: "URL" 
           - Set to: `https://web-production-5c94.up.railway.app?q=`
        4. Add action: "Text" 
           - Tap and select "Shortcut Input"
        5. Add action: "Combine Text"
           - Combine the URL and Text
        6. Add action: "Open URLs"
        7. Name it and add to Siri
        
        **Method 2: Get Contents of URL**
        1. Open Shortcuts app
        2. Create new shortcut
        3. Add action: "Text"
           - Tap and select "Shortcut Input" 
        4. Add action: "URL"
           - Set to: `https://web-production-5c94.up.railway.app?q=`
        5. Add action: "Combine Text"
           - First item: The URL
           - Second item: The Text (Shortcut Input)
        6. Add action: "Get Contents of URL"
           - URL: Combined Text
        7. Add action: "Speak"
           - Text: Contents of URL
        8. Name it and add to Siri
        
        **Test your shortcut:**
        - Say: "Hey Siri, [your shortcut name] test"
        - It should open this page with ?q=test
        """)
    
    # Show available documents
    st.markdown("---")
    st.markdown("### 📁 Available Documents")
    
    if os.path.exists("app/docs"):
        doc_files = [f for f in os.listdir("app/docs") if f.endswith('.txt')]
        if doc_files:
            st.write("Documents in the system:")
            for f in doc_files:
                st.write(f"- {f}")
        else:
            st.warning("No .txt documents found in app/docs/")
    else:
        st.error("Document directory 'app/docs' not found")

# Footer
st.markdown("---")
st.caption(f"Debug Version • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")