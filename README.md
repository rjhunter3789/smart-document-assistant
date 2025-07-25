# 🎙️ Smart Document Assistant - Voice-Enabled Edition

A voice-powered document Q&A assistant that lets you speak questions and hear AI-generated answers about your documents. Built with FastAPI + Streamlit for easy deployment on Railway.

## 🚀 Quick Start (Railway Deployment)

### Prerequisites
- GitHub account
- Railway account (free tier works)
- (Optional) ElevenLabs API key for premium voices

### Step 1: Push This Code to Your GitHub Repo

```bash
# Clone or download these files
git init
git add .
git commit -m "Initial voice-enabled smart document assistant"
git remote add origin https://github.com/rjhunter3789/smart-document-assistant.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Log into Railway** at https://railway.app

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `rjhunter3789/smart-document-assistant`
   - Railway will auto-detect the configuration

3. **Add Environment Variables**
   - Go to your project's "Variables" tab
   - Click "Raw Editor" and paste:

```env
# Required
PORT=8000

# Voice Settings (Optional - defaults to free gTTS)
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Google Drive (from your existing app - add when ready)
# GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account"...}

# Security (Optional)
# ALLOWED_USERS=jeff@wma.com,paul@wma.com,jill@wma.com
```

4. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a URL like: `https://smart-doc-assistant.up.railway.app`

### Step 3: Set Up Auto-Deploy (GitHub Actions)

1. **Get Railway Token**
   - In Railway: Settings → Tokens → Create Token
   - Copy the token

2. **Add to GitHub Secrets**
   - Go to GitHub repo → Settings → Secrets → Actions
   - Add new secret: `RAILWAY_TOKEN` = your token
   - Add new secret: `RAILWAY_PROJECT_ID` = your project ID (from Railway URL)

3. **Enable Actions**
   - Push any change to `main` branch
   - Railway will auto-deploy

## 🎙️ Using the Voice Assistant

### Voice Input Methods

1. **Browser Voice Input** (Recommended)
   - Click "🎙️ Voice Input" button
   - Speak your question clearly
   - Works on Chrome, Edge, Safari (mobile/desktop)

2. **Alternative Browser Method**
   - Use the expandable "Browser Voice Input" section
   - Works with Web Speech API

### Voice Output Options

- **gTTS** (Default): Free Google Text-to-Speech
- **ElevenLabs**: Premium realistic voices (requires API key)

### Example Questions

- "Summarize the Q2 report for Wendle Ford"
- "What were the top issues last quarter?"
- "Show me sales trends for Corwin Spokane"

## 🔧 Local Development

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run both services
python start_app.py

# Or run separately:
# Terminal 1 - Backend
uvicorn backend.main:app --reload

# Terminal 2 - Frontend  
streamlit run frontend/streamlit_app.py
```

### Access Local App
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔌 Integrating Your Existing Code

### 1. Add LlamaIndex/RAG Logic

In `backend/main.py`, replace the dummy response:

```python
# Find this line:
answer = f"Based on your documents, here's what I found..."

# Replace with:
from your_existing_code import process_with_llamaindex
answer = await process_with_llamaindex(request.question)
```

### 2. Add Google Drive Integration

```python
# In backend/main.py
from your_existing_code import GoogleDriveManager

drive_manager = GoogleDriveManager()
documents = await drive_manager.search_documents(query)
```

### 3. Add Your Document Processing

Uncomment the relevant dependencies in `requirements.txt`:
```
llama-index==0.9.13
langchain==0.0.340
sentence-transformers==2.2.2
# etc.
```

## 🛠️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Main app port | 8000 |
| `BACKEND_URL` | Backend API URL | http://localhost:8000 |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | None (uses gTTS) |
| `ELEVENLABS_VOICE_ID` | Voice selection | Rachel (default) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Drive credentials | None |
| `ALLOWED_USERS` | Comma-separated emails | None (open access) |

### Voice Providers

**gTTS (Default)**
- Free, no API key needed
- Good quality
- Multiple language support

**ElevenLabs**
- Premium quality
- Emotional range
- Requires API key from https://elevenlabs.io

## 📱 Mobile Support

- Fully responsive design
- Voice input works on iOS/Android Chrome
- Touch-optimized buttons
- Auto-scaling interface

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Ensure both services are running
- Check `BACKEND_URL` environment variable
- Verify Railway deployment logs

### Voice input not working
- Use Chrome or Edge browser
- Allow microphone permissions
- Ensure HTTPS connection (automatic on Railway)

### No audio playback
- Check browser audio permissions
- Verify voice provider API keys
- Test with gTTS first (no key needed)

## 📊 Monitoring

### Railway Logs
```bash
railway logs
```

### Health Check
- Visit: `https://your-app.railway.app/health`
- Backend API: `https://your-app.railway.app/docs`

## 🔒 Security Notes

1. **API Keys**: Store in Railway environment variables, never commit
2. **User Access**: Set `ALLOWED_USERS` for restricted access
3. **HTTPS**: Automatically enabled on Railway
4. **CORS**: Currently allows all origins (update for production)

## 🚢 Production Checklist

- [ ] Add real document processing logic
- [ ] Configure user authentication
- [ ] Set up proper CORS origins
- [ ] Add rate limiting
- [ ] Configure custom domain
- [ ] Set up monitoring/alerts
- [ ] Add backup strategy

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [ElevenLabs API](https://docs.elevenlabs.io)

## 🤝 Support

- GitHub Issues: [Report bugs or request features](https://github.com/rjhunter3789/smart-document-assistant/issues)
- Change Log: See `CHANGELOG_AND_RECOVERY.md` for version history

---

Built with ❤️ for WMA Smart Document Processing