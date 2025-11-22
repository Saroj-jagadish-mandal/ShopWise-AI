# ShopWise AI

<!--**AI-Powered Amazon Product Q&A Platform**

A production-ready Django application that enables conversational interactions with Amazon product data using RAG (Retrieval-Augmented Generation) architecture.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---  -->

## 🎯 Overview

ShopWise AI transforms Amazon product research by allowing users to ask natural language questions and receive instant, contextual answers derived from product specifications, customer reviews, and Q&As.

**Key Features:**
- Natural language product search and Q&A
- Asynchronous web scraping with Celery
- Semantic search using vector embeddings
- RESTful API architecture
- Real-time chat interface

---

## 🏗️ Architecture

```
┌─────────────┐
│   React.js  │  Frontend
│   Frontend  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Django    │  REST API Layer
│     DRF     │
└──────┬──────┘
       │
   ┌───┴────┬──────────┬─────────┐
   ▼        ▼          ▼         ▼
┌────────┐ ┌───────┐ ┌───────┐ ┌─────────┐
│Postgres│ │ Redis │ │Celery │ │Pinecone │
│   DB   │ │ Cache │ │ Queue │ │ Vector  │
└────────┘ └───────┘ └───────┘ └─────────┘
                        │
                   ┌────▼─────┐
                   │ Selenium │
                   │ Scraper  │
                   └──────────┘
```

**Technology Stack:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Django 4.2 + DRF | REST API & Business Logic |
| Database | PostgreSQL | Data Persistence |
| Cache | Redis | Query Caching & Message Broker |
| Task Queue | Celery | Async Scraping Operations |
| Vector DB | Pinecone | Semantic Search |
| Embeddings | OpenAI API | Text Embeddings (1536 dim) |
| LLM | Google Gemini | Answer Generation |
| Scraping | Selenium | Product Data Extraction |
| Frontend | React.js | User Interface |
| Deployment | Docker Compose | Containerization |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Saroj-jagadish-mandal/ShopWise-AI.git
cd shopwise-ai
```

2. **Environment Setup**
```bash
cp .env.example .env
# Add your API keys to .env
```

3. **Docker Deployment (Recommended)**
```bash
docker-compose up --build -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

4. **Manual Setup**
```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
createdb shopwise_db
python manage.py migrate

# Run services (separate terminals)
python manage.py runserver                    # Django
celery -A amazon_qa_project worker -l info    # Celery Worker
redis-server                                   # Redis
```

**Access:**
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- Frontend: http://localhost:3000/

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Core Endpoints

#### Product Management
```http
POST   /products/              # Create product & start scraping
GET    /products/              # List all products
GET    /products/{id}/         # Get product details
GET    /products/{id}/status/  # Check scraping status
```

#### Conversational AI
```http
POST   /products/{id}/ask/     # Ask question about product
```

**Request:**
```json
{
  "question": "What do customers say about battery life?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Based on customer reviews, the battery life...",
  "session_id": "generated-session-id",
  "context_chunks": [
    {
      "text": "Battery lasts 8-10 hours...",
      "score": 0.89
    }
  ]
}
```

#### Analytics
```http
GET    /products/{id}/reviews/       # Get product reviews
GET    /chat-sessions/{id}/messages/ # Get chat history
```

---

## 🔧 Technical Implementation

### 1. Web Scraping Pipeline
**File:** `products/scraper.py`

```python
class AmazonProductScraper:
    """Selenium-based scraper for Amazon product data"""
    
    def scrape_product_data(self, url):
        # Extracts: title, price, features, specs, reviews, Q&As
        # Handles pagination for reviews
        # Implements retry logic and error handling
```

**Features:**
- Multi-page review extraction
- Headless Chrome operation
- Anti-detection techniques
- Robust error handling

### 2. Embedding Service
**File:** `products/embeddings.py`

```python
class EmbeddingService:
    """Manages vector embeddings in Pinecone"""
    
    def create_embeddings(self, product_id, text):
        # Split text into chunks (800 chars, 100 overlap)
        # Generate embeddings with OpenAI
        # Store in Pinecone with metadata
        # Returns vector count
```

**Process:**
1. Text chunking with RecursiveCharacterTextSplitter
2. Batch embedding generation (50 chunks/batch)
3. Upsert to Pinecone with product namespace
4. Metadata storage for retrieval

### 3. RAG Pipeline
**File:** `products/services.py`

```python
class QAService:
    """Handles question answering with RAG"""
    
    def get_answer(self, product_id, question, chat_history):
        # Query Pinecone for similar chunks (top-5)
        # Format context with chat history
        # Generate answer with Gemini
        # Cache result in Redis
```

**Flow:**
```
Question → Embed Query → Pinecone Search → Top-K Chunks
→ Format Prompt → Gemini LLM → Answer + Context
```

### 4. Async Task Processing
**File:** `products/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def scrape_and_embed_product(self, product_id):
    # 1. Scrape product data
    # 2. Save to PostgreSQL
    # 3. Generate embeddings
    # 4. Store in Pinecone
    # 5. Update product status
```

**Benefits:**
- Non-blocking operations
- Automatic retries on failure
- Progress tracking
- Concurrent processing

### 5. Database Schema

**Models:** `products/models.py`

```python
Product:
  - id (UUID)
  - url, title, brand, price
  - specifications (JSONB)
  - status (pending/scraping/embedding/completed/failed)
  - pinecone_namespace
  - vector_count

Review:
  - product (FK)
  - title, text, rating
  - customer_name, helpful_votes

ChatSession:
  - product (FK)
  - session_id
  
ChatMessage:
  - session (FK)
  - role (user/assistant)
  - content
  - context_chunks (JSONB)
```

---

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Test API
python test_api.py

# Coverage report
coverage run --source='.' manage.py test
coverage report
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Scraping Time | 2-5 min/product |
| Query Response | <2s (cached) |
| Concurrent Scraping | 10+ products |
| Embedding Dimension | 1536 (OpenAI) |
| Cache Hit Rate | ~60% |

---

## 🔒 Security

- Environment-based configuration
- CORS protection
- SQL injection prevention (Django ORM)
- Input validation (DRF serializers)
- HTTPS ready

---

## 📁 Project Structure

```
shopwise-ai/
├── amazon_qa_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── products/                   # Main application
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── tasks.py               # Celery tasks
│   ├── scraper.py             # Web scraper
│   ├── embeddings.py          # Vector operations
│   └── services.py            # RAG pipeline
├── frontend/                   # React application
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🛠️ Configuration

### Required Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=shopwise_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-your-key
GOOGLE_API_KEY=your-key
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-east-1-aws

# Selenium
CHROME_DRIVER_PATH=/path/to/chromedriver
HEADLESS_MODE=True
```

---

## 🐛 Known Limitations

- Currently supports Amazon.com only
- Scraping subject to website structure changes
- Rate limiting on heavy scraping loads
- Requires valid API keys for all services

---

## 🔄 Future Enhancements

- [ ] Multi-marketplace support (eBay, Walmart)
- [ ] Batch product import
- [ ] Advanced analytics dashboard
- [ ] GraphQL API
- [ ] Mobile application

---

## 📝 Development Notes

### Adding New Features

1. **New API Endpoint:**
   - Add view in `products/views.py`
   - Create serializer in `products/serializers.py`
   - Update `products/urls.py`

2. **New Celery Task:**
   - Define in `products/tasks.py`
   - Import in `products/__init__.py`

3. **Database Changes:**
   - Modify `products/models.py`
   - Run `python manage.py makemigrations`
   - Run `python manage.py migrate`

### Debugging

```bash
# Django shell
python manage.py shell

# Celery tasks
celery -A amazon_qa_project inspect active

# Redis data
redis-cli
> KEYS *
> GET key_name

# Database
python manage.py dbshell
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 👤 Author

**Saroj Mandal**

📧 sarojmandalrnp2004@gmail.com 
🔗 [LinkedIn](https://linkedin.com/in/saroj-mandal) | [GitHub](https://github.com/Saroj-jagadish-mandal)

---

## 🙏 Acknowledgments

- LangChain for RAG framework
- OpenAI for embeddings API
- Google for Gemini LLM
- Pinecone for vector database
- Django & DRF communities

---

**Built with Django, React, and AI** 🚀
