# HackIt Database Client

A Python client library for the HackIt Database Service, providing async HTTP operations with automatic authentication.

## 🚀 Features

- **Async HTTP Client** - High-performance async operations with httpx
- **Automatic Authentication** - Handles HMAC signature generation
- **Simple API** - Easy-to-use Python interface
- **Connection Pooling** - Efficient resource management
- **Error Handling** - Comprehensive exception handling
- **Context Manager** - Clean resource management
- **Type Hints** - Full typing support

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Quick Start

```python
from database_client import DatabaseClient

async def main():
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
        print(f"Created user: {new_user}")

# Run with asyncio
import asyncio
asyncio.run(main())
```

## 📚 API Reference

### DatabaseClient

#### Initialization
```python
client = DatabaseClient(
    base_url="http://localhost:8001",
    api_secret_key="your-secret-key"
)
```

#### User Operations

##### Create User
```python
user_data = {
    "user_id": 12345,
    "guild_id": 67890,
    "real_name": "John Doe",
    "email": "john@example.com",
    "source": "registration",
    "education_stage": "undergraduate"
}
result = await client.create_user(user_data)
```

##### Get User by Email
```python
user = await client.get_user_by_email("john@example.com")
if user["success"]:
    user_data = user["data"]
    print(f"User ID: {user_data['id']}")
    print(f"Name: {user_data['real_name']}")
```

##### Get User by ID
```python
user = await client.get_user_by_id("507f1f77bcf86cd799439011")
```

##### Get User by Discord IDs
```python
user = await client.get_user_by_discord_id(
    user_id=12345,
    guild_id=67890
)
```

##### Update User
```python
update_data = {
    "source": "magic_link",
    "education_stage": "graduate"
}
result = await client.update_user("507f1f77bcf86cd799439011", update_data)
```

##### Delete User
```python
result = await client.delete_user("507f1f77bcf86cd799439011")
```

##### Query Users
```python
query = {
    "guild_id": 67890,
    "limit": 20,
    "offset": 0
}
users = await client.query_users(query)
print(f"Found {len(users['data']['users'])} users")
```

##### List Users
```python
users = await client.list_users(limit=10, offset=0)
for user in users["data"]["users"]:
    print(f"{user['real_name']} - {user['email']}")
```

#### System Operations

##### Health Check
```python
health = await client.health_check()
print(f"Service status: {health['status']}")
```

### UserService (Backward Compatibility)

For projects migrating from direct MongoDB access:

```python
from database_client import DatabaseClient, UserService

async def main():
    db_client = DatabaseClient("http://localhost:8001", "secret-key")
    user_service = UserService(db_client)
    
    # Get user (returns None if not found)
    user = await user_service.get_user_by_email("john@example.com")
    if user:
        print(f"Found user: {user['real_name']}")
    
    # Update login info
    success = await user_service.update_user_login_info(
        user_id="507f1f77bcf86cd799439011",
        source="magic_link"
    )
    print(f"Update successful: {success}")
```

## 🔐 Authentication

The client automatically handles HMAC-SHA256 authentication:

1. **Timestamp Generation** - Current Unix timestamp
2. **Signature Creation** - HMAC-SHA256 of "METHOD:PATH:timestamp"
3. **Header Injection** - Adds X-API-Timestamp and X-API-Signature headers

Manual signature verification (for debugging):
```python
import hmac
import hashlib
import time

def create_signature(method, path, timestamp, secret):
    data = f"{method.upper()}:{path}"
    message = f"{data}:{timestamp}"
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

# Example
timestamp = int(time.time())
signature = create_signature("GET", "/users/email/test@example.com", timestamp, "secret")
print(f"Signature: {signature}")
```

## 🛠️ Framework Integration

### FastAPI Integration
```python
from fastapi import FastAPI, Depends, HTTPException
from database_client import DatabaseClient

app = FastAPI()

async def get_db_client():
    async with DatabaseClient("http://localhost:8001", "secret") as client:
        yield client

@app.get("/users/{email}")
async def get_user(email: str, db: DatabaseClient = Depends(get_db_client)):
    user = await db.get_user_by_email(email)
    if not user["success"]:
        raise HTTPException(status_code=404, detail="User not found")
    return user["data"]
```

### Django Integration
```python
from django.conf import settings
from database_client import DatabaseClient
import asyncio

class UserService:
    def __init__(self):
        self.client = DatabaseClient(
            settings.DATABASE_SERVICE_URL,
            settings.DATABASE_SERVICE_SECRET
        )
    
    def get_user_sync(self, email):
        """Synchronous wrapper for Django views"""
        return asyncio.run(self._get_user_async(email))
    
    async def _get_user_async(self, email):
        async with self.client as client:
            return await client.get_user_by_email(email)
```

### Flask Integration
```python
from flask import Flask, jsonify
from database_client import DatabaseClient
import asyncio

app = Flask(__name__)
db_client = DatabaseClient("http://localhost:8001", "secret")

@app.route('/users/<email>')
def get_user(email):
    async def _get_user():
        async with db_client as client:
            return await client.get_user_by_email(email)
    
    result = asyncio.run(_get_user())
    if result["success"]:
        return jsonify(result["data"])
    return jsonify({"error": "User not found"}), 404
```

## 🧪 Testing

### Unit Tests
```python
import pytest
from database_client import DatabaseClient

@pytest.mark.asyncio
async def test_health_check():
    async with DatabaseClient("http://localhost:8001", "test-key") as client:
        result = await client.health_check()
        assert result["status"] == "healthy"

@pytest.mark.asyncio
async def test_get_user_not_found():
    async with DatabaseClient("http://localhost:8001", "test-key") as client:
        result = await client.get_user_by_email("nonexistent@example.com")
        assert not result["success"]
```

### Mock Testing
```python
import pytest
from unittest.mock import AsyncMock, patch
from database_client import DatabaseClient

@pytest.mark.asyncio
async def test_create_user_mock():
    with patch('httpx.AsyncClient.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"success": True, "data": {"id": "123"}}
        mock_response.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response
        
        async with DatabaseClient("http://test", "secret") as client:
            result = await client.create_user({"email": "test@example.com"})
            assert result["success"]
```

## 🔧 Error Handling

### Exception Types
```python
import httpx
from database_client import DatabaseClient

async def handle_errors():
    try:
        async with DatabaseClient("http://localhost:8001", "secret") as client:
            user = await client.get_user_by_email("test@example.com")
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("User not found")
        elif e.response.status_code == 401:
            print("Authentication failed")
        else:
            print(f"HTTP error: {e.response.status_code}")
    
    except httpx.RequestError as e:
        print(f"Connection error: {e}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Retry Logic
```python
import asyncio
from database_client import DatabaseClient

async def get_user_with_retry(email, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with DatabaseClient("http://localhost:8001", "secret") as client:
                return await client.get_user_by_email(email)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## 📊 Performance Tips

### Connection Reuse
```python
# Good: Reuse client instance
client = DatabaseClient("http://localhost:8001", "secret")
async with client as c:
    user1 = await c.get_user_by_email("user1@example.com")
    user2 = await c.get_user_by_email("user2@example.com")

# Bad: Create new client for each request
for email in emails:
    async with DatabaseClient("http://localhost:8001", "secret") as client:
        user = await client.get_user_by_email(email)
```

### Batch Operations
```python
async def get_multiple_users(emails):
    async with DatabaseClient("http://localhost:8001", "secret") as client:
        tasks = [client.get_user_by_email(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

## 📄 License

MIT License - see LICENSE file for details. 