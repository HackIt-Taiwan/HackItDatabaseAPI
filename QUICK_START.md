# HackIt Database Service v1.1.0 - Quick Start Guide

Welcome to the enhanced HackIt Database Service! This guide will help you get up and running with the new features and improvements.

## 🚀 What's New in v1.1.0

- **🔐 Military-grade Security**: HMAC-SHA256 authentication with rate limiting
- **🏗️ Extensible Architecture**: Base classes for easy model/service extension
- **🔍 Advanced Search**: Powerful querying and filtering capabilities
- **🏷️ Tag System**: Flexible user categorization
- **📊 Analytics**: Comprehensive user statistics
- **🔄 Bulk Operations**: Efficient mass updates
- **👥 User Management**: Complete lifecycle management
- **📱 Public/Private Data**: Separate endpoints for different access levels
- **⚡ 22 API Endpoints**: Complete user management suite

## 📋 Prerequisites

- Python 3.11+
- MongoDB 5.0+
- Docker & Docker Compose (optional)

## 🏃‍♂️ Quick Start (5 minutes)

### 1. Clone and Setup

```bash
git clone <repository>
cd hackit-database
cp .env.example .env
```

### 2. Edit Configuration

Edit `.env` file:
```bash
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=hackit_db

# API Security
API_SECRET_KEY=your-super-secret-key-here

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
ENVIRONMENT=development
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
make start

# Or manually
docker-compose up -d
```

### 4. Start Manually (Alternative)

```bash
# Install dependencies
cd database-service
pip install -r requirements.txt

# Start MongoDB (separate terminal)
mongod

# Start the service
python main.py
```

### 5. Verify Installation

```bash
# Check health
curl http://localhost:8001/health

# View documentation
open http://localhost:8001/docs
```

## 🧪 Test the API

Run the comprehensive test suite:

```bash
# Test all endpoints
python test_api.py

# Run feature demo
python demo_usage.py
```

## 🔧 Basic Usage Examples

### Create a User

```python
from database_client import DatabaseClient

async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
    user_data = {
        "user_id": 123456789,
        "guild_id": 987654321,
        "real_name": "John Doe",
        "email": "john@example.com",
        "bio": "Software developer from Taiwan",
        "location": "Taipei",
        "github_username": "johndoe",
        "tags": ["developer", "python"]
    }
    
    result = await client.create_user(user_data)
    if result["success"]:
        print(f"User created: {result['data']['id']}")
```

### Advanced Search

```python
# Search with multiple filters
query = {
    "is_active": True,
    "tag": "developer",
    "location": "Taipei",
    "limit": 10,
    "order_by": "-registered_at"
}

result = await client.query_users(query)
print(f"Found {len(result['data'])} developers in Taipei")
```

### Tag Management

```python
# Add tags
await client.add_user_tag(user_id, "hackathon-winner")

# Find users by tag
developers = await client.get_users_by_tag("developer")
```

### Analytics

```python
# Get comprehensive statistics
stats = await client.get_user_statistics()
print(f"Total users: {stats['data']['total_users']}")
print(f"Active users: {stats['data']['active_users']}")
```

## 📚 Available Commands

```bash
make help          # Show all available commands
make start         # Start all services
make stop          # Stop all services
make logs          # View logs
make test          # Run health checks
make dev           # Start in development mode
make clean         # Clean up containers
```

## 🔗 API Endpoints Overview

### User Management
- `POST /users/` - Create user
- `GET /users/{id}` - Get user details
- `GET /users/{id}/public` - Get public info
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Search & Query
- `POST /users/query` - Advanced search
- `GET /users/` - List with pagination
- `GET /users/search/name/{name}` - Search by name
- `GET /users/email/{email}` - Get by email
- `GET /users/discord/{user_id}/{guild_id}` - Get by Discord

### Tag Management
- `POST /users/{id}/tags` - Add tag
- `DELETE /users/{id}/tags` - Remove tag
- `GET /users/tag/{tag}` - Get users by tag

### User Status
- `PATCH /users/{id}/activate` - Activate user
- `PATCH /users/{id}/deactivate` - Deactivate user
- `PATCH /users/{id}/login` - Update login time

### Analytics
- `GET /users/analytics/statistics` - User statistics
- `PUT /users/bulk` - Bulk operations

### System
- `GET /health` - Health check
- `GET /` - Service info

## 🔐 Authentication

All requests require HMAC-SHA256 authentication:

```python
# Headers required
{
    "X-API-Timestamp": "1640995200",
    "X-API-Signature": "hmac_sha256_signature",
    "Content-Type": "application/json"
}
```

The client library handles this automatically.

## 🏗️ Adding New Models (For Developers)

Thanks to the new architecture, adding models is simple:

### 1. Create Model

```python
# app/models/project.py
from app.core.base import BaseModel
from mongoengine import StringField, IntField

class Project(BaseModel):
    name = StringField(required=True)
    description = StringField()
    user_count = IntField(default=0)
```

### 2. Create Service

```python
# app/services/project_service.py
from app.core.base import BaseService
from app.models.project import Project

class ProjectService(BaseService):
    @classmethod
    def get_model_class(cls):
        return Project
```

### 3. Add Routes

```python
# app/routers/projects.py
from app.services.project_service import ProjectService

@router.post("/")
async def create_project(project_data: ProjectCreate):
    project = ProjectService.create(project_data.dict())
    # ... rest of implementation
```

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check if port is in use
netstat -an | grep 8001

# Check MongoDB connection
mongo --eval "db.adminCommand('ismaster')"

# View detailed logs
docker-compose logs database-service
```

### Authentication Errors
- Verify API secret key in both service and client
- Check system time (HMAC is time-sensitive)
- Ensure proper headers are sent

### Database Issues
```bash
# Reset database
make clean
docker-compose up -d mongo
```

## 📖 Documentation

- **Interactive API Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Full API Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_api.py`
5. Submit a pull request

## 📞 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check API docs at `/docs`
- **Demo**: Run `python demo_usage.py`

---

🎉 **You're ready to go!** The enhanced HackIt Database Service provides enterprise-grade functionality with developer-friendly APIs.

For detailed information about all features, see the [complete documentation](./API_DOCUMENTATION.md). 