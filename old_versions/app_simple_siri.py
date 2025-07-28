"""
Smart Document Assistant - Simple Siri Integration
Robust URL parameter handling for voice queries
"""
import streamlit as st
from gtts import gTTS
import io
from urllib.parse import unquote

st.set_page_config(
    page_title="Smart Document Assistant", 
    page_icon="🎙️",
    layout="centered"
)

def generate_answer(question: str) -> str:
    """Generate answer - placeholder for your RAG logic"""
    if not question:
        return "No question received."
    return f"Based on your documents, here's what I found about '{question}': This is a placeholder response. In the full implementation, this will query your Google Drive documents and provide a relevant summary."

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS"""
    try:
        text = text[:500] + "..." if len(text) > 500 else text
        tts = gTTS(text=text, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")
        return None

# Header
st.title("🎙️ Smart Document Assistant")

# Try to get query from URL
try:
    # Get all query parameters
    params = st.experimental_get_query_params() if hasattr(st, 'experimental_get_query_params') else {}
    
    # Also try the new API
    if not params and hasattr(st, 'query_params'):
        params = dict(st.query_params)
    
    # Get the 'q' parameter
    voice_query = params.get('q', [''])[0] if isinstance(params.get('q'), list) else params.get('q', '')
    
    # Decode URL encoding
    if voice_query:
        voice_query = unquote(voice_query)
        
except Exception as e:
    st.error(f"Error reading URL parameters: {str(e)}")
    voice_query = ""

# Process voice query if present
if voice_query:
    st.success(f"📱 Voice query received: **{voice_query}**")
    
    # Generate answer
    answer = generate_answer(voice_query)
    
    # Display answer
    st.markdown("### 📢 Answer:")
    st.write(answer)
    
    # Generate and play audio
    audio_data = text_to_speech(answer)
    if audio_data:
        st.audio(audio_data, format='audio/mp3')
    
    # Add a clear button
    if st.button("🔄 Clear and Ask New Question"):
        # Clear query params
        if hasattr(st, 'experimental_set_query_params'):
            st.experimental_set_query_params()
        elif hasattr(st, 'query_params'):
            st.query_params.clear()
        st.rerun()

else:
    # No voice query - show regular interface
    st.markdown("### 📱 Setup Siri Shortcut (iPhone)")
    
    with st.expander("Quick Setup Instructions", expanded=True):
        st.markdown("""
        1. **Copy this URL:**
        ```
        https://web-production-5c94.up.railway.app
        ```
        
        2. **Open Shortcuts app** on iPhone
        
        3. **Create New Shortcut:**
        - Add Action → **Text**
        - Type: `Spoken Text`
        - Add Action → **Get Contents of URL**
        - URL: The URL above + `?q=` + the Text variable
        
        4. **Add to Siri** with phrase like:
        - "Ask my assistant"
        - "Search documents"
        
        5. **Use it:**
        - "Hey Siri, ask my assistant about Q2 sales"
        """)
    
    # Manual input form
    st.markdown("---")
    st.markdown("### ⌨️ Or Type Your Question")
    
    with st.form("manual_form"):
        question = st.text_input("Your question:", placeholder="What would you like to know?")
        submit = st.form_submit_button("🚀 Ask", type="primary", use_container_width=True)
    
    if submit and question:
        # Generate answer
        answer = generate_answer(question)
        
        st.markdown("### Answer:")
        st.write(answer)
        
        # Generate audio
        audio_data = text_to_speech(answer)
        if audio_data:
            st.audio(audio_data, format='audio/mp3')

# Test URLs section
st.markdown("---")
with st.expander("🧪 Test URLs"):
    base_url = "https://web-production-5c94.up.railway.app"
    
    st.markdown("Click these to test:")
    st.markdown(f"- [{base_url}?q=test]({base_url}?q=test)")
    st.markdown(f"- [{base_url}?q=summarize reports]({base_url}?q=summarize%20reports)")
    st.markdown(f"- [{base_url}?q=what were sales last month]({base_url}?q=what%20were%20sales%20last%20month)")

# Footer
st.markdown(
    """<p style='text-align: center; color: #888; margin-top: 2rem;'>
    Voice-enabled via Siri Shortcuts • Works while driving
    </p>""", 
    unsafe_allow_html=True
)