"""
Smart Document Assistant - Final Voice Solution
Using Streamlit components properly for voice input
"""
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
import io
import os

st.set_page_config(
    page_title="Smart Document Assistant", 
    page_icon="🎙️",
    layout="centered"
)

# CSS for better mobile experience
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        min-height: 60px;
        font-size: 1.2rem;
    }
    div[data-testid="column"]:nth-child(2) .stButton > button {
        background-color: #FF4B4B;
        color: white;
        font-size: 2rem;
        height: 120px;
        border-radius: 60px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'question' not in st.session_state:
    st.session_state.question = ""
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

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
st.markdown("**The easiest way to use voice:**")

# Instructions based on device
st.info("""
📱 **Mobile (Recommended):**  
1. Tap the text box below
2. Tap the microphone icon on your keyboard
3. Speak your question
4. Tap 'Done' → then 'Ask Question'

💻 **Desktop:**  
Just type your question in the box below
""")

# Main input area
question = st.text_area(
    "Your Question:",
    height=100,
    placeholder="Tap here, then use 🎤 on keyboard (mobile) or type your question",
    key="main_input"
)

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Ask Question", type="primary", use_container_width=True):
        if question:
            st.session_state.question = question
            with st.spinner("Finding answer..."):
                st.session_state.answer = generate_answer(question)
                st.session_state.audio_data = text_to_speech(st.session_state.answer)

with col2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.question = ""
        st.session_state.answer = ""
        st.session_state.audio_data = None
        st.rerun()

# Show results
if st.session_state.answer:
    st.markdown("---")
    st.markdown("### 💬 You asked:")
    st.write(f"*{st.session_state.question}*")
    
    st.markdown("### 📝 Answer:")
    st.write(st.session_state.answer)
    
    if st.session_state.audio_data:
        st.markdown("### 🔊 Listen:")
        st.audio(st.session_state.audio_data)

# Advanced voice option using component
with st.expander("🎤 Advanced Voice Input (Desktop Chrome/Edge)"):
    # Create custom HTML component for voice
    voice_html = """
    <div style="padding: 20px; text-align: center;">
        <button onclick="startVoice()" style="
            background-color: #FF4B4B;
            color: white;
            padding: 20px 40px;
            font-size: 18px;
            border: none;
            border-radius: 30px;
            cursor: pointer;
        ">🎤 Click to Speak (Chrome/Edge)</button>
        
        <p id="status" style="margin-top: 15px;">Ready</p>
        <p id="transcript" style="margin-top: 10px; font-weight: bold;"></p>
        
        <script>
        function startVoice() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-US';
                recognition.continuous = false;
                recognition.interimResults = false;
                
                recognition.onstart = () => {
                    document.getElementById('status').textContent = '🔴 Listening...';
                };
                
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('transcript').textContent = 'You said: ' + transcript;
                    document.getElementById('status').textContent = '✅ Got it! Copy the text above to the question box.';
                    
                    // Copy to clipboard
                    navigator.clipboard.writeText(transcript).then(() => {
                        document.getElementById('status').textContent += ' (Copied to clipboard!)';
                    });
                };
                
                recognition.onerror = (event) => {
                    document.getElementById('status').textContent = '❌ Error: ' + event.error;
                };
                
                recognition.onend = () => {
                    if (document.getElementById('status').textContent.includes('Listening')) {
                        document.getElementById('status').textContent = 'Ready';
                    }
                };
                
                recognition.start();
            } else {
                alert('Speech recognition not supported in this browser.');
            }
        }
        </script>
    </div>
    """
    components.html(voice_html, height=200)
    st.caption("After speaking, paste (Ctrl+V) into the question box above")

# Footer
st.markdown("---")
st.markdown(
    """<p style='text-align: center; color: #888;'>
    🎤 Best voice experience: Use your phone's keyboard microphone<br>
    Works on all devices • No special setup required
    </p>""", 
    unsafe_allow_html=True
)