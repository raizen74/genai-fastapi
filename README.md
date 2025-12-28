# Building GenAI Services

A comprehensive FastAPI-based platform for serving multiple generative AI models, including text generation, image generation, audio synthesis, and video generation capabilities.

## Features

### Multi-Modal AI Capabilities

- **Text Generation**: LLM-powered chatbot using TinyLlama for conversational AI
- **Image Generation**: Text-to-image synthesis using Stable Diffusion (Tiny-SD)
- **Audio Synthesis**: Text-to-speech generation using Bark model with voice presets
- **Video Generation**: Image-to-video conversion using Stable Video Diffusion
- **3D Model Generation**: Text-to-3D geometry using ShapE (in development)

### Additional Features

- **RAG (Retrieval-Augmented Generation)**: Document-based knowledge retrieval system with PDF upload and semantic search
- **PostgreSQL Database**: Full persistence layer with async SQLAlchemy for conversations and messages
- **Database Migrations**: Alembic integration for schema versioning and migration management
- **RESTful API**: Complete CRUD operations for conversation management
- **Repository Pattern**: Clean architecture with separate repository and service layers
- **BentoML Integration**: Scalable model serving with BentoML
- **Streamlit Clients**: Ready-to-use web interfaces for testing AI endpoints
- **Usage Monitoring**: Built-in middleware for tracking API usage, response times, and request metadata
- **Hardware Acceleration**: Automatic device detection (CUDA, Apple Silicon MPS, or CPU)
- **URL Content Extraction**: Automatic extraction and processing of URLs mentioned in prompts

## Architecture

The project follows a modular architecture:

```
building_genai_services/
├── api/           # FastAPI application and endpoints
├── routers/       # API route handlers
│   └── conversations.py  # Conversation management endpoints
├── database/      # Database layer
│   ├── entities.py       # SQLAlchemy ORM models
│   ├── database.py       # Database connection and session management
│   ├── repositories/     # Data access layer
│   │   ├── conversations.py  # Conversation and Message repositories
│   │   └── interfaces.py     # Repository interface definitions
│   └── services/         # Business logic layer
│       └── conversations.py  # Conversation service
├── models/        # Model loading and inference logic
├── schemas/       # Pydantic schemas and type definitions
├── utils/         # Helper functions for media processing
├── rag/           # RAG system components
│   ├── repository.py  # Qdrant vector database operations
│   ├── services.py    # Vector storage service
│   ├── transform.py   # Text embedding and processing
│   └── extractor.py   # PDF text extraction
├── dependencies/  # FastAPI dependency injection
└── bentoml/       # BentoML service definitions

alembic/           # Database migrations
├── versions/      # Migration scripts
└── env.py         # Alembic environment configuration

streamlit/         # Streamlit client applications
├── client_text.py   # Text chatbot interface
├── client_audio.py  # Audio generation interface
└── client_image.py  # Image generation interface
```

## API Endpoints

### Conversation Management

#### List Conversations
```
GET /conversations?skip=0&take=100
```
Retrieves a paginated list of all conversations.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Discussion about AI",
    "model_type": "tinyLlama",
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:30:00Z",
    "messages": []
  }
]
```

#### Get Conversation
```
GET /conversations/{conversation_id}
```
Retrieves a specific conversation by ID.

#### Create Conversation
```
POST /conversations
Body: {"title": "New Chat", "model_type": "tinyLlama"}
```
Creates a new conversation.

**Response:**
```json
{
  "id": 1,
  "title": "New Chat",
  "model_type": "tinyLlama",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z",
  "messages": []
}
```

#### Update Conversation
```
PUT /conversations/{conversation_id}
Body: {"title": "Updated Title"}
```
Updates an existing conversation.

#### Delete Conversation
```
DELETE /conversations/{conversation_id}
```
Deletes a conversation and all associated messages (cascade delete).

#### List Conversation Messages
```
GET /conversations/{conversation_id}/messages
```
Retrieves all messages for a specific conversation.

**Response:**
```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "prompt_content": "What is AI?",
    "response_content": "AI is...",
    "prompt_tokens": 5,
    "response_tokens": 50,
    "total_tokens": 55,
    "is_success": true,
    "status_code": 200,
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z"
  }
]
```

#### Store Message with Generation
```
POST /store/message/{conversation_id}?prompt=<your_question>
```
Generates text using TinyLlama and stores both the prompt and response in the conversation. The message is stored asynchronously in the background.

### Document Upload (RAG)
```
POST /upload
Form data: file (PDF)
```
Uploads a PDF document for knowledge base integration. The endpoint:
- Accepts only PDF files
- Extracts text content using PyPDF
- Generates embeddings using Jina AI embeddings (768-dimensional vectors)
- Stores chunks in Qdrant vector database with semantic search capabilities
- Processes documents asynchronously in the background

**Response:**
```json
{
  "filename": "document.pdf",
  "message": "File uploaded successfully"
}
```

### Text Generation
```
POST /generate/text
Body: {"prompt": "your question"}
```
Returns generated text from TinyLlama chatbot with RAG-enhanced context. The endpoint automatically:
- Extracts and fetches content from any URLs mentioned in the prompt
- Performs semantic search against the vector database (top 3 results with 0.7 similarity threshold)
- Augments the prompt with retrieved document chunks and URL content
- Generates contextually-aware responses

### Image Generation
```
GET /generate/image?prompt=<your_prompt>
```
Returns a PNG image generated from the text prompt.

### Audio Generation
```
GET /generate/audio?prompt=<your_text>&preset=<voice_preset>
```
Returns WAV audio with synthesized speech. Available presets: `v2/en_speaker_1`, `v2/en_speaker_9`.

### Video Generation
```
POST /generate/video
Form data: image (file), num_frames (int, default: 25)
```
Returns an MP4 video generated from the input image.

### BentoML Image Generation
```
GET /generate/bentoml/image?prompt=<your_prompt>
```
Proxies image generation through BentoML service (requires BentoML server running on port 5000).

## Installation

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Qdrant vector database (for RAG functionality)
- CUDA-capable GPU (optional, for faster inference)
- Apple Silicon Mac (optional, for MPS acceleration)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd genai-fastapi
```

2. Install dependencies using uv:
```bash
uv pip install -e .
```

Or using pip:
```bash
pip install -e .
```

3. Start PostgreSQL database:

Using Docker:
```bash
docker run -d \
    --name postgres \
    -e POSTGRES_USER=fastapi \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -e POSTGRES_DB=backend_db \
    -p 5432:5432 \
    postgres:latest
```

4. Run database migrations:
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to database
alembic upgrade head
```

5. Start Qdrant vector database (required for RAG):

Using Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

Or install locally following [Qdrant installation guide](https://qdrant.tech/documentation/guides/installation/).

## Usage

### Starting the FastAPI Server

```bash
app
```

Or directly with uvicorn:
```bash
uvicorn building_genai_services.api.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

### Running Streamlit Clients

Text Generation Client:
```bash
streamlit run streamlit/client_text.py
```

Audio Generation Client:
```bash
streamlit run streamlit/client_audio.py
```

Image Generation Client:
```bash
streamlit run streamlit/client_image.py
```

### Starting BentoML Service

```bash
bentoml serve building_genai_services.bentoml.bento:Generate
```

### Using RAG with Document Upload

1. Upload a PDF document to build your knowledge base:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"
```

2. Query the knowledge base through text generation:
```bash
curl -X POST "http://localhost:8000/generate/text" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Who is ali parandeh?"}'
```

The system will automatically:
- Search the vector database for relevant document chunks
- Retrieve the top 3 most similar passages (with similarity score > 0.7)
- Include the retrieved context in the LLM prompt
- Generate an informed response based on your uploaded documents

## Monitoring and Usage Tracking

All API requests are automatically logged to `usage.csv` with the following information:

- Request ID
- Timestamp
- Endpoint triggered
- Client IP address
- Response time
- Status code
- Success indicator

Each response includes custom headers:
- `X-Response-Time`: Request processing time in seconds
- `X-API-Request-ID`: Unique identifier for the request

## Models Used

- **TinyLlama-1.1B-Chat-v1.0**: Lightweight language model for text generation
- **Jina AI Embeddings v2**: 768-dimensional text embeddings for semantic search
- **Tiny-SD (Segmind)**: Efficient Stable Diffusion model for image generation
- **Bark (Suno)**: Text-to-audio synthesis model
- **Stable Video Diffusion**: Image-to-video generation
- **ShapE (OpenAI)**: Text-to-3D model (experimental)

## Dependencies

Key dependencies include:
- FastAPI & Uvicorn for API serving
- SQLAlchemy 2.0+ for async ORM
- Alembic for database migrations
- psycopg (PostgreSQL driver) for database connectivity
- Transformers & Diffusers for model inference
- PyTorch for deep learning operations
- Qdrant Client for vector database operations
- PyPDF for PDF text extraction
- Jina AI for text embeddings
- Streamlit for client interfaces
- BentoML for production-ready model serving
- Pillow for image processing
- aiofiles for async file operations

See [pyproject.toml](pyproject.toml) for complete dependency list.

## Database Management

### Database Schema

The application uses two main tables:

**Conversations Table:**
- `id`: Primary key
- `title`: Conversation title
- `model_type`: AI model used (e.g., "tinyLlama")
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Messages Table:**
- `id`: Primary key
- `conversation_id`: Foreign key to conversations (CASCADE delete)
- `prompt_content`: User's prompt
- `response_content`: AI response
- `prompt_tokens`: Token count for prompt (optional)
- `response_tokens`: Token count for response (optional)
- `total_tokens`: Total tokens used (optional)
- `is_success`: Success indicator (optional)
- `status_code`: HTTP status code (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Alembic Migrations

Alembic is configured to manage database schema changes:

**Configuration:**
- Database URL: `postgresql+psycopg://fastapi:mysecretpassword@localhost:5432/backend_db`
- Migrations directory: `alembic/versions/`
- Auto-generation enabled with SQLAlchemy metadata

**Common Migration Commands:**

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "Add new column"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Check current database version
alembic current

# Rollback to specific version
alembic downgrade <revision_id>
```

**Important Notes:**
- Always review auto-generated migrations before applying them
- Database schema is version-controlled through Alembic
- The app no longer uses `Base.metadata.create_all()` - all schema changes are managed through migrations
- Migrations run synchronously while the app uses async SQLAlchemy for queries

### Repository Pattern

The codebase implements the Repository pattern for clean separation of concerns:

- **Entities** ([database/entities.py](building_genai_services/database/entities.py)): SQLAlchemy ORM models
- **Repositories** ([database/repositories/](building_genai_services/database/repositories/)): Data access layer with CRUD operations
- **Services** ([database/services/](building_genai_services/database/services/)): Business logic layer
- **Routers** ([routers/conversations.py](building_genai_services/routers/conversations.py)): API endpoint handlers

This architecture provides:
- Clear separation between data access and business logic
- Easy testing through dependency injection
- Reusable repository methods across different services
- Type-safe database operations with async SQLAlchemy

## Development

The project uses:
- Python 3.13+ type hints throughout
- Async/await patterns for non-blocking I/O
- SQLAlchemy 2.0+ async ORM with PostgreSQL
- Alembic for database schema versioning
- Repository pattern for clean architecture
- Context managers for model lifecycle management
- Middleware for cross-cutting concerns (monitoring, logging)
- Dependency injection for database sessions

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Acknowledgments

Built with models from Hugging Face, Stability AI, Suno, and OpenAI.
