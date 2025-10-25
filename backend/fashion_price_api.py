"""
Flask API for Fashion Price Prediction - Render Deployment Ready
"""
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('closely_india_complete.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import numpy as np
import pandas as pd
from datetime import datetime
import os
import sys

app = Flask(__name__)
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


# MODEL LOADING WITH AUTO-TRAINING


def ensure_model_exists():
    """Train model if it doesn't exist"""
    model_path = 'fashion_price_model.pkl'
    preprocessor_path = 'fashion_preprocessor.pkl'

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        print("\n" + "="*60)
        print("MODEL FILES NOT FOUND - TRAINING NEW MODEL")
        print("="*60 + "\n")

        try:
            # Import the training module
            # Assuming fashion_price_ml.py is in the current directory
            sys.path.insert(0, '.')
            from fashion_price_ml import main as train_model

            print("Starting model training...")
            train_model()
            print("\n✅ Model training completed successfully!\n")

        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("Make sure fashion_price_ml.py is in the same directory")
            raise
        except Exception as e:
            print(f"❌ Error during training: {e}")
            raise

# Ensure model exists before loading
ensure_model_exists()

# Load trained model and preprocessor
try:
    import joblib

    print("Loading model files...")
    with open('fashion_price_model.pkl', 'rb') as f:
        model_data = joblib.load(f)
        model = model_data['model']
        model_name = model_data['model_name']

    with open('fashion_preprocessor.pkl', 'rb') as f:
        preprocessor_data = joblib.load(f)
        label_encoders = preprocessor_data['label_encoders']

    print(f"✅ Loaded {model_name} model successfully!\n")

except FileNotFoundError as e:
    print(f"❌ Model files not found: {e}")
    model = None
    model_name = "Model not loaded"
    label_encoders = {}
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    model_name = "Model loading error"
    label_encoders = {}


# SECURITY


def require_api_key(f):
    """API key authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        secret_key = os.environ.get('API_SECRET_KEY', 'YOUR_SECRET_KEY')
        if api_key != secret_key:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


# HELPER FUNCTIONS


def encode_features(item_data):
    """Encode item features for prediction"""
    try:
        encoded_features = []

        # Encode categorical features
        for col in ['brand', 'category', 'material', 'retailer', 'season']:
            if col in item_data and col in label_encoders:
                try:
                    encoded_val = label_encoders[col].transform([item_data[col]])[0]
                except:
                    # If value not in training data, use 0
                    encoded_val = 0
                encoded_features.append(encoded_val)
            else:
                encoded_features.append(0)

        # Add numerical features
        encoded_features.append(item_data.get('rating', 4.0))
        encoded_features.append(item_data.get('discount_percent', 0))
        encoded_features.append(item_data.get('brand_popularity', 100))

        return encoded_features
    except Exception as e:
        raise ValueError(f"Error encoding features: {str(e)}")



# API ENDPOINTS


@app.route('/')
def home():
    """API Home"""
    return jsonify({
        'message': 'Fashion Price Prediction API',
        'version': '1.0',
        'model': model_name,
        'model_loaded': model is not None,
        'status': 'operational' if model is not None else 'degraded',
        'endpoints': {
            '/predict': 'POST - Predict price for a fashion item',
            '/compare': 'POST - Compare prices across retailers',
            '/batch_predict': 'POST - Predict prices for multiple items',
            '/available_options': 'GET - Get available options',
            '/health': 'GET - Check API health'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model is not None else 'degraded',
        'model_loaded': model is not None,
        'model_name': model_name,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict_price():
    """
    Predict price for a single fashion item

    Request JSON format:
    {
        "brand": "Zara",
        "category": "Blazer",
        "material": "Wool",
        "retailer": "Myntra",
        "season": "Winter",
        "rating": 4.5,
        "discount_percent": 20
    }
    """
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded. Please check server logs.',
                'success': False
            }), 503

        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            }), 400

        # Validate required fields
        required_fields = ['brand', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'success': False
                }), 400

        # Set defaults for optional fields
        data.setdefault('material', 'Cotton')
        data.setdefault('retailer', 'Amazon India')
        data.setdefault('season', 'All-Season')
        data.setdefault('rating', 4.0)
        data.setdefault('discount_percent', 0)
        data.setdefault('brand_popularity', 100)

        # Encode features and predict
        features = encode_features(data)
        predicted_price = model.predict([features])[0]

        # Calculate price range (confidence interval)
        price_std = predicted_price * 0.15
        price_min = max(0, predicted_price - price_std)
        price_max = predicted_price + price_std

        # Calculate original price if discount given
        original_price = predicted_price / (1 - data['discount_percent']/100) if data['discount_percent'] > 0 else predicted_price

        return jsonify({
            'success': True,
            'item': {
                'brand': data['brand'],
                'category': data['category'],
                'material': data['material']
            },
            'prediction': {
                'current_price': round(predicted_price, 2),
                'original_price': round(original_price, 2),
                'price_range': {
                    'min': round(price_min, 2),
                    'max': round(price_max, 2)
                },
                'discount_percent': data['discount_percent'],
                'currency': 'INR'
            },
            'model': model_name,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/compare', methods=['POST'])
@limiter.limit("20 per minute")
def compare_prices():
    """Compare prices across multiple retailers"""
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'success': False
            }), 503

        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            }), 400

        product_name = data.get('product_name', '')
        brand = data.get('brand', '')
        category = data.get('category', '')

        retailers = ['Myntra', 'Ajio', 'Flipkart', 'Amazon India', 'Lifestyle', 'Westside']
        comparisons = []

        for retailer in retailers:
            item_data = {
                'brand': brand,
                'category': category,
                'material': data.get('material', 'Cotton'),
                'retailer': retailer,
                'season': data.get('season', 'All-Season'),
                'rating': data.get('rating', 4.0),
                'discount_percent': np.random.choice([0, 10, 15, 20, 25, 30]),
                'brand_popularity': 100
            }

            features = encode_features(item_data)
            predicted_price = model.predict([features])[0]

            comparisons.append({
                'retailer': retailer,
                'predicted_price': round(predicted_price, 2),
                'discount': item_data['discount_percent'],
                'search_url': f"https://www.{retailer.lower().replace(' ', '')}.com/s?q={product_name}"
            })

        # Sort by price
        comparisons.sort(key=lambda x: x['predicted_price'])

        return jsonify({
            'success': True,
            'product': product_name,
            'brand': brand,
            'comparisons': comparisons,
            'best_deal': comparisons[0],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/batch_predict', methods=['POST'])
@limiter.limit("5 per minute")
def batch_predict():
    """Predict prices for multiple items at once"""
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'success': False
            }), 503

        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            }), 400

        items = data.get('items', [])

        if not items:
            return jsonify({
                'error': 'No items provided',
                'success': False
            }), 400

        predictions = []

        for item in items:
            try:
                # Set defaults
                item.setdefault('material', 'Cotton')
                item.setdefault('retailer', 'Amazon India')
                item.setdefault('season', 'All-Season')
                item.setdefault('rating', 4.0)
                item.setdefault('discount_percent', 0)
                item.setdefault('brand_popularity', 100)

                features = encode_features(item)
                predicted_price = model.predict([features])[0]

                predictions.append({
                    'item': {
                        'brand': item.get('brand', 'Unknown'),
                        'category': item.get('category', 'Unknown')
                    },
                    'predicted_price': round(predicted_price, 2),
                    'success': True
                })
            except Exception as e:
                predictions.append({
                    'item': item,
                    'error': str(e),
                    'success': False
                })

        return jsonify({
            'success': True,
            'total_items': len(items),
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/available_options', methods=['GET'])
def get_available_options():
    """Get available brands, categories, materials, etc."""
    try:
        if not label_encoders:
            return jsonify({
                'error': 'Label encoders not loaded',
                'success': False
            }), 503

        options = {
            'brands': list(label_encoders['brand'].classes_) if 'brand' in label_encoders else [],
            'categories': list(label_encoders['category'].classes_) if 'category' in label_encoders else [],
            'materials': list(label_encoders['material'].classes_) if 'material' in label_encoders else [],
            'retailers': list(label_encoders['retailer'].classes_) if 'retailer' in label_encoders else [],
            'seasons': list(label_encoders['season'].classes_) if 'season' in label_encoders else []
        }

        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500



# ERROR HANDLERS

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded. Please try again later.',
        'success': False
    }), 429



# RUN SERVER


if __name__ == '__main__':
    print("\n" + "="*60)
    print("FASHION PRICE PREDICTION API SERVER")
    print("="*60)
    print(f"Model: {model_name}")
    print(f"Model Loaded: {model is not None}")
    print("Starting server...")
    print("="*60 + "\n")

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
