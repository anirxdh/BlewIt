from . import db
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import ARRAY

class Post(db.Model):
    __tablename__ = 'posts'
    
    pid = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(Text, nullable=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    author_name = Column(String(255), ForeignKey('users.username', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    category = Column(Text, nullable=False) # consider change to ARRAY(TEXT)
    deleted = Column(Boolean, default=False)
    
    # Relationships
    author = db.relationship('User', back_populates='posts')
    replies = db.relationship('Reply', back_populates='post', cascade="all, delete")

    def to_dict(self):
        return {
            'pid': self.pid,
            'title': self.title,
            'content': self.content,
            'upvotes': self.upvotes,
            'image': self.image,
            'downvotes': self.downvotes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author_name': self.author_name,
            'category': self.category,
            'deleted': self.deleted,
            'replies': [reply.to_dict() for reply in self.replies]  # Include related replies
        }