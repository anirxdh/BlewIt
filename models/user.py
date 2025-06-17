from . import db
from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import ARRAY

class User(db.Model):
    __tablename__ = 'users'

    auth0_id = Column(String(255), primary_key=True, unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    category_followed = Column(ARRAY(Text))  # PostgreSQL ARRAY type

    posts = db.relationship('Post', back_populates='author', cascade="all, delete")
    replies = db.relationship('Reply', back_populates='author', cascade="all, delete")

    def to_dict(self):
        return {
            'auth0_id': self.auth0_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_followed': self.category_followed,
            'posts': [post.to_dict() for post in self.posts],
            'replies': [reply.to_dict() for reply in self.replies]
        }
