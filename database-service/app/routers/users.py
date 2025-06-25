from fastapi import APIRouter, HTTPException, status, Query, Path, Depends, Header
from fastapi.responses import Response
from typing import List, Optional, Union
from datetime import datetime

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserPublicResponse, UserQuery, 
    APIResponse, PaginatedResponse, UserTagOperation, UserBulkUpdate, 
    UserStatistics
)
from app.services.user_service import UserService
from app.services.avatar_service import AvatarService
from app.core.security import api_auth_dependency
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User Management"])

# Helper function to create consistent responses
def create_response(success: bool, message: str, data=None, error_code=None) -> APIResponse:
    """Create standardized API response."""
    response = APIResponse(
        success=success,
        message=message,
        data=data,
        error_code=error_code,
        timestamp=datetime.utcnow().isoformat()
    )
    return response

def create_paginated_response(success: bool, message: str, data=None, total=0, limit=10, offset=0) -> PaginatedResponse:
    """Create standardized paginated API response."""
    has_next = (offset + limit) < total
    has_previous = offset > 0
    
    response = PaginatedResponse(
        success=success,
        message=message,
        data=data,
        timestamp=datetime.utcnow().isoformat(),
        pagination={
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )
    return response

# User CRUD Operations

@router.post("/", 
             response_model=APIResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="Create a new user",
             description="Create a new user with Discord ID, email, and profile information")
async def create_user(user_data: UserCreate):
    """Create a new user."""
    try:
        user = UserService.create_user(user_data)
        if user:
            return create_response(
                success=True,
                message="User created successfully",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists or validation failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{user_id}", 
            response_model=APIResponse,
            summary="Get user by ID",
            description="Retrieve a user by their MongoDB ObjectId")
async def get_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Get user by MongoDB ObjectId."""
    try:
        user = UserService.get_user_by_id(user_id)
        if user:
            return create_response(
                success=True,
                message="User found",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{user_id}/public", 
            response_model=APIResponse,
            summary="Get public user information",
            description="Retrieve public information about a user (limited fields)")
async def get_user_public(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Get public user information (limited fields)."""
    try:
        user = UserService.get_user_by_id(user_id)
        if user:
            return create_response(
                success=True,
                message="Public user information retrieved",
                data=user.to_public_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_public endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/email/{email}", 
            response_model=APIResponse,
            summary="Get user by email",
            description="Retrieve a user by their email address")
async def get_user_by_email(email: str = Path(..., description="User email address")):
    """Get user by email address."""
    try:
        user = UserService.get_user_by_email(email)
        if user:
            return create_response(
                success=True,
                message="User found",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_by_email endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/discord/{user_id}/{guild_id}", 
            response_model=APIResponse,
            summary="Get user by Discord IDs",
            description="Retrieve a user by their Discord user_id and guild_id")
async def get_user_by_discord_id(
    user_id: int = Path(..., description="Discord user ID"),
    guild_id: int = Path(..., description="Discord guild ID")
):
    """Get user by Discord user_id and guild_id."""
    try:
        user = UserService.get_user_by_user_id(user_id, guild_id)
        if user:
            return create_response(
                success=True,
                message="User found",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_by_discord_id endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{user_id}", 
            response_model=APIResponse,
            summary="Update user",
            description="Update user information by MongoDB ObjectId")
async def update_user(
    user_data: UserUpdate,
    user_id: str = Path(..., description="User MongoDB ObjectId")
):
    """Update user information."""
    try:
        user = UserService.update_user(user_id, user_data)
        if user:
            return create_response(
                success=True,
                message="User updated successfully",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or update failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{user_id}", 
               response_model=APIResponse,
               summary="Delete user",
               description="Permanently delete a user by MongoDB ObjectId")
async def delete_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Delete user by id."""
    try:
        success = UserService.delete_user(user_id)
        if success:
            return create_response(
                success=True,
                message="User deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or deletion failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# User Status Management

@router.patch("/{user_id}/deactivate", 
              response_model=APIResponse,
              summary="Deactivate user",
              description="Deactivate a user account (soft delete)")
async def deactivate_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Deactivate user account."""
    try:
        success = UserService.deactivate_user(user_id)
        if success:
            return create_response(
                success=True,
                message="User deactivated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deactivate_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/{user_id}/activate", 
              response_model=APIResponse,
              summary="Activate user",
              description="Activate a deactivated user account")
async def activate_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Activate user account."""
    try:
        success = UserService.activate_user(user_id)
        if success:
            return create_response(
                success=True,
                message="User activated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in activate_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/{user_id}/login", 
              response_model=APIResponse,
              summary="Update login timestamp",
              description="Update user's last login timestamp")
async def update_user_login(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Update user's last login timestamp."""
    try:
        success = UserService.update_user_login(user_id)
        if success:
            return create_response(
                success=True,
                message="Login timestamp updated successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_user_login endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Tag Management

@router.post("/{user_id}/tags", 
             response_model=APIResponse,
             summary="Add user tag",
             description="Add a tag to a user")
async def add_user_tag(
    tag_data: UserTagOperation,
    user_id: str = Path(..., description="User MongoDB ObjectId")
):
    """Add a tag to user."""
    try:
        success = UserService.add_user_tag(user_id, tag_data.tag)
        if success:
            return create_response(
                success=True,
                message=f"Tag '{tag_data.tag}' added successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in add_user_tag endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{user_id}/tags", 
               response_model=APIResponse,
               summary="Remove user tag",
               description="Remove a tag from a user")
async def remove_user_tag(
    tag_data: UserTagOperation,
    user_id: str = Path(..., description="User MongoDB ObjectId")
):
    """Remove a tag from user."""
    try:
        success = UserService.remove_user_tag(user_id, tag_data.tag)
        if success:
            return create_response(
                success=True,
                message=f"Tag '{tag_data.tag}' removed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in remove_user_tag endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Query and Search Operations

@router.post("/query", 
             response_model=PaginatedResponse,
             summary="Query users",
             description="Query users with advanced filters and pagination")
async def query_users(query: UserQuery):
    """Query users with filters and pagination."""
    try:
        users = UserService.query_users(query)
        total_count = UserService.get_user_count()
        
        # Convert to appropriate response format
        if query.public_only:
            users_data = [user.to_public_dict() for user in users]
        else:
            users_data = [user.to_dict() for user in users]
        
        return create_paginated_response(
            success=True,
            message=f"Found {len(users)} users",
            data=users_data,
            total=total_count,
            limit=query.limit,
            offset=query.offset
        )
    except Exception as e:
        logger.error(f"Error in query_users endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", 
            response_model=PaginatedResponse,
            summary="List users",
            description="List users with pagination")
async def list_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    active_only: bool = Query(False, description="Return only active users"),
    public_only: bool = Query(False, description="Return only public information")
):
    """List users with pagination."""
    try:
        query = UserQuery(
            limit=limit, 
            offset=offset, 
            is_active=active_only if active_only else None,
            public_only=public_only
        )
        users = UserService.query_users(query)
        total_count = UserService.get_user_count(active_only=active_only)
        
        # Convert to appropriate response format
        if public_only:
            users_data = [user.to_public_dict() for user in users]
        else:
            users_data = [user.to_dict() for user in users]
        
        return create_paginated_response(
            success=True,
            message=f"Retrieved {len(users)} users",
            data=users_data,
            total=total_count,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error in list_users endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/search/name/{name}", 
            response_model=APIResponse,
            summary="Search users by name",
            description="Search users by name (case-insensitive)")
async def search_users_by_name(
    name: str = Path(..., description="Name to search for"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """Search users by name."""
    try:
        users = UserService.search_users_by_name(name, limit)
        users_data = [user.to_public_dict() for user in users]
        
        return create_response(
            success=True,
            message=f"Found {len(users)} users matching '{name}'",
            data=users_data
        )
    except Exception as e:
        logger.error(f"Error in search_users_by_name endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/tag/{tag}", 
            response_model=APIResponse,
            summary="Get users by tag",
            description="Get users that have a specific tag")
async def get_users_by_tag(
    tag: str = Path(..., description="Tag to search for"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """Get users by tag."""
    try:
        users = UserService.get_users_by_tag(tag, limit)
        users_data = [user.to_public_dict() for user in users]
        
        return create_response(
            success=True,
            message=f"Found {len(users)} users with tag '{tag}'",
            data=users_data
        )
    except Exception as e:
        logger.error(f"Error in get_users_by_tag endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Analytics and Statistics

@router.get("/analytics/statistics", 
            response_model=APIResponse,
            summary="Get user statistics",
            description="Get comprehensive user statistics for analytics")
async def get_user_statistics():
    """Get user statistics."""
    try:
        stats = UserService.get_user_statistics()
        return create_response(
            success=True,
            message="User statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error in get_user_statistics endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Bulk Operations

@router.put("/bulk", 
            response_model=APIResponse,
            summary="Bulk update users",
            description="Update multiple users at once")
async def bulk_update_users(bulk_data: UserBulkUpdate):
    """Bulk update multiple users."""
    try:
        update_dict = bulk_data.update_data.model_dump(exclude_unset=True)
        updated_count = UserService.bulk_update_users(bulk_data.user_ids, update_dict)
        
        return create_response(
            success=True,
            message=f"Successfully updated {updated_count} users",
            data={"updated_count": updated_count}
        )
    except Exception as e:
        logger.error(f"Error in bulk_update_users endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Avatar Operations

@router.get("/{user_id}/avatar",
            summary="Get user avatar",
            description="Get user avatar image with optimized caching and HTTP headers")
async def get_user_avatar(
    user_id: str = Path(..., description="User MongoDB ObjectId"),
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    if_modified_since: Optional[str] = Header(None, alias="If-Modified-Since")
):
    """
    Get user avatar with optimized HTTP caching.
    
    Supports:
    - ETag validation for efficient caching
    - Last-Modified header for conditional requests
    - Automatic content type detection
    - In-memory caching to reduce database load
    - HTTP 304 Not Modified responses
    """
    try:
        avatar_data, etag, last_modified, content_type = AvatarService.get_user_avatar(
            user_id, if_none_match, if_modified_since
        )
        
        # Return 304 Not Modified if no changes
        if avatar_data is None:
            response = Response(status_code=status.HTTP_304_NOT_MODIFIED)
            if etag and settings.AVATAR_ENABLE_ETAG:
                response.headers["ETag"] = f'"{etag}"'
            if last_modified and settings.AVATAR_ENABLE_LAST_MODIFIED:
                response.headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
            return response
        
        # Return avatar with optimized headers
        response = Response(
            content=avatar_data,
            media_type=content_type or "image/jpeg",
            status_code=status.HTTP_200_OK
        )
        
        # Add caching headers for optimization
        if settings.AVATAR_CACHE_CONTROL_MAX_AGE > 0:
            response.headers["Cache-Control"] = f"public, max-age={settings.AVATAR_CACHE_CONTROL_MAX_AGE}, immutable"
        
        if etag and settings.AVATAR_ENABLE_ETAG:
            response.headers["ETag"] = f'"{etag}"'
        
        if last_modified and settings.AVATAR_ENABLE_LAST_MODIFIED:
            response.headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        # Add CORS headers for cross-origin access
        allowed_origins = settings.get_allowed_origins_list()
        if allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = ", ".join(allowed_origins)
        
        logger.info(f"Successfully served avatar for user {user_id}")
        return response
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            # Return a placeholder or 404 for missing avatars
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar not found"
            )
        raise
    except Exception as e:
        logger.error(f"Error in get_user_avatar endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve avatar"
        )

@router.delete("/{user_id}/avatar/cache",
               response_model=APIResponse,
               summary="Clear user avatar cache",
               description="Clear cached avatar data for a specific user")
async def clear_user_avatar_cache(
    user_id: str = Path(..., description="User MongoDB ObjectId")
):
    """Clear avatar cache for a specific user."""
    try:
        AvatarService.invalidate_cache(user_id)
        return create_response(
            success=True,
            message=f"Avatar cache cleared for user {user_id}"
        )
    except Exception as e:
        logger.error(f"Error in clear_user_avatar_cache endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )

@router.get("/avatars/cache/stats",
            response_model=APIResponse,
            summary="Get avatar cache statistics",
            description="Get statistics about the avatar cache system")
async def get_avatar_cache_stats():
    """Get avatar cache statistics."""
    try:
        stats = AvatarService.get_cache_stats()
        return create_response(
            success=True,
            message="Avatar cache statistics retrieved",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error in get_avatar_cache_stats endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )

@router.delete("/avatars/cache",
               response_model=APIResponse,
               summary="Clear all avatar cache",
               description="Clear all cached avatar data (admin operation)")
async def clear_all_avatar_cache():
    """Clear all avatar cache (admin operation)."""
    try:
        AvatarService.clear_cache()
        return create_response(
            success=True,
            message="All avatar cache cleared successfully"
        )
    except Exception as e:
        logger.error(f"Error in clear_all_avatar_cache endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear all cache"
        ) 