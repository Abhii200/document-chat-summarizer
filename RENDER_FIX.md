# 🚨 RENDER DEPLOYMENT FIX

## Problem
Your deployment is running the wrong main.py file (the CLI version instead of the FastAPI server).

## ✅ Solution

### Option 1: Fix in Render Dashboard (Recommended)

1. **Go to your Render service settings**
2. **Update the configuration**:
   - **Root Directory**: `backend`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`

3. **Redeploy** by clicking "Manual Deploy" → "Deploy latest commit"

### Option 2: Alternative Commands (if Option 1 doesn't work)

If you can't set Root Directory, use these commands:

- **Build Command**: `cd backend && chmod +x build.sh && ./build.sh`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`

## 🔍 Verification

After deployment, test these endpoints:

1. **Health Check**: `https://your-service.onrender.com/`
   - Should return: `{"message": "Document Summarizer API"}`

2. **API Documentation**: `https://your-service.onrender.com/docs`
   - Should show FastAPI interactive docs

## 📁 File Structure

Make sure your repository has this structure:
```
your-repo/
├── backend/
│   ├── main.py          ← FastAPI server (THIS should run)
│   ├── requirements.txt
│   ├── build.sh
│   └── Procfile
├── frontend/
└── main.py             ← CLI version (ignore this)
```

## 🔧 Environment Variables

Don't forget to set these in Render:
```
OPENROUTER_API_KEY=your_actual_key
TESSERACT_PATH=/usr/bin/tesseract
CORS_ORIGINS=https://your-frontend.onrender.com
```

## 🚀 Expected Result

After the fix, you should see in the logs:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

Instead of:
```
📂 Enter path to PDF or image file:
EOFError: EOF when reading a line
```
