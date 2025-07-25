"""
Simplified Smart Document Assistant - All in one file for Railway
"""
import streamlit as st
import os
from gtts import gTTS
import io
import base64

st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    audio {
        width: 100%;
        margin-top: 1rem;
    }
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

def generate_answer(question: str) -> str:
    """Generate answer - placeholder for your RAG logic"""
    # TODO: Replace with your actual LlamaIndex/RAG logic
    return f"Based on your documents, here's what I found about '{question}': This is a placeholder response. In the full implementation, this will query your Google Drive documents and provide a relevant summary."

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

# Main UI
st.title("🎙️ Smart Document Assistant")
st.markdown("Ask questions about your documents using voice or text")

# Voice provider selection (in sidebar)
with st.sidebar:
    st.header("Settings")
    voice_enabled = st.checkbox("Enable Voice Output", value=True)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Voice-enabled document Q&A assistant")

# Text input
text_input = st.text_input(
    "Type your question or use voice input below:",
    placeholder="e.g., Summarize the Q2 report for Wendle Ford"
)

# Process question
if st.button("🚀 Ask Question", type="primary", use_container_width=True):
    question = text_input
    
    if question:
        with st.spinner("Processing your question..."):
            # Get answer
            answer = generate_answer(question)
            st.session_state.answer = answer
            
            # Generate audio if enabled
            if voice_enabled:
                audio_data = text_to_speech(answer)
                if audio_data:
                    st.session_state.audio_data = audio_data

# Display results
if st.session_state.answer:
    st.markdown("### 📝 Answer")
    st.write(st.session_state.answer)
    
    # Play audio response if available
    if st.session_state.audio_data and voice_enabled:
        st.markdown("### 🔊 Audio Response")
        st.audio(st.session_state.audio_data, format='audio/mp3')

# Browser Voice Input
st.markdown("---")
with st.expander("🎙️ Alternative: Browser Voice Input"):
    st.markdown("""
    <div id="speech-input">
        <button onclick="startSpeechRecognition()" style="
            background-color: #FF4B4B;
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            margin: 1rem 0;">
            Start Voice Input (Browser)
        </button>
        <p id="speech-result"></p>
    </div>
    
    <script>
    function startSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('speech-result').innerHTML = '<b>🎙️ Listening...</b>';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('speech-result').innerHTML = '<b>You said:</b> ' + transcript;
                
                // Update the text input
                const textInput = window.parent.document.querySelector('input[type="text"]');
                if (textInput) {
                    textInput.value = transcript;
                    textInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('speech-result').textContent = 'Error: ' + event.error;
            };
            
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser. Please use Chrome or Edge.');
        }
    }
    </script>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ for WMA RAG | "
    "[GitHub](https://github.com/rjhunter3789/smart-document-assistant)"
)