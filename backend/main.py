from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pytesseract
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

# Try to import EasyOCR as fallback
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("📄 EasyOCR available as fallback")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR not available")

# Load environment variables
load_dotenv()

app = FastAPI(title="Document Summarizer API", version="1.0.0")

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-3n-e4b-it:free")

# Tesseract path - different for local vs Render
TESSERACT_PATH = os.getenv("TESSERACT_PATH")
if not TESSERACT_PATH:
    # Default paths for different environments
    if os.path.exists("/usr/bin/tesseract"):  # Linux (Render)
        TESSERACT_PATH = "/usr/bin/tesseract"
    elif os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):  # Windows
        TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        TESSERACT_PATH = "tesseract"  # Hope it's in PATH

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Validate required environment variables
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set Tesseract path with error handling
try:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    # Test if tesseract is working
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR is available")
except Exception as e:
    TESSERACT_AVAILABLE = False
    print(f"⚠️ Tesseract not available: {e}")

# Initialize EasyOCR reader if available and tesseract fails
ocr_reader = None
if EASYOCR_AVAILABLE and not TESSERACT_AVAILABLE:
    try:
        ocr_reader = easyocr.Reader(['en'])
        print("✅ EasyOCR initialized as fallback")
    except Exception as e:
        print(f"⚠️ EasyOCR initialization failed: {e}")

# Store for document sessions
document_store = {}

class QuestionRequest(BaseModel):
    document_id: str
    question: str

class DocumentResponse(BaseModel):
    document_id: str
    extracted_text: str
    summary: str

# ----- OCR Functions -----
def extract_text_with_ocr(img):
    """Extract text from image using available OCR method"""
    if TESSERACT_AVAILABLE:
        try:
            return pytesseract.image_to_string(img)
        except Exception as e:
            print(f"⚠️ Tesseract failed: {e}")
    
    if ocr_reader is not None:
        try:
            # Convert PIL image to numpy array for EasyOCR
            import numpy as np
            img_array = np.array(img)
            results = ocr_reader.readtext(img_array)
            # Extract text from results
            text = " ".join([result[1] for result in results])
            return text
        except Exception as e:
            print(f"⚠️ EasyOCR failed: {e}")
    
    raise HTTPException(status_code=500, detail="No OCR method available. Please contact support.")

def extract_text_from_pdf(pdf_path):
    print("📄 Converting PDF to images...")
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for i, img in enumerate(images):
            print(f"🔍 OCR on page {i+1}...")
            text = extract_text_with_ocr(img)
            full_text += text + "\n\n"
        return full_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

def extract_text_from_image(image_path):
    print(f"🔍 OCR on image: {image_path}")
    try:
        img = Image.open(image_path)
        return extract_text_with_ocr(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

def chunk_text(text, max_words=1500):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# ----- API Helper -----
async def call_openrouter_api(messages, max_tokens=300):
    """Make API call to OpenRouter"""
    print("🌐 Making API call to OpenRouter...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "document-summarizer",
        "X-Title": "Document Summarizer",
    }
    
    data = {
        "model": MODEL_NAME,
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

async def summarize_text(text):
    """Summarize text using OpenRouter API"""
    prompt = f"Summarize the following document in a clear and concise manner:\n\n{text[:2000]}"
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return await call_openrouter_api(messages)

async def ask_question_api(context, question):
    """Answer questions about the document using OpenRouter API"""
    prompt = f"""You are a helpful assistant. Answer the question based on the provided document.

Document:
\"\"\"{context[:3000]}\"\"\"

Question: {question}

Answer:"""
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return await call_openrouter_api(messages)

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
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
        
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
    answer = await ask_question_api(document_data["text"], request.question)
    
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
    uvicorn.run(app, host=HOST, port=PORT)
