"""
FordDirect RAG Script (Starter Version)
This script connects to Google Drive, authenticates using your credentials.json file,
indexes documents with LlamaIndex, and uses GPT-4 for Q&A.
"""

import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Step 1: Authenticate with Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
drive_service = build('drive', 'v3', credentials=creds)

# Step 2: Download and save some documents manually for now
print("Authenticated with Google Drive. (Automatic sync coming soon)")

# Step 3: Load and index local documents (place in 'docs' folder)
reader = SimpleDirectoryReader("docs")
documents = reader.load_data()
index = VectorStoreIndex.from_documents(documents)

# Step 4: Ask a question
query_engine = index.as_query_engine()
response = query_engine.query("What are the recent updates for Pierre Ford?")
print(response)
