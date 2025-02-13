import os
from datetime import datetime
from flask import Flask, request, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_talisman import Talisman
from authlib.integrations.flask_client import OAuth
import pymysql

# Initialize the app
app = Flask(__name__)
CORS(app)  # Enable CORS for front-end communication
Talisman(app)  # Secure app with HTTPS headers
bcrypt = Bcrypt(app)  # Password hashing
oauth = OAuth(app)  # OAuth setup

# Configure MySQL Database using environment variables
pymysql.install_as_MySQLdb()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'mysql+pymysql://user:password@localhost/carpool_db'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = True  # Disable for production

db = SQLAlchemy(app)

# Google OAuth Configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    preferences = db.Column(db.String(255), nullable=True)

class RideRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_location = db.Column(db.String(120), nullable=False)
    end_location = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=False)
    time = db.Column(db.String(120), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return "Welcome to the Carpooling Backend API!"

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def authorized():
    token = google.authorize_access_token()
    if not token:
        return jsonify({"error": "Failed to retrieve access token"}), 400

    user_info = google.get('userinfo').json()
    email = user_info.get('email')

    if not email or not email.endswith("@yourcollege.edu"):
        return jsonify({"error": "Unauthorized email domain."}), 403

    user = User.query.filter_by(email=email).first()
    if not user:
        new_user = User(name=user_info.get('name', 'Unknown'), email=email, location="Unknown")
        db.session.add(new_user)
        db.session.commit()

    return jsonify({"message": "Login successful", "email": email})

@app.route('/ride-request', methods=['POST'])
def ride_request():
    data = request.json
    new_request = RideRequest(
        user_id=data['user_id'],
        start_location=data['start_location'],
        end_location=data['end_location'],
        date=data['date'],
        time=data['time']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"message": "Ride request submitted successfully!"}), 201

@app.route('/match', methods=['POST'])
def match_users():
    data = request.json
    user_id = data['user_id']
    start_location = data['start_location']
    end_location = data['end_location']

    today = datetime.today().strftime('%Y-%m-%d')

    matches = RideRequest.query.filter(
        RideRequest.start_location == start_location,
        RideRequest.end_location == end_location,
        RideRequest.date >= today  # Only return future rides
    ).all()

    matched_users = [
        {
            "user_id": request.user_id,
            "start_location": request.start_location,
            "end_location": request.end_location,
            "date": request.date,
            "time": request.time
        } for request in matches if request.user_id != user_id
    ]

    return jsonify(matched_users), 200

@app.route('/update-preferences', methods=['POST'])
def update_preferences():
    data = request.json
    user = User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.preferences = data.get('preferences', user.preferences)
    db.session.commit()
    return jsonify({"message": "Preferences updated successfully!"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
