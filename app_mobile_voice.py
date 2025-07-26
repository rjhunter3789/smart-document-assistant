"""
Smart Document Assistant - Mobile-First Voice Interface
Simple, reliable voice input that works on all devices
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

# Mobile-optimized CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 0.5rem;
    }
    .main-input {
        font-size: 18px !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.fixed-header) {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding: 1rem 0;
    }
    .big-button {
        font-size: 1.5rem !important;
        padding: 1rem !important;
        width: 100% !important;
    }
    audio {
        width: 100%;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'question' not in st.session_state:
    st.session_state.question = ""

def generate_answer(question: str) -> str:
    """Generate answer - placeholder for your RAG logic"""
    # TODO: Replace with your actual LlamaIndex/RAG logic
    return f"Based on your documents, here's what I found about '{question}': This is a placeholder response. In the full implementation, this will query your Google Drive documents and provide a relevant summary."

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS"""
    try:
        # Limit text length for TTS
        text = text[:500] + "..." if len(text) > 500 else text
        tts = gTTS(text=text, lang='en', tld='com')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        st.error(f"Voice generation error: {str(e)}")
        return None

# Main UI - Fixed header
st.markdown('<div class="fixed-header">', unsafe_allow_html=True)
st.title("🎙️ Smart Document Assistant")
st.markdown("</div>", unsafe_allow_html=True)

# Voice input instructions
st.info("""
**🎤 Voice Input Options:**
1. **Mobile**: Tap the text box below → tap microphone on keyboard
2. **Desktop**: Click text box → click microphone icon (if available)
3. **Or just type** your question
""")

# Main input form
with st.form("voice_form", clear_on_submit=False):
    # Text input with placeholder
    question = st.text_input(
        "Ask your question:",
        placeholder="Tap here and use 🎤 on your keyboard (mobile) or type",
        key="question_input",
        help="On mobile: Tap here, then tap the microphone on your keyboard"
    )
    
    # Submit button
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button(
            "🚀 Get Answer",
            type="primary",
            use_container_width=True
        )

# Process the question
if submitted and question:
    st.session_state.question = question
    
    with st.spinner("🤔 Finding answer..."):
        # Generate answer
        answer = generate_answer(question)
        st.session_state.answer = answer
        
        # Generate audio (optional)
        with st.spinner("🎙️ Generating voice response..."):
            audio_data = text_to_speech(answer)
            if audio_data:
                st.session_state.audio_data = audio_data

# Display results
if st.session_state.question:
    st.markdown("### 💬 You asked:")
    st.write(f"*\"{st.session_state.question}\"*")

if st.session_state.answer:
    st.markdown("### 📝 Answer:")
    st.write(st.session_state.answer)
    
    # Audio player (without autoplay to avoid errors)
    if st.session_state.audio_data:
        st.markdown("### 🔊 Listen to Answer:")
        audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
        audio_html = f"""
        <audio controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <p style="text-align: center; color: #666; margin-top: 10px;">
            Tap play ▶️ to hear the answer
        </p>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Quick tips
with st.expander("💡 Voice Input Tips"):
    st.markdown("""
    **For Best Results:**
    - **iPhone/iPad**: Tap text box → tap 🎤 on keyboard
    - **Android**: Tap text box → tap microphone on keyboard
    - **Desktop Chrome**: Click text box → use microphone if shown
    - **All devices**: You can always just type!
    
    **Troubleshooting:**
    - Make sure microphone permissions are enabled
    - Use Chrome or Safari for best compatibility
    - If voice doesn't work, just type your question
    """)

# Clear button
if st.session_state.answer:
    if st.button("🔄 Ask Another Question"):
        st.session_state.answer = ""
        st.session_state.audio_data = None
        st.session_state.question = ""
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.9rem;'>Voice input uses your device's built-in speech recognition</p>",
    unsafe_allow_html=True
)