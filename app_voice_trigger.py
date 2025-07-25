"""
Smart Document Assistant - Voice with Trigger Word
Say your question, then say "GO" to submit (perfect for driving)
"""
import streamlit as st
from gtts import gTTS
import io
import re

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
    .trigger-word {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
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
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""

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

def check_for_trigger(text: str):
    """Check if the text ends with trigger word 'go' and extract the question"""
    if not text:
        return None, False
    
    # Check if text ends with "go" (case insensitive)
    text = text.strip()
    words = text.split()
    
    if len(words) > 1 and words[-1].lower() == 'go':
        # Remove the trigger word and return the question
        question = ' '.join(words[:-1])
        return question, True
    
    return text, False

# Header
st.title("🎙️ Smart Document Assistant")
st.markdown("### 🚗 Perfect for Driving!")

# Instructions
st.info("""
**How to use voice (hands-free):**
1. 📱 Tap the text box below
2. 🎤 Tap microphone on keyboard
3. 🗣️ Say your question
4. 🎯 Say **"GO"** when done
5. 🔊 Listen to the answer

Example: *"Summarize the Q2 report for Wendell Ford **GO**"*
""")

# Show the trigger word prominently
st.markdown("""
<div style="text-align: center; margin: 20px 0;">
    <span class="trigger-word">Say "GO" to submit</span>
</div>
""", unsafe_allow_html=True)

# Main input area
voice_input = st.text_area(
    "Your Question:",
    height=100,
    placeholder='Tap here, use 🎤, speak your question, then say "GO"',
    key="voice_input",
    help='Say "GO" at the end to submit your question'
)

# Check for trigger word in real-time
if voice_input and voice_input != st.session_state.last_input:
    st.session_state.last_input = voice_input
    question, has_trigger = check_for_trigger(voice_input)
    
    if has_trigger:
        st.session_state.question = question
        # Process automatically when trigger word detected
        with st.spinner("🎯 Trigger word detected! Processing..."):
            st.session_state.answer = generate_answer(question)
            st.session_state.audio_data = text_to_speech(st.session_state.answer)
        # Clear the input
        st.rerun()

# Manual buttons as backup
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.button("🚀 Ask Question (Manual)", type="primary", use_container_width=True):
        if voice_input:
            # Remove trigger word if present
            question, _ = check_for_trigger(voice_input)
            st.session_state.question = question
            with st.spinner("Processing..."):
                st.session_state.answer = generate_answer(question)
                st.session_state.audio_data = text_to_speech(st.session_state.answer)

with col2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.question = ""
        st.session_state.answer = ""
        st.session_state.audio_data = None
        st.session_state.last_input = ""
        st.rerun()

with col3:
    if st.button("❓ Help", use_container_width=True):
        st.session_state.show_help = not st.session_state.get('show_help', False)

# Show help if requested
if st.session_state.get('show_help', False):
    with st.expander("Help & Tips", expanded=True):
        st.markdown("""
        **Trigger Words:**
        - ✅ "GO" - Submits your question
        - ❌ Won't trigger on: "Where did they go", "Ford Go Further"
        - ✅ Only triggers when "GO" is the last word
        
        **Examples:**
        - ✅ "What were last month's sales GO"
        - ✅ "Summarize the dealer report GO"
        - ❌ "Where should we go for lunch" (no trigger)
        
        **Tips:**
        - Speak naturally, pause, then clearly say "GO"
        - Works great while driving
        - Manual button available as backup
        """)

# Show results
if st.session_state.answer:
    st.markdown("---")
    st.success(f"**You asked:** {st.session_state.question}")
    
    st.markdown("### 📝 Answer:")
    st.write(st.session_state.answer)
    
    if st.session_state.audio_data:
        st.markdown("### 🔊 Audio Response:")
        st.audio(st.session_state.audio_data, autoplay=False)
        st.caption("Audio will play - adjust volume as needed")

# Alternative trigger words setting
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Future: Allow custom trigger words
    st.markdown("""
    **Current trigger word:** <span class="trigger-word">GO</span>
    
    This word was chosen because:
    - Short and clear
    - Unlikely in queries
    - Easy to say while driving
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    **Why use a trigger word?**
    - No accidental submissions
    - Natural pauses allowed
    - Hands-free operation
    - Perfect for driving
    """)

# Footer
st.markdown("---")
st.markdown(
    """<p style='text-align: center; color: #888;'>
    🎤 Say your question, then say "GO" to submit<br>
    Safe for driving • No accidental submissions
    </p>""", 
    unsafe_allow_html=True)