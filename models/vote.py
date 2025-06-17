from . import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class Vote(db.Model):
    __tablename__ = 'votes'
    vid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.auth0_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.pid'), nullable=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('replies.cid'), nullable=True)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='votes')
    post = db.relationship('Post', backref='votes')
    reply = db.relationship('Reply', backref='votes')