# AI Study Buddy - Backend

FastAPI backend for AI Study Buddy with ML-powered question answering using microsoft/Phi-3-mini-4k-instruct.

## Features

- 🤖 **AI Chat**: Phi-3 model with RAG for context-aware responses
- 📚 **PDF Processing**: Extract training data from study materials
- 🎯 **Fine-Tuning**: LoRA/QLoRA fine-tuning pipeline
- 🔍 **RAG**: Vector search with ChromaDB for relevant context
- 🔐 **Authentication**: JWT-based auth with bcrypt password hashing
- 📊 **Admin Dashboard**: Statistics and management APIs

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (async with Motor)
- **ML Model**: microsoft/Phi-3-mini-4k-instruct
- **Fine-Tuning**: HuggingFace Transformers + PEFT (LoRA)
- **Vector Store**: ChromaDB
- **Embeddings**: sentence-transformers

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB connection
│   │
│   ├── models/              # Pydantic schemas
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── chat.py
│   │   └── stats.py
│   │
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # /api/auth/*
│   │   ├── chat.py          # /api/chat
│   │   ├── user.py          # /api/user/*
│   │   ├── admin.py         # /api/admin/*
│   │   └── db.py            # /api/db/*
│   │
│   ├── services/            # Business logic
│   │   └── auth_service.py
│   │
│   └── ml/                  # ML components
│       ├── phi3_client.py   # Phi-3 inference
│       ├── fine_tune.py     # LoRA fine-tuning
│       ├── pdf_processor.py # PDF extraction
│       ├── embeddings.py    # Text embeddings
│       ├── rag_service.py   # RAG retrieval
│       └── gemini_fallback.py # Gemini API fallback
│
├── scripts/                 # CLI scripts
│   ├── prepare_data.py      # Process PDFs
│   ├── train.py             # Fine-tuning
│   └── index_rag.py         # RAG indexing
│
├── study_pdfs/              # Input PDF files
├── training_data/           # Generated training data
├── models/                  # Fine-tuned models
├── chroma_db/               # Vector store
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Quick Start

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your settings
# Required:
#   - MONGODB_URI
#   - JWT_SECRET
```

### 3. Add Study Materials

Place your PDF files in the `study_pdfs/` directory:
```
study_pdfs/
├── machine_learning.pdf
├── data_science.pdf
└── python_programming.pdf
```

### 4. Process PDFs & Prepare Data

```bash
# Extract text and generate training data
python scripts/prepare_data.py --load-to-rag
```

### 5. Fine-Tune Model (Optional but Recommended)

```bash
# Fine-tune Phi-3 on your study materials
python scripts/train.py --epochs 3 --batch-size 4
```

Requirements:
- NVIDIA GPU with 12GB+ VRAM (for 4-bit training)
- ~24GB RAM

### 6. Run Server

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/session` | Get current session |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to AI |
| POST | `/api/chat/stream` | Stream response |
| GET | `/api/chat/model-info` | Get model info |

### User
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/chat-history` | Get user's history |
| DELETE | `/api/user/chat-history` | Delete chat entry |
| GET | `/api/user/stats` | Get user stats |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/courses` | List courses |
| POST | `/api/admin/courses` | Create course |
| PUT | `/api/admin/courses` | Update course |
| DELETE | `/api/admin/courses` | Delete course |
| GET | `/api/admin/chat-history` | All chat history |
| GET | `/api/admin/stats` | Dashboard stats |

### Database
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/db/init` | Initialize database |
| GET | `/api/db/health` | Database health |

## ML Pipeline

### 1. PDF Processing

```python
from app.ml.pdf_processor import PDFProcessor

processor = PDFProcessor()
result = processor.process_all_pdfs()
# Generates: training_data/training_data.json
# Generates: training_data/rag_chunks.json
```

### 2. RAG Indexing

```python
from app.ml.rag_service import get_rag_service

rag = get_rag_service()
rag.initialize()

# Search for relevant context
context = rag.get_context_for_query("What is gradient descent?")
```

### 3. Fine-Tuning

```python
from app.ml.fine_tune import run_fine_tuning, FineTuningConfig

config = FineTuningConfig(
    lora_r=16,
    lora_alpha=32,
    num_epochs=3,
    batch_size=4,
    learning_rate=2e-4
)

result = run_fine_tuning(config=config)
```

### 4. Inference

```python
from app.ml.phi3_client import get_phi3_client

client = get_phi3_client()
response, tokens = client.generate(
    prompt="Explain neural networks",
    max_tokens=500
)
```

## Docker Deployment

```bash
# Build image
docker build -t ai-study-buddy-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e MONGODB_URI=your_mongodb_uri \
  -e JWT_SECRET=your_secret \
  -v ./study_pdfs:/app/study_pdfs \
  -v ./models:/app/models \
  ai-study-buddy-backend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | Required |
| `JWT_SECRET` | Secret for JWT tokens | Required |
| `MODEL_NAME` | HuggingFace model | microsoft/Phi-3-mini-4k-instruct |
| `MODEL_PATH` | Fine-tuned model path | ./models/phi3-finetuned |
| `USE_GPU` | Enable GPU inference | true |
| `MAX_TOKENS` | Max response tokens | 1000 |
| `TEMPERATURE` | Sampling temperature | 0.7 |
| `GEMINI_API_KEY_1` | Gemini fallback key | Optional |

## Development

```bash
# Format code
black app/

# Sort imports
isort app/

# Run tests
pytest tests/
```

## License

MIT License
