import base64
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from fastapi.responses import Response

from app.models.user import RegisteredUser
from app.core.config import settings

logger = logging.getLogger(__name__)

class AvatarService:
    """Service for handling user avatar operations with caching and optimization."""
    
    # In-memory cache for avatars (in production, you might want to use Redis)
    _cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def _generate_etag(cls, avatar_data: str) -> str:
        """Generate ETag from avatar data."""
        return hashlib.md5(avatar_data.encode()).hexdigest()
    
    @classmethod
    def _is_cache_valid(cls, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not settings.AVATAR_CACHE_ENABLED:
            return False
        
        cached_at = cache_entry.get('cached_at')
        if not cached_at:
            return False
            
        expiry_time = cached_at + timedelta(seconds=settings.AVATAR_CACHE_TTL_SECONDS)
        return datetime.utcnow() < expiry_time
    
    @classmethod
    def _add_to_cache(cls, user_id: str, avatar_data: bytes, etag: str, last_modified: datetime) -> None:
        """Add avatar to cache."""
        if not settings.AVATAR_CACHE_ENABLED:
            return
            
        cls._cache[user_id] = {
            'data': avatar_data,
            'etag': etag,
            'last_modified': last_modified,
            'cached_at': datetime.utcnow()
        }
        
        logger.debug(f"Added avatar for user {user_id} to cache")
    
    @classmethod
    def _get_from_cache(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get avatar from cache if valid."""
        if not settings.AVATAR_CACHE_ENABLED:
            return None
            
        cache_entry = cls._cache.get(user_id)
        if cache_entry and cls._is_cache_valid(cache_entry):
            logger.debug(f"Cache hit for user {user_id}")
            return cache_entry
            
        # Clean up expired cache entry
        if cache_entry:
            del cls._cache[user_id]
            logger.debug(f"Removed expired cache entry for user {user_id}")
            
        return None
    
    @classmethod
    def _detect_image_format(cls, avatar_data: bytes) -> Tuple[str, str]:
        """Detect image format and return MIME type and file extension."""
        # Check for common image file signatures
        if avatar_data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg', 'jpg'
        elif avatar_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png', 'png'
        elif avatar_data.startswith(b'GIF87a') or avatar_data.startswith(b'GIF89a'):
            return 'image/gif', 'gif'
        elif avatar_data.startswith(b'\x00\x00\x01\x00') or avatar_data.startswith(b'\x00\x00\x02\x00'):
            return 'image/x-icon', 'ico'
        elif avatar_data.startswith(b'RIFF') and b'WEBP' in avatar_data[:12]:
            return 'image/webp', 'webp'
        else:
            # Default to JPEG if unknown
            return 'image/jpeg', 'jpg'
    
    @classmethod
    def get_user_avatar(
        cls, 
        user_id: str, 
        if_none_match: Optional[str] = None,
        if_modified_since: Optional[str] = None
    ) -> Tuple[Optional[bytes], Optional[str], Optional[datetime], Optional[str]]:
        """
        Get user avatar with caching support.
        
        Returns:
            Tuple of (avatar_data, etag, last_modified, content_type)
        """
        try:
            # Try cache first
            cached_avatar = cls._get_from_cache(user_id)
            if cached_avatar:
                etag = cached_avatar['etag']
                last_modified = cached_avatar['last_modified']
                
                # Check conditional requests
                if if_none_match and if_none_match.strip('"') == etag:
                    logger.debug(f"ETag match for user {user_id}, returning 304")
                    return None, etag, last_modified, None
                
                if if_modified_since:
                    try:
                        if_modified_dt = datetime.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
                        if last_modified <= if_modified_dt:
                            logger.debug(f"Not modified for user {user_id}, returning 304")
                            return None, etag, last_modified, None
                    except ValueError:
                        logger.warning(f"Invalid If-Modified-Since header: {if_modified_since}")
                
                avatar_data = cached_avatar['data']
                content_type, _ = cls._detect_image_format(avatar_data)
                return avatar_data, etag, last_modified, content_type
            
            # Cache miss, fetch from database
            logger.debug(f"Cache miss for user {user_id}, fetching from database")
            user = RegisteredUser.objects(id=user_id).first()
            
            if not user or not user.avatar_base64:
                logger.debug(f"No avatar found for user {user_id}")
                return None, None, None, None
            
            try:
                # Decode base64 avatar
                avatar_data = base64.b64decode(user.avatar_base64)
                
                # Validate file size
                if len(avatar_data) > settings.AVATAR_MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.warning(f"Avatar for user {user_id} exceeds size limit")
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Avatar file size exceeds limit"
                    )
                
                # Generate cache headers
                etag = cls._generate_etag(user.avatar_base64)
                last_modified = user.last_updated or user.registered_at or datetime.utcnow()
                
                # Check conditional requests before caching
                if if_none_match and if_none_match.strip('"') == etag:
                    return None, etag, last_modified, None
                
                if if_modified_since:
                    try:
                        if_modified_dt = datetime.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
                        if last_modified <= if_modified_dt:
                            return None, etag, last_modified, None
                    except ValueError:
                        logger.warning(f"Invalid If-Modified-Since header: {if_modified_since}")
                
                # Detect content type
                content_type, _ = cls._detect_image_format(avatar_data)
                
                # Add to cache
                cls._add_to_cache(user_id, avatar_data, etag, last_modified)
                
                logger.info(f"Successfully retrieved avatar for user {user_id}")
                return avatar_data, etag, last_modified, content_type
                
            except Exception as e:
                logger.error(f"Error decoding avatar for user {user_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid avatar data"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving avatar for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve avatar"
            )
    
    @classmethod
    def invalidate_cache(cls, user_id: str) -> None:
        """Invalidate cache for a specific user."""
        if user_id in cls._cache:
            del cls._cache[user_id]
            logger.debug(f"Invalidated cache for user {user_id}")
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all avatar cache."""
        cls._cache.clear()
        logger.info("Cleared all avatar cache")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(cls._cache)
        valid_entries = sum(1 for entry in cls._cache.values() if cls._is_cache_valid(entry))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_enabled': settings.AVATAR_CACHE_ENABLED,
            'cache_ttl_seconds': settings.AVATAR_CACHE_TTL_SECONDS
        } 