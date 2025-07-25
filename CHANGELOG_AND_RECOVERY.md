# Smart Document Assistant - Change Log & Recovery Guide

## Version History & Complete Code Archive

### Version 3.3.0 - Google Drive Integration Complete (2025-07-26)

**FINAL MILESTONE - Full Google Drive Search via iOS Shortcuts!**

**Major Features:**
- Complete Google Drive integration with OAuth 2.0
- Searches both local files AND Google Drive documents
- Supports PDF, DOCX, TXT, and Google Docs formats
- Auto-refreshes expired tokens
- Works seamlessly with iOS Shortcuts

**Technical Implementation:**
- New `app_flask_drive.py` with Drive API integration
- OAuth 2.0 authentication with refresh token support
- Environment variables for Railway deployment:
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - GOOGLE_REFRESH_TOKEN
  - GOOGLE_TOKEN
- Status endpoint at `/api/status` to check Drive connection
- Maintains all existing iOS Shortcuts compatibility

**Setup Requirements:**
- Google Cloud Console project with Drive API enabled
- OAuth 2.0 credentials configured
- Environment variables set in Railway
- See GOOGLE_DRIVE_SETUP.md for complete instructions

### Version 3.2.0 - Flask API with Working iOS Shortcuts (2025-07-26)

**BREAKTHROUGH - iOS Shortcuts Finally Working!**

**Major Features:**
- Replaced Streamlit with Flask for true API endpoints
- iOS Shortcuts can now parse responses correctly
- Plain text API endpoint at `/api/search/text`
- Two-tap operation: dictate, then hear response
- Successfully searches and returns document content

**Technical Implementation:**
- Flask app serving multiple endpoints:
  - `/` - Browser interface
  - `/api/search` - JSON/text response
  - `/api/search/text` - Pure text for iOS
- Embedded search function directly in Flask
- Uses Railway's PORT environment variable
- Returns plain text without HTML wrapper

**iOS Shortcut Setup:**
1. Dictate text
2. Get contents of URL: `https://web-production-5c94.up.railway.app/api/search/text?q=[Dictated Text]`
3. Show in Quick Look (optional for debugging)
4. Get text from Contents of URL
5. Speak Text

**Key Files:**
- `app_flask.py` - Flask API server
- `Procfile` - Points to Flask app
- Documents in `app/docs/*.txt`

### Version 3.1.1 - Automatic Changelog Updates (2025-07-26)

**Changes:**
- Added automatic changelog update script

**Commit:**
- c4e7ffc - Add automatic changelog update script

### Version 3.1.0 - Working Shortcuts Integration (2025-07-26)

**FINALLY - iOS Dictation Works End-to-End!**

**Major Features:**
- iOS Shortcuts with Dictate Text fully functional
- URL parameter integration fixed
- Streamlit app properly handles query strings
- Voice input → Document search → Voice output complete

### Version 3.0.0 - Siri/Google Assistant Integration (2025-07-25)

**GAME CHANGER - True Hands-Free Operation**

**Major Features:**
- Direct integration with Siri Shortcuts (iPhone)
- Google Assistant compatible (Android)
- Zero taps required - just speak to Siri/Google
- URL parameter support for voice queries
- Auto-plays audio response
- Perfect for driving - completely hands-free

**How it Works:**
1. Create a Siri Shortcut once
2. Say: "Hey Siri, ask document assistant to [your question]"
3. App opens, processes, and speaks the answer
4. No taps, no buttons - pure voice

**Technical Implementation:**
- Uses URL parameters (?q=your+question)
- Auto-processes on page load
- Returns voice response immediately
- Maintains conversation history

### Version 2.3.0 - Voice Trigger Word "GO" (2025-07-25)

**Major Changes:**
- Added verbal trigger word "GO" to submit questions
- Prevents accidental submissions during natural pauses
- Truly hands-free operation perfect for driving
- Trigger word is removed from the actual query
- Manual submit button still available as backup

**Usage Example:** "Summarize the Q2 report for Wendell Ford GO"

**Key Innovation:** Verbal command submission without accidental triggers

### Version 2.2.0 - Final Reliable Voice Interface (2025-07-25)

**Major Changes:**
- Simplified to use native mobile keyboard microphone (most reliable)
- Clear instructions for both mobile and desktop
- Removed complex JavaScript that Streamlit was blocking
- Added clipboard copy for desktop voice input
- Stable, works on all devices

**Key Learning:** Mobile keyboard microphone is the most reliable voice input method

### Version 2.1.0 - Voice-First One-Click Interface (2025-07-25)

**Major Changes:**
- Created voice-first interface with one-click operation
- Auto-submission after speaking (no manual submit needed)
- Mobile-optimized with large microphone button
- Auto-play voice responses
- Safe for driving - minimal interaction required
- Removed multi-step voice input process

**New File:** `app_voice_simple.py` - Streamlined voice interface

**Git Commit:** `voice-first-interface`

### Version 2.0.0 - Voice-Enabled Hybrid Architecture (2025-07-25)

**Major Changes:**
- Migrated from Streamlit-only to FastAPI + Streamlit hybrid architecture
- Added voice input via Web Speech API and SpeechRecognition
- Added voice output via gTTS (default) and ElevenLabs (premium)
- Prepared for Railway deployment with auto-deploy pipeline
- Made mobile-responsive UI improvements

**Git Commit:** `initial-voice-hybrid` (to be created)

---

## Complete Code Snapshot (v3.1.0)

### Working Shortcuts App (app_shortcut_simple.py)
```python
"""
Simple URL parameter handler for Shortcuts
Returns PLAIN TEXT instead of HTML when ?q= parameter is present
"""
import streamlit as st
from datetime import datetime
import os

# Simple document search function
def search_local_docs(query):
    """Search through local documents in app/docs folder"""
    docs_path = "app/docs"
    results = []
    
    if os.path.exists(docs_path):
        for filename in os.listdir(docs_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(docs_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            # Extract relevant snippet
                            index = content.lower().find(query.lower())
                            start = max(0, index - 100)
                            end = min(len(content), index + 200)
                            snippet = content[start:end].strip()
                            results.append(f"From {filename}: ...{snippet}...")
                except:
                    pass
    
    if results:
        return " ".join(results[:2])  # Return first 2 results
    else:
        return f"No specific information found about '{query}' in the documents. Please try a different search term."

# Hide Streamlit UI when URL parameter is present
query_params = st.query_params
voice_query = query_params.get("q", "")

if voice_query:
    # For URL parameters, search docs and return plain text
    answer = search_local_docs(voice_query)
    
    # Display as plain text for Shortcuts to speak
    st.text(answer)
else:
    # Normal web interface
    st.title("Smart Document Assistant")
    st.write("Add ?q=your+question to the URL to get a response")
    
    # Show available documents
    if os.path.exists("app/docs"):
        st.write("Available documents:")
        for f in os.listdir("app/docs"):
            if f.endswith('.txt'):
                st.write(f"- {f}")
```

### Deployment (Procfile)
```
web: streamlit run app_shortcut_simple.py --server.port $PORT --server.address 0.0.0.0
```

---

## Troubleshooting Shortcuts (v3.1.0)

### If no voice response:
1. Check Railway deployment is active
2. Test URL in browser: `https://web-production-5c94.up.railway.app?q=test`
3. Ensure "Get Text from Input" is between Get Contents and Speak
4. Verify Speak uses "Text" not "Contents of URL"

### If getting HTML instead of text:
- Add "Get Text from Input" action after Get Contents
- Make sure app_shortcut_simple.py is deployed (check Procfile)

### Testing document search:
- Documents must be .txt files in app/docs folder
- Try queries like "AI agent", "Ford", "sales journey"
- App returns first 2 matching snippets

---

## Complete Code Snapshot (v2.0.0)

### Project Structure
```
smart-document-assistant/
├── backend/
│   └── main.py           # FastAPI backend with voice synthesis
├── frontend/
│   └── streamlit_app.py  # Streamlit UI with voice input
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions for Railway auto-deploy
├── requirements.txt      # Python dependencies
├── start_app.py         # Railway startup script
├── railway.json         # Railway configuration
├── Procfile            # Alternative deployment config
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── README.md           # Setup and deployment guide
└── CHANGELOG_AND_RECOVERY.md  # This file
```

### 1. Backend Code (backend/main.py)
```python
"""
FastAPI backend for Smart Document Assistant with Voice Support
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from typing import Optional
import httpx
import json
import io
from gtts import gTTS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Document Assistant API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    voice_enabled: bool = True
    voice_provider: str = "gtts"  # Options: "gtts", "elevenlabs", "google"
    
class AnswerResponse(BaseModel):
    answer: str
    audio_url: Optional[str] = None

# Voice synthesis configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice

@app.get("/")
async def root():
    return {"message": "Smart Document Assistant API is running"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Process a question and return text answer with optional voice synthesis
    """
    try:
        # TODO: Replace with actual RAG/LlamaIndex logic
        # For now, return a dummy response
        answer = f"Based on your documents, here's what I found about '{request.question}': This is a placeholder response. In the full implementation, this will query your Google Drive documents and provide a relevant summary."
        
        # If voice is disabled, return text only
        if not request.voice_enabled:
            return AnswerResponse(answer=answer)
            
        # Generate voice response based on provider
        audio_content = None
        
        if request.voice_provider == "elevenlabs" and ELEVENLABS_API_KEY:
            audio_content = await generate_elevenlabs_audio(answer)
        else:
            # Default to gTTS (Google Text-to-Speech) - free tier
            audio_content = generate_gtts_audio(answer)
            
        # Return response with audio
        return AnswerResponse(
            answer=answer,
            audio_url="audio_embedded"  # Placeholder - audio will be streamed
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def synthesize_speech(text: str, provider: str = "gtts"):
    """
    Generate audio from text and return as streaming response
    """
    try:
        if provider == "elevenlabs" and ELEVENLABS_API_KEY:
            audio_content = await generate_elevenlabs_audio(text)
        else:
            audio_content = generate_gtts_audio(text)
            
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_gtts_audio(text: str) -> bytes:
    """Generate audio using Google Text-to-Speech (free)"""
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        logger.error(f"gTTS error: {str(e)}")
        raise

async def generate_elevenlabs_audio(text: str) -> bytes:
    """Generate audio using ElevenLabs API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs API error: {response.status_code}")
                # Fallback to gTTS
                return generate_gtts_audio(text)
                
    except Exception as e:
        logger.error(f"ElevenLabs error: {str(e)}")
        # Fallback to gTTS
        return generate_gtts_audio(text)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "voice_providers": ["gtts", "elevenlabs"]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2. Frontend Code (frontend/streamlit_app.py)
```python
"""
Streamlit frontend for Smart Document Assistant with Voice Input/Output
"""
import streamlit as st
import requests
import base64
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
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
    """Record audio using speech_recognition library"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now!")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            # Try Google Speech Recognition
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"
        except sr.WaitTimeoutError:
            return "No speech detected"

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
```

### 3. Requirements (requirements.txt)
```
# Core dependencies
streamlit==1.28.2
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
httpx==0.25.2
pydantic==2.5.0

# Voice/Audio processing
gTTS==2.4.0
SpeechRecognition==3.10.0
pyaudio==0.2.13
streamlit-webrtc==0.47.1

# Document processing (to be added when integrating with existing code)
# llama-index==0.9.13
# langchain==0.0.340
# sentence-transformers==2.2.2
# faiss-cpu==1.7.4
# PyMuPDF==1.23.8
# python-docx==1.1.0

# Google Drive integration (to be added)
# google-api-python-client==2.108.0
# google-auth==2.23.4
# google-auth-oauthlib==1.1.0
# google-auth-httplib2==0.1.1

# Utils
python-dotenv==1.0.0
requests==2.31.0
aiofiles==23.2.1

# For Railway deployment
gunicorn==21.2.0
```

### 4. Startup Script (start_app.py)
```python
"""
Start both FastAPI backend and Streamlit frontend for Railway deployment
"""
import subprocess
import os
import time
import sys

def start_services():
    # Get PORT from environment (Railway provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Set backend URL for Streamlit to use
    os.environ["BACKEND_URL"] = f"http://localhost:{port}"
    
    # Start FastAPI backend
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ])
    
    print(f"Started FastAPI backend on port {port}")
    
    # Give backend time to start
    time.sleep(3)
    
    # Start Streamlit frontend on a different port
    streamlit_port = port + 1
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "frontend/streamlit_app.py",
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    print(f"Started Streamlit frontend on port {streamlit_port}")
    
    # Wait for both processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    start_services()
```

---

## Recovery Procedures

### 1. Rolling Back to Previous Version
```bash
# View commit history
git log --oneline

# Rollback to specific commit
git checkout <commit-hash>

# Or revert last commit
git revert HEAD
```

### 2. Switching Voice Providers
```bash
# In .env or Railway settings, change:
# From ElevenLabs to gTTS (free):
VOICE_PROVIDER=gtts

# To use ElevenLabs:
VOICE_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key_here
```

### 3. Emergency Disable Voice Features
In `backend/main.py`, set default voice_enabled to False:
```python
class QuestionRequest(BaseModel):
    question: str
    voice_enabled: bool = False  # Changed from True
```

### 4. Debugging Deployment Issues
```bash
# Check Railway logs
railway logs

# Test locally first
python start_app.py

# Or run services separately:
# Terminal 1:
uvicorn backend.main:app --reload

# Terminal 2:
streamlit run frontend/streamlit_app.py
```

### 5. Common Fixes

**Backend not connecting:**
- Check BACKEND_URL in environment variables
- Ensure both services are running
- Check CORS settings in FastAPI

**Voice input not working:**
- Browser must support Web Speech API (Chrome/Edge)
- HTTPS required for production
- Check microphone permissions

**Audio playback issues:**
- Check audio synthesis provider settings
- Verify API keys are correct
- Test with gTTS first (no API key needed)

---

## Integration Points

### Adding LlamaIndex/RAG:
Replace the dummy response in `backend/main.py`:
```python
# TODO: Replace with actual RAG/LlamaIndex logic
answer = await process_with_llamaindex(request.question)
```

### Adding Google Drive:
1. Add credentials to environment
2. Import existing Drive integration code
3. Connect to document retrieval in `/ask` endpoint

### Adding Authentication:
1. Add user verification middleware
2. Check ALLOWED_USERS environment variable
3. Implement session management

---

## Deployment Checklist

- [ ] Push code to GitHub
- [ ] Set up Railway project
- [ ] Add environment variables in Railway
- [ ] Connect GitHub repo to Railway
- [ ] Enable auto-deploy
- [ ] Test voice input/output
- [ ] Verify mobile responsiveness

---

## Version Roadmap

### v2.1.0 (Next)
- [ ] Integrate existing LlamaIndex/RAG logic
- [ ] Connect Google Drive document access
- [ ] Add user authentication

### v2.2.0 (Future)
- [ ] Multi-language support
- [ ] Custom voice training
- [ ] Webhook notifications
- [ ] Analytics dashboard

---

---

## Latest Code Snapshot (v2.1.0)

### Voice-First App (app_voice_simple.py)
```python
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

# [Full code in app_voice_simple.py]
```

### Key Features of v2.1.0:
1. **One-Click Voice Input**: Large microphone button - tap once to start
2. **Auto-Submit**: Automatically processes when you stop speaking
3. **Auto-Play Response**: Voice response plays immediately
4. **Mobile-First**: Huge button for easy access while driving
5. **Visual Feedback**: Button pulses while listening
6. **Error Recovery**: Clear status messages and easy retry

### Deployment Command:
```bash
streamlit run app_voice_simple.py --server.port $PORT --server.address 0.0.0.0
```

---

Last Updated: 2025-07-26
Maintained by: Jeff Hunter (rjhunter3789)