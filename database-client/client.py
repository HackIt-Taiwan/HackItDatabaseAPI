import httpx
import hmac
import hashlib
import time
from typing import Optional, Dict, Any, List, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Enhanced client for HackIt Database Service with full API support."""
    
    def __init__(self, base_url: str, api_secret_key: str, timeout: float = 30.0):
        """
        Initialize database client.
        
        Args:
            base_url: Base URL of the database service (e.g., http://localhost:8001)
            api_secret_key: Secret key for API authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret_key = api_secret_key
        self.client = httpx.AsyncClient(timeout=timeout)
        
    def _create_api_signature(self, data: str, timestamp: int) -> str:
        """Create HMAC signature for API request validation."""
        message = f"{data}:{timestamp}"
        signature = hmac.new(
            self.api_secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        """Get authentication headers for API request."""
        timestamp = int(time.time())
        data = f"{method.upper()}:{path}"
        signature = self._create_api_signature(data, timestamp)
        
        return {
            "X-API-Timestamp": str(timestamp),
            "X-API-Signature": signature,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to database service."""
        url = f"{self.base_url}{path}"
        headers = self._get_auth_headers(method, path)
        
        # Merge with any existing headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code} error in {method} {path}: {e.response.text}")
            try:
                error_data = e.response.json()
                raise DatabaseClientError(
                    message=error_data.get('detail', str(e)),
                    status_code=e.response.status_code,
                    error_code=error_data.get('error_code')
                )
            except ValueError:
                raise DatabaseClientError(
                    message=str(e),
                    status_code=e.response.status_code
                )
        except httpx.RequestError as e:
            logger.error(f"Request error in {method} {path}: {str(e)}")
            raise DatabaseClientError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {method} {path}: {str(e)}")
            raise DatabaseClientError(f"Unexpected error: {str(e)}")

    # User CRUD Operations
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        return await self._make_request("POST", "/users/", json=user_data)
    
    async def get_user_by_id(self, user_id: str, public_only: bool = False) -> Dict[str, Any]:
        """Get user by MongoDB ObjectId."""
        endpoint = f"/users/{user_id}/public" if public_only else f"/users/{user_id}"
        return await self._make_request("GET", endpoint)
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email address."""
        return await self._make_request("GET", f"/users/email/{email}")
    
    async def get_user_by_discord_id(self, user_id: int, guild_id: int) -> Dict[str, Any]:
        """Get user by Discord user_id and guild_id."""
        return await self._make_request("GET", f"/users/discord/{user_id}/{guild_id}")
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information."""
        return await self._make_request("PUT", f"/users/{user_id}", json=user_data)
    
    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user by id."""
        return await self._make_request("DELETE", f"/users/{user_id}")
    
    # User Status Management
    
    async def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivate user account (soft delete)."""
        return await self._make_request("PATCH", f"/users/{user_id}/deactivate")
    
    async def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Activate deactivated user account."""
        return await self._make_request("PATCH", f"/users/{user_id}/activate")
    
    async def update_user_login(self, user_id: str) -> Dict[str, Any]:
        """Update user's last login timestamp."""
        return await self._make_request("PATCH", f"/users/{user_id}/login")
    
    # Tag Management
    
    async def add_user_tag(self, user_id: str, tag: str) -> Dict[str, Any]:
        """Add a tag to user."""
        return await self._make_request("POST", f"/users/{user_id}/tags", json={"tag": tag})
    
    async def remove_user_tag(self, user_id: str, tag: str) -> Dict[str, Any]:
        """Remove a tag from user."""
        return await self._make_request("DELETE", f"/users/{user_id}/tags", json={"tag": tag})
    
    # Query and Search Operations
    
    async def query_users(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Query users with advanced filters."""
        return await self._make_request("POST", "/users/query", json=query_params)
    
    async def list_users(self, limit: int = 10, offset: int = 0, 
                        active_only: bool = False, public_only: bool = False) -> Dict[str, Any]:
        """List users with pagination."""
        params = {
            "limit": limit, 
            "offset": offset,
            "active_only": active_only,
            "public_only": public_only
        }
        return await self._make_request("GET", "/users/", params=params)
    
    async def search_users_by_name(self, name: str, limit: int = 20) -> Dict[str, Any]:
        """Search users by name (case-insensitive)."""
        params = {"limit": limit}
        return await self._make_request("GET", f"/users/search/name/{name}", params=params)
    
    async def get_users_by_tag(self, tag: str, limit: int = 50) -> Dict[str, Any]:
        """Get users that have a specific tag."""
        params = {"limit": limit}
        return await self._make_request("GET", f"/users/tag/{tag}", params=params)
    
    # Analytics and Statistics
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        return await self._make_request("GET", "/users/analytics/statistics")
    
    # Bulk Operations
    
    async def bulk_update_users(self, user_ids: List[str], update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple users at once."""
        bulk_data = {
            "user_ids": user_ids,
            "update_data": update_data
        }
        return await self._make_request("PUT", "/users/bulk", json=bulk_data)
    
    # System Operations
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database service health."""
        return await self._make_request("GET", "/health")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and available endpoints."""
        return await self._make_request("GET", "/")
    
    # Helper Methods
    
    async def get_user_simple(self, identifier: Union[str, int], guild_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get user by various identifiers (email, user_id, or MongoDB ObjectId).
        
        Args:
            identifier: Email, Discord user_id, or MongoDB ObjectId
            guild_id: Required if identifier is Discord user_id
            
        Returns:
            User data if found, None otherwise
        """
        try:
            if isinstance(identifier, int) and guild_id is not None:
                # Discord user_id
                response = await self.get_user_by_discord_id(identifier, guild_id)
            elif isinstance(identifier, str) and '@' in identifier:
                # Email
                response = await self.get_user_by_email(identifier)
            elif isinstance(identifier, str):
                # MongoDB ObjectId
                response = await self.get_user_by_id(identifier)
            else:
                return None
            
            return response.get('data') if response.get('success') else None
            
        except DatabaseClientError as e:
            if e.status_code == 404:
                return None
            raise
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user or update existing one based on Discord ID.
        
        Args:
            user_data: User data including user_id and guild_id
            
        Returns:
            User data for created or updated user
        """
        user_id = user_data.get('user_id')
        guild_id = user_data.get('guild_id')
        
        if not user_id or not guild_id:
            raise ValueError("user_id and guild_id are required")
        
        # Try to get existing user
        existing_user = await self.get_user_simple(user_id, guild_id)
        
        if existing_user:
            # Update existing user
            update_data = {k: v for k, v in user_data.items() 
                          if k not in ['user_id', 'guild_id']}
            return await self.update_user(existing_user['id'], update_data)
        else:
            # Create new user
            return await self.create_user(user_data)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class DatabaseClientError(Exception):
    """Custom exception for database client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
    
    def __str__(self):
        if self.status_code:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message


# Backward compatibility classes
class UserService:
    """Backward compatible user service interface."""
    
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address (backward compatible)."""
        try:
            user = await self.db_client.get_user_simple(email)
            return user
        except DatabaseClientError as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def get_user_by_discord_id(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Discord IDs (backward compatible)."""
        try:
            user = await self.db_client.get_user_simple(user_id, guild_id)
            return user
        except DatabaseClientError as e:
            logger.error(f"Error getting user by Discord ID {user_id}: {str(e)}")
            return None
    
    async def update_user_login_info(self, user_id: str, source: str = "magic_link") -> bool:
        """Update user's last login information (backward compatible)."""
        try:
            await self.db_client.update_user_login(user_id)
            if source:
                await self.db_client.update_user(user_id, {"source": source})
            return True
        except DatabaseClientError as e:
            logger.error(f"Error updating user login info for {user_id}: {str(e)}")
            return False
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create user (backward compatible)."""
        try:
            response = await self.db_client.create_user(user_data)
            return response.get('data') if response.get('success') else None
        except DatabaseClientError as e:
            logger.error(f"Error creating user: {str(e)}")
            return None


# Convenience factory functions
def create_client(base_url: str, api_secret_key: str, **kwargs) -> DatabaseClient:
    """Create a new database client instance."""
    return DatabaseClient(base_url, api_secret_key, **kwargs)

async def create_async_client(base_url: str, api_secret_key: str, **kwargs) -> DatabaseClient:
    """Create and return a new async database client instance."""
    return DatabaseClient(base_url, api_secret_key, **kwargs) 