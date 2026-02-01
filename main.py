"""
Main FastAPI application for RAG Chatbot
Imports all necessary components and sets up the Uvicorn server
"""

import os
import sys
from pathlib import Path


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from app modules
from app.retriever import  embed_texts
from app.rag_graph import rag
from app.ingest import load_txt, load_pdf

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="A Retrieval-Augmented Generation Chatbot using LangChain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import ingest functions
from app.ingest import load_txt, load_pdf
from app.retriever import embed_texts

# Load documents and embeddings at startup
DOCUMENTS = None
DOC_EMBEDDINGS = None

@app.on_event("startup")
async def startup_event():
    """Load documents on server startup"""
    global DOCUMENTS, DOC_EMBEDDINGS
    print("\n📚 Loading documents and building index...")
    try:
        # Load from both TXT and PDF
        docs_txt = load_txt("data/input.txt")
        docs_pdf = load_pdf("data/doc.pdf")
        DOCUMENTS = docs_txt + docs_pdf
        DOC_EMBEDDINGS = embed_texts(DOCUMENTS)
        print(f"✓ Index built with {len(DOCUMENTS)} documents (Text: {len(docs_txt)}, PDF: {len(docs_pdf)})\n")
    except Exception as e:
        print(f"⚠️  Error loading documents: {e}\n")
        # Set empty defaults if loading fails
        DOCUMENTS = []
        DOC_EMBEDDINGS = None


# Pydantic models
class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str
    k: int = 2  # Number of context documents to retrieve


class QuestionResponse(BaseModel):
    """Response model for question answers"""
    question: str
    k: int
    answer: str
    contexts: list[str]
    confidence: float


# Routes
@app.get("/", tags=["Health"])
def home():
    """Root endpoint - Returns API status"""
    return {
        "status": "✓ RAG Chatbot API is running",
        "docs": "/docs",
        "message": "Go to /docs for Swagger UI to test the API"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if DOCUMENTS else "documents_not_loaded",
        "documents_loaded": len(DOCUMENTS) if DOCUMENTS else 0,
        "embeddings_ready": DOC_EMBEDDINGS is not None,
        "message": "Set OPENAI_API_KEY environment variable to enable document loading" if not DOCUMENTS else "Ready"
    }


@app.post("/ask", response_model=QuestionResponse, tags=["Chat"])
def ask_question(payload: QuestionRequest):
    """
    Ask a question to the RAG chatbot
    
    Parameters:
    - question: The question to ask
    - k: Number of context documents to retrieve (default: 2)
    
    Returns:
    - question: The original question
    - k: Number of retrieved contexts
    - answer: The generated answer from the LLM
    - contexts: List of retrieved relevant documents
    - confidence: Confidence score based on similarity scores (0-1)
    """
    if not DOCUMENTS:
        return {
            "question": payload.question,
            "k": payload.k,
            "answer": "Error: Documents not loaded. Check your .env file and ensure OPENAI_API_KEY is set.",
            "contexts": [],
            "confidence": 0.0
        }
    
    if not payload.question or not payload.question.strip():
        return {
            "question": payload.question,
            "k": payload.k,
            "answer": "Please provide a valid question.",
            "contexts": [],
            "confidence": 0.0
        }
    
    try:
        # Get RAG response
        answer, contexts, confidence = rag(
            payload.question,
            DOCUMENTS,
            DOC_EMBEDDINGS,
            k=payload.k
        )

        return {
            "question": payload.question,
            "k": payload.k,
            "answer": answer,
            "contexts": contexts,
            "confidence": confidence
        }
    except Exception as e:
        return {
            "question": payload.question,
            "k": payload.k,
            "answer": f"Error processing question: {str(e)}",
            "contexts": [],
            "confidence": 0.0
        }


@app.get("/stats", tags=["Info"])
def get_stats():
    """Get statistics about the loaded documents"""
    return {
        "total_documents": len(DOCUMENTS) if DOCUMENTS else 0,
        "embedding_dimension": DOC_EMBEDDINGS.shape[1] if DOC_EMBEDDINGS is not None else 0,
        "total_embeddings": len(DOC_EMBEDDINGS) if DOC_EMBEDDINGS is not None else 0
    }


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting RAG Chatbot Server...")
    print("="*60)
    print("📚 Documents loaded:", len(DOCUMENTS))
    print("🔗 Swagger UI: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
