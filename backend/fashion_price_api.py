def get_real_time_prices(product_name, brand):
    """Fetch real-time prices from Indian retailers (simplified)"""
    # In production, integrate with Myntra API, Flipkart API, or similar
    # This is a placeholder that returns mock data
    
    retailers = {
        'Myntra': {'price': None, 'url': f"https://www.myntra.com/{product_name.replace(' ', '-')}"},
        'Flipkart': {'price': None, 'url': f"https://www.flipkart.com/search?q={product_name}"},
        'Amazon India': {'price': None, 'url': f"https://www.amazon.in/s?k={product_name}"},
        'Ajio': {'price': None, 'url': f"https://www.ajio.com/search/?text={product_name}"},
        'Lifestyle': {'price': None, 'url': f"https://www.lifestylestores.com/in/en/search/?text={product_name}"}
    }
    
    """
Flask API for Fashion Price Prediction
Integrates ML model with web application
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS for web app integration

# Load trained model and preprocessor
with open('fashion_price_model.pkl', 'rb') as f:
    model_data = pickle.load(f)
    model = model_data['model']
    model_name = model_data['model_name']

with open('fashion_preprocessor.pkl', 'rb') as f:
    preprocessor_data = pickle.load(f)
    label_encoders = preprocessor_data['label_encoders']

print(f"Loaded {model_name} model successfully!")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def encode_features(item_data):
    """Encode item features for prediction"""
    try:
        encoded_features = []
        
        # Encode categorical features
        for col in ['brand', 'category', 'material', 'retailer', 'season']:
            if col in item_data:
                try:
                    encoded_val = label_encoders[col].transform([item_data[col]])[0]
                except:
                    # If brand/value not in training data, use most common value
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


def get_real_time_prices(product_name, brand):
    """Fetch real-time prices from Indian retailers (simplified)"""
    # In production, integrate with Myntra API, Flipkart API, or similar
    # This is a placeholder that returns mock data
    
    retailers = {
        'Myntra': {'price': None, 'url': f"https://www.myntra.com/{product_name.replace(' ', '-')}"},
        'Flipkart': {'price': None, 'url': f"https://www.flipkart.com/search?q={product_name}"},
        'Amazon India': {'price': None, 'url': f"https://www.amazon.in/s?k={product_name}"},
        'Ajio': {'price': None, 'url': f"https://www.ajio.com/search/?text={product_name}"},
        'Lifestyle': {'price': None, 'url': f"https://www.lifestylestores.com/in/en/search/?text={product_name}"}
    }
    
    # Placeholder: In real implementation, scrape or use APIs
    return retailers


# =====================================================
# API ENDPOINTS
# =====================================================

@app.route('/')
def home():
    """API Home"""
    return jsonify({
        'message': 'Fashion Price Prediction API',
        'version': '1.0',
        'model': model_name,
        'endpoints': {
            '/predict': 'POST - Predict price for a fashion item',
            '/compare': 'POST - Compare prices across retailers',
            '/batch_predict': 'POST - Predict prices for multiple items',
            '/health': 'GET - Check API health'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict_price():
    """
    Predict price for a single fashion item
    
    Request JSON format:
    {
        "brand": "Zara",
        "category": "Blazer",
        "material": "Wool",
        "retailer": "Nordstrom",
        "season": "Fall",
        "rating": 4.5,
        "discount_percent": 20
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['brand', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Set defaults for optional fields
        data.setdefault('material', 'Cotton')
        data.setdefault('retailer', 'Amazon')
        data.setdefault('season', 'All-Season')
        data.setdefault('rating', 4.0)
        data.setdefault('discount_percent', 0)
        data.setdefault('brand_popularity', 100)
        
        # Encode features and predict
        features = encode_features(data)
        predicted_price = model.predict([features])[0]
        
        # Calculate price range (confidence interval)
        price_std = predicted_price * 0.15  # 15% standard deviation
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
                'currency': 'USD'
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
def compare_prices():
    """
    Compare prices across multiple retailers
    
    Request JSON format:
    {
        "product_name": "Women's Blazer",
        "brand": "Zara",
        "category": "Blazer"
    }
    """
    try:
        data = request.get_json()
        product_name = data.get('product_name', '')
        brand = data.get('brand', '')
        category = data.get('category', '')
        
        retailers = ['Amazon', 'Walmart', 'Target', 'Nordstrom', 'Macy\'s', 'ASOS']
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
def batch_predict():
    """
    Predict prices for multiple items at once
    
    Request JSON format:
    {
        "items": [
            {"brand": "Zara", "category": "Blazer", ...},
            {"brand": "H&M", "category": "Dress", ...}
        ]
    }
    """
    try:
        data = request.get_json()
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
                item.setdefault('retailer', 'Amazon')
                item.setdefault('season', 'All-Season')
                item.setdefault('rating', 4.0)
                item.setdefault('discount_percent', 0)
                item.setdefault('brand_popularity', 100)
                
                features = encode_features(item)
                predicted_price = model.predict([features])[0]
                
                predictions.append({
                    'item': {
                        'brand': item['brand'],
                        'category': item['category']
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
        options = {
            'brands': list(label_encoders['brand'].classes_),
            'categories': list(label_encoders['category'].classes_),
            'materials': list(label_encoders['material'].classes_),
            'retailers': list(label_encoders['retailer'].classes_),
            'seasons': list(label_encoders['season'].classes_)
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


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FASHION PRICE PREDICTION API SERVER")
    print("="*60)
    print(f"Model: {model_name}")
    print("Starting server on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
