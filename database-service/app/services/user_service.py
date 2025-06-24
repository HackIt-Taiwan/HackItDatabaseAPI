from typing import Optional, List, Dict, Any
from mongoengine import DoesNotExist, ValidationError
import logging
from datetime import datetime

from app.models.user import RegisteredUser
from app.schemas.user import UserCreate, UserUpdate, UserQuery
from app.core.base import BaseService

logger = logging.getLogger(__name__)

class UserService(BaseService):
    """Enhanced service class for user-related database operations."""
    
    @classmethod
    def get_model_class(cls):
        """Return the RegisteredUser model class."""
        return RegisteredUser
    
    @classmethod
    def create_user(cls, user_data: UserCreate) -> Optional[RegisteredUser]:
        """Create a new user with enhanced validation."""
        try:
            # Check if user already exists by Discord ID
            existing_user = RegisteredUser.get_by_discord_id(
                user_data.user_id, 
                user_data.guild_id
            )
            
            if existing_user:
                logger.warning(
                    f"User already exists with Discord ID: user_id={user_data.user_id}, "
                    f"guild_id={user_data.guild_id}"
                )
                return None
            
            # Check if email is already taken
            existing_email = RegisteredUser.get_by_email(user_data.email)
            if existing_email:
                logger.warning(f"Email already exists: {user_data.email}")
                return None
            
            # Convert Pydantic model to dict
            user_dict = user_data.model_dump(exclude_unset=True)
            
            # Create new user using base service
            user = cls.create(user_dict)
            if user:
                logger.info(f"Created user: {user.email} (Discord: {user.user_id})")
            
            return user
            
        except ValidationError as e:
            logger.error(f"Validation error creating user: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    @classmethod
    def get_user_by_id(cls, user_object_id: str) -> Optional[RegisteredUser]:
        """Get user by MongoDB ObjectId."""
        return cls.get_by_id(user_object_id)
    
    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[RegisteredUser]:
        """Get user by email address."""
        try:
            return RegisteredUser.get_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    @classmethod
    def get_user_by_user_id(cls, user_id: int, guild_id: int) -> Optional[RegisteredUser]:
        """Get user by Discord user_id and guild_id."""
        try:
            return RegisteredUser.get_by_discord_id(user_id, guild_id)
        except Exception as e:
            logger.error(f"Error getting user by Discord ID {user_id}, guild {guild_id}: {str(e)}")
            return None
    
    @classmethod
    def update_user(cls, user_object_id: str, user_data: UserUpdate) -> Optional[RegisteredUser]:
        """Update user information with enhanced validation."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                logger.warning(f"User not found for update: {user_object_id}")
                return None
            
            # Get only the fields that were provided (exclude unset)
            update_data = user_data.model_dump(exclude_unset=True)
            
            # Check if email is being changed and if new email already exists
            if 'email' in update_data and update_data['email'] != user.email:
                existing_email = RegisteredUser.get_by_email(update_data['email'])
                if existing_email and str(existing_email.id) != user_object_id:
                    logger.warning(f"Cannot update to existing email: {update_data['email']}")
                    return None
            
            # Update fields
            user.update_from_dict(update_data)
            user.save()
            
            logger.info(f"Updated user: {user.email}")
            return user
            
        except ValidationError as e:
            logger.error(f"Validation error updating user {user_object_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_object_id}: {str(e)}")
            return None
    
    @classmethod
    def delete_user(cls, user_object_id: str) -> bool:
        """Delete user by id."""
        return cls.delete(user_object_id)
    
    @classmethod
    def deactivate_user(cls, user_object_id: str) -> bool:
        """Deactivate user instead of deleting."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.deactivate()
            logger.info(f"Deactivated user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_object_id}: {str(e)}")
            return False
    
    @classmethod
    def activate_user(cls, user_object_id: str) -> bool:
        """Activate deactivated user."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.activate()
            logger.info(f"Activated user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user {user_object_id}: {str(e)}")
            return False
    
    @classmethod
    def update_user_login(cls, user_object_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.update_last_login()
            logger.info(f"Updated login timestamp for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating login for user {user_object_id}: {str(e)}")
            return False
    
    @classmethod
    def query_users(cls, query: UserQuery) -> List[RegisteredUser]:
        """Query users with enhanced filters."""
        try:
            queryset = RegisteredUser.objects
            
            # Apply filters
            if query.email:
                queryset = queryset.filter(email=query.email)
            if query.user_id is not None:
                queryset = queryset.filter(user_id=query.user_id)
            if query.guild_id is not None:
                queryset = queryset.filter(guild_id=query.guild_id)
            if query.is_active is not None:
                queryset = queryset.filter(is_active=query.is_active)
            if query.is_verified is not None:
                queryset = queryset.filter(is_verified=query.is_verified)
            if query.tag:
                queryset = queryset.filter(tags=query.tag)
            if query.search_name:
                queryset = queryset.filter(real_name__icontains=query.search_name)
            if query.education_stage:
                queryset = queryset.filter(education_stage=query.education_stage)
            
            # Apply date filters
            if query.registered_after:
                queryset = queryset.filter(registered_at__gte=query.registered_after)
            if query.registered_before:
                queryset = queryset.filter(registered_at__lte=query.registered_before)
            
            # Apply ordering
            if query.order_by:
                if query.order_by.startswith('-'):
                    queryset = queryset.order_by(query.order_by)
                else:
                    queryset = queryset.order_by(f'-{query.order_by}')
            
            # Apply pagination
            queryset = queryset.skip(query.offset).limit(query.limit)
            
            return list(queryset)
            
        except Exception as e:
            logger.error(f"Error querying users: {str(e)}")
            return []
    
    @classmethod
    def get_user_count(cls, active_only: bool = False) -> int:
        """Get total user count with optional active filter."""
        try:
            if active_only:
                return RegisteredUser.objects(is_active=True).count()
            return RegisteredUser.objects.count()
        except Exception as e:
            logger.error(f"Error getting user count: {str(e)}")
            return 0
    
    @classmethod
    def search_users_by_name(cls, name: str, limit: int = 20) -> List[RegisteredUser]:
        """Search users by name (case-insensitive)."""
        try:
            return RegisteredUser.search_by_name(name, limit)
        except Exception as e:
            logger.error(f"Error searching users by name '{name}': {str(e)}")
            return []
    
    @classmethod
    def get_users_by_tag(cls, tag: str, limit: int = 50) -> List[RegisteredUser]:
        """Get users by specific tag."""
        try:
            return RegisteredUser.get_by_tag(tag, limit)
        except Exception as e:
            logger.error(f"Error getting users by tag '{tag}': {str(e)}")
            return []
    
    @classmethod
    def add_user_tag(cls, user_object_id: str, tag: str) -> bool:
        """Add a tag to user."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.add_tag(tag)
            logger.info(f"Added tag '{tag}' to user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tag to user {user_object_id}: {str(e)}")
            return False
    
    @classmethod
    def remove_user_tag(cls, user_object_id: str, tag: str) -> bool:
        """Remove a tag from user."""
        try:
            user = RegisteredUser.objects(id=user_object_id).first()
            if not user:
                return False
            
            user.remove_tag(tag)
            logger.info(f"Removed tag '{tag}' from user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing tag from user {user_object_id}: {str(e)}")
            return False
    
    @classmethod
    def get_user_statistics(cls) -> Dict[str, Any]:
        """Get user statistics for analytics."""
        try:
            total_users = RegisteredUser.objects.count()
            active_users = RegisteredUser.objects(is_active=True).count()
            verified_users = RegisteredUser.objects(is_verified=True).count()
            
            # Get registration stats for last 30 days
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = RegisteredUser.objects(
                registered_at__gte=thirty_days_ago
            ).count()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'inactive_users': total_users - active_users,
                'recent_registrations_30d': recent_registrations,
                'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}
    
    @classmethod
    def bulk_update_users(cls, user_ids: List[str], update_data: Dict[str, Any]) -> int:
        """Bulk update multiple users."""
        updated_count = 0
        try:
            for user_id in user_ids:
                user = RegisteredUser.objects(id=user_id).first()
                if user:
                    user.update_from_dict(update_data)
                    user.save()
                    updated_count += 1
            
            logger.info(f"Bulk updated {updated_count} users")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            return updated_count 