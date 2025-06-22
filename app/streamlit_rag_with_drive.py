import os
import io
import fitz  # PyMuPDF
from docx import Document as DocxDoc
import streamlit as st
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
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
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("app/credentials.json", SCOPES)
            creds = flow.run_local_server(port=8502)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

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

# AI setup (unchanged)
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained("t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("t5-small", torch_dtype=torch.float32)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)

def generate_summary(text):
    if not text.strip():
        return "No readable content found."
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = summarizer(chunks[:2], max_length=150, min_length=50, do_sample=False)
    return "\n\n".join([s['summary_text'] for s in summaries])

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

# File listing with demo mode support
docs = []
if demo_mode:
    # Use demo documents
    docs = demo_docs
    st.info("📁 **Demo Mode:** Showing sample documents to demonstrate the interface")
elif selected_folder_id:
    try:
        files = list_files(service, selected_folder_id)
        docs = [f for f in files if any(f['name'].lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt', '.xlsx'])]
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")

# Apply search filter (voice or text)
if active_query:
    docs = [doc for doc in docs if active_query.lower() in doc["name"].lower()]

# Mobile-friendly results display
st.markdown('<div class="results-header">📊 Results</div>', unsafe_allow_html=True)

if docs:
    st.markdown(f"<div class='status-success'>✅ Found {len(docs)} documents</div>", unsafe_allow_html=True)
    
    for doc in docs:
        # Mobile-optimized file card
        st.markdown(f"""
        <div class="file-card">
            <div class="file-name">📄 {doc['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons in mobile-friendly layout with enhanced text-to-speech
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("📖 Summary", key=f"sum_{doc['id']}", use_container_width=True):
                if demo_mode:
                    # Generate demo summaries
                    demo_summaries = {
                        'demo_1': "This AI Strategy presentation outlines our company's approach to implementing artificial intelligence across key business functions. It covers current market trends, competitive analysis, and a 3-year roadmap for AI adoption including machine learning, automation, and data analytics initiatives.",
                        'demo_2': "Q4 sales exceeded targets by 15% with strong performance in enterprise accounts. Key highlights include 23% growth in recurring revenue, successful launch of premium tier services, and expansion into 3 new geographic markets. Customer retention improved to 94%.",
                        'demo_3': "Customer analysis reveals strong engagement patterns with mobile app usage up 45%. Demographic trends show growth in 25-34 age segment. Satisfaction scores improved across all touchpoints with notable increases in support response times and product quality ratings.",
                        'demo_4': "2025 product roadmap focuses on user experience enhancements, AI-powered features, and platform scalability. Major releases planned for Q2 and Q4 with emphasis on mobile optimization, advanced analytics dashboard, and enterprise integration capabilities.",
                        'demo_5': "Team performance metrics show consistent improvement across all departments. Productivity increased 12% with new workflow optimizations. Employee satisfaction scores reached all-time high of 4.6/5. Training completion rates improved significantly with new learning management system.",
                        'demo_6': "Marketing campaign achieved 3.2x ROI with particularly strong performance in digital channels. Email campaigns saw 28% open rates, social media engagement up 67%, and conversion rates improved by 19%. Brand awareness increased measurably in target demographics."
                    }
                    
                    summary = demo_summaries.get(doc['id'], "This is a demo summary showcasing the AI-powered document analysis capability. In the full version, this would contain an actual AI-generated summary of the document content using advanced natural language processing.")
                    
                    st.markdown('<div class="status-success">', unsafe_allow_html=True)
                    st.markdown("**📋 AI Summary:**")
                    st.write(summary)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store summary for text-to-speech
                    st.session_state[f"summary_{doc['id']}"] = summary
                else:
                    # Real document processing
                    with st.spinner("🤖 AI analyzing..."):
                        try:
                            file_path = download_file(service, doc['id'], doc['name'])
                            text_content = extract_text(file_path)
                            
                            if text_content:
                                summary = generate_summary(text_content)
                                if len(summary) > 400:
                                    summary = summary[:400] + "..."
                                
                                st.markdown('<div class="status-success">', unsafe_allow_html=True)
                                st.markdown("**📋 AI Summary:**")
                                st.write(summary)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Store summary for text-to-speech
                                st.session_state[f"summary_{doc['id']}"] = summary
                            else:
                                st.markdown('<div class="status-warning">⚠️ Could not extract text from document</div>', unsafe_allow_html=True)
                                
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
        
        with col2:
            if st.button("🔊 Read Info", key=f"speak_{doc['id']}", use_container_width=True):
                # Enhanced text-to-speech instructions
                summary_key = f"summary_{doc['id']}"
                if summary_key in st.session_state:
                    summary_text = st.session_state[summary_key]
                    
                    st.markdown(f"""
                    <div class="audio-player">
                        <p><strong>🔊 Ready to Read Aloud:</strong></p>
                        <p><em>"{summary_text[:100]}..."</em></p>
                        
                        <p><strong>📱 To hear this summary:</strong></p>
                        <ul>
                            <li><strong>iPhone:</strong> Select text above → "Speak"</li>
                            <li><strong>Android:</strong> Select text → "Listen" or "Read aloud"</li>
                            <li><strong>Desktop:</strong> Use system text-to-speech</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a selectable text block
                    st.text_area(
                        "📄 Summary Text (select and use device text-to-speech):",
                        value=summary_text,
                        height=100,
                        key=f"tts_text_{doc['id']}"
                    )
                    
                else:
                    st.markdown('<div class="status-warning">⚠️ Generate a summary first to use text-to-speech</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("⬇️ Download", key=f"dl_{doc['id']}", use_container_width=True):
                if demo_mode:
                    st.info("📥 **Demo Mode:** In the full version, this would download the actual document from Google Drive. Click to see download functionality demonstration.")
                    st.markdown(f"""
                    <div class="status-success">
                        ✅ <strong>Download Ready:</strong> {doc['name']}<br>
                        <small>File would be downloaded from Google Drive in production mode</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Real download functionality
                    try:
                        file_path = download_file(service, doc['id'], doc['name'])
                        
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label="💾 Get File",
                                data=f.read(),
                                file_name=doc['name'],
                                mime="application/octet-stream",
                                key=f"dlbtn_{doc['id']}",
                                use_container_width=True
                            )
                        st.markdown('<div class="status-success">✅ Ready to download!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Download failed: {str(e)}")
        
        with col4:
            if st.button("🔗 Share", key=f"share_{doc['id']}", use_container_width=True):
                if demo_mode:
                    demo_url = f"https://demo-documents.example.com/file/{doc['id']}"
                    st.markdown('<div class="status-success">', unsafe_allow_html=True)
                    st.markdown("**🔗 Demo Share Link:**")
                    st.code(demo_url, language=None)
                    st.markdown("💡 In production, this would be a real Google Drive share link!")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Real share functionality
                    share_url = f"https://drive.google.com/file/d/{doc['id']}/view"
                    st.markdown('<div class="status-success">', unsafe_allow_html=True)
                    st.markdown("**🔗 Share Link:**")
                    st.code(share_url, language=None)
                    st.markdown("💡 Copy this link to share!")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
else:
    st.markdown('<div class="status-warning">🔍 No documents found. Try adjusting your search or folder selection.</div>', unsafe_allow_html=True)

# Mobile footer with voice info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    🎤 Voice-Powered Smart Document Assistant<br>
    Powered by AI • Built for productivity • Voice-enabled<br>
    <small>💡 Tip: Use Chrome or Edge for best voice experience</small>
</div>
""", unsafe_allow_html=True)
