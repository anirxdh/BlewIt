from flask import Blueprint, redirect, url_for, session, flash, request, render_template
from authlib.integrations.flask_client import OAuth
import os
from services.user_service import UserService

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

auth0 = None

def init_oauth(app):
    global auth0
    oauth.init_app(app)
    auth0 = oauth.register(
        'auth0',
        client_id=os.getenv('AUTH0_CLIENT_ID'),
        client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
        api_base_url=f'https://{os.getenv("AUTH0_DOMAIN")}',
        access_token_url=f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token',
        authorize_url=f'https://{os.getenv("AUTH0_DOMAIN")}/authorize',
        client_kwargs={'scope': 'openid profile email'},
        server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )

@auth_bp.route('/signup')
def signup():
    return auth0.authorize_redirect(redirect_uri=url_for('auth.callback', _external=True), screen_hint='signup')

@auth_bp.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('auth.callback', _external=True))

@auth_bp.route('/callback')
def callback():
    auth0.authorize_access_token()
    user_info = auth0.get('userinfo').json()
    
    # Print the user_info object to see if email exists
    print("User Info received from Auth0:", user_info)

    auth0_id = user_info['sub']
    user = UserService.get_user_by_auth0_id(auth0_id)
    
    if user:
        # Check if the email exists in the user object
        print("User found in database. Email:", user.email)

        session['user'] = {'username': user.username, 'auth0_id': user.auth0_id, 'email': user.email,'category_followed':user.category_followed}
        return redirect(url_for('myprofile', username=user.username))
    else:
        session['user_info'] = user_info
        return redirect(url_for('auth.create_username'))

@auth_bp.route('/create_username', methods=['GET', 'POST'])
def create_username():
    user_info = session.get('user_info')
    
    # Print user_info from the session to ensure email exists
    print("User Info in session (during username creation):", user_info)
    
    if request.method == 'POST':
        username = request.form['username'].strip()

        categories_followed = request.form.getlist('categories_followed')
        print(categories_followed)
        if not categories_followed:
            flash('Please select at least one category to follow.', 'error')
            return render_template('create_username.html')


        if UserService.get_user_by_username(username):
            flash('Username is already taken, please choose another one.', 'error')
            return render_template('create_username.html')

        if user_info:
            # Ensure the email is being saved when creating the user
            print("Creating new user with email:", user_info.get('email'))

            UserService.create_user(auth0_id=user_info['sub'], username=username, email=user_info['email'],category_followed=categories_followed)
            session['user'] = {'username': username, 'auth0_id': user_info['sub'], 'email': user_info['email'], 'category_followed':categories_followed}
            session.pop('user_info', None)
            return redirect(url_for('myprofile', username=username))
# session['user']
    return render_template('create_username.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?client_id={os.getenv("AUTH0_CLIENT_ID")}&returnTo={url_for("homePage", _external=True)}')
