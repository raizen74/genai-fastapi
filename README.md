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

- **BentoML Integration**: Scalable model serving with BentoML
- **Streamlit Clients**: Ready-to-use web interfaces for testing AI endpoints
- **Usage Monitoring**: Built-in middleware for tracking API usage, response times, and request metadata
- **Hardware Acceleration**: Automatic device detection (CUDA, Apple Silicon MPS, or CPU)

## Architecture

The project follows a modular architecture:

```
building_genai_services/
├── api/           # FastAPI application and endpoints
├── models/        # Model loading and inference logic
├── schemas/       # Pydantic schemas and type definitions
├── utils/         # Helper functions for media processing
└── bentoml/       # BentoML service definitions

streamlit/         # Streamlit client applications
├── client_text.py   # Text chatbot interface
├── client_audio.py  # Audio generation interface
└── client_image.py  # Image generation interface
```

## API Endpoints

### Text Generation
```
GET /generate/text?prompt=<your_prompt>
```
Returns generated text from TinyLlama chatbot.

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

- Python 3.9+
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
- **Tiny-SD (Segmind)**: Efficient Stable Diffusion model for image generation
- **Bark (Suno)**: Text-to-audio synthesis model
- **Stable Video Diffusion**: Image-to-video generation
- **ShapE (OpenAI)**: Text-to-3D model (experimental)

## Dependencies

Key dependencies include:
- FastAPI & Uvicorn for API serving
- Transformers & Diffusers for model inference
- PyTorch for deep learning operations
- Streamlit for client interfaces
- BentoML for production-ready model serving
- Pillow for image processing

See [pyproject.toml](pyproject.toml) for complete dependency list.

## Development

The project uses:
- Python 3.9+ type hints throughout
- Async/await patterns for non-blocking I/O
- Context managers for model lifecycle management
- Middleware for cross-cutting concerns (monitoring, logging)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Acknowledgments

Built with models from Hugging Face, Stability AI, Suno, and OpenAI.
