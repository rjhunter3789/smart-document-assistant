"""
Smart Document Assistant - Auto Voice Detection
One tap to start, automatic processing when you stop speaking
"""
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
import io
import time

st.set_page_config(
    page_title="Smart Document Assistant", 
    page_icon="🎙️",
    layout="centered"
)

# CSS for large button
st.markdown("""
<style>
    div[data-testid="column"] .stButton > button {
        background-color: #FF4B4B;
        color: white;
        height: 150px;
        font-size: 4rem;
        border-radius: 75px;
        border: none;
        box-shadow: 0 4px 15px rgba(255,75,75,0.3);
    }
    div[data-testid="column"] .stButton > button:hover {
        background-color: #FF6B6B;
        transform: scale(1.05);
    }
    .status-text {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'answer' not in st.session_state:
    st.session_state.answer = ""
if 'question' not in st.session_state:
    st.session_state.question = ""

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
st.markdown("<p class='status-text'>One tap voice assistant</p>", unsafe_allow_html=True)

# Create columns for centering
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Voice activation button
    voice_button = st.button("🎤", key="voice_btn", help="Tap to speak")
    
    if voice_button:
        st.session_state.processing = True

# Status display
status_container = st.empty()

# If voice button was pressed, show the voice interface
if st.session_state.processing:
    # Use JavaScript Web Speech API with automatic submission
    voice_component = components.html("""
    <div style="text-align: center; padding: 20px;">
        <div style="
            width: 120px;
            height: 120px;
            background-color: #FF0000;
            border-radius: 50%;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse 1s infinite;
        ">
            <span style="font-size: 3rem;">🎤</span>
        </div>
        <p id="status" style="margin-top: 20px; font-size: 1.2rem;">Listening...</p>
        <p id="transcript" style="margin-top: 10px; font-style: italic;"></p>
        
        <form id="voiceForm" action="#" method="post" style="display: none;">
            <input type="text" id="questionInput" name="question" />
            <input type="submit" id="submitBtn" />
        </form>
    </div>
    
    <style>
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
    
    <script>
    // Start speech recognition immediately
    window.onload = function() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            let finalTranscript = '';
            let silenceTimer = null;
            
            recognition.onresult = function(event) {
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                        document.getElementById('transcript').textContent = finalTranscript.trim();
                        
                        // Reset silence timer
                        clearTimeout(silenceTimer);
                        silenceTimer = setTimeout(() => {
                            // Auto-submit after 2 seconds of silence
                            recognition.stop();
                            submitQuestion(finalTranscript.trim());
                        }, 2000);
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (interimTranscript) {
                    document.getElementById('transcript').textContent = finalTranscript + interimTranscript;
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').textContent = 'Error: ' + event.error;
                // Send error back to Streamlit
                window.parent.postMessage({
                    type: 'voice_error',
                    error: event.error
                }, '*');
            };
            
            recognition.onend = function() {
                if (finalTranscript) {
                    document.getElementById('status').textContent = 'Processing...';
                    submitQuestion(finalTranscript.trim());
                } else {
                    document.getElementById('status').textContent = 'No speech detected';
                    setTimeout(() => {
                        window.parent.postMessage({
                            type: 'voice_complete',
                            question: ''
                        }, '*');
                    }, 1000);
                }
            };
            
            // Start listening
            recognition.start();
            
            function submitQuestion(question) {
                // Send to parent Streamlit app
                window.parent.postMessage({
                    type: 'voice_complete',
                    question: question
                }, '*');
            }
        } else {
            document.getElementById('status').textContent = 'Voice not supported. Please use Chrome or Edge.';
        }
    };
    </script>
    """, height=300)

# Create a form for processing the voice input
with st.form("voice_processor", clear_on_submit=True):
    voice_question = st.text_input("Voice Input", key="voice_result", label_visibility="hidden")
    process_btn = st.form_submit_button("Process", disabled=True)

# JavaScript to handle the voice result
components.html("""
<script>
// Listen for messages from the voice component
window.addEventListener('message', function(event) {
    if (event.data.type === 'voice_complete' && event.data.question) {
        // Find the Streamlit text input and update it
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        for (let input of inputs) {
            if (input.id && input.id.includes('voice_result')) {
                input.value = event.data.question;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Submit the form
                setTimeout(() => {
                    const forms = window.parent.document.querySelectorAll('form');
                    for (let form of forms) {
                        const submitBtn = form.querySelector('button[type="submit"]');
                        if (submitBtn && submitBtn.textContent.includes('Process')) {
                            submitBtn.click();
                            break;
                        }
                    }
                }, 100);
                break;
            }
        }
    } else if (event.data.type === 'voice_complete' && !event.data.question) {
        // Reset if no question
        window.parent.location.reload();
    }
});
</script>
""", height=0)

# Process the voice input
if voice_question:
    st.session_state.question = voice_question
    st.session_state.processing = False
    
    with st.spinner("🤔 Finding answer..."):
        answer = generate_answer(voice_question)
        st.session_state.answer = answer
        
        audio_data = text_to_speech(answer)
        if audio_data:
            st.session_state.audio_data = audio_data
    
    st.rerun()

# Display results
if st.session_state.answer and not st.session_state.processing:
    st.markdown("---")
    st.success(f"**You asked:** {st.session_state.question}")
    
    st.markdown("### 📝 Answer:")
    st.write(st.session_state.answer)
    
    if hasattr(st.session_state, 'audio_data') and st.session_state.audio_data:
        st.markdown("### 🔊 Listen:")
        st.audio(st.session_state.audio_data)
    
    # New question button
    if st.button("🔄 Ask Another Question", use_container_width=True):
        st.session_state.answer = ""
        st.session_state.question = ""
        st.session_state.processing = False
        if hasattr(st.session_state, 'audio_data'):
            st.session_state.audio_data = None
        st.rerun()

# Fallback text input
with st.expander("⌨️ Type your question instead"):
    text_form = st.form("text_input")
    typed_question = text_form.text_input("Your question:")
    if text_form.form_submit_button("Ask"):
        if typed_question:
            st.session_state.question = typed_question
            with st.spinner("Processing..."):
                st.session_state.answer = generate_answer(typed_question)
                audio_data = text_to_speech(st.session_state.answer)
                if audio_data:
                    st.session_state.audio_data = audio_data
            st.rerun()

# Mobile-specific instructions
st.markdown("---")
st.info("""
**How it works:**
1. 🎤 Tap the big microphone button
2. 🗣️ Start speaking immediately
3. ⏸️ Pause when done (2 seconds)
4. 🤖 Automatically processes your question
5. 🔊 Listen to the answer

**No manual submit needed!**
""")

# Footer
st.markdown(
    "<p style='text-align: center; color: #888; margin-top: 2rem;'>One-tap voice • Auto-processes after you stop speaking</p>",
    unsafe_allow_html=True
)