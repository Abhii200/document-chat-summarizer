# Render Deployment Guide for DocuMind Backend

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenRouter API Key**: Your API key ready

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ai-document-summarizer.git
   git push -u origin main
   ```

2. **Make sure these files are in your repository**:
   - `backend/requirements.txt`
   - `backend/main.py`
   - `backend/build.sh` (created above)
   - `backend/Procfile` (created above)

### Step 2: Create Render Web Service

1. **Go to Render Dashboard**:
   - Visit [render.com/dashboard](https://render.com/dashboard)
   - Click "New +" → "Web Service"

2. **Connect Repository**:
   - Connect your GitHub account
   - Select your repository
   - Click "Connect"

3. **Configure Service**:
   ```
   Name: documind-backend
   Environment: Python 3
   Root Directory: backend
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
   ```

   **Important**: Set "Root Directory" to `backend` so Render runs commands from the backend folder.

### Step 3: Set Environment Variables

In Render dashboard, go to "Environment" tab and add:

```
OPENROUTER_API_KEY = your_actual_api_key_here
OPENROUTER_URL = https://openrouter.ai/api/v1/chat/completions
MODEL_NAME = google/gemma-3n-e4b-it:free
TESSERACT_PATH = /usr/bin/tesseract
CORS_ORIGINS = https://your-frontend-domain.onrender.com,http://localhost:3000
HOST = 0.0.0.0
PYTHON_VERSION = 3.11.0
```

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Wait for build to complete** (5-10 minutes)
3. **Your API will be available at**: `https://your-service-name.onrender.com`

## 🔧 Configuration Details

### Build Process
Render will:
1. Install system dependencies (Tesseract, Poppler)
2. Install Python dependencies from requirements.txt
3. Start the FastAPI server

### System Dependencies
The `build.sh` script installs:
- `tesseract-ocr`: For text extraction
- `poppler-utils`: For PDF processing

### Port Configuration
Render automatically provides the `$PORT` environment variable, which the app uses.

## 🌐 Frontend Integration

After backend deployment, update your frontend:

1. **Update frontend/.env**:
   ```env
   REACT_APP_API_BASE_URL=https://your-backend-service.onrender.com
   ```

2. **Update backend CORS_ORIGINS**:
   ```env
   CORS_ORIGINS=https://your-frontend-domain.onrender.com
   ```

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check build logs in Render dashboard
   - Ensure `build.sh` has execute permissions
   - Verify all dependencies in requirements.txt

2. **Tesseract Not Found**:
   - Check if build.sh installed tesseract correctly
   - Verify TESSERACT_PATH environment variable

3. **API Key Issues**:
   - Ensure OPENROUTER_API_KEY is set correctly
   - Check for trailing spaces in environment variables

4. **CORS Errors**:
   - Update CORS_ORIGINS with your frontend domain
   - Include both HTTP and HTTPS if needed

### Debug Commands:

```bash
# Check logs
curl https://your-service.onrender.com/

# Test health endpoint
curl https://your-service.onrender.com/docs
```

## 📊 Monitoring

1. **Render Dashboard**: Monitor deployments, logs, and metrics
2. **Health Checks**: Render automatically monitors your service
3. **Logs**: View real-time logs in the dashboard

## 💰 Pricing

- **Free Tier**: 750 hours/month (enough for development)
- **Paid Plans**: Start at $7/month for production use
- **Auto-sleep**: Free services sleep after 15 minutes of inactivity

## 🔄 Auto-Deploy

Render automatically deploys when you push to your main branch:
1. Push changes to GitHub
2. Render detects changes
3. Automatically rebuilds and deploys
4. Zero-downtime deployments

## ✅ Verification

After deployment, test these endpoints:

1. **Health Check**: `GET https://your-service.onrender.com/`
2. **API Docs**: `GET https://your-service.onrender.com/docs`
3. **Upload Test**: Use the frontend or Postman to test file upload

## 🚀 Next Steps

1. **Deploy Frontend**: Deploy React app to Render/Vercel/Netlify
2. **Custom Domain**: Add your custom domain in Render settings
3. **SSL Certificate**: Automatically provided by Render
4. **Database**: Add persistent storage if needed for document history

Your DocuMind backend will be live and accessible globally! 🌍
