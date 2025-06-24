from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from datetime import datetime

class UserBase(BaseModel):
    """Base schema for user data."""
    user_id: int = Field(..., description="Discord user ID", gt=0)
    guild_id: int = Field(..., description="Discord guild/server ID", gt=0)
    real_name: str = Field(..., description="User's real name", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="User's email address")
    source: Optional[str] = Field(None, description="Registration source", max_length=200)
    education_stage: Optional[str] = Field(None, description="Current education level", max_length=50)
    avatar_base64: Optional[str] = Field(None, description="Base64 encoded user avatar")
    
    # Additional profile fields
    bio: Optional[str] = Field(None, description="User biography", max_length=500)
    location: Optional[str] = Field(None, description="User location", max_length=100)
    website: Optional[str] = Field(None, description="Personal website URL", max_length=200)
    github_username: Optional[str] = Field(None, description="GitHub username", max_length=50)
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL", max_length=200)
    
    # System fields
    is_active: Optional[bool] = Field(True, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(False, description="Whether the user email is verified")
    tags: Optional[List[str]] = Field(None, description="User tags for categorization")

    @validator('website', 'linkedin_url')
    def validate_urls(cls, v):
        """Validate URL format."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f'https://{v}'
        return v

    @validator('github_username')
    def validate_github_username(cls, v):
        """Validate GitHub username format."""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('GitHub username can only contain alphanumeric characters, hyphens, and underscores')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        if v:
            # Remove duplicates and empty strings
            v = list(set([tag.strip() for tag in v if tag.strip()]))
            # Limit to 10 tags
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v

class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass

class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    real_name: Optional[str] = Field(None, description="User's real name", min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, description="User's email address")
    source: Optional[str] = Field(None, description="Registration source", max_length=200)
    education_stage: Optional[str] = Field(None, description="Current education level", max_length=50)
    avatar_base64: Optional[str] = Field(None, description="Base64 encoded user avatar")
    
    # Additional profile fields
    bio: Optional[str] = Field(None, description="User biography", max_length=500)
    location: Optional[str] = Field(None, description="User location", max_length=100)
    website: Optional[str] = Field(None, description="Personal website URL", max_length=200)
    github_username: Optional[str] = Field(None, description="GitHub username", max_length=50)
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL", max_length=200)
    
    # System fields
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether the user email is verified")
    tags: Optional[List[str]] = Field(None, description="User tags for categorization")

    @validator('website', 'linkedin_url')
    def validate_urls(cls, v):
        """Validate URL format."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f'https://{v}'
        return v

    @validator('github_username')
    def validate_github_username(cls, v):
        """Validate GitHub username format."""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('GitHub username can only contain alphanumeric characters, hyphens, and underscores')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        if v:
            # Remove duplicates and empty strings
            v = list(set([tag.strip() for tag in v if tag.strip()]))
            # Limit to 10 tags
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v

class UserResponse(UserBase):
    """Schema for user response."""
    id: str = Field(..., description="MongoDB ObjectId")
    registered_at: Optional[str] = Field(None, description="Registration timestamp (ISO format)")
    last_updated: Optional[str] = Field(None, description="Last update timestamp (ISO format)")
    last_login: Optional[str] = Field(None, description="Last login timestamp (ISO format)")
    display_name: Optional[str] = Field(None, description="User's display name")
    profile_completeness: Optional[float] = Field(None, description="Profile completeness percentage")

    class Config:
        from_attributes = True

class UserPublicResponse(BaseModel):
    """Schema for public user information (limited fields)."""
    id: str = Field(..., description="MongoDB ObjectId")
    real_name: str = Field(..., description="User's real name")
    bio: Optional[str] = Field(None, description="User biography")
    location: Optional[str] = Field(None, description="User location")
    website: Optional[str] = Field(None, description="Personal website URL")
    github_username: Optional[str] = Field(None, description="GitHub username")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    tags: Optional[List[str]] = Field(None, description="User tags")
    registered_at: Optional[str] = Field(None, description="Registration timestamp (ISO format)")
    display_name: Optional[str] = Field(None, description="User's display name")

    class Config:
        from_attributes = True

class UserQuery(BaseModel):
    """Schema for user query parameters with enhanced filters."""
    # Basic filters
    email: Optional[EmailStr] = Field(None, description="Filter by email address")
    user_id: Optional[int] = Field(None, description="Filter by Discord user ID")
    guild_id: Optional[int] = Field(None, description="Filter by Discord guild ID")
    
    # Status filters
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(None, description="Filter by verification status")
    
    # Profile filters
    tag: Optional[str] = Field(None, description="Filter by specific tag")
    search_name: Optional[str] = Field(None, description="Search by name (case-insensitive)")
    education_stage: Optional[str] = Field(None, description="Filter by education stage")
    location: Optional[str] = Field(None, description="Filter by location")
    
    # Date filters
    registered_after: Optional[datetime] = Field(None, description="Filter users registered after this date")
    registered_before: Optional[datetime] = Field(None, description="Filter users registered before this date")
    
    # Pagination and ordering
    limit: Optional[int] = Field(10, description="Number of results to return", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Number of results to skip", ge=0)
    order_by: Optional[str] = Field(None, description="Field to order by (prefix with '-' for descending)")
    
    # Response format
    public_only: Optional[bool] = Field(False, description="Return only public user information")

    @validator('order_by')
    def validate_order_by(cls, v):
        """Validate order_by field."""
        if v:
            valid_fields = [
                'registered_at', 'real_name', 'email', 'last_updated', 'last_login',
                '-registered_at', '-real_name', '-email', '-last_updated', '-last_login'
            ]
            if v not in valid_fields:
                raise ValueError(f'order_by must be one of: {valid_fields}')
        return v

class UserTagOperation(BaseModel):
    """Schema for user tag operations."""
    tag: str = Field(..., description="Tag to add or remove", min_length=1, max_length=50)

    @validator('tag')
    def validate_tag_format(cls, v):
        """Validate tag format."""
        if not v.strip():
            raise ValueError('Tag cannot be empty')
        # Allow alphanumeric, spaces, hyphens, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Tag can only contain letters, numbers, spaces, hyphens, and underscores')
        return v.strip()

class UserBulkUpdate(BaseModel):
    """Schema for bulk user updates."""
    user_ids: List[str] = Field(..., description="List of user IDs to update", min_items=1, max_items=100)
    update_data: UserUpdate = Field(..., description="Data to update for all users")

class UserStatistics(BaseModel):
    """Schema for user statistics response."""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    verified_users: int = Field(..., description="Number of verified users")
    inactive_users: int = Field(..., description="Number of inactive users")
    recent_registrations_30d: int = Field(..., description="New registrations in last 30 days")
    verification_rate: float = Field(..., description="Percentage of verified users")

class APIResponse(BaseModel):
    """Generic API response schema with enhanced structure."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message about the operation")
    data: Optional[Union[dict, list]] = Field(None, description="Response data")
    error_code: Optional[str] = Field(None, description="Error code for debugging")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    
    # Pagination metadata (when applicable)
    pagination: Optional[dict] = Field(None, description="Pagination information")

class PaginatedResponse(APIResponse):
    """Paginated API response schema."""
    pagination: dict = Field(..., description="Pagination metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Users retrieved successfully",
                "data": [],
                "pagination": {
                    "total": 100,
                    "limit": 10,
                    "offset": 0,
                    "has_next": True,
                    "has_previous": False
                }
            }
        } 