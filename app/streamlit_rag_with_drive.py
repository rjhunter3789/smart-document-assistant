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
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

# Mobile-optimized page configuration
st.set_page_config(
    page_title="🎤 Voice-Powered Document Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
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
""", unsafe_allow_html=True)

# Authentication function
def authenticate_gdrive():
    """Authenticate with Google Drive using Streamlit secrets"""
    try:
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

def get_all_folders_recursive(service, parent_id, parent_path=""):
    """Recursively get all folders from Google Drive"""
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
            # Recursively get subfolders
            folders.extend(get_all_folders_recursive(service, item["id"], full_path))
    except Exception as e:
        st.error(f"Error accessing folder {parent_path}: {str(e)}")
    
    return folders

def list_files(service, folder_id):
    """List files in a specific folder"""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType, modifiedTime, size)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def download_file(service, file_id, name):
    """Download a file from Google Drive"""
    try:
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
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

def generate_summary(text):
    """Generate a simple summary (lightweight version)"""
    if not text.strip():
        return "No readable content found."
    
    # Simple text truncation for demo
    sentences = text.split('.')[:3]  # First 3 sentences
    summary = '. '.join(sentences).strip()
    
    if len(summary) > 300:
        summary = summary[:300] + "..."
    
    return summary if summary else "Document summary would appear here with full AI capabilities."

# Demo documents for fallback
demo_docs = [
    {'id': 'demo_1', 'name': 'AI Strategy Presentation.pdf', 'mimeType': 'application/pdf'},
    {'id': 'demo_2', 'name': 'Q4 Sales Report.docx', 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    {'id': 'demo_3', 'name': 'Customer Analysis Dashboard.xlsx', 'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    {'id': 'demo_4', 'name': 'Product Roadmap 2025.pdf', 'mimeType': 'application/pdf'},
    {'id': 'demo_5', 'name': 'Team Performance Metrics.docx', 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    {'id': 'demo_6', 'name': 'Marketing Campaign Results.pdf', 'mimeType': 'application/pdf'}
]

# Main UI
st.markdown("""
<div class="main-header">
    <h1>🎤 Voice-Powered Document Assistant</h1>
    <p>AI-powered mobile document search with voice commands</p>
</div>
""", unsafe_allow_html=True)

# Voice Interface Section
st.markdown("""
<div class="voice-container">
    <h3 style="margin-top: 0;">🎙️ Voice Commands</h3>
    <p>Use the voice input below to search your documents</p>
</div>
""", unsafe_allow_html=True)

# Voice input
col1, col2 = st.columns([2, 1])

with col1:
    voice_input = st.text_input(
        "🎤 Voice Search", 
        placeholder="Tap here, then use your keyboard's voice button...",
        help="On mobile: Tap here and use your keyboard's microphone button 🎤",
        label_visibility="collapsed"
    )

with col2:
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

# Search interface
st.markdown("### 🔍 Search Documents")
col1, col2 = st.columns([1, 1])

with col1:
    filename_query = st.text_input(
        "📄 Search by filename", 
        placeholder="Type filename or use voice input above...", 
        label_visibility="collapsed"
    )

with col2:
    st.text_input(
        "🔗 Combined Search", 
        value=voice_input if voice_input else filename_query,
        placeholder="Auto-filled from voice or text search...",
        disabled=True,
        label_visibility="collapsed"
    )

# Use the combined search query
active_query = voice_input if voice_input else filename_query

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'selected_folder_id' not in st.session_state:
    st.session_state.selected_folder_id = None
if 'selected_folder_path' not in st.session_state:
    st.session_state.selected_folder_path = None

# Authentication and Google Drive setup
try:
    service = authenticate_gdrive()
    demo_mode = service is None
    
    if service:
        st.success("🔗 Connected to Google Drive! Loading your folders...")
    else:
        st.warning("⚠️ Google Drive not connected. Using demo mode.")
        
except Exception as e:
    st.error(f"🚫 Authentication setup failed: {str(e)}")
    service = None
    demo_mode = True

# Google Drive folder setup
root_id = "1galnuNa9g7xoULx3Ka8vs79-NuJUA4n6"  # Your root folder ID
all_folders = []
docs = []

if not demo_mode and service:
    # Get all folders
    try:
        with st.spinner("🔄 Loading folder structure..."):
            all_folders = get_all_folders_recursive(service, root_id)
        
        if all_folders:
            st.success(f"📁 Found {len(all_folders)} folders in your Google Drive")
            
            # Filter out WMA Test and excluded paths
            excluded_names = ["WMA Test"]
            excluded_paths = ["WMA RAG/WMA Team/RAG_App"]
            
            filtered_folders = [
                f for f in all_folders 
                if f['name'] not in excluded_names and 
                not any(f['full_path'].startswith(p) for p in excluded_paths)
            ]
            
            # Find team folders and WMA folders
            team_names = ["Aaron", "Brody", "Dona", "Eric", "Grace", "Jeff", "Jessica", "Jill", "John", "Jon", "Kirk", "Owen", "Paul"]
            wma_folders = [f for f in filtered_folders if 'WMA' in f['name']]
            team_folders = [f for f in filtered_folders if f['name'] in team_names]
            
            # Combine and sort available folders
            available_folders = wma_folders + team_folders
            
            if available_folders:
                # Step 1: Select main folder
                folder_options = list(set([f['name'] for f in available_folders]))
                folder_options.sort()
                
                st.markdown('<div class="nav-section">', unsafe_allow_html=True)
                st.markdown('<div class="nav-title">📁 Step 1: Select Your Main Folder</div>', unsafe_allow_html=True)
                
                selected_main_folder = st.selectbox(
                    "Choose main folder:", 
                    folder_options, 
                    label_visibility="collapsed",
                    key="main_folder_select"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 2: Get subfolders for selected main folder
                main_folder_subfolders = [
                    f for f in filtered_folders 
                    if f['full_path'].startswith(selected_main_folder + '/') or f['name'] == selected_main_folder
                ]
                
                if main_folder_subfolders:
                    # Get level 1 subfolders
                    level_1_folders = [
                        f for f in main_folder_subfolders 
                        if f['full_path'].count('/') == (1 if selected_main_folder in f['full_path'] else 0) and f['name'] != selected_main_folder
                    ]
                    
                    if level_1_folders:
                        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
                        st.markdown('<div class="nav-title">📂 Step 2: Select Subfolder</div>', unsafe_allow_html=True)
                        
                        level_1_options = [f['full_path'] for f in level_1_folders]
                        level_1_options.sort()
                        
                        selected_level_1 = st.selectbox(
                            "Choose subfolder:", 
                            level_1_options, 
                            label_visibility="collapsed",
                            key="level_1_select"
                        )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Step 3: Get level 2 subfolders
                        level_2_folders = [
                            f for f in filtered_folders 
                            if f['full_path'].startswith(selected_level_1 + '/') and f['full_path'] != selected_level_1
                        ]
                        
                        if level_2_folders:
                            # Get immediate children only (not nested deeper)
                            immediate_level_2 = [
                                f for f in level_2_folders 
                                if f['full_path'].count('/') == selected_level_1.count('/') + 1
                            ]
                            
                            if immediate_level_2:
                                st.markdown('<div class="nav-section">', unsafe_allow_html=True)
                                st.markdown('<div class="nav-title">📋 Step 3: Select Final Folder</div>', unsafe_allow_html=True)
                                
                                level_2_options = [f['full_path'] for f in immediate_level_2]
                                level_2_options.sort()
                                
                                selected_final_folder = st.selectbox(
                                    "Choose final folder:", 
                                    level_2_options, 
                                    label_visibility="collapsed",
                                    key="final_folder_select"
                                )
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Set the selected folder
                                final_folder = next((f for f in immediate_level_2 if f['full_path'] == selected_final_folder), None)
                                if final_folder:
                                    st.session_state.selected_folder_id = final_folder['id']
                                    st.session_state.selected_folder_path = final_folder['full_path']
                            else:
                                # Use level 1 as final folder
                                level_1_folder = next((f for f in filtered_folders if f['full_path'] == selected_level_1), None)
                                if level_1_folder:
                                    st.session_state.selected_folder_id = level_1_folder['id']
                                    st.session_state.selected_folder_path = level_1_folder['full_path']
                        else:
                            # Use level 1 as final folder
                            level_1_folder = next((f for f in filtered_folders if f['full_path'] == selected_level_1), None)
                            if level_1_folder:
                                st.session_state.selected_folder_id = level_1_folder['id']
                                st.session_state.selected_folder_path = level_1_folder['full_path']
                    else:
                        # Use main folder as final folder
                        main_folder = next((f for f in available_folders if f['name'] == selected_main_folder), None)
                        if main_folder:
                            st.session_state.selected_folder_id = main_folder['id']
                            st.session_state.selected_folder_path = main_folder['full_path']
                
                # Now list files from selected folder
                if st.session_state.selected_folder_id and st.session_state.selected_folder_path:
                    st.info(f"📂 Loading files from: {st.session_state.selected_folder_path}")
                    
                    with st.spinner(f"🔄 Scanning {st.session_state.selected_folder_path}..."):
                        docs = list_files(service, st.session_state.selected_folder_id)
                    
                    if docs:
                        st.success(f"📄 **Found {len(docs)} files in {st.session_state.selected_folder_path.split('/')[-1]}**")
                        demo_mode = False
                    else:
                        st.warning(f"📄 No files found in {st.session_state.selected_folder_path}. This might be an empty folder or you might not have permission to read files.")
                        st.info("🔄 Showing demo documents instead.")
                        docs = demo_docs
                        demo_mode = True
                else:
                    st.warning("Please select a folder to view its contents.")
                    docs = demo_docs
                    demo_mode = True
            else:
                st.warning("No recognized folders found (WMA folders or team folders). Showing demo documents.")
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
else:
    # Demo mode
    st.markdown('<div class="status-info">📁 <strong>Demo Mode:</strong> Showing sample documents</div>', unsafe_allow_html=True)
    docs = demo_docs

# Apply search filter
if active_query and docs:
    original_count = len(docs)
    filtered_docs = [doc for doc in docs if active_query.lower() in doc["name"].lower()]
    if filtered_docs:
        docs = filtered_docs
        st.info(f"🔍 **Search Results:** Found {len(docs)} documents matching '{active_query}' (out of {original_count} total)")
    else:
        st.warning(f"❌ No documents found matching '{active_query}' in the selected folder")

# Display results
st.markdown("---")
if docs:
    if demo_mode:
        st.markdown('<div class="results-header">📊 Demo Documents</div>', unsafe_allow_html=True)
        st.success(f"✅ Found {len(docs)} demo documents")
    else:
        st.markdown('<div class="results-header">📊 Your Google Drive Documents</div>', unsafe_allow_html=True)
        st.success(f"✅ Found {len(docs)} documents from {st.session_state.selected_folder_path}")
    
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
                    st.success(f"**📋 Real Document Analysis:** This would analyze '{doc_name}' from your Google Drive folder '{st.session_state.selected_folder_path}' using AI!")
        
        with col2:
            if st.button("🔊 Read", key=f"speak_{i}", use_container_width=True):
                st.info("💡 **Text-to-Speech:** Select any text above and use your device's built-in 'Speak' feature!")
        
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
else:
    st.warning("📄 No documents found in the selected location.")
    if not demo_mode:
        st.info("💡 Try selecting a different folder or check if the folder contains any files.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    🎤 Voice-Powered Smart Document Assistant<br>
    Powered by AI • Built for productivity • Voice-enabled<br>
    <small>💡 Tip: Use Chrome or Edge for best voice experience</small>
</div>
""", unsafe_allow_html=True)
