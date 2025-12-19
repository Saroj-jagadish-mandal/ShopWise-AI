<p align="center">
  <h1 align="center">ShopWise AI</h1>
  <p align="center">
    <strong>AI-Powered Amazon Product Q&A Assistant</strong>
  </p>
  <p align="center">
    A full-stack RAG application that scrapes Amazon product data and provides intelligent, context-aware answers using LLM technology.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/LangChain-1.0-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Pinecone-Vector_DB-000000?style=for-the-badge" alt="Pinecone" />
  <img src="https://img.shields.io/badge/Celery-5.5-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />
</p>

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React)"]
        UI[Chat Interface]
        Sidebar[Product Sidebar]
    end

    subgraph Backend["Backend (Django REST)"]
        API[REST API]
        Views[Views Layer]
        Services[QA Service]
    end

    subgraph Workers["Async Processing (Celery)"]
        Scraper[Playwright Scraper]
        Embedder[Embedding Generator]
    end

    subgraph External["External Services"]
        Amazon[(Amazon.com)]
        Pinecone[(Pinecone Vector DB)]
        Gemini[Google Gemini 2.0]
        OpenAI[OpenAI Embeddings]
    end

    subgraph Storage["Data Storage"]
        Postgres[(PostgreSQL)]
        Redis[(Redis)]
    end

    UI --> API
    Sidebar --> API
    API --> Views
    Views --> Services
    Views --> Scraper
    Scraper --> Amazon
    Scraper --> Embedder
    Embedder --> OpenAI
    Embedder --> Pinecone
    Services --> Pinecone
    Services --> Gemini
    Views --> Postgres
    Scraper --> Redis
```

---

## Features

### Product Intelligence
- **Automated Web Scraping**: Playwright-based scraper extracts product titles, prices, features, specifications, variants, and customer reviews from Amazon product pages
- **Multi-Page Review Extraction**: Pagination-aware scraper captures up to 5 pages of customer reviews for comprehensive product insights
- **Real-Time Status Tracking**: Celery task queue with polling mechanism provides live scraping progress updates

### RAG-Powered Q&A
- **Vector Similarity Search**: OpenAI embeddings stored in Pinecone enable semantic search across product data
- **Context-Aware Responses**: Google Gemini 2.0 Flash generates answers grounded in retrieved product context
- **Conversation Memory**: Chat sessions maintain history for multi-turn conversations with context carryover
- **Response Caching**: Redis-backed caching reduces latency for repeated queries

### Frontend Experience
- **Dark/Light Theme**: Persistent theme preference with system-level CSS variables
- **Responsive Layout**: Collapsible sidebar with adaptive main content area
- **Markdown Rendering**: AI responses rendered with proper formatting
- **Product Management**: Add, delete, and retry failed product scrapes from the UI

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, Axios, Lucide Icons, react-markdown |
| **Backend** | Django 5.2, Django REST Framework |
| **Task Queue** | Celery 5.5, Redis, django-celery-beat |
| **Scraping** | Playwright (Chromium) |
| **Vector DB** | Pinecone |
| **Embeddings** | OpenAI `text-embedding-ada-002` |
| **LLM** | Google Gemini 2.0 Flash Lite |
| **Database** | PostgreSQL |
| **Caching** | Redis |

---

## Project Structure

```
amazon-qa-django/
├── amazon_qa_project/          # Django project settings
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── products/                   # Main application
│   ├── models.py               # Product, Review, ChatSession, ChatMessage
│   ├── views.py                # REST API endpoints
│   ├── scraper.py              # Playwright Amazon scraper
│   ├── embeddings.py           # Pinecone/OpenAI integration
│   ├── services.py             # RAG QA service with Gemini
│   ├── tasks.py                # Celery async tasks
│   └── serializers.py          # DRF serializers
├── frontend/                   # React application
│   └── src/
│       ├── App.js              # Main app with state management
│       ├── components/
│       │   ├── Navbar/
│       │   ├── Sidebar/
│       │   └── ChatWindow/
│       └── services/
│           └── api.js          # Axios API client
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products/` | List all products (paginated) |
| `POST` | `/api/products/` | Add product URL, triggers scraping |
| `GET` | `/api/products/{id}/` | Get product details |
| `DELETE` | `/api/products/{id}/` | Delete product and embeddings |
| `GET` | `/api/products/{id}/status/` | Get scraping task status |
| `POST` | `/api/products/{id}/retry/` | Retry failed scrape |
| `POST` | `/api/products/{id}/ask/` | Ask question about product |
| `GET` | `/api/products/{id}/reviews/` | Get product reviews |
| `GET` | `/api/products/{id}/chat-sessions/` | Get chat sessions |

---

## Data Flow

### 1. Product Ingestion
```
User submits Amazon URL → API creates Product record → Celery task dispatched
    → Playwright scrapes product page → Extracts: title, price, features, specs, reviews
    → Text concatenated → Split into chunks → OpenAI generates embeddings
    → Vectors upserted to Pinecone namespace → Product status → "completed"
```

### 2. Question Answering
```
User asks question → API receives request → QA Service invoked
    → OpenAI embeds question → Pinecone similarity search (top-5 chunks)
    → Context + question → Gemini 2.0 Flash generates answer
    → Response cached in Redis → Chat message saved → Answer returned
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Environment Variables

Create `.env` in project root:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/shopwise_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=shopwise-products
```

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

### Celery Worker

```bash
# In separate terminal
celery -A amazon_qa_project worker -l info -P solo
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Access application at `http://localhost:3000`

---

## Database Schema

### Product
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `url` | URL | Amazon product URL |
| `title` | Text | Product title |
| `brand` | CharField | Brand name |
| `current_price` | CharField | Current price |
| `features` | Text | Bullet point features |
| `specifications` | JSON | Technical specifications |
| `status` | Enum | pending/scraping/embedding/completed/failed |
| `pinecone_namespace` | CharField | Vector DB namespace |
| `vector_count` | Integer | Number of stored vectors |

### ChatSession / ChatMessage
Maintains conversation state with `session_id` continuity and stores context chunks used for each response.

---

## Key Implementation Details

### Playwright Scraper
- Headless Chromium with anti-bot headers
- CSS selector-based extraction with fallbacks
- Review pagination up to 5 pages
- Error handling with task retry mechanism

### Embedding Pipeline
- `RecursiveCharacterTextSplitter`: 800 char chunks, 100 overlap
- Batch processing (50 vectors per upsert)
- Per-product Pinecone namespaces for isolation

### QA Service
- Top-5 semantic similarity retrieval
- Last 5 messages as chat history context
- 1-hour response caching

---

## License

MIT

---

## Author

Built as a demonstration of full-stack AI application development integrating web scraping, vector databases, and LLM-powered retrieval augmented generation.
