from mongoengine import IntField, StringField, DateTimeField, EmailField, BooleanField, ListField
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.core.base import BaseModel

class RegisteredUser(BaseModel):
    """Enhanced model for storing user registration information."""

    # Core user information
    user_id = IntField(required=True, help_text="Discord user ID")
    guild_id = IntField(required=True, help_text="Discord guild/server ID")
    real_name = StringField(required=True, max_length=100, help_text="User's real name")
    email = EmailField(required=True, help_text="User's email address")
    
    # Optional profile information
    source = StringField(max_length=200, help_text="Registration source (e.g., magic_link, form)")
    education_stage = StringField(max_length=50, help_text="Current education level")
    avatar_base64 = StringField(help_text="Base64 encoded user avatar")
    
    # Additional profile fields for extensibility
    bio = StringField(max_length=500, help_text="User biography")
    location = StringField(max_length=100, help_text="User location")
    website = StringField(max_length=200, help_text="Personal website URL")
    github_username = StringField(max_length=50, help_text="GitHub username")
    linkedin_url = StringField(max_length=200, help_text="LinkedIn profile URL")
    
    # System fields
    is_active = BooleanField(default=True, help_text="Whether the user account is active")
    is_verified = BooleanField(default=False, help_text="Whether the user email is verified")
    tags = ListField(StringField(max_length=50), help_text="User tags for categorization")
    
    # Timestamps
    registered_at = DateTimeField(default=datetime.utcnow, help_text="Registration timestamp")
    last_updated = DateTimeField(default=datetime.utcnow, help_text="Last update timestamp")
    last_login = DateTimeField(help_text="Last login timestamp")

    meta = {
        'collection': 'registered_users',
        'indexes': [
            ('user_id', 'guild_id'),  # Compound index for Discord lookups
            'email',                   # Index for email lookups
            'is_active',              # Index for filtering active users
            'registered_at',          # Index for date-based queries
            'tags',                   # Index for tag-based searches
            {
                'fields': ['email'],
                'unique': True,
                'sparse': True
            },  # Unique email constraint
            {
                'fields': ['user_id', 'guild_id'],
                'unique': True
            }  # Unique Discord user per guild
        ],
        'ordering': ['-registered_at']  # Default ordering by registration date
    }
    
    def clean(self):
        """Custom validation before saving."""
        super().clean()
        
        # Update last_updated timestamp on save
        self.last_updated = datetime.utcnow()
        
        # Validate email format (additional validation beyond EmailField)
        if self.email and '@' not in self.email:
            raise ValueError("Invalid email format")
        
        # Validate user_id and guild_id are positive
        if self.user_id and self.user_id <= 0:
            raise ValueError("User ID must be positive")
        if self.guild_id and self.guild_id <= 0:
            raise ValueError("Guild ID must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for API response with enhanced formatting."""
        result = super().to_dict()
        
        # Format datetime fields consistently
        if self.registered_at:
            result['registered_at'] = self.registered_at.isoformat()
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
        if self.last_login:
            result['last_login'] = self.last_login.isoformat()
        
        # Add computed fields
        result['display_name'] = self.get_display_name()
        result['profile_completeness'] = self.get_profile_completeness()
        
        return result
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with only public information."""
        return {
            'id': str(self.id),
            'real_name': self.real_name,
            'bio': self.bio,
            'location': self.location,
            'website': self.website,
            'github_username': self.github_username,
            'linkedin_url': self.linkedin_url,
            'tags': self.tags or [],
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'display_name': self.get_display_name()
        }
    
    def get_display_name(self) -> str:
        """Get user's display name."""
        return self.real_name or f"User_{self.user_id}"
    
    def get_profile_completeness(self) -> float:
        """Calculate profile completeness percentage."""
        total_fields = ['real_name', 'email', 'bio', 'location', 'avatar_base64']
        completed_fields = 0
        
        for field in total_fields:
            if getattr(self, field, None):
                completed_fields += 1
        
        return (completed_fields / len(total_fields)) * 100
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        self.save()
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.save()
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.save()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the user."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the user."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.save()
    
    @classmethod
    def get_by_discord_id(cls, user_id: int, guild_id: int) -> Optional['RegisteredUser']:
        """Get user by Discord user_id and guild_id."""
        return cls.objects(user_id=user_id, guild_id=guild_id).first()
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['RegisteredUser']:
        """Get user by email address."""
        return cls.objects(email=email).first()
    
    @classmethod
    def get_active_users(cls, limit: int = 100, offset: int = 0) -> List['RegisteredUser']:
        """Get list of active users."""
        return list(cls.objects(is_active=True).skip(offset).limit(limit))
    
    @classmethod
    def search_by_name(cls, name: str, limit: int = 20) -> List['RegisteredUser']:
        """Search users by name (case-insensitive)."""
        return list(cls.objects(real_name__icontains=name, is_active=True).limit(limit))
    
    @classmethod
    def get_by_tag(cls, tag: str, limit: int = 50) -> List['RegisteredUser']:
        """Get users by tag."""
        return list(cls.objects(tags=tag, is_active=True).limit(limit))
    
    def __str__(self):
        return f"RegisteredUser(user_id={self.user_id}, email={self.email}, active={self.is_active})"
    
    def __repr__(self):
        return f"<RegisteredUser {self.id}: {self.email}>" 