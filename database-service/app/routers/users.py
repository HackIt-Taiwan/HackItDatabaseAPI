from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserQuery, APIResponse
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    try:
        user = UserService.create_user(user_data)
        if user:
            return APIResponse(
                success=True,
                message="User created successfully",
                data=user.to_dict()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists or creation failed"
            )
    except Exception as e:
        logger.error(f"Error in create_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Get user by MongoDB ObjectId."""
    try:
        user = UserService.get_user_by_id(user_id)
        if user:
            return APIResponse(
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

@router.get("/email/{email}", response_model=APIResponse)
async def get_user_by_email(email: str = Path(..., description="User email address")):
    """Get user by email address."""
    try:
        user = UserService.get_user_by_email(email)
        if user:
            return APIResponse(
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

@router.get("/discord/{user_id}/{guild_id}", response_model=APIResponse)
async def get_user_by_discord_id(
    user_id: int = Path(..., description="Discord user ID"),
    guild_id: int = Path(..., description="Discord guild ID")
):
    """Get user by Discord user_id and guild_id."""
    try:
        user = UserService.get_user_by_user_id(user_id, guild_id)
        if user:
            return APIResponse(
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

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: str = Path(..., description="User MongoDB ObjectId")
):
    """Update user information."""
    try:
        user = UserService.update_user(user_id, user_data)
        if user:
            return APIResponse(
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

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(user_id: str = Path(..., description="User MongoDB ObjectId")):
    """Delete user by id."""
    try:
        success = UserService.delete_user(user_id)
        if success:
            return APIResponse(
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

@router.post("/query", response_model=APIResponse)
async def query_users(query: UserQuery):
    """Query users with filters and pagination."""
    try:
        users = UserService.query_users(query)
        total_count = UserService.get_user_count()
        
        return APIResponse(
            success=True,
            message=f"Found {len(users)} users",
            data={
                "users": [user.to_dict() for user in users],
                "total": total_count,
                "offset": query.offset,
                "limit": query.limit
            }
        )
    except Exception as e:
        logger.error(f"Error in query_users endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=APIResponse)
async def list_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip")
):
    """List users with pagination."""
    try:
        query = UserQuery(limit=limit, offset=offset)
        users = UserService.query_users(query)
        total_count = UserService.get_user_count()
        
        return APIResponse(
            success=True,
            message=f"Found {len(users)} users",
            data={
                "users": [user.to_dict() for user in users],
                "total": total_count,
                "offset": offset,
                "limit": limit
            }
        )
    except Exception as e:
        logger.error(f"Error in list_users endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 