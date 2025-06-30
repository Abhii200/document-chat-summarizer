# Document Summarizer - Full Stack Application

A modern web application that uses AI to extract text from documents (PDFs and images), generate summaries, and answer questions about the content.

## 🚀 Features

- **Document Upload**: Support for PDF files and images (JPEG, PNG)
- **OCR Text Extraction**: Extract text from scanned documents and images
- **AI-Powered Summarization**: Generate concise summaries using Google's Gemma model
- **Interactive Q&A**: Ask questions about your documents and get AI-powered answers
- **Modern UI**: Beautiful, responsive React interface with drag-and-drop file upload
- **Real-time Processing**: Live updates and progress indicators

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with OpenRouter AI API integration
- **Frontend**: React.js with Tailwind CSS
- **OCR**: Tesseract OCR for text extraction
- **AI Model**: Google Gemma 3n 4B via OpenRouter API

## 📋 Prerequisites

Before running this application, make sure you have:

1. **Python 3.8+** installed
2. **Node.js 16+** and npm installed
3. **Tesseract OCR** installed:
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to: `C:\Program Files\Tesseract-OCR\`
4. **OpenRouter API Key**: Get one from [OpenRouter](https://openrouter.ai/)

## 🛠️ Installation & Setup

### 1. Clone or Setup Project Structure

```bash
Document_summarizer/
├── backend/
├── frontend/
└── README.md
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file and add your OpenRouter API key
```

**Environment Configuration (backend/.env):**
```env
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
MODEL_NAME=google/gemma-3n-e4b-it:free
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
HOST=0.0.0.0
PORT=8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env file if needed (default values should work for local development)
```

**Environment Configuration (frontend/.env):**
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 🚀 Running the Application

### Start the Backend Server

```bash
cd backend
python main.py
```

The API will be available at: `http://localhost:8000`

### Start the Frontend Development Server

```bash
cd frontend
npm start
```

The web application will be available at: `http://localhost:3000`

## 📖 Usage

1. **Upload Document**: 
   - Drag and drop a PDF or image file, or click to browse
   - Supported formats: PDF, JPEG, PNG

2. **View Summary**: 
   - After processing, view the AI-generated summary
   - Copy summary to clipboard with one click

3. **Ask Questions**: 
   - Use the chat interface to ask questions about your document
   - Get instant AI-powered answers based on the document content

4. **Process New Documents**: 
   - Click "New Document" to upload and analyze another file

## 🔧 Configuration

### Backend Configuration (backend/.env)

- **OPENROUTER_API_KEY**: Your OpenRouter API key (required)
- **OPENROUTER_URL**: OpenRouter API endpoint (default: provided)
- **MODEL_NAME**: AI model to use (default: google/gemma-3n-e4b-it:free)
- **TESSERACT_PATH**: Path to Tesseract executable
- **CORS_ORIGINS**: Comma-separated list of allowed frontend origins
- **HOST**: Server host (default: 0.0.0.0)
- **PORT**: Server port (default: 8000)

### Frontend Configuration (frontend/.env)

- **REACT_APP_API_BASE_URL**: Backend API URL (update for production deployment)

### Deployment Configuration

For production deployment:

**Backend (.env):**
```env
OPENROUTER_API_KEY=your_production_api_key
CORS_ORIGINS=https://your-frontend-domain.com
HOST=0.0.0.0
PORT=8000
```

**Frontend (.env):**
```env
REACT_APP_API_BASE_URL=https://your-backend-domain.com
```

## 🎯 API Endpoints

### POST /upload
Upload and process a document
- **Input**: Multipart form data with file
- **Output**: Document ID, extracted text preview, and summary

### POST /ask
Ask a question about a document
- **Input**: `{ "document_id": "uuid", "question": "text" }`
- **Output**: `{ "answer": "AI response" }`

### GET /document/{document_id}
Get document information
- **Output**: Document summary and text preview

### DELETE /document/{document_id}
Delete a document and its associated file

## 🔍 Technical Details

### Text Extraction
- **PDF Processing**: Uses `pdf2image` to convert PDF pages to images, then OCR
- **Image Processing**: Direct OCR processing with Tesseract
- **Text Chunking**: Large documents are processed in chunks for better AI performance

### AI Integration
- **Model**: Google Gemma 3n 4B (free tier)
- **API**: OpenRouter for model access
- **Processing**: Async operations for better performance
- **Error Handling**: Comprehensive error handling for API failures

### Frontend Features
- **Drag & Drop**: Modern file upload interface
- **Real-time Chat**: Interactive Q&A with message history
- **Responsive Design**: Works on desktop and mobile devices
- **Loading States**: Progress indicators for all operations

## 🚨 Troubleshooting

### Common Issues

1. **Tesseract not found**:
   - Verify installation path in `main.py`
   - Ensure Tesseract is installed correctly

2. **API Key errors**:
   - Check your `.env` file exists and contains valid OpenRouter API key
   - Verify API key format and permissions
   - Ensure environment variables are loaded correctly

3. **CORS errors**:
   - Ensure frontend URL is in CORS allowed origins
   - Check both servers are running

4. **File upload errors**:
   - Verify file format is supported
   - Check file size limits
   - Ensure `uploads/` directory exists

### Debug Mode

Enable debug logging by adding to backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 Dependencies

### Backend
- FastAPI: Web framework
- Uvicorn: ASGI server
- Pytesseract: OCR functionality
- PDF2Image: PDF processing
- Requests: HTTP client for API calls
- Pillow: Image processing

### Frontend
- React: UI framework
- Axios: HTTP client
- React Dropzone: File upload component
- Lucide React: Icons
- Tailwind CSS: Styling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🎉 Acknowledgments

- OpenRouter for AI model access
- Google for the Gemma model
- Tesseract OCR team
- React and FastAPI communities
