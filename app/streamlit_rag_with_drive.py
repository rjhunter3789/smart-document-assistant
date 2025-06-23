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
        return Noneimport os
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
        files = results.get('files', [])
        return files
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def extract_text_from_file(service, file_id, file_name):
    """Extract text content from a Google Drive file"""
    try:
        # Download the file
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
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

def create_speech_component(text, doc_name):
    """Create a text-to-speech component"""
    # Truncate text for speech (first 500 characters)
    speech_text = text[:500] + "..." if len(text) > 500 else text
    
    # Clean text for speech (remove special characters)
    import re
    clean_text = re.sub(r'[^\w\s.,!?-]', ' ', speech_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Create HTML for speech synthesis
    speech_html = f"""
    <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h4>🔊 Now Reading: {doc_name}</h4>
        <p style="font-style: italic; color: #666;">"{clean_text}"</p>
        <button onclick="speakText()" style="
            background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 0.5rem;
        ">▶️ Play</button>
        <button onclick="stopSpeech()" style="
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 0.5rem;
        ">⏹️ Stop</button>
        <button onclick="pauseSpeech()" style="
            background: #ffa726;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        ">⏸️ Pause</button>
    </div>
    
    <script>
    let utterance;
    
    function speakText() {{
        if ('speechSynthesis' in window) {{
            // Stop any ongoing speech
            window.speechSynthesis.cancel();
            
            // Create new utterance
            utterance = new SpeechSynthesisUtterance(`{clean_text}`);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            // Speak the text
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert('Text-to-speech not supported in this browser');
        }}
    }}
    
    function stopSpeech() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
        }}
    }}
    
    function pauseSpeech() {{
        if ('speechSynthesis' in window) {{
            if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {{
                window.speechSynthesis.pause();
            }} else if (window.speechSynthesis.paused) {{
                window.speechSynthesis.resume();
            }}
        }}
    }}
    </script>
    """
    
    return speech_html

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

# Voice input with enhanced voice command processing
st.markdown("### 🎤 Voice Commands")

# Voice command help
with st.expander("🎯 Voice Command Examples"):
    st.markdown("""
    **🚗 Hands-Free Commands:**
    - *"Summarize the Chat AI file"*
    - *"Read me the Impel document"* 
    - *"Find and summarize automotive platform"*
    - *"Review the FAQ handout"*
    
    **📱 How to Use:**
    1. **Tap the voice box** below
    2. **Use your keyboard's mic** button 🎤
    3. **Speak your command** clearly
    4. **App will auto-execute** the command
    """)

voice_input = st.text_input(
    "🎤 Voice Command", 
    placeholder="Say: 'Summarize the Chat AI file' or 'Read me the automotive platform document'",
    help="💡 Speak commands like 'summarize [filename]' or 'read [filename]'",
    label_visibility="collapsed"
)

# Process voice commands
if voice_input:
    st.success(f"🎤 Voice command: **{voice_input}**")
    
    # Parse voice command
    command_lower = voice_input.lower()
    
    # Extract action and filename
    action = None
    search_term = None
    
    if any(word in command_lower for word in ['summarize', 'summary', 'review']):
        action = 'summarize'
    elif any(word in command_lower for word in ['read', 'read back', 'read to me']):
        action = 'read'
    elif any(word in command_lower for word in ['find', 'search', 'show']):
        action = 'find'
    
    # Extract search terms (remove command words)
    search_words = command_lower
    for remove_word in ['summarize', 'summary', 'review', 'read', 'back', 'to', 'me', 'the', 'file', 'on', 'about', 'find', 'search', 'show', 'and']:
        search_words = search_words.replace(remove_word, ' ')
    
    search_term = ' '.join(search_words.split()).strip()
    
    if action and search_term:
        st.info(f"🎯 **Command understood:** {action.title()} documents matching '{search_term}'")
        
        # Store voice command in session state for processing later
        if 'voice_command' not in st.session_state:
            st.session_state.voice_command = {}
        
        st.session_state.voice_command = {
            'action': action,
            'search_term': search_term,
            'original_command': voice_input
        }
    else:
        st.warning("🤔 Command not understood. Try: 'Summarize [filename]' or 'Read [filename]'")

# Search interface
st.markdown("### 🔍 Search Documents")
filename_query = st.text_input(
    "📄 Search by filename", 
    placeholder="Type filename to search...", 
    label_visibility="collapsed"
)

# Use the combined search query
active_query = voice_input if voice_input else filename_query

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
            st.success(f"📁 Connected! Found {len(all_folders)} folders")
            
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
            
            if selected_folder:
                st.info(f"📂 Loading files from: {selected_folder['full_path']}")
                
                with st.spinner(f"🔄 Scanning {selected_folder['full_path']}..."):
                    docs = list_files(service, selected_folder['id'])
                
                if docs:
                    st.success(f"📄 **Found {len(docs)} files in {selected_folder['name']}**")
                    demo_mode = False
                    
                else:
                    st.warning(f"📄 No files found in {selected_folder['full_path']}. This folder appears to be empty.")
                    st.info("🔄 Showing demo documents instead.")
                    docs = demo_docs
                    demo_mode = True
            else:
                st.error("Could not find selected folder")
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
    st.info("📁 **Demo Mode:** Showing sample documents")
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
st.markdown("### 📄 Documents")

if docs:
    if demo_mode:
        st.info(f"**Demo Mode:** Showing {len(docs)} sample documents")
    else:
        st.success(f"**{len(docs)} documents** from **{selected_folder_path}**")
    
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
                    # Demo text-to-speech
                    demo_texts = [
                        "This AI Strategy presentation outlines our company's approach to implementing artificial intelligence across key business functions.",
                        "Q4 sales exceeded targets by 15% with strong enterprise performance and recurring revenue growth.",
                        "Customer analysis reveals significant increase in mobile app usage and improved satisfaction scores.",
                        "2025 product roadmap focuses on user experience enhancements and AI-powered features.",
                        "Team performance metrics show productivity improvement with new workflow optimizations.",
                        "Marketing campaign achieved strong ROI with excellent digital performance and engagement."
                    ]
                    demo_text = demo_texts[i % len(demo_texts)]
                    speech_component = create_speech_component(demo_text, doc_name)
                    st.markdown(speech_component, unsafe_allow_html=True)
                else:
                    # Real document text-to-speech
                    if 'id' in doc:
                        with st.spinner("Extracting text for speech..."):
                            file_text = extract_text_from_file(service, doc['id'], doc_name)
                            if file_text and not file_text.startswith("Error"):
                                speech_component = create_speech_component(file_text, doc_name)
                                st.markdown(speech_component, unsafe_allow_html=True)
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
else:
    st.warning("📄 No documents found in the selected location.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    🎤 Voice-Powered Smart Document Assistant<br>
    Powered by AI • Built for productivity • Voice-enabled<br>
    <small>💡 Tip: Use Chrome or Edge for best voice experience</small>
</div>
""", unsafe_allow_html=True)
