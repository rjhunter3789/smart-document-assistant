"""
Streamlit frontend for Smart Document Assistant with Voice Input/Output
"""
import streamlit as st
import requests
import base64
# from streamlit_webrtc import webrtc_streamer, WebRtcMode  # Optional - removed
# import speech_recognition as sr  # Optional - removed for Railway deployment
import tempfile
import os
import json
from typing import Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
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
    .voice-button {
        background-color: #FF4B4B;
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        margin: 1rem 0;
    }
    .voice-button:hover {
        background-color: #FF6B6B;
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
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

def record_audio_with_speech_recognition():
    """Placeholder for audio recording - use browser speech API instead"""
    return "Please use the browser voice input below"

def send_question_to_backend(question: str, voice_enabled: bool = True) -> dict:
    """Send question to FastAPI backend and get response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": question,
                "voice_enabled": voice_enabled,
                "voice_provider": st.session_state.get('voice_provider', 'gtts')
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return {"answer": "Error getting response", "audio_url": None}
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure the FastAPI server is running.")
        return {"answer": "Backend connection error", "audio_url": None}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {"answer": f"Error: {str(e)}", "audio_url": None}

def get_audio_from_text(text: str) -> Optional[bytes]:
    """Get audio synthesis from backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/synthesize",
            params={
                "text": text,
                "provider": st.session_state.get('voice_provider', 'gtts')
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Audio synthesis error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None

# Main UI
st.title("🎙️ Smart Document Assistant")
st.markdown("Ask questions about your documents using voice or text")

# Voice provider selection (in sidebar)
with st.sidebar:
    st.header("Settings")
    voice_provider = st.selectbox(
        "Voice Output Provider",
        ["gtts", "elevenlabs"],
        help="Select voice synthesis provider"
    )
    st.session_state.voice_provider = voice_provider
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Voice-enabled document Q&A assistant")

# Main interaction area
col1, col2 = st.columns([3, 1])

with col1:
    # Text input option
    text_input = st.text_input(
        "Type your question or use voice input below:",
        value=st.session_state.transcript,
        placeholder="e.g., Summarize the Q2 report for Wendle Ford"
    )

with col2:
    # Voice input button
    if st.button("🎙️ Voice Input", use_container_width=True):
        with st.spinner("Listening..."):
            transcript = record_audio_with_speech_recognition()
            if transcript and transcript not in ["Could not understand audio", "No speech detected"]:
                st.session_state.transcript = transcript
                st.rerun()
            else:
                st.warning(transcript)

# Process question
if st.button("🚀 Ask Question", type="primary", use_container_width=True):
    question = text_input or st.session_state.transcript
    
    if question:
        with st.spinner("Processing your question..."):
            # Get answer from backend
            response = send_question_to_backend(question)
            st.session_state.answer = response['answer']
            
            # Get audio if enabled
            if response.get('audio_url'):
                audio_data = get_audio_from_text(response['answer'])
                if audio_data:
                    st.session_state.audio_data = audio_data

# Display results
if st.session_state.answer:
    st.markdown("### 📝 Answer")
    st.write(st.session_state.answer)
    
    # Play audio response if available
    if st.session_state.audio_data:
        st.markdown("### 🔊 Audio Response")
        st.audio(st.session_state.audio_data, format='audio/mp3')

# Alternative: Web Speech API for browsers that support it
st.markdown("---")
with st.expander("🎙️ Alternative: Browser Voice Input"):
    st.markdown("""
    <div id="speech-input">
        <button onclick="startSpeechRecognition()" class="voice-button">
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
                document.getElementById('speech-result').textContent = 'Listening...';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('speech-result').textContent = 'You said: ' + transcript;
                
                // Send to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }, '*');
            };
            
            recognition.onerror = function(event) {
                document.getElementById('speech-result').textContent = 'Error: ' + event.error;
            };
            
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser.');
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