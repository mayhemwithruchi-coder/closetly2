"""
Enhanced Fashion App Backend with Authentication & Accurate Analysis
- User authentication with SQLite database
- Accurate undertone analysis using color science
- Personalized recommendations engine
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import numpy as np
import cv2
import base64
from datetime import datetime, timedelta
import os
import secrets
import json
from PIL import Image
import io

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ============================================
# DATABASE SETUP
# ============================================

def init_db():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect('closetly_users.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # User profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            gender TEXT,
            body_type TEXT,
            measurements JSON,
            undertone TEXT,
            season TEXT,
            color_palette JSON,
            skin_analysis JSON,
            preferences JSON,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Saved outfits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            outfit_data JSON,
            rating REAL,
            occasion TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database on startup
init_db()


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per hour")
def signup():
    """User registration"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password required', 'success': False}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters', 'success': False}), 400
        
        # Check if user exists
        conn = sqlite3.connect('closetly_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered', 'success': False}), 409
        
        # Create user
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)',
            (email, password_hash, full_name)
        )
        user_id = cursor.lastrowid
        
        # Create empty profile
        cursor.execute(
            'INSERT INTO user_profiles (user_id, preferences) VALUES (?, ?)',
            (user_id, '{}')
        )
        
        conn.commit()
        conn.close()
        
        # Set session
        session.permanent = True
        session['user_id'] = user_id
        session['email'] = email
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name
            },
            'message': 'Account created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """User login"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required', 'success': False}), 400
        
        # Find user
        conn = sqlite3.connect('closetly_users.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, email, password_hash, full_name FROM users WHERE email = ?',
            (email,)
        )
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user[2], password):
            conn.close()
            return jsonify({'error': 'Invalid email or password', 'success': False}), 401
        
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user[0])
        )
        conn.commit()
        conn.close()
        
        # Set session
        session.permanent = True
        session['user_id'] = user[0]
        session['email'] = user[1]
        
        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'email': user[1],
                'full_name': user[3]
            },
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session['user_id'],
            'email': session['email']
        }), 200
    else:
        return jsonify({'authenticated': False}), 401


# ============================================
# ACCURATE UNDERTONE ANALYSIS
# ============================================

class AccurateUndertoneAnalyzer:
    """Advanced undertone analysis using color science"""
    
    @staticmethod
    def analyze_skin_undertone(image_data):
        """
        Analyze skin undertone using multiple methods:
        1. RGB ratio analysis
        2. HSV color space analysis
        3. Lab color space analysis
        4. Vein color detection (simulated through skin tone)
        """
        try:
            # Decode base64 image
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            img_bytes = base64.b64decode(image_data)
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Face detection for better accuracy
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Extract skin region
            if len(faces) > 0:
                x, y, w, h = faces[0]
                # Focus on cheek area (middle-lower face)
                cheek_region = img_rgb[y+h//3:y+2*h//3, x+w//4:x+3*w//4]
                skin_sample = cheek_region
            else:
                # Use center region if no face detected
                h, w = img_rgb.shape[:2]
                skin_sample = img_rgb[h//4:3*h//4, w//4:3*w//4]
            
            # Get average skin color
            avg_color = np.mean(skin_sample.reshape(-1, 3), axis=0)
            
            # Method 1: RGB Ratio Analysis
            r, g, b = avg_color
            rgb_undertone = AccurateUndertoneAnalyzer._analyze_rgb_ratios(r, g, b)
            
            # Method 2: HSV Analysis
            hsv_img = cv2.cvtColor(skin_sample, cv2.COLOR_RGB2HSV)
            avg_hsv = np.mean(hsv_img.reshape(-1, 3), axis=0)
            hsv_undertone = AccurateUndertoneAnalyzer._analyze_hsv(avg_hsv)
            
            # Method 3: Lab Color Space Analysis (most accurate)
            lab_img = cv2.cvtColor(skin_sample, cv2.COLOR_RGB2LAB)
            avg_lab = np.mean(lab_img.reshape(-1, 3), axis=0)
            lab_undertone = AccurateUndertoneAnalyzer._analyze_lab(avg_lab)
            
            # Method 4: Yellowness Index
            yellowness = AccurateUndertoneAnalyzer._calculate_yellowness(r, g, b)
            
            # Combine all methods with weighted confidence
            undertone_votes = {
                'warm': 0,
                'cool': 0,
                'neutral': 0
            }
            
            # Weight each method
            undertone_votes[rgb_undertone] += 2.0  # RGB is reliable
            undertone_votes[hsv_undertone] += 1.5
            undertone_votes[lab_undertone] += 3.0  # Lab is most accurate
            
            if yellowness > 0.6:
                undertone_votes['warm'] += 1.5
            elif yellowness < 0.4:
                undertone_votes['cool'] += 1.5
            else:
                undertone_votes['neutral'] += 1.0
            
            # Determine final undertone
            final_undertone = max(undertone_votes, key=undertone_votes.get)
            confidence = undertone_votes[final_undertone] / sum(undertone_votes.values())
            
            # Determine season
            season = AccurateUndertoneAnalyzer._determine_season(
                final_undertone, avg_lab[0], confidence
            )
            
            # Generate accurate color palette
            palette = AccurateUndertoneAnalyzer._generate_accurate_palette(
                season, final_undertone, avg_color
            )
            
            return {
                'undertone': final_undertone,
                'season': season,
                'confidence': round(confidence * 100, 1),
                'color_palette': palette,
                'skin_analysis': {
                    'rgb': avg_color.tolist(),
                    'lab': avg_lab.tolist(),
                    'hsv': avg_hsv.tolist(),
                    'yellowness_index': round(yellowness, 3)
                },
                'methods_agreement': {
                    'rgb': rgb_undertone,
                    'hsv': hsv_undertone,
                    'lab': lab_undertone
                }
            }
            
        except Exception as e:
            raise Exception(f"Undertone analysis error: {str(e)}")
    
    @staticmethod
    def _analyze_rgb_ratios(r, g, b):
        """Analyze RGB ratios for undertone"""
        # Warm: higher red/yellow (R > B significantly)
        # Cool: higher blue (B > R)
        # Neutral: balanced
        
        rg_ratio = r / (g + 1)
        rb_ratio = r / (b + 1)
        gb_ratio = g / (b + 1)
        
        if rb_ratio > 1.15 and rg_ratio > 0.95:
            return 'warm'
        elif rb_ratio < 1.05:
            return 'cool'
        else:
            return 'neutral'
    
    @staticmethod
    def _analyze_hsv(hsv):
        """Analyze HSV color space"""
        h, s, v = hsv
        
        # Hue analysis (0-180 in OpenCV)
        # Warm: yellow-red range (15-45)
        # Cool: blue-purple range (90-130)
        
        if 15 <= h <= 45 and s > 30:
            return 'warm'
        elif 90 <= h <= 130:
            return 'cool'
        else:
            return 'neutral'
    
    @staticmethod
    def _analyze_lab(lab):
        """Analyze Lab color space (most accurate)"""
        l, a, b = lab
        
        # a: green (-) to red (+)
        # b: blue (-) to yellow (+)
        
        # Warm: positive b (yellow), positive a (red)
        # Cool: negative b (blue), or low b with low a
        # Neutral: balanced
        
        if b > 10 and a > 5:
            return 'warm'
        elif b < 5 or (b < 10 and a < 5):
            return 'cool'
        else:
            return 'neutral'
    
    @staticmethod
    def _calculate_yellowness(r, g, b):
        """Calculate yellowness index (0-1)"""
        # Higher values = more yellow (warm)
        # Lower values = less yellow (cool)
        yellowness = (r + g - 2*b) / (r + g + b + 1)
        return max(0, min(1, (yellowness + 1) / 2))
    
    @staticmethod
    def _determine_season(undertone, lightness, confidence):
        """Determine color season based on undertone and lightness"""
        # Spring: Warm + Light
        # Summer: Cool + Light
        # Autumn: Warm + Deep
        # Winter: Cool + Deep
        
        is_light = lightness > 140  # Lab L* value
        
        if undertone == 'warm':
            return 'Spring' if is_light else 'Autumn'
        elif undertone == 'cool':
            return 'Summer' if is_light else 'Winter'
        else:  # neutral
            return 'Summer' if is_light else 'Autumn'
    
    @staticmethod
    def _generate_accurate_palette(season, undertone, base_color):
        """Generate scientifically accurate color palette"""
        palettes = {
            'Spring': {
                'warm': ['#FFD700', '#FF6B6B', '#FFA07A', '#98D8C8', '#F7DC6F', '#85C1E2'],
                'neutral': ['#F4E4C1', '#FF9F80', '#FFB6B9', '#8FD1D7', '#F9E79F', '#A8D8EA']
            },
            'Summer': {
                'cool': ['#B4A7D6', '#87CEEB', '#DDA0DD', '#E6E6FA', '#AFEEEE', '#D8BFD8'],
                'neutral': ['#C5CAE9', '#90CAF9', '#E1BEE7', '#F0E68C', '#B2DFDB', '#D1C4E9']
            },
            'Autumn': {
                'warm': ['#CD853F', '#D2691E', '#8B4513', '#DAA520', '#B8860B', '#BC8F8F'],
                'neutral': ['#C19A6B', '#B87333', '#9C661F', '#C68E17', '#A0826D', '#D4A574']
            },
            'Winter': {
                'cool': ['#000080', '#8B0000', '#4B0082', '#2F4F4F', '#DC143C', '#191970'],
                'neutral': ['#2C3E50', '#8E44AD', '#C0392B', '#1C2833', '#922B21', '#4A235A']
            }
        }
        
        # Select palette based on season and undertone
        if season in palettes:
            if undertone in palettes[season]:
                return palettes[season][undertone]
            else:
                # Return first available palette for season
                return list(palettes[season].values())[0]
        
        # Default fallback
        return ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']


# ============================================
# PERSONALIZED RECOMMENDATIONS ENGINE
# ============================================

class PersonalizedRecommendations:
    """Generate highly specific, non-generic recommendations"""
    
    # Detailed body-type specific recommendations
    BODY_TYPE_RECOMMENDATIONS = {
        'women': {
            'Hourglass': {
                'description': 'Balanced proportions with defined waist - your silhouette is naturally harmonious',
                'specific_styles': [
                    {'item': 'Wrap Dress in Jersey', 'why': 'The wrap style cinches at your natural waist, emphasizing your curves without adding bulk', 'avoid': 'Avoid boxy shift dresses'},
                    {'item': 'High-Waisted Wide-Leg Trousers', 'why': 'Creates vertical lines while highlighting your waist, elongates legs', 'avoid': 'Skip low-rise pants'},
                    {'item': 'Fitted Blazer with Peplum', 'why': 'Follows your curves and the peplum adds playful movement', 'avoid': 'Oversized blazers hide your shape'},
                    {'item': 'Bodycon Midi Dress', 'why': 'Shows off your proportions without being too revealing', 'avoid': 'Avoid empire waist dresses'},
                    {'item': 'Belted Trench Coat', 'why': 'The belt defines your waist even in outerwear', 'avoid': 'Skip unstructured coats'},
                    {'item': 'V-Neck Fitted Top', 'why': 'Draws eyes to your face while skimming your curves', 'avoid': 'Crew necks can make you look boxy'}
                ],
                'styling_tips': [
                    'Always emphasize your waist - use belts on dresses, coats, and cardigans',
                    'Choose fabrics with stretch (jersey, ponte) that move with your body',
                    'Wrap styles are your best friend - dresses, tops, and skirts',
                    'Tuck in tops to showcase your waist definition'
                ],
                'necklines': ['V-neck', 'Sweetheart', 'Scoop neck', 'Wrap neckline'],
                'avoid_completely': ['Shapeless tunics', 'Drop-waist styles', 'Boxy oversized pieces', 'Empire waist cuts']
            },
            'Pear': {
                'description': 'Narrow shoulders with fuller hips - balance is key to creating visual harmony',
                'specific_styles': [
                    {'item': 'Boat Neck Striped Top', 'why': 'Horizontal stripes on top broaden shoulders, creating balance', 'avoid': 'Avoid spaghetti straps'},
                    {'item': 'Statement Sleeve Blouse', 'why': 'Volume on shoulders draws eyes upward and balances hips', 'avoid': 'Skip plain sleeveless tops'},
                    {'item': 'Dark Bootcut Jeans', 'why': 'Dark wash minimizes hips, bootcut balances proportions', 'avoid': 'Avoid light wash skinny jeans'},
                    {'item': 'A-Line Midi Skirt', 'why': 'Flows away from hips, creating elegant silhouette', 'avoid': 'Skip tight pencil skirts'},
                    {'item': 'Embellished Collar Dress', 'why': 'Draws attention to upper body and shoulders', 'avoid': 'Avoid bottom-heavy patterns'},
                    {'item': 'Structured Shoulder Blazer', 'why': 'Creates width on top to match your natural bottom', 'avoid': 'Unstructured or thin blazers'}
                ],
                'styling_tips': [
                    'Wear bright colors, patterns, and embellishments on top',
                    'Keep bottoms in darker, solid colors',
                    'Add volume to shoulders with pads, ruffles, or statement sleeves',
                    'Use scarves and statement necklaces to draw eyes upward'
                ],
                'necklines': ['Boat neck', 'Off-shoulder', 'Square neck', 'Wide scoop'],
                'avoid_completely': ['Hip-hugging styles', 'Light-colored bottoms', 'Tapered ankle pants', 'Tight tops with flare bottoms']
            },
            'Apple': {
                'description': 'Fuller midsection with shapely legs - elongate your torso and draw eyes vertically',
                'specific_styles': [
                    {'item': 'Empire Waist Dress', 'why': 'Cinches above natural waist, flows over midsection gracefully', 'avoid': 'Avoid waist-defining belts'},
                    {'item': 'Deep V-Neck Top', 'why': 'Creates vertical line, elongates torso, draws eyes up', 'avoid': 'Skip crew necks'},
                    {'item': 'Longline Open Cardigan', 'why': 'Vertical lines create length, open front is slimming', 'avoid': 'Cropped cardigans add bulk'},
                    {'item': 'Straight-Leg Mid-Rise Jeans', 'why': 'Comfortable at waist, showcases your great legs', 'avoid': 'High-waisted styles can bunch'},
                    {'item': 'Flowy Tunic with Leggings', 'why': 'Skims over midsection, shows off legs', 'avoid': 'Clingy, tucked-in tops'},
                    {'item': 'Wrap Top (Not Tied)', 'why': 'Creates diagonal lines that flatter', 'avoid': 'Tied wrap styles emphasize waist'}
                ],
                'styling_tips': [
                    'Look for tops that skim rather than cling',
                    'Create vertical lines with long necklaces, open cardigans, and V-necks',
                    'Show off your legs - they\'re your asset!',
                    'Avoid adding volume at the midsection'
                ],
                'necklines': ['Deep V-neck', 'Scoop neck', 'Surplice', 'Cowl neck'],
                'avoid_completely': ['Belted at natural waist', 'Clingy fabrics', 'Horizontal stripes', 'Double-breasted styles']
            },
            'Rectangle': {
                'description': 'Straight, athletic build - create the illusion of curves and waist definition',
                'specific_styles': [
                    {'item': 'Peplum Top', 'why': 'Flare at waist creates hourglass illusion', 'avoid': 'Straight-cut tops are too linear'},
                    {'item': 'Ruffled Wrap Dress', 'why': 'Ruffles add dimension, wrap creates waist', 'avoid': 'Shift dresses emphasize straight lines'},
                    {'item': 'High-Waisted Belted Pants', 'why': 'Belt creates waist definition', 'avoid': 'Mid-rise straight cuts'},
                    {'item': 'Fit-and-Flare Dress', 'why': 'Fitted top with flared skirt creates curves', 'avoid': 'Column dresses'},
                    {'item': 'Layered Textured Outfit', 'why': 'Multiple layers add visual dimension', 'avoid': 'Single flat layers'},
                    {'item': 'Color-Block Dress', 'why': 'Different colors create curves visually', 'avoid': 'Monochrome straight cuts'}
                ],
                'styling_tips': [
                    'Use belts religiously to create a waist',
                    'Choose textured fabrics, ruffles, and peplums',
                    'Layer different lengths to break up straight lines',
                    'Wear patterns and prints to add dimension'
                ],
                'necklines': ['Sweetheart', 'Scoop neck', 'Boat neck', 'Ruffle collar'],
                'avoid_completely': ['Shapeless styles', 'Straight cuts', 'Minimal designs', 'Plain column dresses']
            },
            'Inverted Triangle': {
                'description': 'Broad shoulders with narrow hips - create balance by softening top and adding volume below',
                'specific_styles': [
                    {'item': 'A-Line Full Skirt', 'why': 'Volume on bottom balances broad shoulders', 'avoid': 'Pencil skirts emphasize disproportion'},
                    {'item': 'Wide-Leg Trousers', 'why': 'Creates width at hips to match shoulders', 'avoid': 'Skinny jeans make top look bigger'},
                    {'item': 'Soft V-Neck Tee', 'why': 'V-neck narrows shoulders, soft fabric doesn\'t add bulk', 'avoid': 'Boat necks widen shoulders'},
                    {'item': 'Flowy Wrap Dress', 'why': 'Soft on top, flows into fuller skirt', 'avoid': 'Structured shoulder dresses'},
                    {'item': 'Bootcut Jeans with Bright Top', 'why': 'Boot cut adds volume below, bright top is okay if V-neck', 'avoid': 'Tight bottom/wide top combos'},
                    {'item': 'Unstructured Blazer', 'why': 'No shoulder pads, soft drape minimizes width', 'avoid': 'Structured blazers with shoulder pads'}
                ],
                'styling_tips': [
                    'Avoid shoulder pads and structured shoulders at all costs',
                    'Wear dark, solid colors on top',
                    'Add patterns, light colors, and volume to bottom half',
                    'Choose soft, drapey fabrics for tops'
                ],
                'necklines': ['V-neck', 'Scoop neck', 'Cowl neck', 'Surplice'],
                'avoid_completely': ['Boat necks', 'Off-shoulder', 'Shoulder pads', 'Horizontal stripes on top', 'Structured jackets']
            }
        },
        'men': {
            'Athletic': {
                'description': 'Broad shoulders, narrow waist, muscular build - you can wear almost anything, focus on fit',
                'specific_styles': [
                    {'item': 'Fitted Dress Shirt', 'why': 'Shows off your V-shape without being too tight', 'avoid': 'Baggy shirts hide your physique'},
                    {'item': 'Slim-Fit Blazer', 'why': 'Tailored to your shoulders, nips at waist', 'avoid': 'Regular fit looks too boxy'},
                    {'item': 'Tapered Chinos', 'why': 'Fitted at top, tapers down to balance shoulders', 'avoid': 'Straight-leg can look disproportionate'},
                    {'item': 'V-Neck Sweater', 'why': 'Emphasizes your chest and shoulders', 'avoid': 'Crew necks can make you look bulky'},
                    {'item': 'Structured Suit', 'why': 'Your build was made for suits - tailored perfection', 'avoid': 'Unstructured makes you look sloppy'},
                    {'item': 'Form-Fitting Polo', 'why': 'Casual but still shows your physique', 'avoid': 'Loose polos waste your build'}
                ],
                'styling_tips': [
                    'Always get clothes tailored - your build deserves perfect fit',
                    'Show off your V-shape with fitted tops',
                    'Balance broad shoulders with tapered bottoms',
                    'Avoid baggy clothes that hide your physique'
                ],
                'patterns': ['Vertical stripes', 'Small checks', 'Subtle patterns'],
                'avoid_completely': ['Oversized fits', 'Boxy cuts', 'Horizontal stripes', 'Baggy pants']
            },
            'Rectangle': {
                'description': 'Straight build, similar measurements - create dimension and visual interest',
                'specific_styles': [
                    {'item': 'Layered Look (Vest over Shirt)', 'why': 'Multiple layers create dimension and shape', 'avoid': 'Single layers look flat'},
                    {'item': 'Textured Knit Sweater', 'why': 'Texture adds visual bulk and interest', 'avoid': 'Plain smooth fabrics'},
                    {'item': 'Double-Breasted Blazer', 'why': 'Creates width and structure', 'avoid': 'Single-button blazers'},
                    {'item': 'Patterned Shirt', 'why': 'Horizontal patterns add width', 'avoid': 'Vertical stripes make you look thinner'},
                    {'item': 'Chunky Knit Cardigan', 'why': 'Adds bulk and creates shape', 'avoid': 'Thin cardigans'},
                    {'item': 'Contrast Waistband Pants', 'why': 'Creates visual break and interest', 'avoid': 'Same-color top and bottom'}
                ],
                'styling_tips': [
                    'Layer constantly - vest, cardigan, jacket',
                    'Choose textured and patterned fabrics',
                    'Horizontal patterns are your friend',
                    'Create visual breaks between top and bottom'
                ],
                'patterns': ['Horizontal stripes', 'Checks', 'Bold patterns'],
                'avoid_completely': ['Vertical stripes', 'Monochrome outfits', 'Single thin layers', 'Plain solid colors']
            },
            'Inverted Triangle': {
                'description': 'Broad shoulders, narrow waist and hips - balance your upper body',
                'specific_styles': [
                    {'item': 'Relaxed-Fit Jeans', 'why': 'Adds volume to lower body to balance broad top', 'avoid': 'Skinny jeans emphasize disproportion'},
                    {'item': 'Unstructured Blazer', 'why': 'No shoulder pads, soft drape minimizes width', 'avoid': 'Structured blazers add more width'},
                    {'item': 'Crew Neck Tee', 'why': 'Simple neckline doesn\'t emphasize shoulders', 'avoid': 'Wide collars make shoulders look bigger'},
                    {'item': 'Dark Top, Light Bottoms', 'why': 'Dark minimizes top, light adds attention to bottom', 'avoid': 'Opposite color scheme'},
                    {'item': 'Straight-Leg Trousers', 'why': 'Adds visual weight to lower body', 'avoid': 'Tapered pants make top look huge'},
                    {'item': 'Soft Drapey Shirt', 'why': 'Doesn\'t emphasize broad shoulders', 'avoid': 'Stiff structured shirts'}
                ],
                'styling_tips': [
                    'Avoid shoulder pads and structured shoulders',
                    'Wear darker colors on top, lighter below',
                    'Choose soft, drapey fabrics for shirts',
                    'Add volume to lower body with relaxed fits'
                ],
                'patterns': ['Solid tops', 'Patterned bottoms', 'Minimal top designs'],
                'avoid_completely': ['Shoulder pads', 'Boat necks', 'Horizontal stripes on top', 'Structured jackets']
            },
            'Trapezoid': {
                'description': 'Narrower shoulders, broader hips - create upper body width and streamline lower body',
                'specific_styles': [
                    {'item': 'Structured Blazer with Padding', 'why': 'Shoulder pads create width to match hips', 'avoid': 'Unstructured blazers'},
                    {'item': 'Horizontal Stripe Shirt', 'why': 'Stripes on top create visual width', 'avoid': 'Vertical stripes'},
                    {'item': 'Fitted Shirt with Broad Collar', 'why': 'Wide collar makes shoulders look broader', 'avoid': 'Narrow collars'},
                    {'item': 'Dark Straight-Cut Trousers', 'why': 'Dark streamlines hips, straight cut balances', 'avoid': 'Light baggy pants'},
                    {'item': 'V-Neck Layered Look', 'why': 'V creates width, layers add bulk on top', 'avoid': 'Single thin layer'},
                    {'item': 'Epaulette Detail Jacket', 'why': 'Shoulder details create visual width', 'avoid': 'Plain shoulders'}
                ],
                'styling_tips': [
                    'Embrace shoulder pads and structured tops',
                    'Wear patterns and light colors on top',
                    'Keep bottoms streamlined and dark',
                    'Layer on top to add visual bulk'
                ],
                'patterns': ['Horizontal stripes on top', 'Checks on top', 'Solid dark bottoms'],
                'avoid_completely': ['Unstructured tops', 'Tight bottoms', 'Light-colored pants', 'Narrow shoulders']
            },
            'Oval': {
                'description': 'Fuller midsection - create vertical lines and elongate your torso',
                'specific_styles': [
                    {'item': 'V-Neck Shirt', 'why': 'V-shape creates vertical line, draws eyes up', 'avoid': 'Crew necks shorten torso'},
                    {'item': 'Open Cardigan', 'why': 'Open front creates vertical slimming line', 'avoid': 'Closed cardigans add width'},
                    {'item': 'Vertical Stripe Shirt', 'why': 'Vertical lines elongate and slim', 'avoid': 'Horizontal stripes widen'},
                    {'item': 'Longer Length Shirt', 'why': 'Covers midsection, creates length', 'avoid': 'Short shirts that bunch'},
                    {'item': 'Straight-Leg Dark Trousers', 'why': 'Dark is slimming, straight balances', 'avoid': 'Pleated pants add bulk'},
                    {'item': 'Monochrome Dark Outfit', 'why': 'Creates unbroken vertical line', 'avoid': 'Color blocking at waist'}
                ],
                'styling_tips': [
                    'Wear darker colors, especially on top',
                    'Create vertical lines with V-necks and open fronts',
                    'Choose longer shirt lengths',
                    'Avoid belts and anything that draws attention to waist'
                ],
                'patterns': ['Vertical stripes', 'Subtle patterns', 'Monochrome'],
                'avoid_completely': ['Horizontal stripes', 'Tight-fitting tops', 'Short shirts', 'Belts', 'Pleats']
            }
        },
        'unisex': {
            'Balanced': {
                'description': 'Well-proportioned silhouette - you have versatile styling options',
                'specific_styles': [
                    {'item': 'Oversized Tailored Blazer', 'why': 'Modern, creates interesting proportions', 'avoid': 'Too tight loses cool factor'},
                    {'item': 'High-Waisted Pants with Tucked Shirt', 'why': 'Elongates legs, defines shape', 'avoid': 'Low-rise shortens legs'},
                    {'item': 'Structured Minimalist Outfit', 'why': 'Clean lines complement your balance', 'avoid': 'Too much chaos'},
                    {'item': 'Monochrome Layered Look', 'why': 'Sophisticated, lets proportions shine', 'avoid': 'Too many colors'},
                    {'item': 'Statement Outerwear', 'why': 'You can pull off bold pieces', 'avoid': 'Boring basics only'},
                    {'item': 'Asymmetric Cuts', 'why': 'Interesting lines on balanced frame', 'avoid': 'Too symmetrical'}
                ],
                'styling_tips': [
                    'Experiment with proportions - you can pull off most looks',
                    'Try oversized on top, fitted on bottom or vice versa',
                    'Monochrome looks sophisticated on you',
                    'Don\'t be afraid of statement pieces'
                ],
                'patterns': ['Any - you\'re versatile', 'Geometric', 'Color blocks'],
                'avoid_completely': ['Nothing specific - experiment freely!']
            },
            'Linear': {
                'description': 'Straight, elongated silhouette - embrace clean lines and structure',
                'specific_styles': [
                    {'item': 'Structured Pieces', 'why': 'Geometric lines complement your shape', 'avoid': 'Too soft and drapey'},
                    {'item': 'Tailored Fit Throughout', 'why': 'Clean silhouette enhances your linear build', 'avoid': 'Baggy loose fits'},
                    {'item': 'Monochrome Outfits', 'why': 'Unbroken line creates elegance', 'avoid': 'Too many color breaks'},
                    {'item': 'Sharp Silhouettes', 'why': 'Angular cuts work with your shape', 'avoid': 'Rounded shapes'},
                    {'item': 'Minimal Jewelry', 'why': 'Keeps clean aesthetic', 'avoid': 'Chunky accessories'},
                    {'item': 'Contemporary Minimalist', 'why': 'Modern, sophisticated aesthetic', 'avoid': 'Bohemian or romantic styles'}
                ],
                'styling_tips': [
                    'Embrace minimalism and clean lines',
                    'Stick to tailored, structured pieces',
                    'Monochrome is your power look',
                    'Less is more with accessories'
                ],
                'patterns': ['Solid colors', 'Subtle textures', 'Geometric'],
                'avoid_completely': ['Ruffles', 'Too much draping', 'Busy patterns', 'Romantic styles']
            }
        }
    }
    
    @staticmethod
    def get_recommendations(user_profile):
        """Get personalized recommendations based on complete profile"""
        gender = user_profile.get('gender', 'unisex')
        body_type = user_profile.get('body_type', 'Balanced')
        season = user_profile.get('season', 'Spring')
        
        # Get body type recommendations
        recommendations = PersonalizedRecommendations.BODY_TYPE_RECOMMENDATIONS.get(
            gender, {}
        ).get(body_type, PersonalizedRecommendations.BODY_TYPE_RECOMMENDATIONS['unisex']['Balanced'])
        
        return recommendations


# ============================================
# USER PROFILE ENDPOINTS
# ============================================

@app.route('/api/profile/save', methods=['POST'])
def save_profile():
    """Save or update user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        conn = sqlite3.connect('closetly_users.db')
        cursor = conn.cursor()
        
        # Update profile
        cursor.execute('''
            UPDATE user_profiles SET
                gender = ?,
                body_type = ?,
                measurements = ?,
                undertone = ?,
                season = ?,
                color_palette = ?,
                skin_analysis = ?,
                preferences = ?,
                updated_at = ?
            WHERE user_id = ?
        ''', (
            data.get('gender'),
            data.get('body_type'),
            json.dumps(data.get('measurements', {})),
            data.get('undertone'),
            data.get('season'),
            json.dumps(data.get('color_palette', [])),
            json.dumps(data.get('skin_analysis', {})),
            json.dumps(data.get('preferences', {})),
            datetime.now(),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Profile saved'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/profile/get', methods=['GET'])
def get_profile():
    """Get user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401
    
    try:
        user_id = session['user_id']
        
        conn = sqlite3.connect('closetly_users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gender, body_type, measurements, undertone, season,
                   color_palette, skin_analysis, preferences
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            return jsonify({
                'success': True,
                'profile': {
                    'gender': profile[0],
                    'body_type': profile[1],
                    'measurements': json.loads(profile[2]) if profile[2] else {},
                    'undertone': profile[3],
                    'season': profile[4],
                    'color_palette': json.loads(profile[5]) if profile[5] else [],
                    'skin_analysis': json.loads(profile[6]) if profile[6] else {},
                    'preferences': json.loads(profile[7]) if profile[7] else {}
                }
            }), 200
        else:
            return jsonify({'success': True, 'profile': None}), 200
            
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/analyze/undertone', methods=['POST'])
def analyze_undertone():
    """Analyze skin undertone from image"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided', 'success': False}), 400
        
        # Perform accurate analysis
        analyzer = AccurateUndertoneAnalyzer()
        result = analyzer.analyze_skin_undertone(image_data)
        
        return jsonify({
            'success': True,
            **result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/recommendations/get', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401
    
    try:
        user_id = session['user_id']
        
        conn = sqlite3.connect('closetly_users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gender, body_type, undertone, season, color_palette
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        
        if not profile or not profile[1]:
            return jsonify({
                'error': 'Profile incomplete. Complete assessment first.',
                'success': False
            }), 400
        
        user_profile = {
            'gender': profile[0],
            'body_type': profile[1],
            'undertone': profile[2],
            'season': profile[3],
            'color_palette': json.loads(profile[4]) if profile[4] else []
        }
        
        recommendations = PersonalizedRecommendations.get_recommendations(user_profile)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# ============================================
# SERVER
# ============================================

@app.route('/')
def home():
    """Serve main page"""
    if os.path.exists('closetly_enhanced.html'):
        return send_file('closetly_enhanced.html')
    return jsonify({
        'message': 'Closetly Enhanced API',
        'features': ['Authentication', 'Accurate Undertone Analysis', 'Personalized Recommendations']
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'features': {
            'authentication': True,
            'undertone_analysis': True,
            'personalized_recommendations': True
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
