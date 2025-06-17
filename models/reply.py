from . import db
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import ARRAY

class Reply(db.Model):
    __tablename__ = 'replies'
    
    cid = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    author_name = Column(String(255), ForeignKey('users.username', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.pid', ondelete='CASCADE'), nullable=False)
    deleted = Column(Boolean, default=False)
    
    # Relationships
    author = db.relationship('User', back_populates='replies')
    post = db.relationship('Post', back_populates='replies')

    def to_dict(self):
        return {
            'cid': self.cid,
            'content': self.content,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author_name': self.author_name,
            'post_id': self.post_id,
            'deleted': self.deleted
        }