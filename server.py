import functools
import os
import requests
from flask import Flask, abort, jsonify, render_template, redirect, url_for, session, flash , request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from models import db
from services.post_service import PostService
from services.user_service import UserService
from services.reply_service import ReplyService
from auth import auth_bp, init_oauth  # Importing the authentication blueprint
from models import Vote

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

upload_url = 'https://api.imgbb.com/1/upload?key=' + os.getenv('IMG_BB_SECRET')
from flask_migrate import Migrate

# Load environment variables
load_dotenv(override=True)

#Declare allowed files validator
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')
db.init_app(app)

init_oauth(app)

# Initialize the database tables
with app.app_context():
    db.create_all()

# Register the authentication blueprint
app.register_blueprint(auth_bp)

migrate = Migrate(app, db)

# Intercepter for any login needed action
def require_auth(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        print("intercepter")
        if 'user' not in session:
            # flash("You need to log in to perform this operation.", "warning")
            return redirect(url_for('auth.login'))  # Unauthorized
        return f(*args, **kwargs)
    return decorated_function

# Home Page
@app.route('/')
def homePage():
    category = request.args.get('category', 'home')
    
    if 'user' in session:
        user_info = session['user']
        category_followed = UserService.get_categories_by_user(user_info["auth0_id"])
        
        if category == 'home':
            posts = PostService.get_posts_by_categories(category_followed)
        else:
            posts = PostService.get_posts_by_category(category)

        return render_template("homePage.html", user=user_info, posts=posts, category_followed=category_followed)
    else:

        if category == 'home':
            posts = PostService.get_all_post()
        else:
            posts = PostService.get_posts_by_category(category)

        return render_template("homePage.html", posts=posts)



@app.route('/profile/<username>')
def profilePage(username):
    if 'user' in session and session['user']['username'] == username:
        user_info = session['user']
        is_current_user = True
    else:
        user_info = UserService.get_user_by_username(username)
        is_current_user = False

    if not user_info:
        flash("User not found.", "warning")
        return redirect(url_for('homePage'))
    
    user_posts = PostService.get_posts_by_author_name(username)
    
    return render_template("myprofile.html", 
                           user=user_info, 
                           posts=user_posts,
                           category_followed = session['user']['category_followed'],
                           is_current_user=is_current_user)

# Database CRUD on post (Login needed)
@app.route('/api/post/', defaults={'pid': None},methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/api/post/<int:pid>',methods=["GET", "POST", "PUT", "DELETE"])
def post(pid):
    if request.method == "POST":
        has_file = False
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            has_file = True
            filename = secure_filename(file.filename)
            file_saved_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_saved_path)
            print("file saved at", file_saved_path)
            file_to_upload = open(file_saved_path, 'rb')
            files = {'image': file_to_upload}  
            print(files)
            response = requests.post(upload_url, files=files)
            response_data = response.json()
            os.remove(file_saved_path)
        image =  response_data["data"]["url"] if has_file else None
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        username = session['user']['username']
        response = PostService.newpost(title, content, category, username, image)
        return redirect(url_for('myprofile'))
        # return response
    elif request.method == "GET":
        pid = request.args.get('pid')
        author_name = request.args.get('author')
        category = request.args.get('category')
        content = request.args.get('content')
        responses = None
        if pid:
            responses = PostService.get_post_by_ID(pid)
        elif author_name:
            responses = PostService.get_posts_by_author_name(author_name)
        elif category and category != 'all':
            print(f"Filtering by category: {category}")
            responses = PostService.get_posts_by_category(category)
        elif content:
            responses = PostService.get_posts_by_content_partial(content)
        else:
            # No specific filter, fetch all posts
            if 'user' in session:
                # If the user is logged in, filter by the categories they follow
                followed_categories = session['user']['category_followed'] 
                print(f"Fetching posts for categories followed by the user: {followed_categories}")
                if followed_categories:
                    responses = PostService.get_posts_by_categories(followed_categories)
                else:
                    responses = PostService.get_all_post()  # User has no followed categories, get all posts
            else:
                # User is not logged in, fetch all posts
                print("User not logged in, fetching all posts")
                responses = PostService.get_all_post()

        if len(responses) <= 0:
            return jsonify({"code":404,"message":"No posts found"})
        else:
            return jsonify([response.to_dict() for response in responses])
    
    elif request.method == "DELETE":
        if pid :
            if 'user' in session:
                post = PostService.get_post_by_ID(pid)
                if session['user']['username'] == post.author_name:           
                    responses = PostService.delete_post_by_ID(pid)
                    return responses
                else:
                    abort(403)
            else:
                abort(403)
        else:
            return jsonify({"code": 400, "message": "Bad Request"})
    elif request.method == "PUT":
        post = PostService.get_post_by_ID(pid)
        if post and post.author_name == session['user']['username']:
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            is_change = request.form.get('isChange') == 'true'
            file = request.files['file']
            if file.filename == '':
                if is_change:
                    # User want to remove the img
                    response = PostService.update_post_by_ID(pid,title,content,None,category)
                    return response
                else:
                    # User want to keep the original img
                    response = PostService.update_post_by_ID(pid,title,content,post.image,category)
                    return response
                # return redirect(request.url)
            if file and allowed_file(file.filename):
                # User want to use a new img
                filename = secure_filename(file.filename)
                file_saved_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_saved_path)
                file_to_upload = open(file_saved_path, 'rb')
                files = {'image': file_to_upload}  
                response = requests.post(upload_url, files=files)
                response_data = response.json()
                os.remove(file_saved_path)
                image =  response_data["data"]["url"]
                response = PostService.update_post_by_ID(pid,title,content,image,category)
                return response
            else:
                # unsupported file type
                abort(403)
        else:   
            abort(403)

# Database CRUD on post - Get post by id, author_name, category, categories, title, and content


# Database CRUD - User
@app.route('/api/user/', defaults={'email': None}, methods=["GET", "POST"])
@app.route('/api/user/<email>',methods=["GET", "POST"])
def user(email):
    if request.method == "POST":
        mail = request.form.get('email')
        category_raw = request.form.get('category')
        username = request.form.get('username')
        category = category_raw.split(';')

        # Check if the username and email is unique
        user = UserService.get_user_by_username(username)
        if user:
            return jsonify({"code":5000,"message":"username already exists"})
        else:
            response = UserService.create_user(mail, category, username)
            return response
    elif request.method == "GET":
        if email:
            responses = UserService.get_user_by_email(email)
            if len(responses) <= 0:
                return jsonify({"code":404,"message":f"no user found with email: {email}"})
            else:
                return jsonify([response.to_dict() for response in responses])
        else:
            return jsonify({"code": 400, "message": "Bad Request"})

# Database CRUD - Reply
@app.route('/api/reply/', defaults={'cid': None},methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/api/reply/<int:cid>', methods=["GET", "POST", "PUT", "DELETE"])
def reply(cid):
    if request.method == "GET":
        pid = request.args.get('pid')
        sort = request.args.get('sort')  # 'upvotes', 'downvotes', 'newest', 'oldest'
        if pid:
            if sort == 'upvotes':
                replies = ReplyService.get_replies_by_post_id_sorted(pid, 'upvotes')
            elif sort == 'downvotes':
                replies = ReplyService.get_replies_by_post_id_sorted(pid, 'downvotes')
            elif sort == 'newest':
                replies = ReplyService.get_replies_by_post_id_sorted(pid, 'newest')
            elif sort == 'oldest':
                replies = ReplyService.get_replies_by_post_id_sorted(pid, 'oldest')
            else:
                replies = ReplyService.get_replies_by_post_id(pid)
            if not replies:
                return jsonify({"code":404,"message":"No replies found"}), 404
            else:
                return jsonify([response.to_dict() for response in replies])
        else:
            if cid:
                reply = ReplyService.get_reply_by_cid(cid)
                if not reply:
                    return jsonify({"code":404,"message":f"No reply found with id {cid}"}), 404
                return jsonify(reply.to_dict())
            else:
                return jsonify({"code":400, "message":"Bad Request"}), 400

    elif request.method == "POST":
        if 'user' not in session:
            return jsonify({"code":401, "message":"Unauthorized"}), 401
        content = request.form.get('content')
        pid = request.form.get('post_id')
        username = session['user']['username']
        post = PostService.get_post_by_ID(pid)
        if not post:
            return jsonify({"code":404,"message":f"No post found with id: {pid}"}), 404
        reply = ReplyService.new_reply(content, username, pid)
        return jsonify(reply.to_dict()), 201

    elif request.method == "DELETE":
        if not cid:
            return jsonify({"code":400, "message": "Bad Request"}), 400
        if 'user' not in session:
            return jsonify({"code":401, "message":"Unauthorized"}), 401
        reply = ReplyService.get_reply_by_cid(cid)
        if not reply:
            return jsonify({"code":404, "message":"Reply not found"}), 404
        if reply.author_name != session['user']['username']:
            return jsonify({"code":403, "message":"Forbidden"}), 403
        responses = ReplyService.delete_reply_by_cid(cid)
        return jsonify({"code":200, "message":"Reply deleted"}), 200

    elif request.method == "PUT":
        if not cid:
            return jsonify({"code":400, "message": "Bad Request"}), 400
        if 'user' not in session:
            return jsonify({"code":401, "message":"Unauthorized"}), 401
        content = request.form.get('content')
        upvotes = request.form.get('upvotes')
        downvotes = request.form.get('downvotes')

        reply = ReplyService.get_reply_by_cid(cid)
        if not reply:
            return jsonify({"code":404, "message":"Reply not found"}), 404
        if reply.author_name != session['user']['username']:
            return jsonify({"code":403, "message":"Forbidden"}), 403

        response = ReplyService.update_reply_by_cid(cid, content, upvotes, downvotes)
        return jsonify(response.to_dict()), 200

# Create New Post
@app.route("/newpost", methods=["GET"])
def new_post():
    if 'user' in session:
    
        user_info = session['user']
        user_posts = PostService.get_posts_by_author_name(user_info['username'])
        category_followed = UserService.get_categories_by_user(user_info["auth0_id"])
        print(user_posts)  
    return render_template("newpost.html", category_followed=category_followed)

@app.route("/api/updateuser",methods=["POST"])
def update_user():
    user_id = session['user']['auth0_id']
    user_newname = request.form.get('username')
    if UserService.get_user_by_username(user_newname):
        flash('Username is already taken, please choose another one.', 'error')
        return render_template('update_username.html')
    
    response = UserService.update_user_by_auth0_id(user_id,user_newname)
    session['user']['username'] = user_newname
    session.modified = True
    return redirect(url_for('myprofile'))

# My Profile Page
@app.route('/myprofile')
def myprofile():
    username = request.args.get('username')
    
    if not username and 'user' in session:
        username = session['user']['username']
    
    profile_user = UserService.get_user_by_username(username)
    if not profile_user:
        flash(f"No user found with username {username}", "error")
        return redirect(url_for('homePage'))

    user_posts = PostService.get_posts_by_author_name(username)
    
    is_current_user = 'user' in session and session['user']['username'] == username

    return render_template("myprofile.html", 
                           user=profile_user.to_dict(), 
                           category_followed = session['user']['category_followed'],
                           posts=user_posts, 
                           is_current_user=is_current_user,
                           username=profile_user.username,
                           email=profile_user.email)

# View a post
@app.route('/viewpost')
def viewpost():
    pid = request.args.get('pid')
    if not pid:
        flash("Post ID not provided.", "warning")
        return redirect(url_for('homePage'))
    post = PostService.get_post_by_ID(pid)
    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for('homePage'))
    replies = ReplyService.get_replies_by_post_id(pid)
    if 'user' in session:
        user_info = session['user']
        category_followed = UserService.get_categories_by_user(user_info["auth0_id"])
        return render_template("viewPost.html", post=post, replies=replies, category_followed=category_followed, current_user=session['user']['username'])
    else:
        return render_template("viewPost.html", post=post, replies=replies)
    
# Needs login
@app.route('/edituser',methods=["GET"])
@require_auth
def editUserPage():
    return render_template("update_username.html")


@app.route('/api/user/categories/<username>')
def get_user_categories(username):
    if session.get('user') and session['user']['username'] == username:
        return jsonify(session['user']['category_followed'])
    else:
        return jsonify([]), 404


@app.route('/api/user/categories/', methods=['PUT']) 
@require_auth
def update_user_categories():
    print("Called category update API")  
    uid = session['user']['auth0_id']
    user = UserService.get_user_by_auth0_id(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    categories = request.json.get('categories')
    print(f"Categories received for update: {categories}") 

    
    UserService.update_user_category_by_auth0_id(uid, categories)
    
    # Updating session with new category_followed data
    session['user']['category_followed'] = categories
    session.modified = True  # Ensuring session changes are saved
    print(f"Updated session categories: {session['user']['category_followed']}") 

    return jsonify({"message": "Categories updated"}), 200


@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return render_template('search_results.html')
 

    posts_by_title = PostService.get_posts_by_title_partial(query)
    posts_by_content = PostService.get_posts_by_content_partial(query)

    posts = list({post.pid: post for post in posts_by_title + posts_by_content}.values())

    if not posts:
        flash(f'No posts found for "{query}".', "info")


    return render_template('search_results.html', query=query, posts=posts)
@app.route('/api/post/<int:pid>/vote', methods=['POST'])
def vote_post(pid):
    if 'user' not in session:
        return jsonify({"code": 401, "message": "Unauthorized"}), 401
    
    vote_type = request.json.get('vote')  # 'upvote', 'downvote', 'undo'
    username = session['user']['username']
    user_id = session['user']['auth0_id']

    # Fetch user
    user = UserService.get_user_by_username(username)
    if not user:
        return jsonify({"code": 404, "message": "User not found"}), 404

    # Fetch post
    post = PostService.get_post_by_ID(pid)
    if not post:
        return jsonify({"code": 404, "message": "Post not found"}), 404

    # Check existing vote
    existing_vote = Vote.query.filter_by(user_id=user_id, post_id=pid).first()

    if vote_type == 'undo':
        # Undo the existing vote if it exists
        if existing_vote:
            if existing_vote.vote_type == 'upvote':
                post.upvotes = max(0, post.upvotes - 1)
            elif existing_vote.vote_type == 'downvote':
                post.downvotes = max(0, post.downvotes - 1)
            db.session.delete(existing_vote)
            db.session.commit()
    else:
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # If user is clicking the same vote again, undo it
                if vote_type == 'upvote':
                    post.upvotes = max(0, post.upvotes - 1)
                else:
                    post.downvotes = max(0, post.downvotes - 1)
                db.session.delete(existing_vote)
            else:
                # User is switching from upvote to downvote or vice versa
                if existing_vote.vote_type == 'upvote':
                    post.upvotes = max(0, post.upvotes - 1)
                else:
                    post.downvotes = max(0, post.downvotes - 1)
                
                # Update the existing vote
                existing_vote.vote_type = vote_type
                if vote_type == 'upvote':
                    post.upvotes += 1
                else:
                    post.downvotes += 1
        else:
            # New vote
            new_vote = Vote(user_id=user_id, post_id=pid, vote_type=vote_type)
            db.session.add(new_vote)
            if vote_type == 'upvote':
                post.upvotes += 1
            else:
                post.downvotes += 1

        db.session.commit()

    return jsonify({"upvotes": post.upvotes, "downvotes": post.downvotes}), 200

# Handle voting on replies
@app.route('/api/reply/<int:cid>/vote', methods=['POST'])
def vote_reply(cid):
    if 'user' not in session:
        return jsonify({"code":401, "message":"Unauthorized"}), 401
    vote_type = request.json.get('vote')  # 'upvote', 'downvote', 'undo'
    username = session['user']['username']
    user_id = session['user']['auth0_id']

    # Fetch user
    user = UserService.get_user_by_username(username)
    if not user:
        return jsonify({"code":404, "message":"User not found"}), 404

    # Fetch reply
    reply = ReplyService.get_reply_by_cid(cid)
    if not reply:
        return jsonify({"code":404, "message":"Reply not found"}), 404

    # Check existing vote
    existing_vote = Vote.query.filter_by(user_id=user_id, reply_id=cid).first()

    if vote_type == 'undo':
        if existing_vote:
            if existing_vote.vote_type == 'upvote':
                reply.upvotes -= 1
            elif existing_vote.vote_type == 'downvote':
                reply.downvotes -= 1
            db.session.delete(existing_vote)
            db.session.commit()
    else:
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # User is toggling the same vote, undo it
                if vote_type == 'upvote':
                    reply.upvotes -= 1
                else:
                    reply.downvotes -= 1
                db.session.delete(existing_vote)
            else:
                # User is changing vote
                if existing_vote.vote_type == 'upvote':
                    reply.upvotes -= 1
                else:
                    reply.downvotes -= 1
                existing_vote.vote_type = vote_type
                if vote_type == 'upvote':
                    reply.upvotes += 1
                else:
                    reply.downvotes += 1
        else:
            # New vote
            new_vote = Vote(user_id=user_id, reply_id=cid, vote_type=vote_type)
            print(new_vote)
            db.session.add(new_vote)
            if vote_type == 'upvote':
                reply.upvotes += 1
            else:
                reply.downvotes += 1

        db.session.commit()

    return jsonify({"upvotes": reply.upvotes, "downvotes": reply.downvotes}), 200

@app.route('/editpost/<pid>',methods=['GET'])
@require_auth
def update_post_page(pid):
    post = PostService.get_post_by_ID(pid)
    if post and post.author_name == session['user']['username'] and not post.deleted:
        return render_template("update_post.html",post=post,category_followed=session['user']['category_followed'])
    else:
        abort(403)


@app.route('/editreply/<cid>',methods=["GET"])
@require_auth
def update_reply_page(cid):
    reply = ReplyService.get_reply_by_cid(cid)
    pid = request.args.get("pid")
    print(pid)
    if reply and reply.author_name == session['user']['username'] and not reply.deleted:
        return render_template("update_reply.html",reply=reply,category_followed=session['user']['category_followed'],pid=pid)
    else:
        abort(403)
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
