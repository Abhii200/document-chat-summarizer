from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
from PIL import Image
import requests
import json
import os
import uuid
from typing import Optional
import asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
import io

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind - AI Document Summarizer", 
    version="2.0.0",
    description="AI-powered document summarizer with OCR and Q&A capabilities"
)

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
DEFAULT_MODEL = os.getenv("MODEL_NAME", "google/gemma-3n-e4b-it:free")
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

# Server configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Validate required environment variables
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=" * 60)
print("🚀 DocuMind API Server Initializing...")
print("=" * 60)
print("🦙 OCR Engine: Llama 3.2 Vision (Free)")
print(f"🤖 Default Model: {DEFAULT_MODEL}")
print(f"🌐 CORS Origins: {CORS_ORIGINS}")
print("=" * 60)

# Data models
class QuestionRequest(BaseModel):
    document_id: str
    question: str

class DocumentResponse(BaseModel):
    document_id: str
    extracted_text: str
    summary: str

# Document store for sessions
document_store = {}

# Constants
MAX_IMAGE_SIZE = 1024
MAX_TEXT_CHUNK_WORDS = 1500
MAX_SUMMARY_TOKENS = 300
MAX_QA_TOKENS = 500

# ----- Core Functions -----

def prepare_image_for_vision(img):
    """Prepare image for vision model processing"""
    buffer = io.BytesIO()
    
    # Optimize image size for vision model
    if img.width > MAX_IMAGE_SIZE or img.height > MAX_IMAGE_SIZE:
        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
        print(f"📏 Resized image to {img.width}x{img.height}")
    
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

async def extract_text_with_vision(img):
    """Extract text from image using Llama 3.2 Vision model"""
    try:
        img_b64 = prepare_image_for_vision(img)
        print("🦙 Processing with Llama Vision...")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract ALL text from this image. Return ONLY the text content, preserving formatting, line breaks, and structure as much as possible. Do not add any explanations or comments."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
        
        response = await call_openrouter_api(messages, model=VISION_MODEL, max_tokens=2000)
        extracted_text = response.strip()
        print(f"✅ Vision OCR extracted {len(extracted_text)} characters")
        return extracted_text
        
    except Exception as e:
        print(f"❌ Vision OCR failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

async def extract_text_from_pdf(pdf_path):
    """Extract text from PDF by converting to images and using vision OCR"""
    print("📄 Converting PDF to images...")
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        
        for i, img in enumerate(images):
            print(f"🔍 Processing page {i+1}/{len(images)}...")
            text = await extract_text_with_vision(img)
            if text.strip():
                full_text += text + "\n\n"
        
        return full_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

async def extract_text_from_image(image_path):
    """Extract text from image file using vision OCR"""
    print(f"🔍 Processing image: {os.path.basename(image_path)}")
    try:
        img = Image.open(image_path)
        return await extract_text_with_vision(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

def chunk_text(text, max_words=None):
    """Split text into manageable chunks for processing"""
    max_words = max_words or MAX_TEXT_CHUNK_WORDS
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# ----- API Helper -----
async def call_openrouter_api(messages, max_tokens=300, model=None):
    """Make API call to OpenRouter"""
    print("🌐 Making API call to OpenRouter...")
    
    # Use custom model or default
    selected_model = model or DEFAULT_MODEL
    print(f"📱 Using model: {selected_model}")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "document-summarizer",
        "X-Title": "Document Summarizer",
    }
    
    data = {
        "model": selected_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
    except KeyError as e:
        print(f"❌ Response Error: {e}")
        raise HTTPException(status_code=500, detail="Invalid API response")

# ----- AI Processing Functions -----

async def summarize_text(text):
    """Generate summary using AI"""
    # Truncate text if too long
    max_chars = 4000
    truncated_text = text[:max_chars] + "..." if len(text) > max_chars else text
    
    prompt = f"""Summarize the following document in a clear, concise, and well-structured manner. Focus on the main points and key information:

{truncated_text}"""
    
    messages = [{"role": "user", "content": prompt}]
    return await call_openrouter_api(messages, max_tokens=MAX_SUMMARY_TOKENS)

async def answer_question(context, question):
    """Answer questions about the document using AI"""
    # Truncate context if too long
    max_chars = 5000
    truncated_context = context[:max_chars] + "..." if len(context) > max_chars else context
    
    prompt = f"""Based on the following document, answer the question accurately and concisely:

Document:
{truncated_context}

Question: {question}

Answer:"""
    
    messages = [{"role": "user", "content": prompt}]
    return await call_openrouter_api(messages, max_tokens=MAX_QA_TOKENS)

# ----- API Endpoints -----
@app.get("/")
async def root():
    return {"message": "Document Summarizer API"}

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF or image)"""
    
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, JPEG, or PNG files.")
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_extension = ".pdf" if file.content_type == "application/pdf" else ".jpg"
    file_path = f"uploads/{document_id}{file_extension}"
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Extract text
        if file.content_type == "application/pdf":
            extracted_text = await extract_text_from_pdf(file_path)
        else:
            extracted_text = await extract_text_from_image(file_path)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the document.")
        
        # Generate summary
        chunks = chunk_text(extracted_text)
        summaries = []
        for chunk in chunks:
            summary = await summarize_text(chunk)
            summaries.append(summary)
        
        # Create final summary
        final_summary = await summarize_text(" ".join(summaries))
        
        # Store document data
        document_store[document_id] = {
            "text": extracted_text,
            "summary": final_summary,
            "file_path": file_path
        }
        
        return DocumentResponse(
            document_id=document_id,
            extracted_text=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            summary=final_summary
        )
        
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about a previously uploaded document"""
    
    if request.document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a document first.")
    
    document_data = document_store[request.document_id]
    answer = await answer_question(document_data["text"], request.question)
    
    return {"answer": answer}

@app.get("/document/{document_id}")
async def get_document(document_id: str):
    """Get document information"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    document_data = document_store[document_id]
    return {
        "document_id": document_id,
        "summary": document_data["summary"],
        "text_preview": document_data["text"][:500] + "..." if len(document_data["text"]) > 500 else document_data["text"]
    }

@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated file"""
    
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    document_data = document_store[document_id]
    
    # Remove file
    if os.path.exists(document_data["file_path"]):
        os.remove(document_data["file_path"])
    
    # Remove from store
    del document_store[document_id]
    
    return {"message": "Document deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Reduce uvicorn logging noise
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    
    print("=" * 50)
    print("🚀 DocuMind API Server Starting...")
    print("=" * 50)
    print(f"📍 Local URL: http://localhost:{PORT}")
    print(f"📚 API Docs: http://localhost:{PORT}/docs")
    print(f"🌐 CORS enabled for: {CORS_ORIGINS}")
    print("=" * 50)
    
    try:
        # Configure uvicorn for Windows development
        uvicorn.run(
            "main:app",  # Import string instead of app object
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for Windows
            port=PORT,
            log_level="warning",  # Reduce log noise
            access_log=False,
            server_header=False,
            reload=True,  # Auto-reload on file changes
            reload_dirs=["./"],  # Watch current directory
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped gracefully")
    except Exception as e:
        print(f"❌ Server error: {e}")
