from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .user import User
from .post import Post
from .reply import Reply
from .vote import Vote