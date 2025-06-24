from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from mongoengine import Document
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class BaseModel(Document):
    """Base model class with common functionality for all models."""
    
    meta = {
        'abstract': True,
        'indexes': []
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for API response."""
        result = {}
        for field_name in self._fields:
            field_value = getattr(self, field_name, None)
            if field_value is not None:
                if isinstance(field_value, ObjectId):
                    result[field_name] = str(field_value)
                elif isinstance(field_value, datetime):
                    result[field_name] = field_value.isoformat()
                else:
                    result[field_name] = field_value
        
        # Add the MongoDB ObjectId as 'id'
        result['id'] = str(self.id)
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude_fields: Optional[List[str]] = None) -> None:
        """Update model fields from dictionary data."""
        exclude_fields = exclude_fields or ['id', '_id']
        
        for field_name, field_value in data.items():
            if field_name not in exclude_fields and hasattr(self, field_name):
                setattr(self, field_name, field_value)
    
    @classmethod
    def get_field_names(cls) -> List[str]:
        """Get list of all field names for this model."""
        return list(cls._fields.keys())
    
    @classmethod
    def get_required_fields(cls) -> List[str]:
        """Get list of required field names for this model."""
        required_fields = []
        for field_name, field in cls._fields.items():
            if getattr(field, 'required', False):
                required_fields.append(field_name)
        return required_fields
    
    def validate_required_fields(self) -> List[str]:
        """Validate that all required fields have values. Returns list of missing fields."""
        missing_fields = []
        for field_name in self.get_required_fields():
            if not getattr(self, field_name, None):
                missing_fields.append(field_name)
        return missing_fields


class BaseService(ABC):
    """Abstract base service class for all model services."""
    
    model_class: Type[BaseModel] = None
    
    @classmethod
    @abstractmethod
    def get_model_class(cls) -> Type[BaseModel]:
        """Return the model class this service manages."""
        pass
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[BaseModel]:
        """Create a new model instance."""
        try:
            model_class = cls.get_model_class()
            instance = model_class(**data)
            
            # Validate required fields
            missing_fields = instance.validate_required_fields()
            if missing_fields:
                logger.error(f"Missing required fields for {model_class.__name__}: {missing_fields}")
                return None
            
            instance.save()
            logger.info(f"Created {model_class.__name__}: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error creating {cls.get_model_class().__name__}: {str(e)}")
            return None
    
    @classmethod
    def get_by_id(cls, object_id: str) -> Optional[BaseModel]:
        """Get model instance by MongoDB ObjectId."""
        try:
            model_class = cls.get_model_class()
            return model_class.objects(id=object_id).first()
        except Exception as e:
            logger.error(f"Error getting {cls.get_model_class().__name__} by id {object_id}: {str(e)}")
            return None
    
    @classmethod
    def update(cls, object_id: str, data: Dict[str, Any]) -> Optional[BaseModel]:
        """Update model instance."""
        try:
            model_class = cls.get_model_class()
            instance = model_class.objects(id=object_id).first()
            if not instance:
                return None
            
            instance.update_from_dict(data)
            instance.save()
            logger.info(f"Updated {model_class.__name__}: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error updating {cls.get_model_class().__name__} {object_id}: {str(e)}")
            return None
    
    @classmethod
    def delete(cls, object_id: str) -> bool:
        """Delete model instance."""
        try:
            model_class = cls.get_model_class()
            instance = model_class.objects(id=object_id).first()
            if not instance:
                return False
            
            instance.delete()
            logger.info(f"Deleted {model_class.__name__}: {object_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {cls.get_model_class().__name__} {object_id}: {str(e)}")
            return False
    
    @classmethod
    def list_all(cls, limit: int = 100, offset: int = 0) -> List[BaseModel]:
        """List all model instances with pagination."""
        try:
            model_class = cls.get_model_class()
            return list(model_class.objects.skip(offset).limit(limit))
        except Exception as e:
            logger.error(f"Error listing {cls.get_model_class().__name__}: {str(e)}")
            return []
    
    @classmethod
    def count(cls) -> int:
        """Get total count of model instances."""
        try:
            model_class = cls.get_model_class()
            return model_class.objects.count()
        except Exception as e:
            logger.error(f"Error counting {cls.get_model_class().__name__}: {str(e)}")
            return 0 