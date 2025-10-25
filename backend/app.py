"""
Complete Closetly App for Render Deployment
Serves HTML frontend + API backend in one app
"""
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# --------------- INDIAN FASHION DATA ---------------

BRAND_PRICES = {
    'Van Heusen': (800, 2500), 'Allen Solly': (900, 2800), 'Louis Philippe': (1000, 3500),
    'Peter England': (600, 2000), 'Raymond': (1200, 5000), 'AND': (800, 3000),
    'Vero Moda': (1000, 3500), 'Forever New': (1200, 4000), 'Marks & Spencer': (1500, 5500),
    'Zara': (1500, 6000), 'Levi\'s': (1500, 4000), 'Nike': (1200, 5000),
    'Adidas': (1000, 4500), 'H&M': (500, 2000), 'Being Human': (700, 2000)
}

CATEGORY_MULTIPLIERS = {
    'Jeans': 1.0, 'Dress': 1.2, 'Shirt': 0.8, 'Blazer': 1.6, 'T-Shirt': 0.4,
    'Jacket': 1.5, 'Sweater': 0.9, 'Pants': 0.9, 'Skirt': 0.8, 'Suits': 3.0
}

RETAILER_ADJUSTMENTS = {
    'Myntra': 1.0, 'Ajio': 0.98, 'Flipkart': 0.95, 'Amazon India': 0.95,
    'Lifestyle': 1.15, 'Westside': 1.1, 'Shoppers Stop': 1.2
}

# --------------- FRONTEND ROUTES ---------------

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    try:
        return send_from_directory('.', 'closetly_india_complete.html')
    except:
        # If file doesn't exist, serve inline HTML
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Closetly - Fashion Recommendations</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { background: white; color: #333; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto; }
                h1 { color: #667eea; }
                .status { background: #48bb78; color: white; padding: 10px; border-radius: 10px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Closetly API is Running!</h1>
                <div class="status">✅ Server Active</div>
                <p><strong>Upload your closetly_india_complete.html file to see the full app.</strong></p>
                <h3>Available Endpoints:</h3>
                <ul style="text-align: left;">
                    <li>GET / - This page</li>
                    <li>GET /health - Health check</li>
                    <li>POST /predict - Price prediction</li>
                    <li>POST /compare - Price comparison</li>
                </ul>
                <p style="margin-top: 30px;">
                    <a href="/health" style="color: #667eea;">Test Health Endpoint →</a>
                </p>
            </div>
        </body>
        </html>
        '''

@app.route('/closetly_india_complete.html')
def serve_closetly():
    """Serve Closetly HTML"""
    return send_from_directory('.', 'closetly_india_complete.html')

@app.route('/style.css')
def serve_css():
    """Serve CSS file if separate"""
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    """Serve JS file if separate"""
    return send_from_directory('.', 'script.js')

@app.route('/price_api_integration.js')
def serve_price_js():
    """Serve price API integration JS"""
    return send_from_directory('.', 'price_api_integration.js')

# --------------- API ENDPOINTS ---------------

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Closetly API is running',
        'timestamp': datetime.now().isoformat(),
        'region': 'India',
        'version': '1.0'
    })

@app.route('/api/info')
def api_info():
    """API information"""
    return jsonify({
        'app': 'Closetly Fashion API',
        'description': 'AI-powered fashion recommendations for India',
        'endpoints': {
            'GET /': 'Homepage',
            'GET /health': 'Health check',
            'POST /predict': 'Predict single item price',
            'POST /compare': 'Compare prices across retailers',
            'POST /batch_predict': 'Predict multiple items'
        },
        'supported_brands': list(BRAND_PRICES.keys()),
        'supported_retailers': list(RETAILER_ADJUSTMENTS.keys()),
        'currency': 'INR'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict price for a single fashion item"""
    try:
        data = request.get_json()
        
        brand = data.get('brand', 'Generic')
        category = data.get('category', 'Shirt')
        retailer = data.get('retailer', 'Myntra')
        discount_percent = data.get('discount_percent', 0)
        
        # Calculate price
        if brand in BRAND_PRICES:
            base_min, base_max = BRAND_PRICES[brand]
        else:
            base_min, base_max = (500, 2000)
        
        base_price = random.uniform(base_min, base_max)
        category_mult = CATEGORY_MULTIPLIERS.get(category, 1.0)
        retailer_adj = RETAILER_ADJUSTMENTS.get(retailer, 1.0)
        
        price = base_price * category_mult * retailer_adj * random.uniform(0.95, 1.05)
        
        if discount_percent > 0:
            original_price = price / (1 - discount_percent/100)
        else:
            original_price = price * 1.3
        
        return jsonify({
            'success': True,
            'item': {
                'brand': brand,
                'category': category,
                'retailer': retailer
            },
            'prediction': {
                'current_price': round(price, 2),
                'original_price': round(original_price, 2),
                'price_range': {
                    'min': round(price * 0.85, 2),
                    'max': round(price * 1.15, 2)
                },
                'discount_percent': discount_percent,
                'currency': 'INR'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/compare', methods=['POST'])
def compare():
    """Compare prices across retailers"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '')
        brand = data.get('brand', 'Generic')
        category = data.get('category', 'Shirt')
        
        retailers = ['Myntra', 'Flipkart', 'Amazon India', 'Ajio', 'Lifestyle', 'Westside']
        comparisons = []
        
        # Get base price
        if brand in BRAND_PRICES:
            base_min, base_max = BRAND_PRICES[brand]
        else:
            base_min, base_max = (500, 2000)
        
        base_price = random.uniform(base_min, base_max)
        category_mult = CATEGORY_MULTIPLIERS.get(category, 1.0)
        base_price = base_price * category_mult
        
        for retailer in retailers:
            retailer_adj = RETAILER_ADJUSTMENTS.get(retailer, 1.0)
            price = base_price * retailer_adj * random.uniform(0.95, 1.05)
            discount = random.choice([0, 10, 15, 20, 25, 30, 40])
            
            comparisons.append({
                'retailer': retailer,
                'predicted_price': round(price, 2),
                'discount': discount,
                'search_url': get_retailer_url(retailer, product_name)
            })
        
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
    """Predict prices for multiple items"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided', 'success': False}), 400
        
        predictions = []
        
        for item in items:
            brand = item.get('brand', 'Generic')
            category = item.get('category', 'Shirt')
            retailer = item.get('retailer', 'Myntra')
            
            if brand in BRAND_PRICES:
                base_min, base_max = BRAND_PRICES[brand]
            else:
                base_min, base_max = (500, 2000)
            
            base_price = random.uniform(base_min, base_max)
            category_mult = CATEGORY_MULTIPLIERS.get(category, 1.0)
            retailer_adj = RETAILER_ADJUSTMENTS.get(retailer, 1.0)
            
            price = base_price * category_mult * retailer_adj * random.uniform(0.95, 1.05)
            
            predictions.append({
                'item': {'brand': brand, 'category': category},
                'predicted_price': round(price, 2),
                'success': True
            })
        
        return jsonify({
            'success': True,
            'total_items': len(items),
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

def get_retailer_url(retailer, product_name):
    """Generate retailer URLs"""
    product_slug = product_name.lower().replace(' ', '-')
    urls = {
        'Myntra': f"https://www.myntra.com/{product_slug}",
        'Flipkart': f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}",
        'Amazon India': f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}",
        'Ajio': f"https://www.ajio.com/search/?text={product_name.replace(' ', '+')}",
        'Lifestyle': f"https://www.lifestylestores.com/in/en/search/?text={product_name.replace(' ', '+')}",
        'Westside': f"https://www.westside.com/search?q={product_name.replace(' ', '+')}"
    }
    return urls.get(retailer, f"https://www.google.com/search?q={product_name}+{retailer}")

# --------------- ERROR HANDLERS ---------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation',
        'available_endpoints': ['/health', '/predict', '/compare', '/batch_predict']
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'message': str(e)
    }), 500

# --------------- MAIN ENTRY ---------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)