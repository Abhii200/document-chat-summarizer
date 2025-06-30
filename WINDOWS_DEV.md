# Windows Development Troubleshooting

## Common Issues and Solutions

### 1. Backend Warnings About Host Binding
**Issue**: Warnings about "Binding to 0.0.0.0" or host accessibility
**Solution**: These are normal warnings when running FastAPI locally. The updated server configuration uses `127.0.0.1` to reduce these warnings.

### 2. Port Already in Use
**Issue**: `OSError: [WinError 10048] Only one usage of each socket address`
**Solution**: 
```bash
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### 3. Virtual Environment Issues
**Issue**: Virtual environment not activating or packages not found
**Solution**: 
```bash
cd backend
python -m venv openr
openr\Scripts\activate
pip install -r requirements.txt
```

### 4. CORS Errors in Browser
**Issue**: Frontend can't connect to backend
**Solution**: 
- Make sure backend `.env` has `CORS_ORIGINS=http://localhost:3000`
- Make sure frontend `.env` has `REACT_APP_API_BASE_URL=http://localhost:8000`
- Restart both servers after changing .env files

### 5. Node.js/NPM Issues
**Issue**: Frontend won't start or install packages
**Solution**:
```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
npm start
```

### 6. API Key Issues
**Issue**: OpenRouter API not working
**Solution**: 
- Check your API key in `backend/.env`
- Verify the key is valid at https://openrouter.ai/
- Make sure you have credits/free tier access

## Easy Startup Methods

### Method 1: Use Batch Files (Recommended)
1. Double-click `start_local.bat` in the root directory
2. Follow the prompts to start backend and/or frontend

### Method 2: Manual Startup
**Backend:**
```bash
cd backend
openr\Scripts\activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm start
```

### Method 3: Individual Batch Files
- Backend: Double-click `backend/run_server.bat`
- Frontend: Double-click `frontend/run_frontend.bat`

## Performance Tips
- The backend auto-reloads when you change files (development mode)
- Close unnecessary browser tabs to reduce memory usage
- Use Chrome DevTools to debug frontend issues
- Check backend logs in the terminal for API errors

## Environment Variables Quick Reference
**Backend (.env):**
- `OPENROUTER_API_KEY`: Your API key
- `CORS_ORIGINS`: Frontend URLs (localhost:3000 for local dev)
- `HOST`: 127.0.0.1 (for local dev)
- `PORT`: 8000

**Frontend (.env):**
- `REACT_APP_API_BASE_URL`: Backend URL (localhost:8000 for local dev)
