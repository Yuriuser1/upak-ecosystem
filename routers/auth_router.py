
"""
Authentication router for UPAK
Handles user registration, login, and JWT token management
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
import os
import jwt
import bcrypt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////tmp/upak_test/upak_test.db')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def get_db_connection():
    """Get database connection"""
    db_path = DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (payload['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Pass user to the route function
        return f(user=dict(user), *args, **kwargs)
    
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        cursor.execute('''
            INSERT INTO users (email, password_hash, subscription_type, cards_limit, cards_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, 'free', 0, 0, datetime.utcnow().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create access token
        access_token = create_access_token(user_id, email)
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'user': {
                'id': user_id,
                'email': email,
                'subscription_type': 'free'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/token', methods=['POST'])
def login():
    """Login and get access token (OAuth2 compatible)"""
    try:
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json()
            email = data.get('email') or data.get('username')
            password = data.get('password')
        else:
            email = request.form.get('username')  # OAuth2 uses 'username'
            password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(user['id'], user['email'])
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer'
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@get_current_user
def get_me(user):
    """Get current user information (protected route)"""
    return jsonify({
        'email': user['email'],
        'subscription_type': user['subscription_type'] or 'free',
        'subscription_expires': user.get('subscription_expires'),
        'cards_limit': user.get('cards_limit', 0),
        'cards_used': user.get('cards_used', 0)
    })
