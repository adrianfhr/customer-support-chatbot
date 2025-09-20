# Customer Support Chatbot

Sistem chatbot customer support berbasis AI untuk toko online sederhana. Menggunakan Python, LangChain, Ollama (llama3.2:3b), FastAPI, PostgreSQL, dan Docker untuk deployment lokal yang mudah.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (untuk development lokal)
- Minimal 4GB RAM (untuk model Ollama)
- 5GB disk space (untuk model dan containers)

### Installation & Run

1. Clone repository dan masuk ke direktori:
```bash
git clone <repository-url>
cd customer-support-chatbot
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Jalankan semua service:
```bash
docker compose up -d
```

4. Tunggu hingga Ollama selesai download model (pertama kali, ~2GB):
```bash
docker compose logs -f ollama
# Tunggu hingga muncul "llama3.2:3b successfully loaded"
```

5. Test API:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-1", "user_message": "Halo, saya butuh bantuan"}'
```

6. Verifikasi semua services running:
```bash
docker compose ps
# Semua services harus UP
```

## Struktur Project

```
customer-support-chatbot/
├── README.md                 # Dokumentasi ini
├── pyproject.toml           # Konfigurasi Python & dependencies
├── docker-compose.yml       # Multi-service container setup
├── Dockerfile              # Container image definition
├── .env.example            # Template environment variables
├── app/                    # Source code aplikasi
│   ├── main.py            # FastAPI app entry point
│   ├── api/               # REST API layer
│   │   ├── routes.py      # API endpoints
│   │   └── schemas.py     # Request/response models
│   ├── core/              # Business logic layer
│   │   ├── chat_service.py # Chat orchestration
│   │   ├── memory.py      # Conversation memory management
│   │   └── tools.py       # LangChain tools implementation
│   ├── llm/               # LLM integration layer
│   │   ├── prompts.py     # System prompts & templates
│   │   └── chain.py       # Ollama + LangChain setup
│   └── db/                # Database layer
│       ├── models.py      # SQLAlchemy ORM models
│       └── session.py     # Database session management
├── db/                     # Database setup
│   ├── schema.sql         # DDL untuk PostgreSQL
│   └── seed.sql           # Sample data untuk testing
└── tests/                  # Test suite
    └── test_chat_api.py   # Comprehensive tests
```

## Fitur Utama

### Intents yang Didukung

1. **Status Pesanan**: "Di mana pesanan saya? ID: ORD123"
   - Tool: `get_order_status(order_id)`
   - Mencari status pesanan dari database

2. **Info Produk**: "Apa kelebihan produk Laptop Gaming X?"
   - Mengambil features produk dari database
   - Menampilkan spesifikasi dan keunggulan

3. **Klaim Garansi**: "Bagaimana cara klaim garansi?"
   - Menampilkan langkah-langkah policy garansi
   - Informasi kontak dan prosedur

### Memory & Personalisasi
- Menyimpan 3 interaksi terakhir per session
- Context aware conversations
- Persistent history di PostgreSQL

## Contoh Interaksi

### 1. Cek Status Pesanan
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "user_message": "Di mana pesanan saya? ID: ORD123"
  }'
```

**Response:**
```json
{
  "message": "Pesanan ORD123 sedang dalam pengiriman via JNE dengan nomor resi JNE123456789 dengan estimasi tiba 18 September 2025. Terakhir diupdate: 16 September 2025 pukul 14:30. Ringkas: Pesanan Anda sedang dikirim dan akan tiba dalam 2 hari.",
  "session_id": "user123",
  "turn_index": 1,
  "tool_calls": ["get_order_status"],
  "timestamp": "2025-09-16T10:30:05Z"
}
```

### 2. Info Produk
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123", 
    "user_message": "Apa kelebihan Laptop Gaming X?"
  }'
```

### 3. Klaim Garansi
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "user_message": "Bagaimana cara klaim garansi?"
  }'
```

## 🧪 Testing & Validation

### Postman Collection Setup

Kami menyediakan Postman collection komprehensif untuk testing semua aspek Customer Support Chatbot API. Collection ini mencakup 16 test scenarios yang mencakup health checks, chat conversations, session management, error handling, dan performance testing.

#### Files yang Dibuat
- `Customer_Support_Chatbot_API.postman_collection.json` - Main collection
- `Customer_Support_Chatbot.postman_environment.json` - Environment config
- `POSTMAN_TESTING_GUIDE.md` - Detailed guide
- `POSTMAN_QUICK_REFERENCE.md` - Quick reference

#### Quick Start (3 Steps)

1. **Import ke Postman**
   ```
   File → Import → Select both JSON files → Import
   ```

2. **Set Environment**
   ```
   Top-right dropdown → Select "Customer Support Chatbot Environment"
   ```

3. **Run Tests**
   ```
   Right-click collection → Run collection → Run
   ```

### Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| 🔍 **Health & Status** | 2 | API health, documentation |
| 💬 **Chat Conversations** | 6 | Core chatbot functionality |
| 📝 **Session Management** | 2 | Message history |
| 📦 **Data Management** | 1 | Seed test data |
| ❌ **Error Handling** | 3 | Input validation |
| ⚡ **Performance** | 2 | Load & response time |

**Total: 16 comprehensive tests**

### Key Test Scenarios

#### ✅ Happy Path Testing
```json
POST /chat
{
  "session_id": "test-123",
  "user_message": "Check my order ID: ORD555"
}
```

#### ✅ Tool Calling Validation
- **Order Status**: "Where is my order ORD123?"
- **Product Info**: "Apa kelebihan laptop ROG Strix?"
- **Warranty**: "Bagaimana cara klaim garansi?"

#### ❌ Error Cases
- Missing session_id → 422 error
- Empty message → 422 error
- Invalid JSON → 400 error

### Automated Tests

Setiap request dilengkapi dengan automated tests yang mengecek:

#### Status Code Validation
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

#### Response Structure Validation
```javascript
pm.test("Response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('session_id');
});
```

#### Business Logic Validation
```javascript
pm.test("Tool was called", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.tool_calls).to.include('get_order_status');
});
```

#### Performance Validation
```javascript
pm.test("Response time is reasonable", function () {
    pm.expect(pm.response.responseTime).to.be.below(30000);
});
```

### Pre-Test Checklist

- [ ] Docker containers running (`docker-compose ps`)
- [ ] All services healthy (app, db, ollama)
- [ ] Port 8000 accessible (`curl localhost:8000/healthz`)
- [ ] Environment selected in Postman
- [ ] Test data seeded (run "Seed Test Orders" first)

### Expected Test Results

#### ✅ Successful Scenarios
- Health Check: ✅ Status 200, response structure valid
- Chat Greeting: ✅ Status 200, Indonesian fallback response
- Order Query (Valid): ✅ Status 200, tool called, order info returned
- Product Query: ✅ Status 200, tool called, product response
- Warranty Query: ✅ Status 200, tool called, detailed policy returned
- Session Messages: ✅ Status 200, message history retrieved

#### ❌ Error Scenarios
- Missing Session ID: ❌ Status 422, validation error
- Missing Message: ❌ Status 422, validation error
- Empty Message: ❌ Status 422, validation error

#### ⚡ Performance Expectations
- Normal requests: < 15 seconds
- Long messages: < 30 seconds
- Order lookups: < 10 seconds

### Advanced Usage

#### Collection Runner Settings
- **Iterations**: 1 (normal), 5+ (stress test)
- **Delay**: 100ms between requests
- **Data file**: Use for bulk testing
- **Environment**: Always use provided environment

#### Variables Available
- `{{base_url}}` - API base URL
- `{{session_id}}` - Auto-generated unique session
- `{{$randomInt}}` - Random number generator

### Quick Fixes

#### Connection Issues
```bash
cd /path/to/project
docker-compose down
docker-compose up -d
```

#### Slow Responses
```bash
docker-compose logs app --tail=20
# Check for errors, restart if needed
```

#### Test Failures
1. Check environment is selected
2. Verify base_url is correct
3. Run "Health Check" first
4. Seed test data if needed

### Emergency Commands

```bash
# Restart everything
docker-compose restart

# Check logs
docker-compose logs app

# Test manually
curl http://localhost:8000/healthz

# Check API docs
curl http://localhost:8000/docs
```

## 🛠️ API Endpoints

### POST /chat
Mengirim pesan ke chatbot.

**Request:**
```json
{
  "session_id": "demo-session",
  "user_message": "Di mana pesanan saya? ID: ORD123"
}
```

**Response:**
```json
{
  "message": "Pesanan ORD123 sedang dalam pengiriman via JNE dengan estimasi tiba 2 hari. Tracking: JNE123456789. Ringkas: Pesanan Anda dalam perjalanan dan akan tiba dalam 2 hari.",
  "session_id": "demo-session",
  "turn_index": 1,
  "tool_calls": ["get_order_status"],
  "timestamp": "2025-09-16T10:30:00Z"
}
```

### GET /sessions/{session_id}/messages
Mengambil history percakapan.

**Response:**
```json
{
  "session_id": "demo-session",
  "messages": [
    {
      "role": "user",
      "content": "Di mana pesanan saya? ID: ORD123",
      "turn_index": 1,
      "timestamp": "2025-09-16T10:30:00Z"
    },
    {
      "role": "assistant", 
      "content": "Pesanan ORD123 sedang dalam pengiriman...",
      "turn_index": 1,
      "timestamp": "2025-09-16T10:30:05Z"
    }
  ]
}
```

### GET /healthz
Health check endpoint untuk monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-16T10:30:00Z",
  "version": "1.0.0"
}
```

### POST /orders/seed (Optional)
Menambah data demo untuk testing dan development.

**Request:**
```json
{
  "orders": [
    {
      "id": "ORD999",
      "user_id": "testuser",
      "status": "shipped",
      "carrier": "JNE",
      "tracking_number": "JNE999888777"
    }
  ]
}
```

## 🗄️ Database Design

### Tables

**messages**
- `id` (UUID, PK)
- `session_id` (String, Indexed)
- `role` (user/assistant)
- `content` (Text)
- `turn_index` (Integer, Indexed)
- `created_at` (Timestamp)

**orders**
- `id` (String, PK)
- `user_id` (String)
- `status` (String)
- `last_update_at` (Timestamp)
- `eta_date` (Date)
- `carrier` (String)
- `tracking_number` (String)

**products**
- `id` (String, PK)
- `name` (String)
- `features` (Text)
- `price` (Decimal)
- `stock` (Integer)

**policies**
- `id` (UUID, PK)
- `type` (String, Indexed)
- `content_markdown` (Text)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### Relationships & Indexes
- messages ↔ sessions (1:N) dengan index pada session_id + turn_index
- orders ↔ users (1:N) dengan index pada user_id dan status
- products dengan index pada name untuk pencarian cepat
- policies dengan index pada type untuk lookup cepat

### Database Schema Location
- **Schema DDL**: `db/schema.sql` (PostgreSQL compatible)
- **Sample Data**: `db/seed.sql` (demo orders, products, policies)

## Tech Stack

### Core Dependencies
- **Python**: Base language
- **FastAPI**: REST API framework
- **LangChain**: LLM orchestration
- **langchain-community**: Ollama integration
- **SQLAlchemy**: ORM & database
- **psycopg2-binary + asyncpg**: PostgreSQL adapters (sync/async)
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **structlog**: Structured logging

### Development & Quality
- **pytest**: Testing framework
- **ruff**: Linting
- **black**: Code formatting  
- **mypy**: Type checking
- **tenacity**: Retry logic
- **python-dotenv**: Environment management

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **PostgreSQL 15**: Primary database
- **Ollama**: Local LLM serving
- **llama3.2:3b**: Language model

## Model & LLM

**Model**: `llama3.2:3b`
- Size: ~2GB download
- Locally hosted via Ollama
- Temperature: 0.4 (balanced creativity/consistency)
- Context window: 8K tokens
- Response limit: <180 words

**Mengapa llama3.2:3b?**
- Optimal balance size vs performance
- Good Indonesian language support  
- Fast inference on modest hardware
- Strong tool calling capabilities
- Meta's latest 3B parameter model

## 🔧 Tools & Functions

### 1. get_order_status(order_id: str)
**Trigger**: Query tentang status pesanan dengan ID
**Function**: Mencari order dari database, return status, tracking, ETA
**Example**: "ORD123 sedang dikirim via JNE, estimasi 2 hari"

### 2. get_product_info(product_name: str)  
**Trigger**: Query tentang spesifikasi/kelebihan produk
**Function**: Mencari produk by name/ID, return features & price
**Example**: "Laptop Gaming X memiliki RTX 4060, RAM 16GB..."

### 3. get_warranty_policy()
**Trigger**: Query tentang prosedur garansi/klaim
**Function**: Return policy steps dari database
**Example**: "1. Siapkan nota pembelian, 2. Hubungi CS..."


## Troubleshooting

### Ollama Model Download
Jika model belum terdownload:
```bash
docker compose exec ollama ollama pull llama3.2:3b
```

### Database Connection Issues
Pastikan PostgreSQL service running:
```bash
docker compose ps
docker compose logs db
```

### Reset Database (menghapus semua data)
```bash
docker compose down -v
docker compose up -d
```

### Memory Issues
Jika container kehabisan memory:
```bash
# Check resource usage
docker stats

# Increase Docker memory limit atau restart services
docker compose restart
```

### Port Conflicts
Jika port 8000/11434/5432 sudah digunakan:
```bash
# Edit docker-compose.yml untuk menggunakan port lain
# Contoh: "8001:8000" untuk FastAPI
```

## Security & Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string  
- `OLLAMA_HOST`: Ollama service endpoint
- `LOG_LEVEL`: Logging verbosity
- `CORS_ORIGINS`: Allowed origins

### CORS
Default: `http://localhost:3000,http://localhost:8080`

### Logging
Structured JSON logs untuk production monitoring.

## Performance & Limitations

### Current Limits
- Memory: 3 exchanges per session
- Response: <180 words
- Concurrent users: ~10-20 (single container)
- Model: Indonesian + English support

### Known Issues
- Tool calling latency: 2-5s
- Cold start: 10-15s (first request)
- Memory usage: ~2GB (Ollama model)


## Development

### Local Setup (Development tanpa Docker)
```bash
# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Setup PostgreSQL lokal (atau gunakan SQLite)
export DATABASE_URL="sqlite+aiosqlite:///./chatbot.db"
export OLLAMA_HOST="http://localhost:11434"

# Install dan jalankan Ollama lokal
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.2:3b

# Run aplikasi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linting & formatting
ruff check . --fix
black .
mypy .
```

### Adding New Tools
1. Define function in `app/core/tools.py` dengan proper type hints
2. Register dalam `app/llm/chain.py` pada method `get_tools()`
3. Add test cases in `tests/test_chat_api.py`
4. Update system prompt in `app/llm/prompts.py` jika diperlukan
5. Update documentation di README

### Environment Variables
Semua konfigurasi via environment variables di `.env`:
```bash
# Database
DATABASE_URL=postgresql://app:app@db:5432/chatbot

# LLM
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
LLM_TEMPERATURE=0.4

# API
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
MAX_MEMORY_EXCHANGES=3
MAX_RESPONSE_WORDS=180
```

---

## 📋 Quick Reference

### Essential Commands
```bash
# Start system
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f [service_name]

# Stop system
docker compose down

# Reset everything
docker compose down -v && docker compose up -d

# Run tests
docker compose exec app pytest -v

# Access database
docker compose exec db psql -U app -d chatbot
```

### API Endpoints
- **POST /chat** - Send message to chatbot
- **GET /sessions/{id}/messages** - Get conversation history  
- **GET /healthz** - Health check
- **POST /orders/seed** - Add demo data

### Supported Intents
1. **"Di mana pesanan saya? ID: ORD123"** → Order status lookup
2. **"Apa kelebihan produk X?"** → Product information
3. **"Bagaimana cara klaim garansi?"** → Warranty policy

### Key Features
- 3-exchange conversation memory
- Indonesian language support
- Tool calling for data lookups
- PostgreSQL persistence
- Docker containerization
- Comprehensive testing
- Structured logging

**Tim & Support**: Untuk pertanyaan teknis atau bug reports, silakan buat issue di repository atau hubungi tim development.

