# RAG Chatbot - Retrieval-Augmented Generation System with vector db

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot built with **FastAPI**, **LangChain**, and **OpenAI**. Intelligently retrieves context from multiple document sources (TXT, PDF) and generates accurate, context-aware responses.

---

## 🚀 Features

✅ Upload / Read PDF documents
✅ Chunk PDF text for better retrieval
✅ Generate embeddings for all chunks
✅ Store embeddings in **Milvus** (Vector DB)
✅ Retrieve top-k relevant chunks for every query
✅ Generate response using LLM + retrieved context
✅ Returns:

* **Answer**
* **Retrieved Context**
* **Confidence Score**


## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **pip** or **poetry**
- **OpenAI API Key**

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd RAG_chatbot
```

#### 2. Install Dependencies

**Option A: Using pip**
```bash
pip install -r requirements.txt
OR
poetry install
```

**Option B: Using poetry**
```bash
poetry install
```

#### 3. Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=your_token
MILVUS_DB_NAME=default
```

#### 4. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📋 Project Structure

```
RAG_chatbot/
├── main.py                 # FastAPI server entry point
├── pyproject.toml         # Poetry dependencies
├── .env                   # Environment variables
├── test.ipynb            # Jupyter notebook for testing
│
├── app/
│   ├── retriever.py      # Vector search & embedding
│   ├── generator.py      # LLM response generation
│   ├── rag_graph.py      # RAG orchestration
│   ├── ingest.py         # Document loading & processing
│   └── api.py            # Legacy API (deprecated)
│
└── data/
    ├── input.txt         # Sample text documents
    └── doc.pdf           # Sample PDF documents
```

---

## 🏗️ Architecture Overview

### System Flow Diagram

```
User Question
    ↓
[API Endpoint: /ask]
    ↓
[Document Retrieval]
├─→ Embed query using OpenAI embeddings
├─→ Search vector database (Milvus/Pinecone)
└─→ Retrieve top-k similar documents (default k=2)
    ↓
[Context Assembly]
└─→ Combine retrieved documents into context
    ↓
[LLM Response Generation]
├─→ Pass context + question to GPT-4o-mini
├─→ Generate grounded answer
└─→ Compute confidence score
    ↓
[Response to User]
└─→ Return: answer + contexts + confidence
```

### Key Components

#### 1. **Document Ingestion** (`app/ingest.py`)
- Loads documents from TXT and PDF files
- Returns document content as strings for embedding

#### 2. **Embedding & Retrieval** (`app/retriever.py`)
- Uses **OpenAI `text-embedding-3-small`** for embeddings
- Lazy-loads embeddings model to avoid API key errors at import time
- Performs vector similarity search using cosine distance

#### 3. **LLM Response Generation** (`app/generator.py`)
- Uses **GPT-4o-mini** for fast, cost-effective responses
- Lazy-loads LLM to defer initialization
- Generates answers constrained to provided context

#### 4. **RAG Orchestration** (`app/rag_graph.py`)
- Retrieves relevant documents
- Assembles context window
- Computes confidence scores based on similarity

#### 5. **FastAPI Server** (`main.py`)
- Loads all documents on startup
- Exposes `/ask` endpoint for queries
- Provides `/health` and `/stats` endpoints
- Handles errors gracefully

---

## 🔧 Design Decisions

### 1. **Why Lazy Loading of Models?**
- **Problem**: OpenAI API key validation happens at import time
- **Solution**: Defer model initialization using lazy-loading functions
- **Benefit**: Server starts even without API key; models load on first use
- **Implementation**: `get_embeddings_model()` and `get_llm()` functions

### 2. **Why OpenAI `text-embedding-3-small`?**
- **Efficiency**: 512-dimensional vectors (vs 1536 for -large)
- **Performance**: 10x faster, lower cost
- **Quality**: Excellent for semantic search while maintaining quality
- **Use Case**: Perfect for retrieval; larger models not needed for ranking

### 3. **Why GPT-4o-mini for Generation?**
- **Cost**: ~10x cheaper than GPT-4o
- **Speed**: 5-10x faster for text generation
- **Quality**: Sufficient for RAG context-constrained responses
- **Best Practice**: Use larger models only when necessary

### 4. **Why Cosine Similarity for Retrieval?**
- **Standard**: Most common metric for vector similarity
- **Normalized**: Works with normalized embeddings from OpenAI
- **Efficient**: O(n) complexity with optimized implementations
- **Interpretable**: Scores range [0, 1], directly usable as confidence

### 5. **Why Both TXT and PDF Support?**
- **Flexibility**: Supports multiple document formats
- **Real-world**: Most enterprises have both text and PDF documents
- **Consistency**: Both loaders return `list[str]` for uniform processing
- **Scalability**: Easy to add more formats (DOCX, HTML, etc.)

### 6. **Why Milvus Vector Database?**
- **Open-source**: No vendor lock-in
- **Scalable**: Handles millions of vectors efficiently
- **Flexible**: Supports various index types (IVF, HNSW, Annoy)
- **Optional**: Can work without it; uses in-memory embeddings for testing

### 7. **Why FastAPI?**
- **Modern**: Async support, automatic OpenAPI documentation
- **Type-safe**: Pydantic validation out-of-the-box
- **Fast**: Among the fastest Python web frameworks
- **Developer-friendly**: Built-in Swagger UI for testing

---

## 📊 API Endpoints

### 1. POST `/ask` - Ask a Question
**Request:**
```json
{
  "question": "What is the main topic?",
  "k": 2
}
```

**Response:**
```json
{
  "question": "What is the main topic?",
  "k": 2,
  "answer": "The main topic is the representation of meaning as vectors...",
  "contexts": [
    "The throughline is simple yet powerful: represent meaning as vectors...",
    "Vector databases make Approximate Nearest Neighbor searches feasible..."
  ],
  "confidence": 0.82
}
```

### 2. GET `/health` - Health Check
Returns system status and document count.

### 3. GET `/stats` - System Statistics
Returns embedding dimension and total documents loaded.

### 4. GET `/` - Root Endpoint
Returns API information and Swagger UI link.

---

## 🧪 Testing

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click on POST `/ask`
3. Click "Try it out"
4. Enter your question and k value
5. Click "Execute"

### Using Jupyter Notebook
```bash
jupyter notebook test.ipynb
```

The notebook includes:
- Loading documents from both TXT and PDF
- Testing RAG with sample questions
- Viewing contexts and confidence scores

### Using cURL
```bash
curl -X 'POST' \
  'http://localhost:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What is google adk?",
    "k": 2
  }'
```

---

## 📦 Dependencies

### Core RAG Stack
- **langchain**: LLM orchestration framework
- **langchain-openai**: OpenAI integration
- **langchain-community**: Community integrations (PDF loaders, Milvus)
- **langchain-text-splitters**: Document chunking

### Data & Embeddings
- **pymilvus**: Vector database client
- **pypdf**: PDF document loading
- **numpy**: Numerical operations
- **scikit-learn**: Cosine similarity calculations

### API & Server
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation

### Utilities
- **python-dotenv**: Environment variable loading
- **openai**: Direct OpenAI API access

---

## 🚨 Error Handling

The system gracefully handles:
- Missing OpenAI API key → Deferred until first use
- Missing PDF file → Continues with TXT documents
- Empty question → Returns clear error message
- Large document sets → Processes in batches

---

## 🔐 Security Best Practices

1. **Never commit `.env`** - Always add to `.gitignore`
2. **Use environment variables** - For all sensitive data
3. **Validate inputs** - Pydantic handles this automatically
4. **Rate limiting** - Add in production (not implemented in demo)
5. **Authentication** - Add API key validation for production

---

## 📈 Performance Optimization

### For Production:
1. **Use async database queries** - Replace synchronous Milvus calls
2. **Implement caching** - Cache embeddings for repeated queries
3. **Batch embeddings** - Process multiple documents at once
4. **Add rate limiting** - Prevent abuse
5. **Use connection pooling** - For database connections

### Tuning Parameters:
- `k`: Number of documents to retrieve (default: 2, range: 1-10)
- Chunk size: 800 tokens (in `ingest.py`)
- Chunk overlap: 100 tokens (provides context continuity)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Set `OPENAI_API_KEY` in `.env` |
| PDF not loading | Ensure `pypdf` is installed: `pip install pypdf` |
| Port 8000 in use | Change port: `uvicorn main:app --port 8001` |
| Slow embeddings | Use -small model instead of -large |
| Low confidence scores | Increase `k` parameter or improve document chunking |

---

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [Milvus Documentation](https://milvus.io/docs)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👤 Author

**Amrendra Singh**

---

## 🎯 Roadmap

- [ ] Add support for DOCX files
- [ ] Implement streaming responses
- [ ] Add conversation history/memory
- [ ] Fine-tune embedding models
- [ ] Add multi-language support
- [ ] Deploy to production (Docker, K8s)
- [ ] Add user feedback mechanism
- [ ] Implement feedback-based re-ranking

---

**Questions? Open an issue or check the documentation above!**
