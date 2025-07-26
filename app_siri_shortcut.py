"""
Smart Document Assistant - Direct Voice Integration
Works with Siri Shortcuts / Google Assistant for TRUE hands-free
"""
import streamlit as st
from gtts import gTTS
import io
from datetime import datetime

st.set_page_config(
    page_title="Smart Document Assistant", 
    page_icon="🎙️",
    layout="centered"
)

# Check if this is a direct voice request via URL parameter
query_params = st.query_params
voice_query = query_params.get("q", "")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

def generate_answer(question: str) -> str:
    """Generate answer - placeholder for your RAG logic"""
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
    except:
        return None

# Header
st.title("🎙️ Smart Document Assistant")

# If there's a voice query from URL, process it immediately
if voice_query:
    st.info(f"📱 Voice command received: *{voice_query}*")
    
    with st.spinner("Processing your voice request..."):
        answer = generate_answer(voice_query)
        audio_data = text_to_speech(answer)
        
        # Add to history
        st.session_state.history.append({
            'time': datetime.now().strftime("%I:%M %p"),
            'question': voice_query,
            'answer': answer
        })
    
    # Display the answer prominently
    st.success("### 📢 Answer:")
    st.write(answer)
    
    if audio_data:
        st.audio(audio_data, autoplay=True)
    
    # Clear the URL parameter
    st.query_params.clear()

else:
    # Regular interface
    st.markdown("""
    ### 🚀 Ultimate Hands-Free Setup
    
    **For iPhone (Siri Shortcut):**
    1. Save this URL as a Safari bookmark
    2. Open Shortcuts app
    3. Create shortcut: "Get Contents of URL"
    4. URL: `https://your-app.railway.app?q=[Ask for Text]`
    5. Name it: "Ask Document Assistant"
    6. Say: "Hey Siri, Ask Document Assistant"
    
    **For Android (Google Assistant):**
    1. Open Google Assistant
    2. Say: "Open smart document assistant and search for [your question]"
    
    **Direct URL Access:**
    ```
    https://your-app.railway.app?q=YOUR_QUESTION
    ```
    """)
    
    # Manual input as fallback
    with st.form("manual_form"):
        question = st.text_input("Or type your question here:")
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🚀 Ask", type="primary", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🔄 Clear History", use_container_width=True)
    
    if submit and question:
        with st.spinner("Processing..."):
            answer = generate_answer(question)
            audio_data = text_to_speech(answer)
            
            st.session_state.history.append({
                'time': datetime.now().strftime("%I:%M %p"),
                'question': question,
                'answer': answer
            })
        
        st.success("### Answer:")
        st.write(answer)
        
        if audio_data:
            st.audio(audio_data)
    
    if clear:
        st.session_state.history = []
        st.rerun()

# Show history
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 Recent Questions")
    
    for item in reversed(st.session_state.history[-5:]):  # Show last 5
        with st.expander(f"{item['time']} - {item['question'][:50]}..."):
            st.write(f"**Q:** {item['question']}")
            st.write(f"**A:** {item['answer']}")

# Quick copy URLs for setup
st.markdown("---")
with st.expander("🔧 Setup Helper"):
    base_url = "https://web-production-5c94.up.railway.app"
    
    st.markdown("**Example URLs for testing:**")
    st.code(f"{base_url}?q=Summarize the Q2 report")
    st.code(f"{base_url}?q=What were last month sales")
    
    st.markdown("""
    **Siri Shortcut Setup (Detailed):**
    1. Copy one of the URLs above
    2. Open it in Safari
    3. Tap Share → Add to Home Screen
    4. Open Shortcuts app
    5. New Shortcut → Add Action
    6. Search "Open App" → Select your bookmark
    7. Add to Siri with phrase "Ask my assistant"
    
    Now you can say: "Hey Siri, ask my assistant to summarize the Q2 report"
    """)

# Footer
st.markdown(
    "<p style='text-align: center; color: #888; margin-top: 2rem;'>True hands-free via Siri/Google Assistant • Zero taps while driving</p>",
    unsafe_allow_html=True
)