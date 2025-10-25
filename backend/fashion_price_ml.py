"""
Fashion Price Prediction ML Model
Complete pipeline for scraping, training, and predicting fashion item prices
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import requests
from bs4 import BeautifulSoup
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 1. DATA COLLECTION MODULE


class FashionDataScraper:
    """Scrapes fashion product data from multiple retailers"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []

    def scrape_amazon_fashion(self, search_query, pages=5):
        """Scrape Amazon fashion products"""
        base_url = "https://www.amazon.com/s?k="

        for page in range(1, pages + 1):
            url = f"{base_url}{search_query}&page={page}"
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                products = soup.find_all('div', {'data-component-type': 's-search-result'})

                for product in products:
                    try:
                        title = product.find('h2', {'class': 'a-size-mini'})
                        price = product.find('span', {'class': 'a-price-whole'})
                        rating = product.find('span', {'class': 'a-icon-alt'})
                        brand = product.find('span', {'class': 'a-size-base-plus'})

                        if title and price:
                            self.data.append({
                                'name': title.text.strip(),
                                'price': float(price.text.replace(',', '').replace('$', '')),
                                'brand': brand.text.strip() if brand else 'Generic',
                                'rating': float(rating.text.split()[0]) if rating else 0,
                                'retailer': 'Amazon',
                                'date_scraped': datetime.now().strftime('%Y-%m-%d')
                            })
                    except Exception as e:
                        continue

            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

    def generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic fashion data for training - INDIAN MARKET"""

        brands = {
            'premium_indian': ['Van Heusen', 'Allen Solly', 'Louis Philippe', 'Peter England', 'Raymond',
                              'AND', 'W for Woman', 'Forever New', 'Vero Moda', 'Only'],
            'luxury': ['Zara', 'Marks & Spencer', 'Tommy Hilfiger', 'Calvin Klein'],
            'affordable': ['Flying Machine', 'Roadster', 'Wrogn', 'Mast & Harbour', 'Athena',
                          'HRX', 'Being Human', 'Breakbounce'],
            'international': ['Levi\'s', 'Nike', 'Adidas', 'Puma', 'H&M', 'US Polo Assn']
        }

        all_brands = [b for category in brands.values() for b in category]

        categories = ['Jeans', 'Dress', 'Shirt', 'Blazer', 'T-Shirt', 'Jacket',
                      'Sweater', 'Pants', 'Skirt', 'Coat', 'Hoodie', 'Polo', 'Chinos']

        materials = ['Cotton', 'Polyester', 'Denim', 'Wool', 'Silk', 'Leather',
                     'Linen', 'Synthetic', 'Viscose', 'Blend']

        retailers = ['Myntra', 'Ajio', 'Flipkart', 'Amazon India', 'Lifestyle',
                     'Reliance Trends', 'Westside', 'Shoppers Stop', 'Max Fashion']

        seasons = ['Spring', 'Summer', 'Monsoon', 'Winter', 'All-Season']

        # Brand price ranges (base prices in INR)
        brand_base_prices = {
            # Premium Indian
            'Van Heusen': (800, 2500), 'Allen Solly': (900, 2800), 'Louis Philippe': (1000, 3500),
            'Peter England': (600, 2000), 'Raymond': (1200, 5000),
            'AND': (800, 3000), 'W for Woman': (700, 2500), 'Forever New': (1200, 4000),
            'Vero Moda': (1000, 3500), 'Only': (800, 2800),

            # Luxury
            'Zara': (1500, 6000), 'Marks & Spencer': (1500, 5500),
            'Tommy Hilfiger': (2000, 8000), 'Calvin Klein': (1800, 7000),

            # Affordable
            'Flying Machine': (500, 1500), 'Roadster': (400, 1200), 'Wrogn': (600, 1800),
            'Mast & Harbour': (400, 1300), 'Athena': (500, 1500), 'HRX': (600, 1800),
            'Being Human': (700, 2000), 'Breakbounce': (800, 2200),

            # International
            'Levi\'s': (1500, 4000), 'Nike': (1200, 5000), 'Adidas': (1000, 4500),
            'Puma': (900, 3500), 'H&M': (500, 2000), 'US Polo Assn': (800, 2500)
        }

        # Category multipliers
        category_multipliers = {
            'Jeans': 1.0, 'Dress': 1.2, 'Shirt': 0.8, 'Blazer': 1.6,
            'T-Shirt': 0.4, 'Jacket': 1.5, 'Sweater': 0.9, 'Pants': 0.9,
            'Skirt': 0.8, 'Coat': 2.0, 'Hoodie': 0.7, 'Polo': 0.6, 'Chinos': 0.9
        }

        data = []

        for _ in range(n_samples):
            brand = np.random.choice(all_brands)
            category = np.random.choice(categories)
            material = np.random.choice(materials)
            retailer = np.random.choice(retailers)
            season = np.random.choice(seasons)

            # Base price from brand (in INR)
            base_min, base_max = brand_base_prices[brand]
            base_price = np.random.uniform(base_min, base_max)

            # Apply category multiplier
            price = base_price * category_multipliers[category]

            # Material adjustment
            material_adjustments = {
                'Silk': 1.3, 'Leather': 1.5, 'Wool': 1.2,
                'Cotton': 1.0, 'Polyester': 0.9, 'Denim': 1.0,
                'Linen': 1.1, 'Synthetic': 0.8, 'Viscose': 0.9, 'Blend': 0.95
            }
            price *= material_adjustments[material]

            # Retailer adjustment
            retailer_adjustments = {
                'Shoppers Stop': 1.2, 'Lifestyle': 1.15, 'Westside': 1.1,
                'Myntra': 1.0, 'Ajio': 0.98, 'Flipkart': 0.95,
                'Amazon India': 0.95, 'Reliance Trends': 0.9, 'Max Fashion': 0.85
            }
            price *= retailer_adjustments[retailer]

            # Add some randomness
            price *= np.random.uniform(0.9, 1.1)

            # Rating (higher price brands tend to have better ratings)
            base_rating = 3.8
            if brand in ['Zara', 'Marks & Spencer', 'Tommy Hilfiger', 'Calvin Klein', 'Raymond']:
                base_rating = 4.5
            elif brand in ['Van Heusen', 'Allen Solly', 'Louis Philippe', 'Levi\'s']:
                base_rating = 4.3
            rating = min(5.0, base_rating + np.random.uniform(-0.4, 0.4))

            # Discount percentage (common in India)
            discount = np.random.choice([0, 10, 15, 20, 25, 30, 40, 50, 60, 70],
                                       p=[0.1, 0.1, 0.15, 0.15, 0.15, 0.15, 0.1, 0.05, 0.03, 0.02])

            original_price = price / (1 - discount/100) if discount > 0 else price

            data.append({
                'brand': brand,
                'category': category,
                'material': material,
                'retailer': retailer,
                'season': season,
                'rating': round(rating, 1),
                'discount_percent': discount,
                'original_price': round(original_price, 2),
                'current_price': round(price, 2),
                'date_scraped': datetime.now().strftime('%Y-%m-%d')
            })

        return pd.DataFrame(data)

    def save_data(self, filename='fashion_data.csv'):
        """Save scraped data to CSV"""
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        return df


# 2. DATA PREPROCESSING MODULE


class FashionDataPreprocessor:
    """Preprocesses fashion data for ML training"""

    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def preprocess(self, df):
        """Complete preprocessing pipeline"""

        # Create a copy
        df_processed = df.copy()

        # Feature engineering
        df_processed['price_range'] = pd.cut(df_processed['current_price'],
                                             bins=[0, 50, 100, 200, 500, 5000],
                                             labels=['Budget', 'Mid', 'Premium', 'Luxury', 'Ultra-Luxury'])

        # Brand popularity (simplified - based on frequency in dataset)
        brand_counts = df_processed['brand'].value_counts()
        df_processed['brand_popularity'] = df_processed['brand'].map(brand_counts)

        # Encode categorical variables
        categorical_cols = ['brand', 'category', 'material', 'retailer', 'season']

        for col in categorical_cols:
            le = LabelEncoder()
            df_processed[f'{col}_encoded'] = le.fit_transform(df_processed[col])
            self.label_encoders[col] = le

        return df_processed

    def prepare_features(self, df):
        """Prepare feature matrix and target variable"""

        feature_cols = ['brand_encoded', 'category_encoded', 'material_encoded',
                       'retailer_encoded', 'season_encoded', 'rating',
                       'discount_percent', 'brand_popularity']

        X = df[feature_cols]
        y = df['current_price']

        return X, y

    def save_preprocessor(self, filename='preprocessor.pkl'):
        """Save preprocessor for later use"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'label_encoders': self.label_encoders,
                'scaler': self.scaler
            }, f)
        print(f"Preprocessor saved to {filename}")



# 3. MODEL TRAINING MODULE


class FashionPricePredictor:
    """Trains and evaluates price prediction models"""

    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=200, max_depth=20,
                                                   random_state=42, n_jobs=-1),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=200,
                                                          max_depth=10, random_state=42),
            'xgboost': XGBRegressor(n_estimators=200, max_depth=10,
                                   learning_rate=0.1, random_state=42)
        }
        self.best_model = None
        self.best_model_name = None

    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train all models and compare performance"""

        results = {}

        print("\n" + "="*60)
        print("TRAINING MODELS")
        print("="*60)

        for name, model in self.models.items():
            print(f"\nTraining {name}...")

            # Train model
            model.fit(X_train, y_train)

            # Make predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

            results[name] = {
                'model': model,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'mape': mape,
                'predictions': y_pred
            }

            print(f"  MAE: ${mae:.2f}")
            print(f"  RMSE: ${rmse:.2f}")
            print(f"  R² Score: {r2:.4f}")
            print(f"  MAPE: {mape:.2f}%")

        # Select best model (lowest MAE)
        best_name = min(results.keys(), key=lambda k: results[k]['mae'])
        self.best_model = results[best_name]['model']
        self.best_model_name = best_name

        print("\n" + "="*60)
        print(f"BEST MODEL: {best_name.upper()}")
        print("="*60)

        return results

    def predict_price(self, features):
        """Predict price for new item"""
        if self.best_model is None:
            raise ValueError("Model not trained yet!")

        prediction = self.best_model.predict([features])[0]
        return round(prediction, 2)

    def save_model(self, filename='price_predictor_model.pkl'):
        """Save the best trained model"""
        if self.best_model is None:
            raise ValueError("No model to save!")

        with open(filename, 'wb') as f:
            pickle.dump({
                'model': self.best_model,
                'model_name': self.best_model_name
            }, f)
        print(f"\nModel saved to {filename}")



# 4. MAIN EXECUTION


def main():
    print("="*60)
    print("FASHION PRICE PREDICTION ML PIPELINE")
    print("="*60)

    # Step 1: Generate/Load Data
    print("\n[Step 1/4] Generating Training Data...")
    scraper = FashionDataScraper()
    df = scraper.generate_synthetic_data(n_samples=2000)
    print(f"Generated {len(df)} samples")
    print("\nData Sample:")
    print(df.head())

    # Step 2: Preprocess Data
    print("\n[Step 2/4] Preprocessing Data...")
    preprocessor = FashionDataPreprocessor()
    df_processed = preprocessor.preprocess(df)
    X, y = preprocessor.prepare_features(df_processed)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Step 3: Train Models
    print("\n[Step 3/4] Training ML Models...")
    predictor = FashionPricePredictor()
    results = predictor.train_all_models(X_train, y_train, X_test, y_test)

    # Step 4: Save Everything
    print("\n[Step 4/4] Saving Models and Preprocessors...")
    predictor.save_model('fashion_price_model.pkl')
    preprocessor.save_preprocessor('fashion_preprocessor.pkl')
    df.to_csv('fashion_training_data.csv', index=False)

    # Example Prediction
    print("\n" + "="*60)
    print("EXAMPLE PREDICTION")
    print("="*60)

    example_item = {
        'brand': 'Zara',
        'category': 'Blazer',
        'material': 'Wool',
        'retailer': 'Nordstrom',
        'season': 'Fall',
        'rating': 4.5,
        'discount_percent': 20
    }

    print("\nPredicting price for:")
    for key, value in example_item.items():
        print(f"  {key}: {value}")

    # Encode the example
    encoded_features = []
    for col in ['brand', 'category', 'material', 'retailer', 'season']:
        if col in preprocessor.label_encoders and example_item[col] in preprocessor.label_encoders[col].classes_:
            encoded_val = preprocessor.label_encoders[col].transform([example_item[col]])[0]
        else:
            # Handle unseen labels by assigning a default value (e.g., 0)
            encoded_val = 0
        encoded_features.append(encoded_val)

    encoded_features.extend([
        example_item['rating'],
        example_item['discount_percent'],
        100  # brand_popularity (placeholder)
    ])

    predicted_price = predictor.predict_price(encoded_features)
    print(f"\nPredicted Price: ${predicted_price}")

    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print("  - fashion_price_model.pkl (trained model)")
    print("  - fashion_preprocessor.pkl (data preprocessor)")
    print("  - fashion_training_data.csv (training dataset)")


if __name__ == "__main__":
    main()
