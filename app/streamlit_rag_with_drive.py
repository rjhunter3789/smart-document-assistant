import os
import io
import fitz  # PyMuPDF
from docx import Document as DocxDoc
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from datetime import datetime

# Config

SCOPES = [‘https://www.googleapis.com/auth/drive.readonly’]
DOCS_DIR = “docs”
os.makedirs(DOCS_DIR, exist_ok=True)

# Mobile-optimized page configuration

st.set_page_config(
page_title=“🎤 Voice-Powered Document Assistant”,
page_icon=“🎙️”,
layout=“wide”,
initial_sidebar_state=“collapsed”,
menu_items={
‘Get Help’: ‘https://your-help-url.com’,
‘Report a bug’: “https://your-bug-report-url.com”,
‘About’: “# Voice-Powered Smart Document Assistant\nMobile-optimized AI-powered document search with voice commands”
}
)

# Custom CSS for mobile optimization + Voice UI

st.markdown(”””

<style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Voice Interface Styling */
    .voice-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* File cards styling */
    .file-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .file-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .file-name {
        font-weight: 600;
        color: #2c3e50;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        word-break: break-word;
    }
    
    /* Navigation section */
    .nav-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .nav-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    /* Results section */
    .results-header {
        background: linear-gradient(90deg, #56ccf2, #2f80ed);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    /* Status messages */
    .status-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .status-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .status-info {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Mobile-friendly dropdowns */
    .stSelectbox > div > div {
        font-size: 16px !important;
        min-height: 44px;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem 1rem;
        font-size: 16px;
        min-height: 44px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102,126,234,0.25);
    }
    
    /* Responsive font sizes */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header p {
            font-size: 0.9rem;
        }
        
        .file-name {
            font-size: 0.95rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>

“””, unsafe_allow_html=True)

# Authentication function

def authenticate_gdrive():
“”“Authenticate with Google Drive using Streamlit secrets”””
try:
from google.oauth2.credentials import Credentials

```
    # Create credentials from Streamlit secrets
    creds_info = {
        "client_id": st.secrets["google"]["client_id"],
        "client_secret": st.secrets["google"]["client_secret"],
        "refresh_token": st.secrets["google"]["refresh_token"],
        "token": st.secrets["google"]["token"],
        "token_uri": st.secrets["google"]["token_uri"],
    }
    
    # Create credentials object
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    
    # Refresh if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    # Build and return the service
    return build('drive', 'v3', credentials=creds)
    
except Exception as e:
    st.error(f"🚫 Authentication failed: {str(e)}")
    return None
```

def get_all_folders_recursive(service, parent_id, parent_path=””):
“”“Get ALL folders - no limits, full depth for business use”””
folders = []

```
try:
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)", pageSize=1000).execute()
    items = results.get("files", [])

    for item in items:
        full_path = f"{parent_path}/{item['name']}".strip("/")
        folders.append({
            "id": item["id"],
            "name": item["name"],
            "full_path": full_path
        })
        
        # FULL RECURSION - No limits for business requirements
        subfolders = get_all_folders_recursive(service, item["id"], full_path)
        folders.extend(subfolders)
            
except Exception as e:
    st.error(f"Error accessing folder {parent_path}: {str(e)}")

return folders
```

def list_files(service, folder_id):
“”“List files in a specific folder”””
try:
results = service.files().list(
q=f”’{folder_id}’ in parents and trashed=false”,
fields=“files(id, name, mimeType, modifiedTime, size)”
).execute()
files = results.get(‘files’, [])
return files
except Exception as e:
st.error(f”Error listing files: {str(e)}”)
return []

def download_file(service, file_id, name):
“”“Download a file from Google Drive”””
try:
request = service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
_, done = downloader.next_chunk()
path = os.path.join(DOCS_DIR, name)
with open(path, ‘wb’) as f:
f.write(fh.getvalue())
return path
except Exception as e:
st.error(f”Error downloading file: {str(e)}”)
return None

def extract_text_from_file(service, file_id, file_name):
“”“Extract text content from a Google Drive file”””
try:
# Download the file
request = service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
_, done = downloader.next_chunk()

```
    # Extract text based on file type
    file_content = fh.getvalue()
    
    if file_name.lower().endswith('.pdf'):
        # Extract text from PDF
        pdf_doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in pdf_doc:
            text += page.get_text() + "\n"
        pdf_doc.close()
        return text
        
    elif file_name.lower().endswith('.docx'):
        # Extract text from Word document
        doc = DocxDoc(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
        
    elif file_name.lower().endswith('.txt'):
        # Extract text from text file
        return file_content.decode('utf-8')
    
    else:
        return "Text extraction not supported for this file type."
        
except Exception as e:
    return f"Error extracting text: {str(e)}"
```

def create_elevenlabs_audio(text, doc_name):
“”“Create ultra-natural speech using ElevenLabs API”””

```
# For now, show instructions to set up ElevenLabs
st.markdown(f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
    <h4 style="margin-top: 0; color: white;">🎙️ Ultra-Natural Voice Option: {doc_name}</h4>
    <p style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 6px; margin: 1rem 0;">
        "{text[:200]}..."
    </p>
    <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h5>🚀 Want TRULY Natural Voice?</h5>
        <p><strong>ElevenLabs AI Voice</strong> - Sounds completely human!</p>
        <ul style="margin: 0.5rem 0;">
            <li>📈 <strong>Cost:</strong> $5/month for 30K characters</li>
            <li>🎭 <strong>Quality:</strong> Indistinguishable from human speech</li>
            <li>⚡ <strong>Setup:</strong> 5-minute API integration</li>
            <li>🎯 <strong>Perfect for:</strong> Professional automotive presentations</li>
        </ul>
        <p style="margin-top: 1rem;"><strong>For your patent demo, this would be INCREDIBLE!</strong></p>
    </div>
</div>
""", unsafe_allow_html=True)

# Add button to use current voice or upgrade prompt
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔊 Use Current Voice", key=f"current_voice_{doc_name}", use_container_width=True):
        return True  # Trigger current speech system

with col2:
    if st.button("🚀 Get ElevenLabs Setup Guide", key=f"elevenlabs_guide_{doc_name}", use_container_width=True):
        st.markdown("""
        ## 🎙️ ElevenLabs Integration Guide
        
        **Step 1:** Go to [ElevenLabs.io](https://elevenlabs.io)
        **Step 2:** Sign up for $5/month plan
        **Step 3:** Get your API key
        **Step 4:** Add to Streamlit secrets:
        ```toml
        [elevenlabs]
        api_key = "your_api_key_here"
        ```
        **Step 5:** I'll update the code to use ElevenLabs!
        
        **Result:** Human-quality voice that will WOW your patent demo! 🎯
        """)

return False
```

# Alternative: Better browser voice selection for immediate improvement

def get_best_available_voice():
“”“Get the absolute best voice available on the current system”””
return “””
<script>
// Ultra-premium voice hunting
function findUltraBestVoice() {
const voices = speechSynthesis.getVoices();

```
    // Tier 1: Neural/AI voices (best available)
    const tier1 = voices.filter(v => 
        v.name.toLowerCase().includes('neural') ||
        v.name.toLowerCase().includes('wavenet') ||
        v.name.toLowerCase().includes('enhanced') && v.lang.includes('en-US')
    );
    
    // Tier 2: Premium system voices
    const tier2 = voices.filter(v => 
        (v.name.includes('Zira') || v.name.includes('David') || 
         v.name.includes('Samantha') || v.name.includes('Alex')) &&
        v.lang.includes('en')
    );
    
    // Tier 3: Any decent English voice
    const tier3 = voices.filter(v => 
        v.lang.includes('en-US') && !v.name.toLowerCase().includes('compact')
    );
    
    return tier1[0] || tier2[0] || tier3[0] || voices[0];
}

const bestVoice = findUltraBestVoice();
console.log('Selected ultra-premium voice:', bestVoice?.name);

return bestVoice;
</script>
"""
"""Intelligently truncate text at sentence boundaries for natural speech"""
if not text or len(text) <= max_length:
    return text

# Clean up the text first
import re
text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
text = re.sub(r'[^\w\s.,!?;:-]', '', text)  # Remove special chars but keep punctuation

# If text is short enough, return as-is
if len(text) <= max_length:
    return text

# Find the best place to cut - look for sentence endings near the limit
truncated = text[:max_length]

# Look for sentence endings (. ! ?) in the last 100 characters
sentence_endings = []
for i, char in enumerate(truncated):
    if char in '.!?':
        sentence_endings.append(i)

if sentence_endings:
    # Cut at the last complete sentence
    cut_point = sentence_endings[-1] + 1
    result = text[:cut_point].strip()
    if len(result) > 50:  # Make sure we don't get too short
        return result

# If no good sentence ending, look for clause endings (, ; :)
clause_endings = []
for i, char in enumerate(truncated):
    if char in ',;:':
        clause_endings.append(i)

if clause_endings:
    # Cut at the last clause ending
    cut_point = clause_endings[-1] + 1
    result = text[:cut_point].strip()
    if len(result) > 100:  # Make sure we have substantial content
        return result

# Last resort: cut at word boundary
words = truncated.split(' ')
if len(words) > 1:
    # Remove the last incomplete word
    complete_words = ' '.join(words[:-1])
    if len(complete_words) > 50:
        return complete_words + "..."

# Fallback: just truncate and add ellipsis
return truncated + "..."
```

def generate_summary(text):
“”“Generate a simple summary (lightweight version)”””
if not text.strip():
return “No readable content found.”

```
# Simple text truncation for demo
sentences = text.split('.')[:3]  # First 3 sentences
summary = '. '.join(sentences).strip()

if len(summary) > 300:
    summary = summary[:300] + "..."

return summary if summary else "Document summary would appear here with full AI capabilities."
```

def process_voice_command(docs, service, demo_mode):
“”“Process voice commands and execute actions”””
if ‘voice_command’ in st.session_state and st.session_state.voice_command:
command = st.session_state.voice_command
action = command[‘action’]
search_term = command[‘search_term’]

```
    # Search for matching documents
    matching_docs = []
    for doc in docs:
        doc_name = doc.get('name', '').lower()
        if search_term in doc_name:
            matching_docs.append(doc)
    
    if matching_docs:
        st.success(f"🎯 Found {len(matching_docs)} document(s) matching '{search_term}'")
        
        # Process the first matching document
        target_doc = matching_docs[0]
        doc_name = target_doc.get('name', 'Unknown Document')
        
        if action == 'summarize':
            st.markdown("### 🤖 Auto-Generated Summary")
            
            if demo_mode or 'id' not in target_doc:
                # Demo summary
                demo_summaries = {
                    'chat': "ChatAI Introduction and FAQ: This document covers the basics of AI-powered chat systems, including implementation strategies, common questions, and best practices for automotive dealerships.",
                    'impel': "Impel AI Platform Review: Comprehensive analysis of Impel's automotive AI platform, comparing features with competitors and outlining integration benefits for dealership operations.",
                    'automotive': "Automotive AI Platform Comparison: Detailed evaluation of leading AI platforms in the automotive sector, including cost analysis and ROI projections."
                }
                
                summary = next((v for k, v in demo_summaries.items() if k in search_term), 
                             f"AI Summary of {doc_name}: This document contains important information relevant to your automotive business operations and strategic decisions.")
                
                st.info(f"📋 **Summary of {doc_name}:**\n\n{summary}")
                
                # Auto-read the summary
                speech_component = create_speech_component(summary, f"Summary of {doc_name}")
                st.markdown(speech_component, unsafe_allow_html=True)
                
            else:
                # Real document summary
                with st.spinner(f"Analyzing {doc_name}..."):
                    file_text = extract_text_from_file(service, target_doc['id'], doc_name)
                    if file_text and not file_text.startswith("Error"):
                        summary = generate_summary(file_text)
                        st.info(f"📋 **Summary of {doc_name}:**\n\n{summary}")
                        
                        # Auto-read the summary
                        speech_component = create_speech_component(summary, f"Summary of {doc_name}")
                        st.markdown(speech_component, unsafe_allow_html=True)
                    else:
                        st.error("Unable to analyze document")
        
        elif action == 'read':
            st.markdown("### 🔊 Auto-Reading Document")
            
            if demo_mode or 'id' not in target_doc:
                demo_text = f"Now reading {doc_name}. This is a demonstration of the voice reading capability for automotive document management."
                speech_component = create_speech_component(demo_text, doc_name)
                st.markdown(speech_component, unsafe_allow_html=True)
            else:
                with st.spinner(f"Extracting text from {doc_name}..."):
                    file_text = extract_text_from_file(service, target_doc['id'], doc_name)
                    if file_text and not file_text.startswith("Error"):
                        speech_component = create_speech_component(file_text, doc_name)
                        st.markdown(speech_component, unsafe_allow_html=True)
                    else:
                        st.error("Unable to extract text for reading")
        
        elif action == 'find':
            st.markdown("### 🔍 Search Results")
            st.success(f"Found {len(matching_docs)} document(s):")
            for doc in matching_docs:
                st.write(f"📄 {doc.get('name', 'Unknown')}")
        
        # Clear the command after processing
        st.session_state.voice_command = None
        
    else:
        st.warning(f"❌ No documents found matching '{search_term}'. Try a different search term.")
```

# Demo documents for fallback

demo_docs = [
{‘id’: ‘demo_1’, ‘name’: ‘AI Strategy Presentation.pdf’, ‘mimeType’: ‘application/pdf’},
{‘id’: ‘demo_2’, ‘name’: ‘Q4 Sales Report.docx’, ‘mimeType’: ‘application/vnd.openxmlformats-officedocument.wordprocessingml.document’},
{‘id’: ‘demo_3’, ‘name’: ‘Customer Analysis Dashboard.xlsx’, ‘mimeType’: ‘application/vnd.openxmlformats-officedocument.spreadsheetml.sheet’},
{‘id’: ‘demo_4’, ‘name’: ‘Product Roadmap 2025.pdf’, ‘mimeType’: ‘application/pdf’},
{‘id’: ‘demo_5’, ‘name’: ‘Team Performance Metrics.docx’, ‘mimeType’: ‘application/vnd.openxmlformats-officedocument.wordprocessingml.document’},
{‘id’: ‘demo_6’, ‘name’: ‘Marketing Campaign Results.pdf’, ‘mimeType’: ‘application/pdf’}
]

# Main UI

st.markdown(”””

<div class="main-header">
    <h1>🎤 Voice-Powered Document Assistant</h1>
    <p>AI-powered mobile document search with voice commands</p>
</div>
""", unsafe_allow_html=True)

# Voice Interface Section with Audio Permission Request

st.markdown(”””

<div class="voice-container">
    <h3 style="margin-top: 0;">🎙️ Voice Commands</h3>
    <p>Use the voice input below to search your documents</p>
</div>
""", unsafe_allow_html=True)

# Audio permission and test section

st.markdown(”### 🔊 Audio Setup”)
col1, col2 = st.columns([1, 1])

with col1:
if st.button(“🔧 Test Audio System”, use_container_width=True):
st.markdown(”””
<script>
// Request audio permission and test
async function testAudioPermission() {
try {
// Test speech synthesis
if (‘speechSynthesis’ in window) {
const testUtterance = new SpeechSynthesisUtterance(‘Audio test successful. Text to speech is working.’);
testUtterance.volume = 1;
testUtterance.rate = 0.8;
speechSynthesis.speak(testUtterance);

```
                // Show success message
                const statusDiv = document.createElement('div');
                statusDiv.style.cssText = 'background: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0; color: #155724;';
                statusDiv.innerHTML = '✅ Audio test started! You should hear "Audio test successful..."';
                document.body.appendChild(statusDiv);
                
                setTimeout(() => {
                    if (statusDiv.parentNode) {
                        statusDiv.parentNode.removeChild(statusDiv);
                    }
                }, 5000);
                
            } else {
                alert('Speech synthesis not supported in this browser. Try Chrome or Edge.');
            }
        } catch (error) {
            alert('Audio test failed: ' + error.message);
        }
    }
    
    testAudioPermission();
    </script>
    """, unsafe_allow_html=True)
```

with col2:
if st.button(“📋 Audio Troubleshooting”, use_container_width=True):
st.markdown(”””
**🔧 If you can’t hear audio:**

```
    1. **Check browser settings:**
       - Chrome: Settings → Site Settings → Sound → Allow
       - Edge: Settings → Site permissions → Sound → Allow
    
    2. **Try these steps:**
       - Refresh the page
       - Try an incognito/private window
       - Check your system volume
       - Try a different browser (Chrome works best)
    
    3. **Manual test:**
       - Open browser console (F12)
       - Type: `speechSynthesis.speak(new SpeechSynthesisUtterance("test"))`
       - Press Enter
    """)
```

# Add clear folder cache button for troubleshooting

if st.button(“🔄 Clear Cache & Reload Folders”):
st.session_state.all_folders = None
st.session_state.folder_cache_time = None
st.rerun()

# Enhanced voice input with mobile-first design

st.markdown(”### 🎤 Voice Commands”)

# Mobile-optimized voice interface

col1, col2 = st.columns([3, 1])

with col1:
# Always-listening activation phrase
st.markdown(”””
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin: 1rem 0;">
<h4 style="margin: 0; color: white;">🚗 Hands-Free Voice Commands</h4>
<p style="margin: 0.5rem 0; font-size: 18px;"><strong>Just say:</strong></p>
<div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
<p style="margin: 0; font-size: 16px;"><strong>“Hey Assistant, summarize [filename]”</strong></p>
<p style="margin: 0; font-size: 16px;"><strong>“Hey Assistant, read [document]”</strong></p>
<p style="margin: 0; font-size: 16px;"><strong>“Hey Assistant, find [topic]”</strong></p>
</div>
</div>
“””, unsafe_allow_html=True)

with col2:
# Large mobile-friendly microphone button
if st.button(“🎤”, key=“big_mic_button”, use_container_width=True, help=“Tap to start voice command”):
st.components.v1.html(”””
<div style="text-align: center; padding: 20px;">
<div id="listening-status" style="
background: linear-gradient(45deg, #ff6b6b, #ee5a24);
color: white;
padding: 15px;
border-radius: 50px;
font-size: 18px;
font-weight: bold;
animation: pulse 1.5s infinite;
">🎤 LISTENING…</div>
</div>

```
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    </style>
    
    <script>
    // Mobile-optimized speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            document.getElementById('listening-status').innerHTML = '🎤 LISTENING... Speak now!';
            document.getElementById('listening-status').style.background = 'linear-gradient(45deg, #00d2ff, #3a7bd5)';
        };
        
        recognition.onresult = function(event) {
            const command = event.results[0][0].transcript.toLowerCase();
            document.getElementById('listening-status').innerHTML = '✅ Command: "' + command + '"';
            document.getElementById('listening-status').style.background = 'linear-gradient(45deg, #56ab2f, #a8e6cf)';
            
            // Process the voice command
            processVoiceCommand(command);
        };
        
        recognition.onerror = function(event) {
            document.getElementById('listening-status').innerHTML = '❌ Error: ' + event.error;
            document.getElementById('listening-status').style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
        };
        
        recognition.onend = function() {
            setTimeout(() => {
                document.getElementById('listening-status').innerHTML = '👆 Tap microphone to try again';
                document.getElementById('listening-status').style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
            }, 3000);
        };
        
        function processVoiceCommand(command) {
            // Enhanced command processing for automotive use
            let action = null;
            let searchTerm = null;
            
            // Remove activation phrases
            command = command.replace(/hey assistant,?/gi, '').trim();
            command = command.replace(/hey wma,?/gi, '').trim();
            
            // More natural command recognition
            if (command.includes('summarize') || command.includes('summary') || 
                command.includes('tell me about') || command.includes('what is')) {
                action = 'summarize';
            } else if (command.includes('read') || command.includes('play') || 
                      command.includes('speak') || command.includes('listen to')) {
                action = 'read';
            } else if (command.includes('find') || command.includes('search') || 
                      command.includes('show me') || command.includes('get me')) {
                action = 'find';
            }
            
            // Extract the document/topic
            const removeWords = ['summarize', 'summary', 'read', 'play', 'speak', 'find', 
                               'search', 'show', 'me', 'the', 'file', 'document', 'about', 'on'];
            let words = command.split(' ');
            searchTerm = words.filter(word => 
                !removeWords.includes(word.toLowerCase())
            ).join(' ').trim();
            
            if (action && searchTerm) {
                document.getElementById('listening-status').innerHTML = 
                    '🎯 Command: ' + action + ' "' + searchTerm + '"<br>' +
                    '<small>Processing your request...</small>';
                
                // Store command for processing (would trigger Streamlit rerun)
                sessionStorage.setItem('voiceCommand', JSON.stringify({
                    action: action,
                    searchTerm: searchTerm,
                    timestamp: Date.now()
                }));
                
                // Trigger page refresh to process command
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                document.getElementById('listening-status').innerHTML = 
                    '❓ Couldn\'t understand command<br>' +
                    '<small>Try: "Summarize [filename]" or "Read [document]"</small>';
            }
        }
        
        // Start listening immediately
        recognition.start();
        
    } else {
        document.getElementById('listening-status').innerHTML = 
            '❌ Speech recognition not supported<br>' +
            '<small>Please use Chrome or Edge browser</small>';
    }
    </script>
    """, height=150)
```

# Enhanced voice command examples for automotive use

with st.expander(“🚗 Voice Commands for Driving”):
st.markdown(”””
**🎯 Perfect for CarPlay/Android Auto:**

```
**📋 DOCUMENT COMMANDS:**
- *"Hey Assistant, summarize the Chat AI handout"*
- *"Hey Assistant, read the Impel comparison"*
- *"Hey Assistant, find automotive platform docs"*

**🚗 DEALER-SPECIFIC:**
- *"Hey Assistant, show me AutoNation reports"*
- *"Hey Assistant, read dealer inventory"*
- *"Hey Assistant, find sales presentations"*

**💡 TIPS:**
- Works with **Bluetooth** in your car
- **Hands-free** operation while driving
- **Voice feedback** confirms your commands
- Works with **Siri/Google Assistant** activation
""")
```

# Process stored voice commands from mobile

if ‘voiceCommand’ not in st.session_state:
st.session_state.voiceCommand = None

# Check for voice command from mobile interface

try:
# This would be populated by the mobile voice interface
stored_command = st.session_state.get(‘mobile_voice_command’, None)
if stored_command:
st.session_state.voiceCommand = stored_command
st.session_state.mobile_voice_command = None  # Clear after processing
except:
pass

# Search interface

st.markdown(”### 🔍 Search Documents”)
filename_query = st.text_input(
“📄 Search by filename”,
placeholder=“Type filename to search…”,
label_visibility=“collapsed”
)

# Use the combined search query

active_query = voice_input if voice_input else filename_query

# Initialize session state for caching

if ‘all_folders’ not in st.session_state:
st.session_state.all_folders = None
if ‘folder_cache_time’ not in st.session_state:
st.session_state.folder_cache_time = None
if ‘current_step’ not in st.session_state:
st.session_state.current_step = 1
if ‘selected_folder_id’ not in st.session_state:
st.session_state.selected_folder_id = None
if ‘selected_folder_path’ not in st.session_state:
st.session_state.selected_folder_path = None

# Authentication and Google Drive setup

try:
service = authenticate_gdrive()
demo_mode = service is None

```
if service:
    st.success("🔗 Connected to Google Drive! Loading your folders...")
else:
    st.warning("⚠️ Google Drive not connected. Using demo mode.")
```

except Exception as e:
st.error(f”🚫 Authentication setup failed: {str(e)}”)
service = None
demo_mode = True

# Google Drive folder setup

root_id = “1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6”  # Your root folder ID
all_folders = []
docs = []

if not demo_mode and service:
# Get all folders (with smart caching)
try:
# Check if we need to refresh cache (20 minute expiry - balance between freshness and load time)
import time
current_time = time.time()
cache_expired = (
st.session_state.folder_cache_time is None or
current_time - st.session_state.folder_cache_time > 1200  # 20 minutes - longer cache for full load
)

```
    if st.session_state.all_folders is None or cache_expired:
        with st.spinner("📁 Loading complete folder structure (this may take 30-60 seconds for 38 dealers)..."):
            st.session_state.all_folders = get_all_folders_recursive(service, root_id)
            st.session_state.folder_cache_time = current_time
            st.success(f"📁 Complete! Loaded {len(st.session_state.all_folders)} folders from all dealers")
    else:
        st.info(f"📁 Using cached structure ({len(st.session_state.all_folders)} folders) - Refreshes every 20 minutes")
        
    all_folders = st.session_state.all_folders
    
    if all_folders:
        st.success(f"📁 Ready! {len(all_folders)} folders available")
        
        # Filter out WMA Test and excluded paths
        excluded_names = ["WMA Test"]
        excluded_paths = ["WMA RAG/WMA Team/RAG_App"]
        
        filtered_folders = [
            f for f in all_folders 
            if f['name'] not in excluded_names and 
            not any(f['full_path'].startswith(p) for p in excluded_paths)
        ]
        
        # Find team folders and WMA folders for step 1
        team_names = ["Aaron", "Brody", "Dona", "Eric", "Grace", "Jeff", "Jessica", "Jill", "John", "Jon", "Kirk", "Owen", "Paul"]
        wma_folders = [f for f in filtered_folders if 'WMA' in f['name']]
        team_folders = [f for f in filtered_folders if f['name'] in team_names]
        
        # Combine and get unique main folder names
        main_folders = wma_folders + team_folders
        main_folder_names = list(set([f['name'] for f in main_folders if '/' not in f['full_path']]))
        main_folder_names.sort()
        
        # Folder Navigation with Security
        st.markdown("### 👤 User Identity")
        
        # Step 0: User Authentication
        user_identity = st.selectbox(
            "**Who are you?**",
            ["Aaron", "Brody", "Dona", "Eric", "Grace", "Jeff", "Jessica", "Jill", "John", "Jon", "Kirk", "Owen", "Paul"],
            label_visibility="visible"
        )
        
        st.markdown("### 📁 Browse Your Folders")
        
        # Filter folders based on user identity - security layer
        if user_identity:
            allowed_folders = [user_identity, "WMA Team"]  # User can see their own folder + shared WMA folders
            
            # Filter main folders to only show allowed ones
            accessible_main_folders = [name for name in main_folder_names if any(name.startswith(allowed) for allowed in allowed_folders)]
            
            if not accessible_main_folders:
                st.error(f"No folders found for {user_identity}. Please contact your administrator.")
                docs = demo_docs
                demo_mode = True
            else:
                # Step 1: Select main folder (filtered by user identity)
                selected_main_folder = st.selectbox(
                    f"**Step 1:** Choose your folder (showing folders for {user_identity})", 
                    accessible_main_folders,
                    label_visibility="visible"
                )
                
                # Step 2: Get subfolders for selected main folder (with security check)
                if selected_main_folder in accessible_main_folders:
                    subfolders = [f for f in filtered_folders if f['full_path'].startswith(selected_main_folder + '/')]
                    level_1_subfolders = [f for f in subfolders if f['full_path'].count('/') == 1]
                    
                    selected_folder = None
                    selected_folder_path = selected_main_folder
                    
                    if level_1_subfolders:
                        level_1_paths = [f['full_path'] for f in level_1_subfolders]
                        level_1_paths.sort()
                        
                        selected_level_1 = st.selectbox(
                            "**Step 2:** Choose subfolder", 
                            level_1_paths,
                            label_visibility="visible"
                        )
                        
                        # Step 3: Get level 2 subfolders
                        level_2_subfolders = [f for f in filtered_folders if f['full_path'].startswith(selected_level_1 + '/')]
                        immediate_level_2 = [f for f in level_2_subfolders if f['full_path'].count('/') == 2]
                        
                        if immediate_level_2:
                            level_2_paths = [f['full_path'] for f in immediate_level_2]
                            level_2_paths.sort()
                            
                            selected_level_2 = st.selectbox(
                                "**Step 3:** Choose final folder", 
                                level_2_paths,
                                label_visibility="visible"
                            )
                            
                            selected_folder = next((f for f in immediate_level_2 if f['full_path'] == selected_level_2), None)
                            selected_folder_path = selected_level_2
                        else:
                            # Use level 1 as final selection
                            selected_folder = next((f for f in level_1_subfolders if f['full_path'] == selected_level_1), None)
                            selected_folder_path = selected_level_1
                    else:
                        # Use main folder as final selection
                        selected_folder = next((f for f in main_folders if f['name'] == selected_main_folder and '/' not in f['full_path']), None)
                        selected_folder_path = selected_main_folder
                else:
                    st.error(f"🚫 Access denied: {user_identity} cannot access {selected_main_folder} folder")
                    docs = demo_docs
                    demo_mode = True
                    selected_folder = None
                
                # Load files with security validation
                if selected_folder:
                    # Double-check security: ensure user can access this folder
                    folder_owner = selected_folder['full_path'].split('/')[0]
                    if folder_owner in allowed_folders or any(selected_folder['full_path'].startswith(allowed) for allowed in allowed_folders):
                        with st.spinner(f"Loading files from {selected_folder['name']}..."):
                            docs = list_files(service, selected_folder['id'])
                        
                        if docs:
                            st.success(f"📄 Found **{len(docs)}** files in **{selected_folder['name']}**")
                            demo_mode = False
                        else:
                            st.warning(f"No files found in {selected_folder['full_path']}. Folder appears to be empty.")
                            st.info("Showing demo documents instead.")
                            docs = demo_docs
                            demo_mode = True
                    else:
                        st.error(f"🚫 Security violation: {user_identity} attempted to access unauthorized folder {selected_folder['full_path']}")
                        docs = demo_docs
                        demo_mode = True
                else:
                    st.warning("Please select a folder to view its contents.")
                    docs = demo_docs
                    demo_mode = True
        else:
            st.warning("Please select your identity to continue.")
            docs = demo_docs
            demo_mode = True
    else:
        st.warning("No folders found in Google Drive. Showing demo documents.")
        docs = demo_docs
        demo_mode = True
        
except Exception as e:
    st.error(f"Error loading Google Drive folders: {str(e)}")
    docs = demo_docs
    demo_mode = True
```

else:
# Demo mode
st.info(“📁 **Demo Mode:** Showing sample documents”)
docs = demo_docs

# Process voice commands if any

if docs:
process_voice_command(docs, service if not demo_mode else None, demo_mode)

# Apply search filter

if active_query and docs:
original_count = len(docs)
filtered_docs = [doc for doc in docs if active_query.lower() in doc[“name”].lower()]
if filtered_docs:
docs = filtered_docs
st.info(f”🔍 **Search Results:** Found {len(docs)} documents matching ‘{active_query}’ (out of {original_count} total)”)
else:
st.warning(f”❌ No documents found matching ‘{active_query}’ in the selected folder”)

# Display results

st.markdown(”—”)
st.markdown(”### 📄 Documents”)

if docs:
if demo_mode:
st.info(f”**Demo Mode:** Showing {len(docs)} sample documents”)
else:
st.success(f”**{len(docs)} documents** from **{selected_folder_path}**”)

```
# Display each document
for i, doc in enumerate(docs):
    doc_name = doc.get('name', 'Unknown Document')
    
    st.markdown(f"""
    <div class="file-card">
        <div class="file-name">📄 {doc_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📖 Summary", key=f"sum_{i}", use_container_width=True):
            if demo_mode:
                # Demo summaries
                demo_summaries = [
                    "This AI Strategy presentation outlines our company's approach to implementing artificial intelligence across key business functions. It covers market trends, competitive analysis, and a 3-year AI adoption roadmap.",
                    "Q4 sales exceeded targets by 15% with strong enterprise performance. Key highlights include 23% growth in recurring revenue and successful premium tier launch.",
                    "Customer analysis reveals 45% increase in mobile app usage. Demographics show growth in 25-34 age segment with improved satisfaction scores.",
                    "2025 product roadmap focuses on user experience enhancements, AI-powered features, and platform scalability with major Q2 and Q4 releases.",
                    "Team performance metrics show 12% productivity improvement with new workflow optimizations. Employee satisfaction reached 4.6/5.",
                    "Marketing campaign achieved 3.2x ROI with strong digital performance. Email open rates at 28%, social engagement up 67%."
                ]
                summary = demo_summaries[i % len(demo_summaries)]
                st.success(f"**📋 AI Summary:** {summary}")
            else:
                st.success(f"**📋 Real Document Analysis:** This would analyze '{doc_name}' from your Google Drive folder '{selected_folder_path}' using AI!")
    
    with col2:
        if st.button("🔊 Read", key=f"speak_{i}", use_container_width=True):
            if demo_mode:
                # Demo text-to-speech using Streamlit components
                demo_texts = [
                    "This AI Strategy presentation outlines our company's approach to implementing artificial intelligence across key business functions. It covers market trends, competitive analysis, and a comprehensive three-year AI adoption roadmap for automotive dealerships.",
                    "Q4 sales exceeded targets by 15% with exceptional enterprise performance. Key highlights include 23% growth in recurring revenue and successful premium tier launch across all dealer locations.",
                    "Customer analysis reveals a 45% increase in mobile app usage with significant improvements in user experience. Demographics show strong growth in the 25-34 age segment with improved satisfaction scores reaching 4.6 out of 5 stars.",
                    "The 2025 product roadmap focuses on user experience enhancements, AI-powered features, and platform scalability. Major releases are planned for Q2 and Q4 with advanced automotive integration capabilities.",
                    "Team performance metrics demonstrate 12% productivity improvement with new workflow optimizations. Employee satisfaction has reached an all-time high of 4.6 out of 5, reflecting successful change management initiatives.",
                    "Marketing campaign achieved an impressive 3.2x return on investment with strong digital performance. Email open rates reached 28%, social engagement increased by 67%, making this our most successful campaign to date."
                ]
                demo_text = demo_texts[i % len(demo_texts)]
                
                # Use smart truncation for natural speech
                speech_text = smart_text_truncate(demo_text, 400)
                
                # Create a working speech component using Streamlit's method
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
                    <h4 style="margin-top: 0; color: white;">🔊 Now Reading: {doc_name}</h4>
                    <p style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 6px; font-style: italic; margin: 1rem 0;">
                        "{demo_text}"
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show controls after starting speech
                col_stop, col_pause = st.columns([1, 1])
                with col_stop:
                    if st.button("⏹️ Stop Speech", key=f"stop_speech_{i}", use_container_width=True):
                        st.components.v1.html("""
                        <script>
                        if ('speechSynthesis' in window) {
                            speechSynthesis.cancel();
                        }
                        document.body.innerHTML = '<div style="background: #dc3545; color: white; padding: 10px; text-align: center; border-radius: 5px;">⏹️ Speech Stopped</div>';
                        </script>
                        """, height=50)
                
                with col_pause:
                    if st.button("⏸️ Pause/Resume", key=f"pause_speech_{i}", use_container_width=True):
                        st.components.v1.html("""
                        <script>
                        if ('speechSynthesis' in window) {
                            if (speechSynthesis.speaking && !speechSynthesis.paused) {
                                speechSynthesis.pause();
                                document.body.innerHTML = '<div style="background: #ffc107; color: black; padding: 10px; text-align: center; border-radius: 5px;">⏸️ Speech Paused</div>';
                            } else if (speechSynthesis.paused) {
                                speechSynthesis.resume();
                                document.body.innerHTML = '<div style="background: #28a745; color: white; padding: 10px; text-align: center; border-radius: 5px;">▶️ Speech Resumed</div>';
                            }
                        }
                        </script>
                        """, height=50)
                st.components.v1.html(f"""
                <script>
                // Wait for page to load then speak with best voice
                window.addEventListener('load', function() {{
                    setTimeout(function() {{
                        if ('speechSynthesis' in window) {{
                            // Get all available voices
                            let voices = speechSynthesis.getVoices();
                            
                            // If voices not loaded yet, wait for them
                            if (voices.length === 0) {{
                                speechSynthesis.onvoiceschanged = function() {{
                                    voices = speechSynthesis.getVoices();
                                    speakWithBestVoice(voices);
                                }};
                            }} else {{
                                speakWithBestVoice(voices);
                            }}
                            
                            function speakWithBestVoice(voices) {{
                                console.log('Available voices:', voices.length);
                                
                                // Priority list for best English voices (most natural first)
                                const preferredVoices = [
                                    // Windows high-quality voices
                                    'Microsoft Zira - English (United States)',
                                    'Microsoft David - English (United States)', 
                                    'Microsoft Mark - English (United States)',
                                    'Microsoft Hazel - English (Great Britain)',
                                    
                                    // macOS high-quality voices
                                    'Alex', 'Samantha', 'Victoria', 'Karen', 'Daniel',
                                    'Fiona', 'Moira', 'Tessa',
                                    
                                    // Chrome/Edge premium voices
                                    'Google US English', 'Chrome OS US English',
                                    'Microsoft Edge English',
                                    
                                    // Android premium voices
                                    'en-US-language', 'en-us-x-sfg-network',
                                    'en-US-Wavenet', 'English United States',
                                    
                                    // iOS premium voices
                                    'Ava (Enhanced)', 'Allison (Enhanced)', 
                                    'Tom (Enhanced)', 'Susan (Enhanced)'
                                ];
                                
                                let selectedVoice = null;
                                
                                // Try to find the best voice
                                for (let preferred of preferredVoices) {{
                                    selectedVoice = voices.find(voice => 
                                        voice.name.includes(preferred) ||
                                        voice.name === preferred
                                    );
                                    if (selectedVoice) break;
                                }}
                                
                                // Fallback: find any good English voice
                                if (!selectedVoice) {{
                                    selectedVoice = voices.find(voice => 
                                        voice.lang.includes('en-US') && voice.name.toLowerCase().includes('enhanced')
                                    ) || voices.find(voice => 
                                        voice.lang.includes('en-US') && voice.name.toLowerCase().includes('premium')
                                    ) || voices.find(voice => 
                                        voice.lang.includes('en-US') && !voice.name.toLowerCase().includes('compact')
                                    ) || voices.find(voice => 
                                        voice.lang.includes('en')
                                    ) || voices[0];
                                }}
                                
                                const utterance = new SpeechSynthesisUtterance(`{demo_text.replace('"', '\\"').replace("'", "\\'")}`);
                                
                                // Use the selected high-quality voice
                                if (selectedVoice) {{
                                    utterance.voice = selectedVoice;
                                    console.log('Using voice:', selectedVoice.name);
                                }}
                                
                                // Optimize speech parameters for natural sound
                                utterance.rate = 0.85;      // Slightly slower for clarity
                                utterance.pitch = 1.0;     // Natural pitch
                                utterance.volume = 1.0;    // Full volume
                                
                                speechSynthesis.speak(utterance);
                                
                                // Show visual feedback with voice info
                                document.body.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
                                document.body.style.color = 'white';
                                document.body.style.padding = '20px';
                                document.body.style.borderRadius = '10px';
                                document.body.innerHTML = `
                                    <h3>🔊 Speaking: {doc_name}</h3>
                                    <p>Voice: ${{selectedVoice ? selectedVoice.name : 'Default'}}</p>
                                    <p>Audio is playing with enhanced voice quality...</p>
                                `;
                            }}
                        }}
                    }}, 500);
                }});
                </script>
                <div style="background: #28a745; color: white; padding: 10px; text-align: center; border-radius: 5px;">
                    🔊 Loading premium voice... (You should hear high-quality speech)
                </div>
                """, height=100)
                
            else:
                # Real document text-to-speech
                if 'id' in doc:
                    with st.spinner("Extracting text for speech..."):
                        file_text = extract_text_from_file(service, doc['id'], doc_name)
                        if file_text and not file_text.startswith("Error"):
                            # Use smart truncation to end at complete sentences
                            speech_text = smart_text_truncate(file_text, 600)
                            clean_text = speech_text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
                            
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
                                <h4 style="margin-top: 0; color: white;">🔊 Now Reading: {doc_name}</h4>
                                <p style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 6px; font-style: italic; margin: 1rem 0;">
                                    "{speech_text}"
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add stop/pause controls for real documents too
                            col_stop, col_pause = st.columns([1, 1])
                            with col_stop:
                                if st.button("⏹️ Stop Speech", key=f"stop_real_{i}", use_container_width=True):
                                    st.components.v1.html("""
                                    <script>
                                    if ('speechSynthesis' in window) {
                                        speechSynthesis.cancel();
                                    }
                                    document.body.innerHTML = '<div style="background: #dc3545; color: white; padding: 10px; text-align: center; border-radius: 5px;">⏹️ Document Speech Stopped</div>';
                                    </script>
                                    """, height=50)
                            
                            with col_pause:
                                if st.button("⏸️ Pause/Resume", key=f"pause_real_{i}", use_container_width=True):
                                    st.components.v1.html("""
                                    <script>
                                    if ('speechSynthesis' in window) {
                                        if (speechSynthesis.speaking && !speechSynthesis.paused) {
                                            speechSynthesis.pause();
                                            document.body.innerHTML = '<div style="background: #ffc107; color: black; padding: 10px; text-align: center; border-radius: 5px;">⏸️ Document Paused</div>';
                                        } else if (speechSynthesis.paused) {
                                            speechSynthesis.resume();
                                            document.body.innerHTML = '<div style="background: #28a745; color: white; padding: 10px; text-align: center; border-radius: 5px;">▶️ Document Resumed</div>';
                                        }
                                    }
                                    </script>
                                    """, height=50)
                            st.components.v1.html(f"""
                            <script>
                            window.addEventListener('load', function() {{
                                setTimeout(function() {{
                                    if ('speechSynthesis' in window) {{
                                        let voices = speechSynthesis.getVoices();
                                        
                                        if (voices.length === 0) {{
                                            speechSynthesis.onvoiceschanged = function() {{
                                                voices = speechSynthesis.getVoices();
                                                speakDocument(voices);
                                            }};
                                        }} else {{
                                            speakDocument(voices);
                                        }}
                                        
                                        function speakDocument(voices) {{
                                            // Premium voice selection for documents
                                            const preferredVoices = [
                                                'Microsoft Zira - English (United States)',
                                                'Microsoft David - English (United States)', 
                                                'Alex', 'Samantha', 'Victoria',
                                                'Google US English', 'Ava (Enhanced)',
                                                'en-US-Wavenet'
                                            ];
                                            
                                            let selectedVoice = null;
                                            for (let preferred of preferredVoices) {{
                                                selectedVoice = voices.find(voice => 
                                                    voice.name.includes(preferred) || voice.name === preferred
                                                );
                                                if (selectedVoice) break;
                                            }}
                                            
                                            // Fallback to best available English voice
                                            if (!selectedVoice) {{
                                                selectedVoice = voices.find(voice => 
                                                    voice.lang.includes('en-US') && !voice.name.toLowerCase().includes('compact')
                                                ) || voices.find(voice => voice.lang.includes('en')) || voices[0];
                                            }}
                                            
                                            const utterance = new SpeechSynthesisUtterance(`{clean_text}`);
                                            
                                            if (selectedVoice) {{
                                                utterance.voice = selectedVoice;
                                            }}
                                            
                                            // Professional speech settings for documents
                                            utterance.rate = 0.8;       // Slower for business documents
                                            utterance.pitch = 1.0;     // Natural pitch
                                            utterance.volume = 1.0;    // Full volume
                                            
                                            speechSynthesis.speak(utterance);
                                            
                                            document.body.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                                            document.body.style.color = 'white';
                                            document.body.style.padding = '20px';
                                            document.body.style.borderRadius = '10px';
                                            document.body.innerHTML = `
                                                <h3>🔊 Reading Document: {doc_name}</h3>
                                                <p>High-Quality Voice: ${{selectedVoice ? selectedVoice.name : 'Default'}}</p>
                                                <p>Playing professional document audio...</p>
                                            `;
                                        }}
                                    }}
                                }}, 500);
                            }});
                            </script>
                            <div style="background: #28a745; color: white; padding: 10px; text-align: center; border-radius: 5px;">
                                🔊 Loading premium voice for document... Enhanced audio quality
                            </div>
                            """, height=100)
                        else:
                            st.error("Unable to extract text for speech synthesis")
                else:
                    st.error("Unable to read file: File ID not available")
    
    with col3:
        if st.button("⬇️ Download", key=f"dl_{i}", use_container_width=True):
            if demo_mode:
                st.success(f"✅ **Demo Download:** In production, {doc_name} would download from Google Drive!")
            else:
                # Real download functionality
                if 'id' in doc:
                    with st.spinner("Downloading..."):
                        file_path = download_file(service, doc['id'], doc_name)
                        if file_path:
                            st.success(f"✅ **Downloaded:** {doc_name}")
                            with open(file_path, 'rb') as f:
                                st.download_button(
                                    label=f"💾 Save {doc_name}",
                                    data=f.read(),
                                    file_name=doc_name,
                                    key=f"download_btn_{i}"
                                )
                else:
                    st.error("Unable to download: File ID not available")
    
    with col4:
        if st.button("🔗 Share", key=f"share_{i}", use_container_width=True):
            if demo_mode:
                demo_url = f"https://demo-documents.example.com/{doc_name}"
                st.success(f"**🔗 Demo Share Link:** {demo_url}")
            else:
                if 'id' in doc:
                    share_url = f"https://drive.google.com/file/d/{doc['id']}/view"
                    st.success(f"**🔗 Google Drive Link:** {share_url}")
                    st.code(share_url, language=None)
                else:
                    st.error("Unable to generate share link")
    
    st.markdown("---")
```

else:
st.warning(“📄 No documents found in the selected location.”)
if not demo_mode:
st.info(“💡 Try selecting a different folder or check if the folder contains any files.”)

# Footer

st.markdown(”—”)
st.markdown(”””

<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    🎤 Voice-Powered Smart Document Assistant<br>
    Powered by AI • Built for productivity • Voice-enabled<br>
    <small>💡 Tip: Use Chrome or Edge for best voice experience</small>
</div>
""", unsafe_allow_html=True)
