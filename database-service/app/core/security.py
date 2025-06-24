import hmac
import hashlib
import time
import secrets
import re
from typing import Optional, List, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from datetime import datetime, timedelta
import fnmatch

from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class SecurityManager:
    """Enhanced security manager for API authentication and validation."""
    
    @staticmethod
    def create_api_signature(data: str, timestamp: int, secret_key: Optional[str] = None) -> str:
        """Create HMAC-SHA256 signature for API request validation."""
        secret = secret_key or settings.API_SECRET_KEY
        message = f"{data}:{timestamp}"
        signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_api_signature(data: str, timestamp: int, signature: str, secret_key: Optional[str] = None) -> bool:
        """Verify HMAC-SHA256 signature for API request."""
        try:
            # Check timestamp validity window
            current_time = int(time.time())
            time_diff = abs(current_time - timestamp)
            
            if time_diff > settings.SIGNATURE_VALIDITY_WINDOW:
                logger.warning(f"Request timestamp outside validity window: {time_diff}s")
                return False
            
            # Verify signature
            secret = secret_key or settings.API_SECRET_KEY
            expected_signature = SecurityManager.create_api_signature(data, timestamp, secret)
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying API signature: {str(e)}")
            return False
    
    @staticmethod
    def validate_domain(host: str) -> bool:
        """Validate if the request host is allowed."""
        if not host:
            return False
        
        # Remove port from host if present
        host_without_port = host.split(':')[0].lower()
        
        for allowed_host in settings.ALLOWED_HOSTS:
            # Support wildcard matching
            if fnmatch.fnmatch(host_without_port, allowed_host.lower()):
                return True
        
        return False
    
    @staticmethod
    def extract_request_info(request: Request) -> Dict[str, Any]:
        """Extract relevant information from request for logging and validation."""
        client_ip = None
        if request.client:
            client_ip = request.client.host
        
        # Check for forwarded headers (for proxy setups)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            client_ip = real_ip
        
        return {
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'client_ip': client_ip,
            'user_agent': request.headers.get('User-Agent'),
            'host': request.headers.get('Host'),
            'referer': request.headers.get('Referer'),
            'timestamp': int(time.time())
        }
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt (for future use if user authentication is needed)."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash."""
        expected_hash, _ = SecurityManager.hash_password(password, salt)
        return hmac.compare_digest(expected_hash, hashed_password)


class RateLimiter:
    """Simple in-memory rate limiter for API requests."""
    
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.max_requests = settings.API_RATE_LIMIT_REQUESTS
        self.window_minutes = 1
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit."""
        if not settings.API_RATE_LIMIT_ENABLED:
            return True
        
        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old requests for this client
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id] 
                if req_time > window_start
            ]
        else:
            self.requests[client_id] = []
        
        # Check if within limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get number of remaining requests for client."""
        if not settings.API_RATE_LIMIT_ENABLED:
            return self.max_requests
        
        if client_id not in self.requests:
            return self.max_requests
        
        return max(0, self.max_requests - len(self.requests[client_id]))


# Global rate limiter instance
rate_limiter = RateLimiter()


class APIAuthenticator:
    """Main API authentication class."""
    
    @staticmethod
    def verify_request(request: Request) -> tuple[bool, Optional[str]]:
        """Verify API request authenticity and authorization."""
        try:
            # Extract request information
            request_info = SecurityManager.extract_request_info(request)
            
            # Validate domain if in production
            if settings.is_production():
                host = request_info.get('host')
                if not SecurityManager.validate_domain(host):
                    logger.warning(f"Invalid domain in request: {host}")
                    return False, f"Invalid domain: {host}"
            
            # Check rate limiting
            client_id = request_info.get('client_ip', 'unknown')
            if not rate_limiter.is_allowed(client_id):
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                return False, "Rate limit exceeded"
            
            # Check for API signature headers
            timestamp_header = request.headers.get("X-API-Timestamp")
            signature_header = request.headers.get("X-API-Signature")
            
            if not timestamp_header or not signature_header:
                if settings.is_production():
                    logger.warning("Missing authentication headers in production")
                    return False, "Missing authentication headers"
                else:
                    # Allow requests without authentication in development
                    logger.debug("Request without authentication in development mode")
                    return True, None
            
            # Validate timestamp format
            try:
                timestamp = int(timestamp_header)
            except ValueError:
                logger.warning(f"Invalid timestamp format: {timestamp_header}")
                return False, "Invalid timestamp format"
            
            # Create data string for signature verification
            data = f"{request.method}:{request.url.path}"
            
            # Verify signature
            if not SecurityManager.verify_api_signature(data, timestamp, signature_header):
                logger.warning(f"Invalid API signature for request: {request.method} {request.url.path}")
                return False, "Invalid API signature"
            
            # Log successful authentication
            logger.debug(f"Authenticated request: {request.method} {request.url.path} from {client_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error in request verification: {str(e)}")
            return False, "Authentication error"


async def api_auth_dependency(request: Request):
    """FastAPI dependency for API authentication."""
    is_valid, error_message = APIAuthenticator.verify_request(request)
    
    if not is_valid:
        # Log authentication failure
        request_info = SecurityManager.extract_request_info(request)
        logger.warning(
            f"Authentication failed for {request_info.get('client_ip', 'unknown')}: {error_message}"
        )
        
        # In production, always enforce authentication
        if settings.is_production() or error_message == "Rate limit exceeded":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED if error_message != "Rate limit exceeded" else status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message or "Authentication failed",
                headers={"X-Remaining-Requests": str(rate_limiter.get_remaining_requests(request_info.get('client_ip', 'unknown')))}
            )
    
    return True


def create_test_signature(method: str, path: str, secret_key: Optional[str] = None) -> Dict[str, str]:
    """Helper function to create test API signatures for development."""
    timestamp = int(time.time())
    data = f"{method.upper()}:{path}"
    signature = SecurityManager.create_api_signature(data, timestamp, secret_key)
    
    return {
        "X-API-Timestamp": str(timestamp),
        "X-API-Signature": signature
    } 