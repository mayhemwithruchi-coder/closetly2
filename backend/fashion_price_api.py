"""
Flask API for Fashion Price Prediction - Render Deployment Ready
Enhanced with Images and Retailer Links
"""
from flask import Flask, request, jsonify, send_file
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

# Retailer URL mapping
RETAILER_URLS = {
    'Myntra': 'https://www.myntra.com/shop/',
    'Ajio': 'https://www.ajio.com/search/?text=',
    'Flipkart': 'https://www.flipkart.com/search?q=',
    'Amazon India': 'https://www.amazon.in/s?k=',
    'Lifestyle': 'https://www.lifestylestores.com/in/en/search/?text=',
    'Reliance Trends': 'https://www.reliancetrends.com/search?q=',
    'Westside': 'https://www.westside.com/search?q=',
    'Shoppers Stop': 'https://www.shoppersstop.com/search?q=',
    'Max Fashion': 'https://www.maxfashion.in/in/en/search/?text='
}

# Product image mapping
CATEGORY_IMAGES = {
    'Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',
    'Dress': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400',
    'Shirt': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400',
    'Blazer': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400',
    'T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400',
    'Jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400',
    'Sweater': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400',
    'Pants': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400',
    'Skirt': 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400',
    'Coat': 'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400',
    'Hoodie': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400',
    'Polo': 'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400',
    'Chinos': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400'
}


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


def get_product_url(retailer, brand, product_name):
    """Generate retailer-specific product URL"""
    base_url = RETAILER_URLS.get(retailer, 'https://www.google.com/search?q=')
    search_query = f"{brand} {product_name}".replace(' ', '+')
    return base_url + search_query


def get_product_image(category):
    """Get product image URL based on category"""
    return CATEGORY_IMAGES.get(category, 'https://via.placeholder.com/400x400?text=Product')


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
    """Serve the main HTML page or API info"""
    # Try to serve HTML file first (for browser access)
    try:
        if os.path.exists('closetly_india_complete.html'):
            return send_file('closetly_india_complete.html')
    except Exception as e:
        print(f"Could not serve HTML: {e}")
    
    # Fallback to JSON API info (for API testing)
    return jsonify({
        'message': 'Fashion Price Prediction API - Closetly',
        'version': '2.0',
        'model': model_name,
        'model_loaded': model is not None,
        'status': 'operational' if model is not None else 'degraded',
        'features': {
            'product_images': True,
            'retailer_links': True,
            'price_prediction': True,
            'price_comparison': True,
            'ai_chatbot': True
        },
        'endpoints': {
            '/': 'GET - Serve HTML UI or API info',
            '/health': 'GET - Check API health',
            '/predict': 'POST - Predict price for a fashion item',
            '/compare': 'POST - Compare prices across retailers',
            '/batch_predict': 'POST - Predict prices for multiple items',
            '/available_options': 'GET - Get available brands, categories, etc.'
        },
        'documentation': 'https://github.com/yourusername/closetly',
        'support': 'contact@closetly.com'
    })


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy' if model is not None else 'degraded',
        'model_loaded': model is not None,
        'model_name': model_name,
        'features_enabled': {
            'images': True,
            'retailer_links': True,
            'price_prediction': model is not None
        },
        'timestamp': datetime.now().isoformat(),
        'uptime': 'operational'
    })


@app.route('/api/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict_price():
    """
    Predict price for a single fashion item with image and link

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
    
    Response includes: predicted_price, image_url, product_url
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
        data.setdefault('retailer', 'Myntra')
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

        # Get product image and URL
        product_name = f"{data['brand']} {data['category']}"
        image_url = get_product_image(data['category'])
        product_url = get_product_url(data['retailer'], data['brand'], data['category'])

        return jsonify({
            'success': True,
            'item': {
                'brand': data['brand'],
                'category': data['category'],
                'material': data['material'],
                'product_name': product_name
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
            'media': {
                'image_url': image_url,
                'product_url': product_url,
                'retailer': data['retailer']
            },
            'model': model_name,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/compare', methods=['POST'])
@limiter.limit("20 per minute")
def compare_prices():
    """
    Compare prices across multiple retailers with images and links
    
    Request JSON format:
    {
        "product_name": "Formal Blazer",
        "brand": "Van Heusen",
        "category": "Blazer",
        "material": "Wool" (optional)
    }
    
    Response includes comparisons for all major retailers
    """
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

        product_name = data.get('product_name', f"{data.get('brand', '')} {data.get('category', '')}")
        brand = data.get('brand', '')
        category = data.get('category', '')

        retailers = ['Myntra', 'Ajio', 'Flipkart', 'Amazon India', 'Lifestyle', 'Westside']
        comparisons = []

        # Get product image
        image_url = get_product_image(category)

        for retailer in retailers:
            item_data = {
                'brand': brand,
                'category': category,
                'material': data.get('material', 'Cotton'),
                'retailer': retailer,
                'season': data.get('season', 'All-Season'),
                'rating': data.get('rating', 4.0) + np.random.uniform(-0.2, 0.2),
                'discount_percent': np.random.choice([0, 10, 15, 20, 25, 30]),
                'brand_popularity': 100
            }

            features = encode_features(item_data)
            predicted_price = model.predict([features])[0]

            # Generate retailer-specific URL
            product_url = get_product_url(retailer, brand, category)

            comparisons.append({
                'retailer': retailer,
                'predicted_price': round(predicted_price, 2),
                'discount': item_data['discount_percent'],
                'product_url': product_url,
                'image_url': image_url,
                'rating': round(item_data['rating'], 1)
            })

        # Sort by price
        comparisons.sort(key=lambda x: x['predicted_price'])

        return jsonify({
            'success': True,
            'product': product_name,
            'brand': brand,
            'category': category,
            'image_url': image_url,
            'comparisons': comparisons,
            'best_deal': comparisons[0],
            'worst_deal': comparisons[-1],
            'savings': round(comparisons[-1]['predicted_price'] - comparisons[0]['predicted_price'], 2),
            'average_price': round(sum(c['predicted_price'] for c in comparisons) / len(comparisons), 2),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/batch_predict', methods=['POST'])
@limiter.limit("5 per minute")
def batch_predict():
    """
    Predict prices for multiple items at once with images and links
    
    Request JSON format:
    {
        "items": [
            {"brand": "Zara", "category": "Dress"},
            {"brand": "Nike", "category": "Hoodie"}
        ]
    }
    """
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
                item.setdefault('retailer', 'Myntra')
                item.setdefault('season', 'All-Season')
                item.setdefault('rating', 4.0)
                item.setdefault('discount_percent', 0)
                item.setdefault('brand_popularity', 100)

                features = encode_features(item)
                predicted_price = model.predict([features])[0]

                # Get image and URL
                image_url = get_product_image(item.get('category', 'T-Shirt'))
                product_url = get_product_url(
                    item.get('retailer', 'Myntra'),
                    item.get('brand', 'Unknown'),
                    item.get('category', 'Product')
                )

                predictions.append({
                    'item': {
                        'brand': item.get('brand', 'Unknown'),
                        'category': item.get('category', 'Unknown')
                    },
                    'predicted_price': round(predicted_price, 2),
                    'image_url': image_url,
                    'product_url': product_url,
                    'retailer': item.get('retailer', 'Myntra'),
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
            'successful_predictions': sum(1 for p in predictions if p.get('success')),
            'failed_predictions': sum(1 for p in predictions if not p.get('success')),
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/available_options', methods=['GET'])
def get_available_options():
    """Get available brands, categories, materials, retailers, and seasons"""
    try:
        if not label_encoders:
            return jsonify({
                'error': 'Label encoders not loaded',
                'success': False
            }), 503

        options = {
            'brands': sorted(list(label_encoders['brand'].classes_)) if 'brand' in label_encoders else [],
            'categories': sorted(list(label_encoders['category'].classes_)) if 'category' in label_encoders else [],
            'materials': sorted(list(label_encoders['material'].classes_)) if 'material' in label_encoders else [],
            'retailers': sorted(list(label_encoders['retailer'].classes_)) if 'retailer' in label_encoders else [],
            'seasons': sorted(list(label_encoders['season'].classes_)) if 'season' in label_encoders else []
        }

        return jsonify({
            'success': True,
            'options': options,
            'retailer_urls': RETAILER_URLS,
            'total_brands': len(options['brands']),
            'total_categories': len(options['categories'])
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


# Legacy endpoint aliases (for backward compatibility)
@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict_price_legacy():
    """Legacy endpoint - redirects to /api/predict"""
    return predict_price()


@app.route('/compare', methods=['POST'])
@limiter.limit("20 per minute")
def compare_prices_legacy():
    """Legacy endpoint - redirects to /api/compare"""
    return compare_prices()


@app.route('/batch_predict', methods=['POST'])
@limiter.limit("5 per minute")
def batch_predict_legacy():
    """Legacy endpoint - redirects to /api/batch_predict"""
    return batch_predict()


@app.route('/available_options', methods=['GET'])
def get_available_options_legacy():
    """Legacy endpoint - redirects to /api/available_options"""
    return get_available_options()


# ERROR HANDLERS

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False,
        'available_endpoints': [
            '/', '/health', '/api/predict', '/api/compare', 
            '/api/batch_predict', '/api/available_options'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'success': False,
        'message': 'Please contact support if this persists'
    }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded. Please try again later.',
        'success': False,
        'retry_after': '60 seconds'
    }), 429


# RUN SERVER


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CLOSETLY - FASHION PRICE PREDICTION API")
    print("="*60)
    print(f"Model: {model_name}")
    print(f"Model Loaded: {model is not None}")
    print("\n✨ Enhanced Features:")
    print("  ✓ Product Images (Unsplash)")
    print("  ✓ Retailer Links (Direct redirect)")
    print("  ✓ Price Predictions (ML-powered)")
    print("  ✓ Multi-retailer Comparison")
    print("  ✓ AI Chatbot (Frontend)")
    print("\n🌐 API Endpoints:")
    print("  • GET  /              - Home/HTML UI")
    print("  • GET  /health        - Health check")
    print("  • POST /api/predict   - Single prediction")
    print("  • POST /api/compare   - Price comparison")
    print("  • POST /api/batch_predict - Batch predictions")
    print("  • GET  /api/available_options - Get options")
    print("\nStarting server...")
    print("="*60 + "\n")

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
