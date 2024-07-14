import os
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_oauthlib.client import OAuth
from flask_pymongo import PyMongo

load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') 
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') 

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['MONGO_URI'] = MONGODB_URI

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
    request_token_params={'scope': 'email profile https://www.googleapis.com/auth/contacts.readonly'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

mongo = PyMongo(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    
    if 'google_token' in session:
        # User is logged in, redirect to the dashboard
        return redirect('/dashboard')
    else:
        # User is not logged in, render the login page
        return render_template('login.html')
    
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')
    # return 'You are logged in. Go to dashboard!'+ session['email']

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/contacts')
@login_required
def contacts():
    collection= mongo.db.contacts
    history_entries = collection.find({"user_email": session["email"]}) 
    # history_entries = collection.find({"user_email": "arushijain167@gmail.com"}) 
    print(history_entries)
    return render_template('contacts.html', contacts_entries=history_entries)

@app.route('/history')
@login_required
def history():
    collection= mongo.db.history
    history_entries = collection.find({"user_email": session["email"]}) 
    # history_entries = collection.find({}) 
    print(history_entries)
    return render_template('history.html', history_entries=history_entries)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))
    

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')

    user_info = google.get('userinfo')
    user_id = user_info.data["id"]
    email   = user_info.data["email"]
    picture = user_info.data["picture"]
    session['user_full_name'] = user_info.data.get('name')
    session['picture'] = picture
    session['id'] = user_id
    session['email']=email

    # Fetch contacts using Google People API
    headers = {'Authorization': 'Bearer {}'.format(resp['access_token'])}
    params  = {'personFields': 'names,phoneNumbers'}
    response = requests.get('https://people.googleapis.com/v1/people/me/connections', headers=headers, params=params)
    if response.status_code == 200:
        contacts = response.json().get('connections', [])
        # Save contacts to MongoDB
        contacts_collection = mongo.db.contacts
        for contact in contacts:
            name =  contact.get('names', [{}])[0].get('displayName', '')
            phone_number = contact.get('phoneNumbers', [{}])[0].get('value', '')

            existing_contact = contacts_collection.find_one({
                'name': name,
                'phone_number': phone_number,
                'user_email': email,
            })
            if existing_contact:
                continue

            contacts_collection.insert_one({
                'name': name,
                'number': phone_number,
                'user_email': email,
            })

        return redirect(url_for('dashboard'))

    else:
        return response.text

if __name__ == '__main__':

    app.run(debug=True)

