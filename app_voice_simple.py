"""
Smart Document Assistant - Simplified Voice-First Interface
One-click voice input that auto-submits when you're done speaking
"""
import streamlit as st
import os
from gtts import gTTS
import io
import time

st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    .big-voice-button {
        background-color: #FF4B4B;
        color: white;
        padding: 2rem;
        border-radius: 50%;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        width: 120px;
        height: 120px;
        margin: 2rem auto;
        display: block;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .big-voice-button:hover {
        background-color: #FF6B6B;
        transform: scale(1.05);
    }
    .big-voice-button.listening {
        background-color: #FF0000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    audio {
        width: 100%;
        margin-top: 1rem;
    }
    .status-text {
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .big-voice-button {
            width: 150px;
            height: 150px;
            font-size: 3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'auto_process' not in st.session_state:
    st.session_state.auto_process = False

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
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Tap the microphone and speak your question</p>", unsafe_allow_html=True)

# Status placeholder
status_placeholder = st.empty()

# One-click voice interface
st.markdown("""
<div id="voice-container" style="text-align: center;">
    <button id="voice-button" class="big-voice-button" onclick="startListening()">
        🎤
    </button>
    <p class="status-text" id="status">Ready to listen</p>
</div>

<script>
let recognition = null;
let isListening = false;

function startListening() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert('Voice input not supported. Please use Chrome or Edge browser.');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    const button = document.getElementById('voice-button');
    const status = document.getElementById('status');
    
    recognition.onstart = function() {
        isListening = true;
        button.classList.add('listening');
        button.innerHTML = '🔴';
        status.textContent = 'Listening... Speak now';
    };
    
    recognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show what's being heard
        if (interimTranscript) {
            status.textContent = 'Hearing: ' + interimTranscript;
        }
        
        // When we have final result, auto-submit
        if (finalTranscript) {
            status.textContent = 'Processing: ' + finalTranscript;
            
            // Send to Streamlit
            const hiddenInput = document.getElementById('hidden-voice-input');
            if (hiddenInput) {
                hiddenInput.value = finalTranscript;
                hiddenInput.dispatchEvent(new Event('change'));
                
                // Auto-click submit after a short delay
                setTimeout(() => {
                    const submitBtn = document.getElementById('auto-submit-btn');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }, 500);
            }
        }
    };
    
    recognition.onerror = function(event) {
        isListening = false;
        button.classList.remove('listening');
        button.innerHTML = '🎤';
        
        if (event.error === 'no-speech') {
            status.textContent = 'No speech detected. Tap to try again.';
        } else if (event.error === 'network') {
            status.textContent = 'Network error. Check connection.';
        } else {
            status.textContent = 'Error: ' + event.error + '. Tap to try again.';
        }
    };
    
    recognition.onend = function() {
        isListening = false;
        button.classList.remove('listening');
        button.innerHTML = '🎤';
        
        if (!status.textContent.includes('Processing')) {
            status.textContent = 'Tap to speak again';
        }
    };
    
    // Start listening
    recognition.start();
}

// Auto-start on mobile if user clicks anywhere
document.addEventListener('DOMContentLoaded', function() {
    // Make the whole page voice-activated on mobile
    if (window.innerWidth <= 768) {
        document.body.style.minHeight = '100vh';
    }
});
</script>
""", unsafe_allow_html=True)

# Hidden input for voice transcription
voice_input = st.text_input(
    "Voice Input",
    key="hidden-voice-input",
    label_visibility="hidden"
)

# Hidden auto-submit button
if st.button("Submit", key="auto-submit-btn", disabled=False, use_container_width=False):
    st.session_state.auto_process = True

# Process voice input automatically
if st.session_state.auto_process and voice_input:
    with st.spinner("🤔 Thinking..."):
        # Generate answer
        answer = generate_answer(voice_input)
        st.session_state.answer = answer
        st.session_state.transcript = voice_input
        
        # Generate audio
        audio_data = text_to_speech(answer)
        if audio_data:
            st.session_state.audio_data = audio_data
    
    # Reset auto-process flag
    st.session_state.auto_process = False
    st.rerun()

# Display results
if st.session_state.transcript:
    st.markdown("### 💬 You asked:")
    st.write(f"*\"{st.session_state.transcript}\"*")

if st.session_state.answer:
    st.markdown("### 📝 Answer")
    st.write(st.session_state.answer)
    
    # Auto-play audio response
    if st.session_state.audio_data:
        st.markdown("### 🔊 Audio Response")
        st.audio(st.session_state.audio_data, format='audio/mp3', autoplay=True)

# Manual text input (optional, collapsed by default)
with st.expander("⌨️ Type instead of speaking"):
    manual_input = st.text_input(
        "Type your question:",
        placeholder="e.g., Summarize the Q2 report for Wendle Ford"
    )
    if st.button("Ask", type="primary"):
        if manual_input:
            with st.spinner("Processing..."):
                answer = generate_answer(manual_input)
                st.session_state.answer = answer
                st.session_state.transcript = manual_input
                
                audio_data = text_to_speech(answer)
                if audio_data:
                    st.session_state.audio_data = audio_data
            st.rerun()

# Settings (minimal, in sidebar)
with st.sidebar:
    st.header("Settings")
    auto_play_audio = st.checkbox("Auto-play voice responses", value=True)
    st.markdown("---")
    st.markdown("### Tips")
    st.markdown("""
    - 🎤 Tap the big microphone button
    - 🗣️ Speak your question clearly
    - 🤖 Answer plays automatically
    - 🚗 Safe for driving use
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Made with ❤️ for WMA RAG | Voice-First Design</p>",
    unsafe_allow_html=True
)