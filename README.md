# HackIt Database Service

A centralized database API service for the HackIt organization that provides unified database operations through RESTful APIs, eliminating direct MongoDB model dependencies across multiple projects.

## 🏗️ Architecture Overview

This project solves the problem of tight coupling between multiple HackIt projects and MongoDB models by providing a centralized database service with a clean API interface.

```
hackit-database/
├── database-service/          # 🏗️ Centralized Database API Service
│   ├── app/
│   │   ├── core/             # ⚙️ Core configuration and database connection
│   │   ├── models/           # 📊 Data models (RegisteredUser)
│   │   ├── schemas/          # 📋 Pydantic validation schemas
│   │   ├── services/         # 💼 Business logic services
│   │   ├── routers/          # 🛣️ API routes
│   │   └── middleware/       # 🔐 Authentication middleware
│   ├── main.py               # 🚀 Service entry point
│   └── requirements.txt      # 📦 Dependencies
└── database-client/          # 📡 Python client library
    ├── __init__.py
    ├── client.py             # 🌐 HTTP client
    └── requirements.txt
```

## ✨ Key Features

### 🏗️ Database Service
- **Complete RESTful CRUD Operations** - Full user management API
- **Military-Grade Security** - HMAC-SHA256 signature authentication
- **Domain Whitelisting** - Secure access control for HackIt subdomains
- **Comprehensive User Management** - Create, read, update, delete operations
- **Advanced Querying** - Search, filtering, and pagination support
- **Auto-Generated Documentation** - Interactive API docs with Swagger UI
- **Health Monitoring** - Built-in health checks and logging

### 📡 Python Client Library
- **Async HTTP Client** - High-performance async operations
- **Automatic Authentication** - Handles HMAC signature generation
- **Simple Interface** - Easy-to-use Python API
- **Connection Pooling** - Efficient resource management
- **Error Handling** - Comprehensive exception handling
- **Context Manager Support** - Clean resource management

## 🚀 Quick Start

### 1. Start the Database Service

```bash
cd database-service/
cp .env.example .env
# Edit .env with your MongoDB connection and API secret
pip install -r requirements.txt
python main.py
```

The service will start at `http://localhost:8001`

### 2. View API Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

### 3. Use the Python Client

```bash
cd database-client/
pip install -r requirements.txt
```

```python
from database_client import DatabaseClient

async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
    # Get user by email
    user = await client.get_user_by_email("user@example.com")
    if user["success"]:
        print(f"Found user: {user['data']['real_name']}")
    
    # Create new user
    new_user = await client.create_user({
        "user_id": 12345,
        "guild_id": 67890,
        "real_name": "John Doe",
        "email": "john@example.com"
    })
```

## 🔐 Security Features

### HMAC Signature Authentication
- **Algorithm**: HMAC-SHA256
- **Timestamp Protection**: 5-minute window to prevent replay attacks
- **Signature Format**: `HMAC-SHA256(secret, "METHOD:PATH:timestamp")`

### Request Headers
```http
X-API-Timestamp: <unix_timestamp>
X-API-Signature: <hmac_sha256_signature>
Content-Type: application/json
```

### Domain Whitelisting
- Production: `hackit.tw`, `*.hackit.tw`
- Development: `localhost`, `127.0.0.1:*`

## 📖 API Reference

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/{user_id}` | Get user by MongoDB ObjectId |
| `GET` | `/users/email/{email}` | Get user by email address |
| `GET` | `/users/discord/{user_id}/{guild_id}` | Get user by Discord IDs |
| `PUT` | `/users/{user_id}` | Update user information |
| `DELETE` | `/users/{user_id}` | Delete user |
| `POST` | `/users/query` | Query users with filters |
| `GET` | `/users/` | List users with pagination |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/` | Service information |

## 🛠️ Configuration

### Database Service (.env)
```env
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=hackit_db

# API Security
API_SECRET_KEY=your-secret-key-here

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
```

### Client Usage
```python
from database_client import DatabaseClient

client = DatabaseClient(
    base_url="http://localhost:8001",
    api_secret_key="your-secret-key"
)
```

## 🔄 Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI, Depends
from database_client import DatabaseClient

app = FastAPI()

def get_db_client():
    return DatabaseClient("http://localhost:8001", "secret")

@app.get("/users/{email}")
async def get_user(email: str, db: DatabaseClient = Depends(get_db_client)):
    async with db as client:
        return await client.get_user_by_email(email)
```

### Django Integration
```python
from django.conf import settings
from database_client import DatabaseClient

class UserService:
    def __init__(self):
        self.client = DatabaseClient(
            settings.DATABASE_SERVICE_URL,
            settings.DATABASE_SERVICE_SECRET
        )
    
    async def get_user(self, email):
        async with self.client as client:
            return await client.get_user_by_email(email)
```

## 🧪 Testing

### Test the Service
```bash
# Health check
curl http://localhost:8001/health

# Get API documentation
curl http://localhost:8001/docs

# Test user endpoint (with proper authentication)
curl -X GET "http://localhost:8001/users/email/test@example.com" \
  -H "X-API-Timestamp: $(date +%s)" \
  -H "X-API-Signature: <calculated_signature>"
```

### Unit Testing
```python
import pytest
from database_client import DatabaseClient

@pytest.mark.asyncio
async def test_get_user():
    async with DatabaseClient("http://localhost:8001", "test-key") as client:
        result = await client.health_check()
        assert result["status"] == "healthy"
```

## 📊 Monitoring & Logging

### Health Monitoring
- **Endpoint**: `GET /health`
- **Response**: Service status and version
- **Metrics**: Database connectivity, service uptime

### Logging Features
- Structured logging with timestamps
- Request/response tracking
- Error handling and reporting
- Security event logging

## 🚀 Deployment

### Docker Deployment
```dockerfile
# Dockerfile for database-service
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  database-service:
    build: ./database-service
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/
      - MONGODB_DATABASE=hackit_db
    depends_on:
      - mongo
  
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
```

### Production Considerations
- Use environment variables for secrets
- Enable HTTPS in production
- Implement rate limiting
- Set up monitoring and alerting
- Use a reverse proxy (nginx/traefik)

## 🔮 Roadmap

### Planned Features
- [ ] **Database Read/Write Splitting** - Separate read and write operations
- [ ] **Multi-tenancy Support** - Support multiple organizations
- [ ] **Caching Layer** - Redis integration for performance
- [ ] **Audit Logging** - Track all database operations
- [ ] **Data Migration Tools** - Easy schema migrations
- [ ] **Grafana Dashboard** - Advanced monitoring

### Architecture Improvements
- [ ] **Kubernetes Deployment** - Cloud-native deployment
- [ ] **Load Balancing** - High availability setup
- [ ] **Auto-scaling** - Dynamic resource allocation
- [ ] **Circuit Breaker** - Fault tolerance patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a Pull Request

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd hackit-database

# Setup database service
cd database-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup client library
cd ../database-client
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Documentation**: Check the `/docs` endpoint when service is running
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Contact**: Reach out to the HackIt development team

---

**⚠️ Important**: This is a major architectural change. Please test thoroughly before deploying to production environments.

## 🏷️ Version History

- **v1.0.0** - Initial release with complete CRUD operations
- User management API with HMAC authentication
- Python client library with async support
- Comprehensive documentation and examples 