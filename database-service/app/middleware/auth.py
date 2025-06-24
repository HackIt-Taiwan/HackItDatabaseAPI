from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hmac
import hashlib
import time
from typing import Optional

from app.core.config import settings

security = HTTPBearer(auto_error=False)

class APIKeyAuth:
    """Simple API key authentication for database service."""
    
    @staticmethod
    def create_api_signature(data: str, timestamp: int) -> str:
        """Create HMAC signature for API request validation."""
        message = f"{data}:{timestamp}"
        signature = hmac.new(
            settings.API_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_api_signature(data: str, timestamp: int, signature: str) -> bool:
        """Verify HMAC signature for API request."""
        # Check timestamp (allow 5 minutes tolerance)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:  # 5 minutes
            return False
        
        expected_signature = APIKeyAuth.create_api_signature(data, timestamp)
        return hmac.compare_digest(expected_signature, signature)

def verify_api_request(request: Request) -> bool:
    """Verify API request authenticity."""
    try:
        # Check for API signature headers
        timestamp_header = request.headers.get("X-API-Timestamp")
        signature_header = request.headers.get("X-API-Signature")
        
        if not timestamp_header or not signature_header:
            return False
        
        timestamp = int(timestamp_header)
        signature = signature_header
        
        # Create data string from request path and method
        data = f"{request.method}:{request.url.path}"
        
        return APIKeyAuth.verify_api_signature(data, timestamp, signature)
        
    except (ValueError, TypeError):
        return False

async def api_auth_dependency(request: Request):
    """FastAPI dependency for API authentication."""
    # For development, allow requests without authentication
    # In production, you should enforce this
    if not verify_api_request(request):
        # Log unauthorized attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Unauthorized API request from {request.client.host if request.client else 'unknown'}")
        
        # For now, just log and continue (development mode)
        # In production, uncomment the following lines:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid API authentication"
        # )
    
    return True 