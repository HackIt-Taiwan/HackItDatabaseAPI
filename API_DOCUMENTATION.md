# HackIt Database Service - Complete API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base Response Format](#base-response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [User Management API](#user-management-api)
7. [User Status Management](#user-status-management)
8. [Tag Management](#tag-management)
9. [Search and Query Operations](#search-and-query-operations)
10. [Analytics and Statistics](#analytics-and-statistics)
11. [Bulk Operations](#bulk-operations)
12. [System Operations](#system-operations)
13. [Client Library Usage](#client-library-usage)
14. [Examples and Use Cases](#examples-and-use-cases)

---

## Overview

The HackIt Database Service provides a centralized, secure, and scalable API for managing user data across the HackIt organization. This service eliminates direct database dependencies and provides a consistent interface for all user-related operations.

### Base URL
- **Development**: `http://localhost:8001`
- **Production**: `https://api.hackit.tw`

### API Version
- **Current Version**: v1.1.0
- **API Stability**: Stable

### Features
- 🔐 **HMAC-SHA256 Authentication** - Military-grade security
- 🚀 **Complete CRUD Operations** - Full user management
- 🔍 **Advanced Search & Filtering** - Powerful query capabilities
- 📊 **Analytics & Statistics** - User insights and metrics
- 🏷️ **Tag Management** - Flexible user categorization
- 📱 **Mobile-Friendly** - Responsive API design

---

## Authentication

### HMAC-SHA256 Signature Authentication

All API requests must be authenticated using HMAC-SHA256 signatures to ensure security and prevent unauthorized access.

#### Required Headers

```http
X-API-Timestamp: <unix_timestamp>
X-API-Signature: <hmac_sha256_signature>
Content-Type: application/json
```

#### Signature Generation

1. **Create Message String**: `METHOD:PATH:timestamp`
2. **Generate HMAC**: `HMAC-SHA256(secret_key, message)`
3. **Include in Header**: Add as `X-API-Signature`

#### Example Signature Generation (Python)

```python
import hmac
import hashlib
import time

def create_signature(method, path, secret_key):
    timestamp = int(time.time())
    message = f"{method.upper()}:{path}:{timestamp}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'X-API-Timestamp': str(timestamp),
        'X-API-Signature': signature
    }

# Usage
headers = create_signature('GET', '/users/', 'your-secret-key')
```

#### Security Features

- **Timestamp Validation**: 5-minute validity window to prevent replay attacks
- **Constant-Time Comparison**: Prevents timing attacks
- **Rate Limiting**: Configurable request rate limiting
- **Domain Validation**: Host header validation in production

---

## Base Response Format

All API responses follow a consistent structure for easy parsing and error handling.

### Success Response

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Paginated Response

```json
{
    "success": true,
    "message": "Users retrieved successfully",
    "data": [
        // Array of user objects
    ],
    "pagination": {
        "total": 100,
        "limit": 10,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Response

```json
{
    "success": false,
    "message": "User not found",
    "error_code": "USER_NOT_FOUND",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| `200` | OK | Successful GET, PUT, PATCH requests |
| `201` | Created | Successful POST requests |
| `400` | Bad Request | Invalid request data, validation errors |
| `401` | Unauthorized | Invalid or missing authentication |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists, unique constraint violation |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side errors |

### Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `VALIDATION_ERROR` | Request data validation failed | Check request format and required fields |
| `USER_NOT_FOUND` | Requested user does not exist | Verify user ID or search criteria |
| `USER_ALREADY_EXISTS` | User with same identifier exists | Check for existing users before creation |
| `AUTHENTICATION_FAILED` | Invalid authentication credentials | Verify API signature and timestamp |
| `RATE_LIMIT_EXCEEDED` | Too many requests in time window | Implement request throttling |
| `INTERNAL_ERROR` | Server-side error occurred | Contact support if persistent |

---

## Rate Limiting

### Default Limits
- **Requests per minute**: 100 (configurable)
- **Burst allowance**: 10 additional requests
- **Rate limit window**: 60 seconds

### Rate Limit Headers

```http
X-Remaining-Requests: 95
X-Rate-Limit-Reset: 1642248600
```

### Rate Limit Exceeded Response

```json
{
    "success": false,
    "message": "Rate limit exceeded",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## User Management API

### User Data Model

```json
{
    "id": "507f1f77bcf86cd799439011",
    "user_id": 123456789,
    "guild_id": 987654321,
    "real_name": "John Doe",
    "email": "john.doe@example.com",
    "source": "registration_form",
    "education_stage": "university",
    "avatar_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "bio": "Software developer and open source enthusiast",
    "location": "Taipei, Taiwan",
    "website": "https://johndoe.dev",
    "github_username": "johndoe",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "is_active": true,
    "is_verified": false,
    "tags": ["developer", "python", "backend"],
    "registered_at": "2024-01-15T08:30:00.000Z",
    "last_updated": "2024-01-15T10:30:00.000Z",
    "last_login": "2024-01-15T09:45:00.000Z",
    "display_name": "John Doe",
    "profile_completeness": 85.5
}
```

### 1. Create User

Create a new user account with profile information.

**Endpoint**: `POST /users/`

**Request Body**:
```json
{
    "user_id": 123456789,
    "guild_id": 987654321,
    "real_name": "John Doe",
    "email": "john.doe@example.com",
    "source": "registration_form",
    "education_stage": "university",
    "bio": "Software developer",
    "location": "Taipei, Taiwan",
    "website": "https://johndoe.dev",
    "github_username": "johndoe",
    "tags": ["developer", "python"]
}
```

**Success Response**: `201 Created`
```json
{
    "success": true,
    "message": "User created successfully",
    "data": {
        // Complete user object
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation errors
- `409 Conflict`: User already exists

### 2. Get User by ID

Retrieve complete user information by MongoDB ObjectId.

**Endpoint**: `GET /users/{user_id}`

**Parameters**:
- `user_id` (string): MongoDB ObjectId

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User found",
    "data": {
        // Complete user object
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses**:
- `404 Not Found`: User not found

### 3. Get Public User Information

Retrieve limited public user information.

**Endpoint**: `GET /users/{user_id}/public`

**Parameters**:
- `user_id` (string): MongoDB ObjectId

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Public user information retrieved",
    "data": {
        "id": "507f1f77bcf86cd799439011",
        "real_name": "John Doe",
        "bio": "Software developer",
        "location": "Taipei, Taiwan",
        "website": "https://johndoe.dev",
        "github_username": "johndoe",
        "tags": ["developer", "python"],
        "registered_at": "2024-01-15T08:30:00.000Z",
        "display_name": "John Doe"
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 4. Get User by Email

Retrieve user information by email address.

**Endpoint**: `GET /users/email/{email}`

**Parameters**:
- `email` (string): User's email address

**Example**: `GET /users/email/john.doe@example.com`

### 5. Get User by Discord IDs

Retrieve user information by Discord user ID and guild ID.

**Endpoint**: `GET /users/discord/{user_id}/{guild_id}`

**Parameters**:
- `user_id` (integer): Discord user ID
- `guild_id` (integer): Discord guild ID

**Example**: `GET /users/discord/123456789/987654321`

### 6. Update User

Update user information with partial data.

**Endpoint**: `PUT /users/{user_id}`

**Request Body** (all fields optional):
```json
{
    "real_name": "John Smith",
    "bio": "Updated bio information",
    "location": "Tokyo, Japan",
    "tags": ["developer", "python", "ai"]
}
```

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User updated successfully",
    "data": {
        // Updated user object
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 7. Delete User

Permanently delete a user account.

**Endpoint**: `DELETE /users/{user_id}`

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User deleted successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## User Status Management

### 1. Activate User

Activate a deactivated user account.

**Endpoint**: `PATCH /users/{user_id}/activate`

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User activated successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 2. Deactivate User

Deactivate a user account (soft delete).

**Endpoint**: `PATCH /users/{user_id}/deactivate`

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User deactivated successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 3. Update Login Timestamp

Update user's last login timestamp.

**Endpoint**: `PATCH /users/{user_id}/login`

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Login timestamp updated successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Tag Management

### 1. Add User Tag

Add a tag to a user for categorization.

**Endpoint**: `POST /users/{user_id}/tags`

**Request Body**:
```json
{
    "tag": "frontend"
}
```

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Tag 'frontend' added successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 2. Remove User Tag

Remove a tag from a user.

**Endpoint**: `DELETE /users/{user_id}/tags`

**Request Body**:
```json
{
    "tag": "frontend"
}
```

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Tag 'frontend' removed successfully",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Search and Query Operations

### 1. Advanced User Query

Perform complex user searches with multiple filters.

**Endpoint**: `POST /users/query`

**Request Body**:
```json
{
    "email": "john@example.com",
    "user_id": 123456789,
    "guild_id": 987654321,
    "is_active": true,
    "is_verified": false,
    "tag": "developer",
    "search_name": "john",
    "education_stage": "university",
    "location": "taipei",
    "registered_after": "2024-01-01T00:00:00Z",
    "registered_before": "2024-12-31T23:59:59Z",
    "limit": 20,
    "offset": 0,
    "order_by": "-registered_at",
    "public_only": false
}
```

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Found 15 users",
    "data": [
        // Array of user objects
    ],
    "pagination": {
        "total": 150,
        "limit": 20,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 2. List Users

List users with pagination and basic filtering.

**Endpoint**: `GET /users/`

**Query Parameters**:
- `limit` (integer, 1-100): Number of users to return (default: 10)
- `offset` (integer, ≥0): Number of users to skip (default: 0)
- `active_only` (boolean): Return only active users (default: false)
- `public_only` (boolean): Return only public information (default: false)

**Example**: `GET /users/?limit=20&offset=40&active_only=true`

### 3. Search Users by Name

Search users by name with case-insensitive matching.

**Endpoint**: `GET /users/search/name/{name}`

**Parameters**:
- `name` (string): Name to search for
- `limit` (query parameter, integer): Maximum results (default: 20)

**Example**: `GET /users/search/name/john?limit=10`

### 4. Get Users by Tag

Retrieve users that have a specific tag.

**Endpoint**: `GET /users/tag/{tag}`

**Parameters**:
- `tag` (string): Tag to search for
- `limit` (query parameter, integer): Maximum results (default: 50)

**Example**: `GET /users/tag/developer?limit=25`

---

## Analytics and Statistics

### Get User Statistics

Retrieve comprehensive user statistics for analytics.

**Endpoint**: `GET /users/analytics/statistics`

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "User statistics retrieved successfully",
    "data": {
        "total_users": 1250,
        "active_users": 1180,
        "verified_users": 890,
        "inactive_users": 70,
        "recent_registrations_30d": 45,
        "verification_rate": 71.2
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Bulk Operations

### Bulk Update Users

Update multiple users simultaneously with the same data.

**Endpoint**: `PUT /users/bulk`

**Request Body**:
```json
{
    "user_ids": [
        "507f1f77bcf86cd799439011",
        "507f1f77bcf86cd799439012",
        "507f1f77bcf86cd799439013"
    ],
    "update_data": {
        "source": "bulk_import",
        "is_verified": true,
        "tags": ["imported", "verified"]
    }
}
```

**Success Response**: `200 OK`
```json
{
    "success": true,
    "message": "Successfully updated 3 users",
    "data": {
        "updated_count": 3
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## System Operations

### 1. Health Check

Check service health and database connectivity.

**Endpoint**: `GET /health`

**Success Response**: `200 OK`
```json
{
    "status": "healthy",
    "service": "hackit-database-service",
    "version": "1.1.0",
    "environment": "production",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "database": {
        "status": "connected",
        "user_count": 1250
    },
    "features": {
        "rate_limiting": true,
        "audit_logging": false,
        "schema_validation": true
    }
}
```

### 2. Service Information

Get comprehensive service information and available endpoints.

**Endpoint**: `GET /`

**Success Response**: `200 OK`
```json
{
    "service": "hackit-database-service",
    "version": "1.1.0",
    "description": "Centralized database API service for HackIt organization",
    "environment": "production",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "documentation": {
        "interactive_docs": "/docs",
        "redoc": "/redoc",
        "openapi_spec": "/openapi.json"
    },
    "endpoints": {
        "health": "/health",
        "users": {
            "base": "/users",
            "create": "POST /users/",
            "get_by_id": "GET /users/{user_id}",
            // ... other endpoints
        }
    },
    "authentication": {
        "method": "HMAC-SHA256",
        "headers": ["X-API-Timestamp", "X-API-Signature"],
        "validity_window": "300 seconds"
    },
    "rate_limiting": {
        "enabled": true,
        "requests_per_minute": 100
    }
}
```

### 3. Development Test Signature (Development Only)

Generate test API signatures for development purposes.

**Endpoint**: `GET /dev/test-signature`

**Query Parameters**:
- `method` (string): HTTP method (default: "GET")
- `path` (string): API path (default: "/users/")

**Example**: `GET /dev/test-signature?method=POST&path=/users/`

---

## Client Library Usage

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from database_client import DatabaseClient, DatabaseClientError

async def main():
    # Initialize client
    async with DatabaseClient("http://localhost:8001", "your-secret-key") as client:
        try:
            # Create user
            user_data = {
                "user_id": 123456789,
                "guild_id": 987654321,
                "real_name": "John Doe",
                "email": "john@example.com"
            }
            response = await client.create_user(user_data)
            print(f"User created: {response['data']['id']}")
            
            # Get user by email
            user = await client.get_user_by_email("john@example.com")
            print(f"Found user: {user['data']['real_name']}")
            
            # Update user
            update_data = {"bio": "Updated bio"}
            await client.update_user(user['data']['id'], update_data)
            
            # Add tag
            await client.add_user_tag(user['data']['id'], "developer")
            
            # Search users
            results = await client.search_users_by_name("john")
            print(f"Found {len(results['data'])} users")
            
        except DatabaseClientError as e:
            print(f"Error: {e}")
```

### Helper Methods

```python
# Simple user retrieval by various identifiers
user = await client.get_user_simple("john@example.com")  # By email
user = await client.get_user_simple(123456789, 987654321)  # By Discord IDs
user = await client.get_user_simple("507f1f77bcf86cd799439011")  # By ObjectId

# Create or update user
response = await client.create_or_update_user({
    "user_id": 123456789,
    "guild_id": 987654321,
    "real_name": "John Doe",
    "email": "john@example.com"
})
```

### Error Handling

```python
try:
    response = await client.get_user_by_id("invalid-id")
except DatabaseClientError as e:
    if e.status_code == 404:
        print("User not found")
    elif e.status_code == 401:
        print("Authentication failed")
    else:
        print(f"Error: {e.message}")
```

---

## Examples and Use Cases

### 1. User Registration Flow

```python
async def register_user(discord_user_id, guild_id, email, name):
    async with DatabaseClient(BASE_URL, API_KEY) as client:
        # Check if user already exists
        existing_user = await client.get_user_simple(discord_user_id, guild_id)
        
        if existing_user:
            return {"status": "exists", "user": existing_user}
        
        # Create new user
        user_data = {
            "user_id": discord_user_id,
            "guild_id": guild_id,
            "real_name": name,
            "email": email,
            "source": "discord_registration"
        }
        
        response = await client.create_user(user_data)
        return {"status": "created", "user": response["data"]}
```

### 2. User Profile Update

```python
async def update_user_profile(user_id, profile_data):
    async with DatabaseClient(BASE_URL, API_KEY) as client:
        # Validate and clean profile data
        allowed_fields = [
            "real_name", "bio", "location", "website", 
            "github_username", "education_stage"
        ]
        
        update_data = {
            k: v for k, v in profile_data.items() 
            if k in allowed_fields and v
        }
        
        if not update_data:
            return {"status": "no_changes"}
        
        response = await client.update_user(user_id, update_data)
        return {"status": "updated", "user": response["data"]}
```

### 3. User Search and Analytics

```python
async def get_user_analytics():
    async with DatabaseClient(BASE_URL, API_KEY) as client:
        # Get basic statistics
        stats = await client.get_user_statistics()
        
        # Get recent users
        recent_users = await client.query_users({
            "registered_after": "2024-01-01T00:00:00Z",
            "is_active": True,
            "limit": 50,
            "order_by": "-registered_at"
        })
        
        # Get users by tag
        developers = await client.get_users_by_tag("developer")
        
        return {
            "statistics": stats["data"],
            "recent_users": len(recent_users["data"]),
            "developers": len(developers["data"])
        }
```

### 4. Bulk User Management

```python
async def bulk_verify_users(user_ids):
    async with DatabaseClient(BASE_URL, API_KEY) as client:
        # Bulk update verification status
        response = await client.bulk_update_users(
            user_ids,
            {"is_verified": True, "source": "admin_verification"}
        )
        
        # Add verification tag to all users
        for user_id in user_ids:
            await client.add_user_tag(user_id, "verified")
        
        return response["data"]["updated_count"]
```

### 5. Login Tracking

```python
async def track_user_login(discord_user_id, guild_id):
    async with DatabaseClient(BASE_URL, API_KEY) as client:
        # Find user by Discord ID
        user = await client.get_user_simple(discord_user_id, guild_id)
        
        if user:
            # Update login timestamp
            await client.update_user_login(user["id"])
            return {"status": "logged", "user_id": user["id"]}
        else:
            return {"status": "not_found"}
```

---

## Best Practices

### 1. Authentication Security

- **Store API keys securely**: Use environment variables or secure key management
- **Rotate keys regularly**: Implement key rotation for enhanced security
- **Validate timestamps**: Ensure proper time synchronization between systems

### 2. Error Handling

- **Always handle exceptions**: Use try-catch blocks for all API calls
- **Check response status**: Verify `success` field before processing data
- **Log errors appropriately**: Include context for debugging

### 3. Performance Optimization

- **Use pagination**: Implement proper pagination for large datasets
- **Cache frequently accessed data**: Implement client-side caching where appropriate
- **Batch operations**: Use bulk operations for multiple updates

### 4. Data Validation

- **Validate input data**: Check data before sending to API
- **Handle validation errors**: Provide clear error messages to users
- **Use appropriate data types**: Follow schema specifications

### 5. Rate Limiting

- **Implement backoff strategies**: Handle rate limit responses gracefully
- **Monitor usage**: Track API usage to avoid limits
- **Batch requests**: Combine multiple operations when possible

---

## Support and Contact

- **API Documentation**: Visit `/docs` endpoint when service is running
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Contact**: Reach out to the HackIt development team

---

**Last Updated**: January 15, 2024  
**API Version**: v1.1.0  
**Document Version**: 1.0 