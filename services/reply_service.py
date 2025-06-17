from models import db
from models.reply import Reply

class ReplyService:
    @staticmethod
    def get_replies_by_post_id(pid):
        results = Reply.query.filter_by(post_id = pid, deleted=False).all()
        return results

    @staticmethod
    def get_replies_by_post_id_sorted(pid, sort):
        if sort == 'upvotes':
            return Reply.query.filter_by(post_id=pid, deleted=False).order_by(Reply.upvotes.desc()).all()
        elif sort == 'downvotes':
            return Reply.query.filter_by(post_id=pid, deleted=False).order_by(Reply.downvotes.desc()).all()
        elif sort == 'newest':
            return Reply.query.filter_by(post_id=pid, deleted=False).order_by(Reply.created_at.desc()).all()
        elif sort == 'oldest':
            return Reply.query.filter_by(post_id=pid, deleted=False).order_by(Reply.created_at.asc()).all()
        else:
            return Reply.query.filter_by(post_id=pid, deleted=False).all()
    
    @staticmethod
    def get_replies_by_content_partial(search_term):
        results = Reply.query.filter(Reply.content.ilike(f'%{search_term}%'),deleted=False).all()
        return results
    
    @staticmethod
    def get_reply_by_cid(cid):
        return Reply.query.filter_by(cid=cid, deleted=False).first()
    
    @staticmethod
    def update_reply_by_cid(cid, content, upvotes, downvotes):
        reply = Reply.query.filter_by(cid=cid).first()
        if reply:
            reply.content = content or reply.content
            if upvotes is not None:
                reply.upvotes = upvotes
            if downvotes is not None:
                reply.downvotes = downvotes
            db.session.commit()
            return reply
        return {"code":404, "message":"Reply not found"}
        
    @staticmethod
    def new_reply(content, username, pid):
        reply = Reply(content=content, author_name=username, post_id=pid)
        db.session.add(reply)
        db.session.commit()
        return reply
    
    @staticmethod
    def delete_reply_by_cid(cid):
        reply = Reply.query.filter_by(cid=cid).first()
        if reply:
            reply.deleted = True
            db.session.commit()
            return {"code":200, "message":"Reply deleted"}
        return {"code":404, "message":"Reply not found"}