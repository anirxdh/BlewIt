from models import db
from models.post import Post
from models.vote import Vote
from models.user import User

class PostService:

    @staticmethod
    def get_all_post():
        results = Post.query.all()
        return results
    
    @staticmethod
    def get_post_by_ID(pid):
        return Post.query.filter_by(pid=pid).first()

    @staticmethod
    def get_posts_by_author_name(author_name):
        results = Post.query.filter_by(author_name=author_name).all()
        return results

    @staticmethod
    def get_posts_by_category(category):
        results = Post.query.filter(Post.category == category).all()
        print(f"Filtering posts for category: {category}, found {len(results)} posts")
        return results


    @staticmethod
    def get_posts_by_categories(categories):
        results = Post.query.filter(Post.category.in_(categories)).all()
        return results


    @staticmethod
    def get_posts_by_title_partial(search_term):
        results = Post.query.filter(Post.title.ilike(f'%{search_term}%')).all()
        return results

    @staticmethod
    def get_posts_by_content_partial(search_term):
        results = Post.query.filter(Post.content.ilike(f'%{search_term}%')).all()
        return results
    
    @staticmethod
    def newpost(titl,cont,cate,usr_name, image):
        new_post = Post(title=titl,content=cont,category=cate,author_name=usr_name, image =image)
        db.session.add(new_post)
        db.session.commit()

        return {"code":200,
                "message":f"New posts added",
                "id":new_post.pid,    
                }
    @staticmethod
    def update_post_by_ID(id,newtitle,newcontent,newimg,newcategory):
        post = Post.query.get(id)
        if post:
            post.title = newtitle
            post.content = newcontent
            post.category = newcategory
            post.image = newimg
            db.session.commit()
            return {"code":200,"message":f"Post with ID {id} is updated"}
        else:
            return {"code":404,"message":f"No posts found with ID {id}"}

    @staticmethod
    def delete_post_by_ID(id):
        post = Post.query.get(id)
        if post:
            post.deleted = True
            db.session.commit()
            return {"code":200,"message":f"Post with ID {id} is deleted"}
        else:
            return {"code":404,"message":f"No posts found with ID {id}"}

    @staticmethod
    def vote_post(pid, username, vote_type):
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"code":404, "message":"User not found"}

        post = Post.query.filter_by(pid=pid).first()
        if not post:
            return {"code":404, "message":"Post not found"}

        vote = Vote.query.filter_by(user_id=user.auth0_id, post_id=pid).first()

        if vote_type == 'undo':
            if vote:
                if vote.vote_type == 'upvote':
                    post.upvotes -= 1
                elif vote.vote_type == 'downvote':
                    post.downvotes -= 1
                db.session.delete(vote)
                db.session.commit()
        else:
            if vote:
                if vote.vote_type == vote_type:
                    # Undo the vote
                    if vote_type == 'upvote':
                        post.upvotes -= 1
                    else:
                        post.downvotes -= 1
                    db.session.delete(vote)
                else:
                    # Change the vote
                    if vote.vote_type == 'upvote':
                        post.upvotes -= 1
                        post.downvotes += 1
                    else:
                        post.downvotes -= 1
                        post.upvotes += 1
                    vote.vote_type = vote_type
            else:
                # New vote
                new_vote = Vote(user_id=user.auth0_id, post_id=pid, vote_type=vote_type)
                db.session.add(new_vote)
                if vote_type == 'upvote':
                    post.upvotes += 1
                else:
                    post.downvotes += 1
            db.session.commit()

        return {"upvotes": post.upvotes, "downvotes": post.downvotes}
   