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