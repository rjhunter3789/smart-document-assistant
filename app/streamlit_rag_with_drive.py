# streamlit_rag_flexible.py

import os
import io
import fitz  # PyMuPDF
from docx import Document as DocxDoc
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

def authenticate_gdrive():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(host='localhost', port=8502)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def list_folders(parent_id):
    service = authenticate_gdrive()
    results = service.files().list(
        q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def list_files(folder_id):
    service = authenticate_gdrive()
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

def download_file(file_id, name):
    service = authenticate_gdrive()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    save_path = os.path.join(DOCS_DIR, name)
    with open(save_path, 'wb') as f:
        f.write(fh.getvalue())
    return save_path

def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    elif file_path.endswith(".docx"):
        doc = DocxDoc(file_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif file_path.endswith(".txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    return text.strip()

embedder = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("t5-small").to("cpu")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)

def generate_summary(text):
    inputs = tokenizer.encode(text, truncation=True, max_length=512, return_tensors="pt")
    summary_ids = model.generate(inputs, max_length=300, min_length=75, do_sample=False)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

st.title("📁 Smart Document Assistant")
service = authenticate_gdrive()

# Step 1: Select from Root Folder (WMA RAG)
st.subheader("Step 1: Browse or Filter by Folder")
root_results = service.files().list(
    q="name='WMA RAG' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    fields="files(id, name)"
).execute()
root_id = root_results['files'][0]['id']

subfolders = list_folders(root_id)
folder_names = [f['name'] for f in subfolders]
selected_folder = st.selectbox("Choose a subfolder (e.g., Jeff, WMA Communal)", folder_names)
selected_folder_id = [f['id'] for f in subfolders if f['name'] == selected_folder][0]

nested_subfolders = list_folders(selected_folder_id)
if nested_subfolders:
    nested_names = [f['name'] for f in nested_subfolders]
    sub_selection = st.selectbox("Optional: Choose nested subfolder (e.g., Dealers/Product)", ["(none)"] + nested_names)
    if sub_selection != "(none)":
        folder_id = [f['id'] for f in nested_subfolders if f['name'] == sub_selection][0]
    else:
        folder_id = selected_folder_id
else:
    folder_id = selected_folder_id

file_list = list_files(folder_id)
doc_files = [f for f in file_list if any(f['name'].lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt'])]

file_names = [f['name'] for f in doc_files]
selected_file = st.selectbox("Step 2: Choose a document", ["(none)"] + file_names)

if selected_file != "(none)":
    file_obj = next(f for f in doc_files if f['name'] == selected_file)
    downloaded_path = download_file(file_obj['id'], file_obj['name'])
    st.success(f"Downloaded: {selected_file}")
    
    text = extract_text(downloaded_path)
    if text:
        summary = generate_summary(text)
        st.subheader("Summary:")
        st.write(summary)

        if st.button("Download Source File"):
            with open(downloaded_path, "rb") as f:
                st.download_button("Download Original File", f, file_name=file_obj['name'])
    else:
        st.warning("⚠️ Could not extract text from the selected file.")
