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

# Create a unique key for the text input
if 'voice_transcript' not in st.session_state:
    st.session_state.voice_transcript = ""

# Text input with session state
text_input = st.text_input(
    "Type your question or use voice input below:",
    value=st.session_state.voice_transcript,
    key="question_input",
    placeholder="e.g., Summarize the Q2 report for Wendle Ford"
)

# Voice input button (using Streamlit's native approach)
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🎙️ Voice Input", use_container_width=True):
        st.info("Click the browser voice input below to speak")

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

# Browser Voice Input - Simplified approach
st.markdown("---")
st.markdown("### 🎙️ Voice Input Instructions")
st.info("""
**For Voice Input on Mobile:**
1. Tap the text input field above
2. Look for the microphone icon on your keyboard
3. Tap it and speak your question
4. Tap 'Done' when finished

**For Desktop Chrome/Edge:**
1. Click in the text input field
2. Press Windows+H (Windows) or use dictation
3. Or use the browser voice input button below
""")

# Simple HTML5 voice input for compatible browsers
st.markdown("""
<div style="margin: 20px 0;">
    <input type="text" 
           id="voice-input" 
           placeholder="Click and speak (Chrome/Edge only)"
           style="width: 100%; 
                  padding: 10px; 
                  font-size: 16px; 
                  border: 2px solid #ddd; 
                  border-radius: 5px;"
           x-webkit-speech 
           speech />
    <button onclick="copyToMainInput()" 
            style="margin-top: 10px;
                   background-color: #4CAF50;
                   color: white;
                   padding: 10px 20px;
                   border: none;
                   border-radius: 5px;
                   cursor: pointer;">
        Copy to Question Field ⬆️
    </button>
</div>

<script>
function copyToMainInput() {
    const voiceText = document.getElementById('voice-input').value;
    if (voiceText) {
        // Find Streamlit's text input and update it
        const mainInput = document.querySelector('input[aria-label*="Type your question"]');
        if (mainInput) {
            mainInput.value = voiceText;
            mainInput.dispatchEvent(new Event('input', { bubbles: true }));
            mainInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Trigger Streamlit to rerun
            const evt = new Event('input', { bubbles: true });
            mainInput.dispatchEvent(evt);
        }
        alert('Text copied! Now click "Ask Question" above.');
    }
}

// For browsers with Web Speech API
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const voiceBtn = document.createElement('button');
    voiceBtn.innerHTML = '🎙️ Click to Speak';
    voiceBtn.style.cssText = 'background-color: #FF4B4B; color: white; padding: 15px 30px; border: none; border-radius: 50px; font-size: 18px; cursor: pointer; margin: 10px 0;';
    
    voiceBtn.onclick = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            voiceBtn.innerHTML = '🔴 Listening...';
            voiceBtn.style.backgroundColor = '#FF0000';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('voice-input').value = transcript;
            voiceBtn.innerHTML = '🎙️ Click to Speak';
            voiceBtn.style.backgroundColor = '#FF4B4B';
            copyToMainInput();
        };
        
        recognition.onerror = function(event) {
            voiceBtn.innerHTML = '❌ Error - Try Again';
            voiceBtn.style.backgroundColor = '#FF4B4B';
            setTimeout(() => {
                voiceBtn.innerHTML = '🎙️ Click to Speak';
            }, 2000);
        };
        
        recognition.onend = function() {
            voiceBtn.innerHTML = '🎙️ Click to Speak';
            voiceBtn.style.backgroundColor = '#FF4B4B';
        };
        
        recognition.start();
    };
    
    document.getElementById('voice-input').parentNode.appendChild(voiceBtn);
}
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ for WMA RAG | "
    "[GitHub](https://github.com/rjhunter3789/smart-document-assistant)"
)