from models import db
from models.user import User

class UserService:
    @staticmethod
    def create_user(auth0_id, username, email, category_followed):
        new_user = User(auth0_id=auth0_id, username=username, email=email, category_followed = category_followed)
        db.session.add(new_user)
        db.session.commit()
        return {
            "code": 200,
            "message": "New user added",
            "username": new_user.username,
            "email": new_user.email ,
            "category_followed": category_followed
        }
    
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_auth0_id(auth0_id):
        return User.query.filter_by(auth0_id=auth0_id).first()

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_user_by_email(email, newusername, newcategories):
        user = User.query.filter_by(email=email).first()
        if user:
            user.username = newusername
            user.category_followed = newcategories
            db.session.commit()

    @staticmethod
    def update_user_by_auth0_id(id, newusername):
        user = User.query.filter_by(auth0_id=id).first()
        if user:            
            user.username = newusername
            db.session.commit()
            return {
                "code": 200,
                "message": f"User {user.auth0_id} updated",   
            } 
    @staticmethod

    def update_user_category_by_auth0_id(id, newcat):
        user = User.query.filter_by(auth0_id=id).first()
        if user:            
            user.category_followed = newcat
            db.session.commit()
            return {
                "code": 200,
                "message": f"User {user.auth0_id} updated",   
            }  
        

    @staticmethod
    def get_categories_by_user(id):
        return User.query.filter_by(auth0_id=id).first().category_followed
           