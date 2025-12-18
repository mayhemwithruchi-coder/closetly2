"""
Closetly Authentication Server with SQLite Database
Enhanced with user profiles and personalized recommendations
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

DATABASE = 'closetly_users.db'

# Initialize Database
def init_db():
    """Create database tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # User profiles table (style preferences)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gender TEXT,
            body_type TEXT,
            undertone TEXT,
            color_season TEXT,
            dominant_colors TEXT,
            measurements TEXT,
            preferences TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Saved outfits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            outfit_name TEXT,
            items TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Password hashing
def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password, password_hash):
    """Verify password against hash"""
    try:
        salt, pwd_hash = password_hash.split('$')
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return test_hash.hex() == pwd_hash
    except:
        return False

# Session management
def create_session(user_id):
    """Create new session token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    conn.commit()
    conn.close()
    
    return token

def verify_session(token):
    """Verify session token and return user_id"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id FROM user_sessions
        WHERE session_token = ? AND expires_at > ?
    ''', (token, datetime.now()))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

# API Endpoints

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['full_name'].strip()
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Create session
            session_token = create_session(user_id)
            
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name
                },
                'session_token': session_token
            }), 201
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        # Get user
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, password_hash, full_name
            FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        user_id, email, password_hash, full_name = user
        
        # Verify password
        if not verify_password(password, password_hash):
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now(), user_id))
        conn.commit()
        conn.close()
        
        # Create session
        session_token = create_session(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name
            },
            'session_token': session_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'No session token provided'
            }), 400
        
        # Delete session
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (token,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profile/save', methods=['POST'])
def save_profile():
    """Save or update user style profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_session(token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired session'
            }), 401
        
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing profile
            cursor.execute('''
                UPDATE user_profiles
                SET gender = ?, body_type = ?, undertone = ?, color_season = ?,
                    dominant_colors = ?, measurements = ?, preferences = ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', (
                data.get('gender'),
                data.get('body_type'),
                data.get('undertone'),
                data.get('color_season'),
                json.dumps(data.get('dominant_colors', [])),
                json.dumps(data.get('measurements', {})),
                json.dumps(data.get('preferences', {})),
                datetime.now(),
                user_id
            ))
        else:
            # Insert new profile
            cursor.execute('''
                INSERT INTO user_profiles
                (user_id, gender, body_type, undertone, color_season,
                 dominant_colors, measurements, preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('gender'),
                data.get('body_type'),
                data.get('undertone'),
                data.get('color_season'),
                json.dumps(data.get('dominant_colors', [])),
                json.dumps(data.get('measurements', {})),
                json.dumps(data.get('preferences', {}))
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profile/get', methods=['GET'])
def get_profile():
    """Get user style profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_session(token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired session'
            }), 401
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gender, body_type, undertone, color_season,
                   dominant_colors, measurements, preferences
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        
        if not profile:
            return jsonify({
                'success': True,
                'profile': None
            }), 200
        
        return jsonify({
            'success': True,
            'profile': {
                'gender': profile[0],
                'body_type': profile[1],
                'undertone': profile[2],
                'color_season': profile[3],
                'dominant_colors': json.loads(profile[4] or '[]'),
                'measurements': json.loads(profile[5] or '{}'),
                'preferences': json.loads(profile[6] or '{}')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profile/verify', methods=['GET'])
def verify_profile():
    """Verify session is valid"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_session(token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'authenticated': False
            }), 401
        
        # Get user info
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT email, full_name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({
                'success': False,
                'authenticated': False
            }), 401
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': user_id,
                'email': user[0],
                'full_name': user[1]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("CLOSETLY AUTHENTICATION SERVER")
    print("="*60)
    print("\n🔐 Endpoints:")
    print("  • POST /api/auth/signup - Create account")
    print("  • POST /api/auth/login - Login")
    print("  • POST /api/auth/logout - Logout")
    print("  • POST /api/profile/save - Save profile")
    print("  • GET  /api/profile/get - Get profile")
    print("  • GET  /api/profile/verify - Verify session")
    print("\nStarting server...")
    print("="*60 + "\n")
    
    port = int(os.environ.get('AUTH_PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
