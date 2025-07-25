
WMA RAG Clean Setup
--------------------

This folder contains a cleaned and ready-to-run version of your RAG system.

Folder Structure:
- app/ : Your main Streamlit app (streamlit_rag_with_drive.py)
- creds/ : Google API credentials (credentials.json + token.pkl)
- docs/ : Supporting reference PDFs
- data_packs/FordDirect_RAG_Starter_Pack/ : Unzipped contents of your Starter Pack

To run the app:
1. Open a terminal
2. Navigate to app/ folder
3. Run: streamlit run streamlit_rag_with_drive.py

Make sure your virtual environment includes:
- streamlit
- sentence-transformers
- faiss-cpu
- PyMuPDF
- python-docx
- transformers
- google-auth / google-api-python-client

Everything else is self-contained. You’re good to go!
