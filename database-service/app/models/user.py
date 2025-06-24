from mongoengine import Document, IntField, StringField, DateTimeField
from datetime import datetime

class RegisteredUser(Document):
    """Model for storing user registration information."""

    user_id = IntField(required=True)
    guild_id = IntField(required=True)
    real_name = StringField(required=True, max_length=100)
    email = StringField(required=True, max_length=200)
    source = StringField(max_length=200)
    education_stage = StringField(max_length=50)
    avatar_base64 = StringField()  # Base64 encoded user avatar
    registered_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'registered_users',
        'indexes': [
            ('user_id', 'guild_id'),
            'email',
        ]
    }

    def to_dict(self):
        """Convert document to dictionary for API response."""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'guild_id': self.guild_id,
            'real_name': self.real_name,
            'email': self.email,
            'source': self.source,
            'education_stage': self.education_stage,
            'avatar_base64': self.avatar_base64,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None
        }

    def __str__(self):
        return f"RegisteredUser(user_id={self.user_id}, email={self.email})" 