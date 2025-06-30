import pytesseract
from pdf2image import convert_from_path
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from PIL import Image
import torch
import os
import requests
import json

# API Configuration
OPENROUTER_API_KEY = "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"  # Replace with your actual API key
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemma-3n-e4b-it:free"

# Set this to your Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ----- OCR -----
def extract_text_from_pdf(pdf_path):
    print("📄 Converting PDF to images...")
    images = convert_from_path(pdf_path)
    full_text = ""
    for i, img in enumerate(images):
        print(f"🔍 OCR on page {i+1}...")
        text = pytesseract.image_to_string(img)
        full_text += text + "\n\n"
    return full_text.strip()

def extract_text_from_image(image_path):
    print(f"🔍 OCR on image: {image_path}")
    img = Image.open(image_path)
    return pytesseract.image_to_string(img).strip()

# ----- Chunking -----
def chunk_text(text, max_words=1500):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# ----- API Helper -----
def call_openrouter_api(messages, max_tokens=300):
    """Make API call to OpenRouter"""
    print("🌐 Making API call to OpenRouter...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "document-summarizer",  # Your site URL
        "X-Title": "Document Summarizer",  # Your site name
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
        return "Error: Unable to process request"
    except KeyError as e:
        print(f"❌ Response Error: {e}")
        return "Error: Invalid API response"

# ----- Summarize -----
def summarize_text(text):
    """Summarize text using OpenRouter API"""
    prompt = f"Summarize the following document in a clear and concise manner:\n\n{text[:2000]}"
    print("✍️ Summarizing...")
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return call_openrouter_api(messages)

# ----- Q&A -----
def ask_question(context, question):
    """Answer questions about the document using OpenRouter API"""
    prompt = f"""You are a helpful assistant. Answer the question based on the provided document.

Document:
\"\"\"{context[:3000]}\"\"\"

Question: {question}

Answer:"""
    
    print("💬 Answering question...")
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return call_openrouter_api(messages)

# ----- Main -----
if __name__ == "__main__":
    file_path = input("📂 Enter path to PDF or image file: ").strip()

    if not os.path.exists(file_path):
        print("❌ File not found.")
        exit()

    # Step 1: OCR
    if file_path.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    print("\n✅ Text Extraction Complete.")

    # Check API key
    if OPENROUTER_API_KEY == "<OPENROUTER_API_KEY>":
        print("❌ Please set your OpenRouter API key in the OPENROUTER_API_KEY variable.")
        exit()

    # Step 2: Chunk + Summarize
    chunks = chunk_text(extracted_text)
    summaries = [summarize_text(chunk) for chunk in chunks]
    final_summary = summarize_text(" ".join(summaries))

    print("\n📄 Final Summary:\n")
    print(final_summary)

    # Step 3: Q&A
    while True:
        question = input("\n❓ Ask a question about the document (or type 'exit'): ")
        if question.lower() == "exit":
            break
        answer = ask_question(extracted_text, question)
        print(f"\n💡 Answer: {answer}")
