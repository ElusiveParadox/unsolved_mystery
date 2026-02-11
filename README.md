# Cold Case Detective

An intelligent investigation assistant that enables users to analyze uploaded evidence documents and obtain AI-generated answers with cited sources. The system leverages Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses grounded in the provided evidence.

## Features

- **Evidence Management**: Upload PDF or TXT documents to build a searchable knowledge base
- **Intelligent Querying**: Ask questions about uploaded evidence and receive AI-generated answers
- **Source Attribution**: All responses include citations referencing the source documents
- **User Authentication**: Secure registration and login system with JWT token-based authentication
- **Usage Quotas**: Daily query limit of 15 requests per user for fair resource allocation
- **Conversation History**: Persistent chat history for reference during investigations

## Technology Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **JWT Authentication**: Secure user authentication with JSON Web Tokens
- **Python-Jose**: Cryptographic library for JWT token handling

### AI & Machine Learning
- **LangChain**: Framework for developing AI-powered applications
- **FAISS**: Efficient similarity search and clustering of dense vectors
- **Groq API**: Inference engine powered by Llama 3.1 8B Instant model
- **HuggingFace Embeddings**: all-MiniLM-L6-v2 model for text embeddings
- **Sentence Transformers**: Pre-trained models for semantic embeddings

### Frontend
- **Streamlit**: Interactive web application framework for data apps

### Infrastructure
- **Uvicorn**: ASGI server for FastAPI applications
- **python-dotenv**: Environment variable management

## Project Structure

```
unsolved_mystery/
├── backend/
│   ├── __init__.py
│   ├── auth.py           # Authentication utilities (password hashing, JWT)
│   ├── config.py         # Configuration settings
│   ├── db.py             # Database models and initialization
│   ├── main.py           # FastAPI application and endpoints
│   ├── rag_engine.py     # RAG pipeline implementation
│   └── schemas.py        # Pydantic schemas for request/response
├── evidence/             # Storage for uploaded evidence files
├── frontend/
│   └── app.py           # Streamlit frontend application
├── pyproject.toml       # Project dependencies and configuration
└── README.md            # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd unsolved_mystery
```

2. Install dependencies using uv:
```bash
uv pip install -r backend/requirements.txt
uv pip install -r frontend/requirements.txt
```

Alternatively, install all dependencies from pyproject.toml:
```bash
uv pip install -e .
```

3. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```env
GROQ_API_KEY=your_groq_api_key
BACKEND_URL=http://localhost:8000
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

4. Initialize the database:
```bash
# The database is automatically initialized when the backend starts
```

## Usage

### Starting the Backend Server

Navigate to the project root and run:
```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Starting the Frontend Application

In a separate terminal:
```bash
streamlit run frontend/app.py
```

The web interface will open at `http://localhost:8501`

### Workflow

1. **Registration**: Create an account using the sidebar form
2. **Login**: Authenticate with username and password
3. **Upload Evidence**: Upload PDF or TXT files via the sidebar
4. **Ask Questions**: Submit queries about the uploaded evidence
5. **Review Responses**: Receive AI-generated answers with source citations

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register a new user account |
| `/login` | POST | Authenticate and receive JWT token |

### Evidence Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload evidence files (PDF/TXT) |
| `/ask` | POST | Query the RAG system with a question |

### User Resources

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/quota` | GET | Check remaining daily queries |
| `/history` | GET | Retrieve conversation history |
| `/history` | DELETE | Clear conversation history |

## Configuration

### User Limits
- Daily query limit: 15 requests per user
- Conversation history: Last 5 conversations retained

### Supported File Formats
- PDF documents (.pdf)
- Plain text files (.txt)

### Embedding Model
- Model: all-MiniLM-L6-v2
- Provides semantic embeddings for document similarity search

## License

This project is proprietary software. All rights reserved.

