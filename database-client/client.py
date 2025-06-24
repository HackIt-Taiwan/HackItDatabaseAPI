import httpx
import hmac
import hashlib
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Client for HackIt Database Service."""
    
    def __init__(self, base_url: str, api_secret_key: str):
        """
        Initialize database client.
        
        Args:
            base_url: Base URL of the database service (e.g., http://localhost:8001)
            api_secret_key: Secret key for API authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret_key = api_secret_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
    def _create_api_signature(self, data: str, timestamp: int) -> str:
        """Create HMAC signature for API request validation."""
        message = f"{data}:{timestamp}"
        signature = hmac.new(
            self.api_secret_key.encode(),
            message.encode(),
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
        
        try:
            response = await self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in {method} {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in {method} {path}: {str(e)}")
            raise

    # User management methods
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        return await self._make_request("POST", "/users/", json=user_data)
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user by MongoDB ObjectId."""
        return await self._make_request("GET", f"/users/{user_id}")
    
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
    
    async def query_users(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Query users with filters."""
        return await self._make_request("POST", "/users/query", json=query_params)
    
    async def list_users(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List users with pagination."""
        params = {"limit": limit, "offset": offset}
        return await self._make_request("GET", "/users/", params=params)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database service health."""
        return await self._make_request("GET", "/health")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Convenience functions for backward compatibility
class UserService:
    """Backward compatible user service interface."""
    
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address (backward compatible)."""
        try:
            response = await self.db_client.get_user_by_email(email)
            if response.get("success"):
                return response.get("data")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def update_user_login_info(self, user_id: str, source: str = "magic_link") -> bool:
        """Update user's last login information (backward compatible)."""
        try:
            user_data = {"source": source}
            response = await self.db_client.update_user(user_id, user_data)
            return response.get("success", False)
        except Exception as e:
            logger.error(f"Error updating user login info for {user_id}: {str(e)}")
            return False 