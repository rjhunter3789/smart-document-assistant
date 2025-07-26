"""
Simple URL parameter handler for Shortcuts
Returns PLAIN TEXT instead of HTML when ?q= parameter is present
"""
import streamlit as st
from datetime import datetime

# Hide Streamlit UI when URL parameter is present
query_params = st.query_params
voice_query = query_params.get("q", "")

if voice_query:
    # For URL parameters, return plain text only
    answer = f"Based on your documents, here's what I found about {voice_query}: This is a test response. The time is {datetime.now().strftime('%I:%M %p')}. In production, this would search your actual documents."
    
    # Display as plain text
    st.text(answer)
else:
    # Normal web interface
    st.title("Smart Document Assistant")
    st.write("Add ?q=your+question to the URL to get a response")