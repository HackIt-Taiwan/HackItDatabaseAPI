from typing import Optional, List
from mongoengine import DoesNotExist
import logging

from app.models.user import RegisteredUser
from app.schemas.user import UserCreate, UserUpdate, UserQuery

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related database operations."""
    
    @staticmethod
    def create_user(user_data: UserCreate) -> Optional[RegisteredUser]:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = RegisteredUser.objects(
                user_id=user_data.user_id,
                guild_id=user_data.guild_id
            ).first()
            
            if existing_user:
                logger.warning(f"User already exists: user_id={user_data.user_id}, guild_id={user_data.guild_id}")
                return None
            
            # Create new user
            user = RegisteredUser(
                user_id=user_data.user_id,
                guild_id=user_data.guild_id,
                real_name=user_data.real_name,
                email=user_data.email,
                source=user_data.source,
                education_stage=user_data.education_stage,
                avatar_base64=user_data.avatar_base64
            )
            user.save()
            logger.info(f"Created user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_object_id: str) -> Optional[RegisteredUser]:
        """Get user by MongoDB ObjectId."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            return user
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting user by id {user_object_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[RegisteredUser]:
        """Get user by email address."""
        try:
            user = RegisteredUser.objects(email=email).first()
            return user
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_user_id(user_id: int, guild_id: int) -> Optional[RegisteredUser]:
        """Get user by user_id and guild_id."""
        try:
            user = RegisteredUser.objects(user_id=user_id, guild_id=guild_id).first()
            return user
        except DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting user by user_id {user_id}, guild_id {guild_id}: {str(e)}")
            return None
    
    @staticmethod
    def update_user(user_object_id: str, user_data: UserUpdate) -> Optional[RegisteredUser]:
        """Update user information."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return None
            
            # Update only provided fields
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.save()
            logger.info(f"Updated user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user_object_id}: {str(e)}")
            return None
    
    @staticmethod
    def delete_user(user_object_id: str) -> bool:
        """Delete user by id."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.delete()
            logger.info(f"Deleted user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_object_id}: {str(e)}")
            return False
    
    @staticmethod
    def query_users(query: UserQuery) -> List[RegisteredUser]:
        """Query users with filters."""
        try:
            queryset = RegisteredUser.objects
            
            # Apply filters
            if query.email:
                queryset = queryset.filter(email=query.email)
            if query.user_id:
                queryset = queryset.filter(user_id=query.user_id)
            if query.guild_id:
                queryset = queryset.filter(guild_id=query.guild_id)
            
            # Apply pagination
            queryset = queryset.skip(query.offset).limit(query.limit)
            
            return list(queryset)
            
        except Exception as e:
            logger.error(f"Error querying users: {str(e)}")
            return []
    
    @staticmethod
    def get_user_count() -> int:
        """Get total user count."""
        try:
            return RegisteredUser.objects.count()
        except Exception as e:
            logger.error(f"Error getting user count: {str(e)}")
            return 0 