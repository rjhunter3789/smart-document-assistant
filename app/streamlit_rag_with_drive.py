import os
import io
import fitz  # PyMuPDF
from docx import Document as DocxDoc
import streamlit as st
# Removed heavy AI imports that might be causing startup hang
# from sentence_transformers import SentenceTransformer
# from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from datetime import datetime

# Config
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

# Mobile-optimized page configuration
st.set_page_config(
    page_title="🎤 Voice-Powered Document Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",  # Start with sidebar collapsed on mobile
    menu_items={
        'Get Help': 'https://your-help-url.com',
        'Report a bug': "https://your-bug-report-url.com",
        'About': "# Voice-Powered Smart Document Assistant\nMobile-optimized AI-powered document search with voice commands"
    }
)

# Custom CSS for mobile optimization + Voice UI
st.markdown("""
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
    
    .voice-button {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        width: 80px;
        height: 80px;
        margin: 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .voice-button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(1.1);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }
    
    .voice-button.listening {
        background: #e74c3c;
        border-color: #c0392b;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .voice-status {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .voice-transcript {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        min-height: 50px;
        font-style: italic;
        backdrop-filter: blur(5px);
    }
    
    /* Audio player styling */
    .audio-player {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Mobile-friendly dropdowns */
    .stSelectbox > div > div {
        font-size: 16px !important;
        min-height: 44px;
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
    
    /* Action buttons */
    .action-btn {
        width: 100%;
        margin: 0.25rem 0;
        border-radius: 8px;
        font-weight: 500;
        border: none;
        padding: 0.75rem;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .summarize-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }
    
    .download-btn {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        color: white;
    }
    
    .share-btn {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        color: white;
    }
    
    .speak-btn {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: white;
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
    
    /* Mobile sidebar adjustments */
    .css-1d391kg {
        padding-top: 1rem;
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
        
        .voice-button {
            width: 70px;
            height: 70px;
        }
    }
    
    /* Hide Streamlit branding on mobile */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Authentication functions (unchanged)
def authenticate_gdrive():
    """Authenticate with Google Drive using Streamlit secrets"""
    try:
        # Import here to avoid import errors if not available
        from google.oauth2.credentials import Credentials
        
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

def list_all_folders(service, parent_id, depth=0):
    results = service.files().list(
        q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    folders = results.get('files', [])
    for folder in folders:
        folder['depth'] = depth
        folder['full_path'] = folder['name']
        sub_folders = list_all_folders(service, folder['id'], depth + 1)
        for sub in sub_folders:
            sub['full_path'] = f"{folder['name']}/{sub['full_path']}"
        folders.extend(sub_folders)
    return folders

def list_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

def download_file(service, file_id, name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    path = os.path.join(DOCS_DIR, name)
    with open(path, 'wb') as f:
        f.write(fh.getvalue())
    return path

def extract_text(file_path):
    try:
        if file_path.endswith(".pdf"):
            with fitz.open(file_path) as doc:
                return "\n".join([p.get_text() for p in doc if p.get_text().strip()])
        elif file_path.endswith(".docx"):
            doc = DocxDoc(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception:
        return ""
    return ""

# Lightweight AI setup (commenting out heavy models for cloud deployment)
try:
    # embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    # tokenizer = AutoTokenizer.from_pretrained("t5-small")
    # model = AutoModelForSeq2SeqLM.from_pretrained("t5-small", torch_dtype=torch.float32)
    # summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)
    
    # Use lightweight summarization for demo
    ai_models_loaded = False
    st.info("🔄 Running in lightweight mode - using simplified AI summaries")
except Exception as e:
    ai_models_loaded = False
    st.warning(f"⚠️ AI models not loaded: {str(e)}")

def generate_summary(text):
    """Lightweight summary generation for demo mode"""
    if not text.strip():
        return "No readable content found."
    
    # Simple text truncation for demo (instead of heavy AI models)
    sentences = text.split('.')[:3]  # First 3 sentences
    summary = '. '.join(sentences).strip()
    
    if len(summary) > 300:
        summary = summary[:300] + "..."
    
    return summary if summary else "Document summary would appear here with full AI capabilities."

# Mobile-optimized UI with Voice Interface
st.markdown("""
<div class="main-header">
    <h1>🎤 Voice-Powered Document Assistant</h1>
    <p>AI-powered mobile document search with voice commands</p>
</div>
""", unsafe_allow_html=True)

# Voice Interface Section with Streamlit Native Components
st.markdown("""
<div class="voice-container">
    <h3 style="margin-top: 0;">🎙️ Voice Commands</h3>
    <p>Use the voice input below to search your documents</p>
</div>
""", unsafe_allow_html=True)

# Streamlit Native Voice Interface
voice_component = st.container()
with voice_component:
    # Voice input using Streamlit's built-in microphone support
    st.markdown("### 🎤 Voice Search")
    
    # Create columns for better mobile layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use Streamlit's experimental audio input
        voice_input = st.text_input(
            "🎤 Voice Search", 
            placeholder="Tap here, then use your keyboard's voice button...",
            help="On mobile: Tap here and use your keyboard's microphone button 🎤",
            label_visibility="collapsed"
        )
    
    with col2:
        # Voice instructions button
        if st.button("📱 How to Voice Search", use_container_width=True):
            st.info("""
            **📱 Mobile Voice Search:**
            
            1. **Tap the search box** above
            2. **Look for the microphone icon** on your mobile keyboard 🎤
            3. **Tap the keyboard mic** and speak
            4. **Your voice will be converted to text** automatically!
            
            **💡 Alternative:** Just type your search normally!
            """)
    
    # Voice status indicator
    if voice_input:
        st.markdown(f"""
        <div class="status-success">
            🎤 <strong>Voice Input Detected:</strong> "{voice_input}"
        </div>
        """, unsafe_allow_html=True)

# Text-to-Speech Section
st.markdown("---")
st.markdown("### 🔊 Text-to-Speech")
st.info("""
**💡 Pro Tip:** After generating document summaries, you can use your device's built-in text-to-speech:

📱 **On Mobile:**
- **iPhone:** Settings → Accessibility → Spoken Content → "Speak Selection"
- **Android:** Settings → Accessibility → Text-to-speech

🖥️ **On Desktop:**
- **Windows:** Narrator (Windows key + Ctrl + Enter)
- **Mac:** VoiceOver (Cmd + F5)
- **Chrome:** Right-click text → "Read aloud" (if available)
""")

# Voice-enabled search (now using mobile keyboard voice input)
st.markdown("### 🔍 Search Documents")
col1, col2 = st.columns([1, 1])

with col1:
    filename_query = st.text_input(
        "📄 Search by filename", 
        placeholder="Type filename or use voice input above...", 
        label_visibility="collapsed"
    )

with col2:
    # Combine voice input with filename search
    st.text_input(
        "🔗 Combined Search", 
        value=voice_input if voice_input else filename_query,
        placeholder="Auto-filled from voice or text search...",
        disabled=True,
        label_visibility="collapsed"
    )

# Use the combined search query
active_query = voice_input if voice_input else filename_query

# Initialize session state for mobile navigation
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

try:
    service = authenticate_gdrive()
    if service is None:
        st.warning("🔐 Google Drive not connected. Voice features and search will work, but showing demo documents.")
        # Set up demo mode with sample documents
        demo_mode = True
    else:
        demo_mode = False
except Exception as e:
    st.error(f"🚫 Authentication setup failed: {str(e)}")
    st.info("Running in demo mode with sample documents.")
    service = None
    demo_mode = True

# Demo documents for showcase
demo_docs = [
    {
        'id': 'demo_1',
        'name': 'AI Strategy Presentation.pdf',
        'mimeType': 'application/pdf'
    },
    {
        'id': 'demo_2', 
        'name': 'Q4 Sales Report.docx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },
    {
        'id': 'demo_3',
        'name': 'Customer Analysis Dashboard.xlsx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    },
    {
        'id': 'demo_4',
        'name': 'Product Roadmap 2025.pdf',
        'mimeType': 'application/pdf'
    },
    {
        'id': 'demo_5',
        'name': 'Team Performance Metrics.docx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },
    {
        'id': 'demo_6',
        'name': 'Marketing Campaign Results.pdf',
        'mimeType': 'application/pdf'
    }
]

# Google Drive setup with demo mode check
root_id = "1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6"

if not demo_mode:
    def get_all_folders_recursive(service, parent_id, parent_path=""):
        folders = []
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
                folders.extend(get_all_folders_recursive(service, item["id"], full_path))
        except Exception as e:
            st.error(f"Error accessing folder {parent_path}: {str(e)}")
        
        return folders

    try:
        all_folders = get_all_folders_recursive(service, root_id)
    except Exception as e:
        st.error(f"Failed to load folders: {str(e)}")
        demo_mode = True
        all_folders = []

    if all_folders:
        # Normalize paths
        for f in all_folders:
            f['full_path'] = f['full_path'].strip()
            f['name'] = f['name'].strip()
            f['full_path'] = f['full_path'].replace(' /', '/').replace('/ ', '/')

        # Filter folders
        excluded_paths = ["WMA RAG/WMA Team/RAG_App"]
        filtered_folders = [f for f in all_folders if not any(f['full_path'].startswith(p) for p in excluded_paths)]

        # Team selection
        team_names = ["Aaron", "Brody", "Dona", "Eric", "Grace", "Jeff", "Jessica", "Jill", "John", "Jon", "Kirk", "Owen", "Paul", "WMA Team"]
        user_folders = [f for f in filtered_folders if f['name'] in team_names and '/' not in f['full_path']]

        if not user_folders:
            user_folders = [f for f in filtered_folders if f['name'] in team_names]

        user_names = sorted([f['name'] for f in user_folders])
    else:
        demo_mode = True
        user_names = []
else:
    all_folders = []
    filtered_folders = []
    user_names = []

if not user_names:
    st.error("🚫 No user folders found. Please check your folder structure.")
    st.stop()

# Mobile navigation with demo mode support
if not demo_mode and user_names:
    with st.container():
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">📁 Step 1: Select Your Folder</div>', unsafe_allow_html=True)
        selected_user = st.selectbox("Choose folder:", user_names, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    # Dynamic folder navigation for real Google Drive
    selected_user_folder = next((f for f in user_folders if f['name'] == selected_user), None)
    user_folder_path = selected_user_folder['full_path'] if selected_user_folder else selected_user

    search_path = user_folder_path
    if not search_path.endswith('/'):
        search_path += '/'

    subfolders = [f for f in filtered_folders if f['full_path'].startswith(search_path) and f['full_path'] != user_folder_path]
    subfolder_paths = sorted([f["full_path"] for f in subfolders])

    selected_folder_path = None
    selected_folder_id = None

    if subfolder_paths:
        level_1_folders = [f for f in subfolders if f['full_path'].count('/') == user_folder_path.count('/') + 1]
        level_1_paths = sorted([f["full_path"] for f in level_1_folders])
        
        if level_1_paths:
            with st.container():
                st.markdown('<div class="nav-section">', unsafe_allow_html=True)
                st.markdown('<div class="nav-title">📂 Step 2: Select Subfolder</div>', unsafe_allow_html=True)
                selected_level_1 = st.selectbox("Choose subfolder:", level_1_paths, label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
            
            level_2_folders = [f for f in subfolders if f['full_path'].startswith(f"{selected_level_1}/") and f['full_path'] != selected_level_1]
            level_2_paths = sorted([f["full_path"] for f in level_2_folders])
            
            if level_2_paths:
                level_2_display = [f["full_path"] for f in level_2_folders if f['full_path'].count('/') == selected_level_1.count('/') + 1]
                if level_2_display:
                    with st.container():
                        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
                        st.markdown('<div class="nav-title">📋 Step 3: Select Final Folder</div>', unsafe_allow_html=True)
                        selected_level_2 = st.selectbox("Choose final folder:", sorted(level_2_display), label_visibility="collapsed")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    level_3_folders = [f for f in subfolders if f['full_path'].startswith(f"{selected_level_2}/") and f['full_path'] != selected_level_2]
                    level_3_paths = sorted([f["full_path"] for f in level_3_folders])
                    
                    if level_3_paths:
                        level_3_display = [f["full_path"] for f in level_3_folders if f['full_path'].count('/') == selected_level_2.count('/') + 1]
                        if level_3_display:
                            selected_folder_path = st.selectbox("Choose deeper folder:", sorted(level_3_display))
                        else:
                            selected_folder_path = selected_level_2
                    else:
                        selected_folder_path = selected_level_2
                else:
                    selected_folder_path = selected_level_1
            else:
                selected_folder_path = selected_level_1
        
        folder_map = {f["full_path"]: f for f in all_folders}
        selected_folder_id = folder_map[selected_folder_path]['id'] if selected_folder_path and selected_folder_path in folder_map else None
    else:
        st.markdown('<div class="status-warning">🔍 No subfolders found for this selection</div>', unsafe_allow_html=True)
else:
    # Demo mode - skip all folder navigation
    st.markdown('<div class="status-info">📁 <strong>Demo Mode:</strong> Showing sample documents</div>', unsafe_allow_html=True)
    selected_folder_id = None

# Mobile search interface
st.markdown("---")
st.markdown("### 🔍 Search Documents")

col1, col2 = st.columns([1, 1])
with col1:
    filename_query = st.text_input("📄 Search by filename", placeholder="Enter filename...", label_visibility="collapsed")

with col2:
    semantic_query = st.text_input("🧠 AI search (coming soon)", placeholder="AI search...", disabled=True, label_visibility="collapsed")

# SIMPLIFIED FILE LISTING - FORCE DEMO DOCS TO SHOW
docs = []

# ALWAYS show demo documents in lightweight mode
demo_docs = [
    {
        'id': 'demo_1',
        'name': 'AI Strategy Presentation.pdf',
        'mimeType': 'application/pdf'
    },
    {
        'id': 'demo_2', 
        'name': 'Q4 Sales Report.docx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },
    {
        'id': 'demo_3',
        'name': 'Customer Analysis Dashboard.xlsx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    },
    {
        'id': 'demo_4',
        'name': 'Product Roadmap 2025.pdf',
        'mimeType': 'application/pdf'
    },
    {
        'id': 'demo_5',
        'name': 'Team Performance Metrics.docx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },
    {
        'id': 'demo_6',
        'name': 'Marketing Campaign Results.pdf',
        'mimeType': 'application/pdf'
    }
]

# Set docs to demo_docs directly - no complex logic
docs = demo_docs
st.success(f"📄 **Demo Documents Loaded:** {len(docs)} files available")

# Apply search filter if there's a query
if active_query:
    docs = [doc for doc in docs if active_query.lower() in doc["name"].lower()]
    if active_query:
        st.info(f"🔍 **Search Results:** Found {len(docs)} documents matching '{active_query}'")

# Mobile-friendly results display
st.markdown('<div class="results-header">📊 Demo Documents</div>', unsafe_allow_html=True)

# FORCE SHOW DEMO DOCUMENTS - NO CONDITIONS!
demo_documents = [
    "AI Strategy Presentation.pdf",
    "Q4 Sales Report.docx", 
    "Customer Analysis Dashboard.xlsx",
    "Product Roadmap 2025.pdf",
    "Team Performance Metrics.docx",
    "Marketing Campaign Results.pdf"
]

st.markdown('<div class="status-success">✅ Found 6 demo documents</div>', unsafe_allow_html=True)

# Display each document with buttons
for i, doc_name in enumerate(demo_documents):
    st.markdown(f"""
    <div class="file-card">
        <div class="file-name">📄 {doc_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📖 Summary", key=f"sum_demo_{i}", use_container_width=True):
            # Demo summaries
            demo_summaries = {
                0: "This AI Strategy presentation outlines our company's approach to implementing artificial intelligence across key business functions. It covers market trends, competitive analysis, and a 3-year AI adoption roadmap.",
                1: "Q4 sales exceeded targets by 15% with strong enterprise performance. Key highlights include 23% growth in recurring revenue and successful premium tier launch.",
                2: "Customer analysis reveals 45% increase in mobile app usage. Demographics show growth in 25-34 age segment with improved satisfaction scores.",
                3: "2025 product roadmap focuses on user experience enhancements, AI-powered features, and platform scalability with major Q2 and Q4 releases.",
                4: "Team performance metrics show 12% productivity improvement with new workflow optimizations. Employee satisfaction reached 4.6/5.",
                5: "Marketing campaign achieved 3.2x ROI with strong digital performance. Email open rates at 28%, social engagement up 67%."
            }
            
            summary = demo_summaries.get(i, "This is a demo summary showcasing AI-powered document analysis.")
            st.success(f"**📋 AI Summary:** {summary}")
    
    with col2:
        if st.button("🔊 Read", key=f"speak_demo_{i}", use_container_width=True):
            st.info("💡 **Text-to-Speech:** Select any text above and use your device's built-in 'Speak' feature!")
    
    with col3:
        if st.button("⬇️ Download", key=f"dl_demo_{i}", use_container_width=True):
            st.success(f"✅ **Demo Download:** In production, {doc_name} would download from Google Drive!")
    
    with col4:
        if st.button("🔗 Share", key=f"share_demo_{i}", use_container_width=True):
            demo_url = f"https://demo-documents.example.com/{doc_name}"
            st.success(f"**🔗 Demo Share Link:** {demo_url}")
    
    st.markdown("---")

# Mobile footer with voice info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    🎤 Voice-Powered Smart Document Assistant<br>
    Powered by AI • Built for productivity • Voice-enabled<br>
    <small>💡 Tip: Use Chrome or Edge for best voice experience</small>
</div>
""", unsafe_allow_html=True)
