from flask import Flask, redirect, render_template, session, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url='https://' + os.getenv("AUTH0_DOMAIN"),
    access_token_url='https://' + os.getenv("AUTH0_DOMAIN") + '/oauth/token',
    authorize_url='https://' + os.getenv("AUTH0_DOMAIN") + '/authorize',
    client_kwargs={'scope': 'openid profile email'},
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    session['user'] = auth0.parse_id_token(token)
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user=session['user'])

@app.route('/protected')
def protected():
    if 'user' not in session:
        return redirect('/login')
    return render_template('protected.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo={url_for('home', _external=True)}&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )
