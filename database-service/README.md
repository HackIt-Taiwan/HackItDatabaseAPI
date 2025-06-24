# HackIt Database Service

A high-performance, secure database API service built with FastAPI and MongoDB.

## 🚀 Features

- **RESTful API** - Complete CRUD operations for user management
- **HMAC Authentication** - Military-grade security with SHA-256 signatures
- **MongoDB Integration** - Efficient data storage with MongoEngine
- **Auto-Documentation** - Interactive API docs with Swagger UI
- **Async Support** - High-performance asynchronous operations
- **Health Monitoring** - Built-in health checks and logging

## 📦 Installation

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file based on `.env.example`:

```env
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=hackit_db

# API Security
API_SECRET_KEY=your-very-secure-secret-key

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
```

## 🏃‍♂️ Running the Service

```bash
python main.py
```

The service will be available at:
- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📚 API Endpoints

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create new user |
| `GET` | `/users/{user_id}` | Get user by ID |
| `GET` | `/users/email/{email}` | Get user by email |
| `GET` | `/users/discord/{user_id}/{guild_id}` | Get user by Discord IDs |
| `PUT` | `/users/{user_id}` | Update user |
| `DELETE` | `/users/{user_id}` | Delete user |
| `POST` | `/users/query` | Query users with filters |
| `GET` | `/users/` | List users (paginated) |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/` | Service info |

## 🔐 Authentication

All requests require HMAC-SHA256 authentication:

```http
X-API-Timestamp: <unix_timestamp>
X-API-Signature: <hmac_signature>
```

Signature calculation:
```
HMAC-SHA256(api_secret, "METHOD:PATH:timestamp")
```

## 📖 Usage Examples

### Create User
```bash
curl -X POST "http://localhost:8001/users/" \
  -H "Content-Type: application/json" \
  -H "X-API-Timestamp: $(date +%s)" \
  -H "X-API-Signature: <calculated_signature>" \
  -d '{
    "user_id": 12345,
    "guild_id": 67890,
    "real_name": "John Doe",
    "email": "john@example.com"
  }'
```

### Get User by Email
```bash
curl -X GET "http://localhost:8001/users/email/john@example.com" \
  -H "X-API-Timestamp: $(date +%s)" \
  -H "X-API-Signature: <calculated_signature>"
```

## 🏗️ Architecture

```
app/
├── core/           # Configuration and database
├── models/         # MongoDB models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── routers/        # API routes
└── middleware/     # Authentication
```

## 🧪 Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Testing
```bash
# Health check
curl http://localhost:8001/health

# API documentation
open http://localhost:8001/docs
```

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "main.py"]
```

```bash
docker build -t hackit-database-service .
docker run -p 8001:8001 --env-file .env hackit-database-service
```

## 📊 Monitoring

The service includes comprehensive logging and monitoring:

- Request/response logging
- Error tracking
- Performance metrics
- Health check endpoint

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```
   Check MONGODB_URI in .env file
   Ensure MongoDB is running
   Verify network connectivity
   ```

2. **Authentication Errors**
   ```
   Verify API_SECRET_KEY matches client
   Check timestamp synchronization
   Validate signature calculation
   ```

3. **Port Already in Use**
   ```bash
   # Change port in .env or kill existing process
   lsof -ti:8001 | xargs kill -9
   ```

## 📄 License

MIT License - see LICENSE file for details. 