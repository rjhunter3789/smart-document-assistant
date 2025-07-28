"""
Smart Document Assistant - True One-Tap Voice Interface
Big red button that actually starts voice input immediately
"""
import streamlit as st
import os
from gtts import gTTS
import io
import base64
import json

st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS with proper voice button
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    /* Hide Streamlit's default hamburger menu for cleaner mobile UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Make the main content area larger */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Style for results */
    .result-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'question' not in st.session_state:
    st.session_state.question = ""
if 'show_input' not in st.session_state:
    st.session_state.show_input = False

def generate_answer(question: str) -> str:
    """Generate answer - placeholder for your RAG logic"""
    return f"Based on your documents, here's what I found about '{question}': This is a placeholder response. In the full implementation, this will query your Google Drive documents and provide a relevant summary."

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS"""
    try:
        text = text[:500] + "..." if len(text) > 500 else text
        tts = gTTS(text=text, lang='en', tld='com')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        return None

# Header
st.markdown("<h1 style='text-align: center;'>🎙️ Smart Document Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Tap the microphone to speak</p>", unsafe_allow_html=True)

# Create the main voice interface
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # This is the key part - using HTML form with speech input
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <!-- Hidden form with speech input that auto-submits -->
        <form id="voiceForm" style="margin: 0;">
            <input type="text" 
                   id="speechInput" 
                   name="speech" 
                   x-webkit-speech 
                   speech 
                   onwebkitspeechchange="submitVoice()"
                   style="position: absolute; left: -9999px;">
        </form>
        
        <!-- The big red button that triggers the hidden input -->
        <button onclick="startVoice()" style="
            background-color: #FF4B4B;
            color: white;
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: none;
            font-size: 4rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.1)'" 
           onmouseout="this.style.transform='scale(1)'">
            🎤
        </button>
        
        <p id="status" style="margin-top: 1rem; color: #666;">Ready to listen</p>
    </div>
    
    <script>
    function startVoice() {
        // For browsers that support x-webkit-speech
        const input = document.getElementById('speechInput');
        if (input) {
            input.click();
            document.getElementById('status').textContent = 'Listening...';
        }
        
        // For modern browsers, use Web Speech API
        if (!('webkitSpeechRecognition' in window) && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('status').textContent = '🔴 Listening... Speak now';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('status').textContent = 'Heard: ' + transcript;
                
                // Submit to Streamlit
                const textArea = window.parent.document.querySelector('textarea[aria-label="Voice question"]');
                if (textArea) {
                    textArea.value = transcript;
                    textArea.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    // Auto-submit after a brief delay
                    setTimeout(() => {
                        const submitButton = window.parent.document.querySelector('button[kind="primary"]');
                        if (submitButton && submitButton.textContent.includes('Process')) {
                            submitButton.click();
                        }
                    }, 500);
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').textContent = 'Error: ' + event.error + '. Try again.';
            };
            
            recognition.onend = function() {
                if (!document.getElementById('status').textContent.includes('Heard')) {
                    document.getElementById('status').textContent = 'Ready to listen';
                }
            };
            
            recognition.start();
        }
    }
    
    function submitVoice() {
        const input = document.getElementById('speechInput');
        if (input && input.value) {
            document.getElementById('status').textContent = 'Heard: ' + input.value;
            // Submit to Streamlit
            const textArea = window.parent.document.querySelector('textarea[aria-label="Voice question"]');
            if (textArea) {
                textArea.value = input.value;
                textArea.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    }
    </script>
    """, unsafe_allow_html=True)

# Hidden text area for voice input
voice_text = st.text_area("Voice question", key="voice_input", height=100, label_visibility="hidden")

# Process button (hidden but functional)
if st.button("Process", type="primary", key="process_btn", use_container_width=True):
    if voice_text:
        st.session_state.question = voice_text
        with st.spinner("🤔 Processing..."):
            answer = generate_answer(voice_text)
            st.session_state.answer = answer
            
            audio_data = text_to_speech(answer)
            if audio_data:
                st.session_state.audio_data = audio_data

# Alternative: Manual input (collapsible)
with st.expander("⌨️ Type instead"):
    manual_form = st.form("manual_input")
    manual_text = manual_form.text_input("Type your question:")
    if manual_form.form_submit_button("Ask"):
        if manual_text:
            st.session_state.question = manual_text
            with st.spinner("Processing..."):
                answer = generate_answer(manual_text)
                st.session_state.answer = answer
                
                audio_data = text_to_speech(answer)
                if audio_data:
                    st.session_state.audio_data = audio_data

# Display results
if st.session_state.question:
    st.markdown("### 💬 You asked:")
    st.markdown(f"<div class='result-box'><em>{st.session_state.question}</em></div>", unsafe_allow_html=True)

if st.session_state.answer:
    st.markdown("### 📝 Answer:")
    st.markdown(f"<div class='result-box'>{st.session_state.answer}</div>", unsafe_allow_html=True)
    
    if st.session_state.audio_data:
        st.markdown("### 🔊 Audio Response:")
        st.audio(st.session_state.audio_data, format='audio/mp3')

# Clear button
if st.session_state.answer:
    if st.button("🔄 New Question", use_container_width=True):
        for key in ['answer', 'audio_data', 'question']:
            st.session_state[key] = "" if key == 'question' else None
        st.rerun()

# Mobile keyboard trigger (backup method)
st.markdown("""
<div style="margin-top: 2rem; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
    <p style="text-align: center; margin: 0;">
        <strong>Not working?</strong> Try this:
    </p>
    <input type="text" 
           placeholder="Tap here for keyboard microphone" 
           id="mobileBackup"
           style="width: 100%; 
                  padding: 12px; 
                  font-size: 16px; 
                  margin-top: 10px;
                  border: 2px solid #ddd; 
                  border-radius: 5px;"
           onchange="
               const textArea = window.parent.document.querySelector('textarea[aria-label=\\'Voice question\\']');
               if (textArea && this.value) {
                   textArea.value = this.value;
                   textArea.dispatchEvent(new Event('input', { bubbles: true }));
                   this.value = '';
                   setTimeout(() => {
                       const btn = window.parent.document.querySelector('button[kind=\\'primary\\']');
                       if (btn) btn.click();
                   }, 500);
               }
           ">
</div>
""", unsafe_allow_html=True)

# Footer with tips
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🎤 Tap the big red button to start speaking</p>
    <p>Works best in Chrome, Edge, or Safari</p>
</div>
""", unsafe_allow_html=True)