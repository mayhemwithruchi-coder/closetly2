/**
 * Fashion Price Prediction API Integration
 * Connect your web app to the ML price prediction API
 */

class FashionPriceAPI {
    constructor(baseURL = '') {
        // Use relative URLs for Render deployment
        this.baseURL = baseURL || '';
        this.cache = new Map();
        this.cacheExpiry = 3600000; // 1 hour in milliseconds
    }

    /**
     * Make API request with error handling
     */
    async makeRequest(endpoint, method = 'GET', data = null) {
        const cacheKey = `${method}:${endpoint}:${JSON.stringify(data)}`;
        
        // Check cache for GET requests
        if (method === 'GET' && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheExpiry) {
                console.log('Returning cached result');
                return cached.data;
            }
        }

        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data && method !== 'GET') {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            
            // Cache successful GET requests
            if (method === 'GET') {
                this.cache.set(cacheKey, {
                    data: result,
                    timestamp: Date.now()
                });
            }

            return result;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Predict price for a single item
     */
    async predictPrice(itemData) {
        try {
            const result = await this.makeRequest('/predict', 'POST', itemData);
            return result;
        } catch (error) {
            console.error('Price prediction failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Compare prices across retailers
     */
    async comparePrices(productData) {
        try {
            const result = await this.makeRequest('/compare', 'POST', productData);
            return result;
        } catch (error) {
            console.error('Price comparison failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Batch predict prices for multiple items
     */
    async batchPredict(items) {
        try {
            const result = await this.makeRequest('/batch_predict', 'POST', { items });
            return result;
        } catch (error) {
            console.error('Batch prediction failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get available options (brands, categories, etc.)
     */
    async getAvailableOptions() {
        try {
            const result = await this.makeRequest('/api/info', 'GET');
            return result;
        } catch (error) {
            console.error('Failed to fetch options:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Check API health
     */
    async checkHealth() {
        try {
            const result = await this.makeRequest('/health', 'GET');
            return result;
        } catch (error) {
            console.error('Health check failed:', error);
            return {
                status: 'unhealthy',
                error: error.message
            };
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('Cache cleared');
    }
}

// =====================================================
// INTEGRATION WITH CLOSETLY APP
// =====================================================

// Initialize API client with relative URLs for Render deployment
const priceAPI = new FashionPriceAPI();

/**
 * Enhanced product recommendation with real price predictions
 */
async function generateProductRecommendationsWithML() {
    const productGrid = document.getElementById('productGrid');
    if (!productGrid) return;
    
    productGrid.innerHTML = '<div class="loading"><div class="spinner"></div><p>Fetching best prices...</p></div>';
    
    try {
        const products = sampleProducts[selectedGender] || sampleProducts.unisex;
        
        // Prepare items for batch prediction
        const itemsForPrediction = products.map(product => ({
            brand: product.brand,
            category: product.category,
            material: 'Cotton', // Default, can be enhanced
            retailer: 'Amazon',
            season: 'All-Season',
            rating: product.rating,
            discount_percent: Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
        }));
        
        // Get ML predictions
        const predictions = await priceAPI.batchPredict(itemsForPrediction);
        
        productGrid.innerHTML = '';
        
        if (predictions.success) {
            products.forEach((product, index) => {
                const prediction = predictions.predictions[index];
                const mlPrice = prediction.success ? prediction.predicted_price : product.price;
                const discount = Math.round(((product.originalPrice - mlPrice) / product.originalPrice) * 100);
                
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    ${discount > 0 ? `<div class="product-badge">-${discount}%</div>` : ''}
                    ${prediction.success ? '<div class="product-badge" style="top: 40px; background: #48bb78;">ML Price</div>' : ''}
                    <div class="product-image">
                        ${getProductIcon(product.category)}
                    </div>
                    <div class="product-info">
                        <div class="product-brand">${product.brand}</div>
                        <div class="product-name">${product.name}</div>
                        <div class="product-rating">
                            <div class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5-Math.floor(product.rating))}</div>
                            <div class="rating-count">(${Math.floor(Math.random() * 500) + 50} reviews)</div>
                        </div>
                        <div class="product-price">
                            <div class="price-current">₹${mlPrice}</div>
                            ${product.originalPrice > mlPrice ? `<div class="price-compare">₹${product.originalPrice}</div>` : ''}
                        </div>
                        <button class="shop-btn" onclick="compareItemPrices('${product.name}', '${product.brand}', '${product.category}')">
                            Compare Prices
                        </button>
                    </div>
                `;
                productGrid.appendChild(card);
            });
        } else {
            // Fallback to original prices if ML fails
            generateProductRecommendations();
        }
        
    } catch (error) {
        console.error('Error generating ML recommendations:', error);
        // Fallback to original implementation
        generateProductRecommendations();
    }
}

/**
 * Compare prices across retailers using ML
 */
async function compareItemPrices(productName, brand, category) {
    // Show loading modal
    showPriceComparisonModal(productName, true);
    
    try {
        const comparison = await priceAPI.comparePrices({
            product_name: productName,
            brand: brand,
            category: category
        });
        
        if (comparison.success) {
            displayPriceComparison(comparison);
        } else {
            alert('Unable to fetch price comparison. Please try again.');
        }
    } catch (error) {
        console.error('Price comparison error:', error);
        alert('Error fetching prices. Please try again later.');
    }
}

/**
 * Show price comparison modal
 */
function showPriceComparisonModal(productName, loading = false) {
    // Remove existing modal if any
    const existingModal = document.getElementById('priceComparisonModal');
    if (existingModal) existingModal.remove();
    
    const modal = document.createElement('div');
    modal.id = 'priceComparisonModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 20px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0;">Price Comparison: ${productName}</h3>
                <button onclick="closePriceModal()" style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
            </div>
            <div id="comparisonContent">
                ${loading ? '<div class="loading"><div class="spinner"></div><p>Comparing prices...</p></div>' : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closePriceModal();
    });
}

/**
 * Display price comparison results
 */
function displayPriceComparison(comparison) {
    const content = document.getElementById('comparisonContent');
    if (!content) return;
    
    const comparisons = comparison.comparisons;
    const bestDeal = comparison.best_deal;
    
    let html = `
        <div style="background: #f0fff4; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #48bb78;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 24px;">🏆</span>
                <strong style="color: #48bb78;">Best Deal: ${bestDeal.retailer}</strong>
            </div>
            <div style="font-size: 24px; font-weight: bold; color: #48bb78;">₹${bestDeal.predicted_price}</div>
            ${bestDeal.discount > 0 ? `<div style="color: #666; margin-top: 5px;">${bestDeal.discount}% discount</div>` : ''}
        </div>
        <div style="margin-top: 20px;">
    `;
    
    comparisons.forEach((item, index) => {
        const isBest = index === 0;
        html += `
            <div style="padding: 15px; margin-bottom: 10px; border-radius: 10px; background: ${isBest ? '#f0fff4' : '#f7fafc'}; border: 2px solid ${isBest ? '#48bb78' : '#e2e8f0'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 5px;">${item.retailer}</div>
                        ${item.discount > 0 ? `<div style="font-size: 12px; color: #666;">${item.discount}% OFF</div>` : ''}
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: bold; color: #667eea;">₹${item.predicted_price}</div>
                        <a href="${item.search_url}" target="_blank" style="font-size: 12px; color: #667eea; text-decoration: none;">View →</a>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    content.innerHTML = html;
}

/**
 * Close price comparison modal
 */
function closePriceModal() {
    const modal = document.getElementById('priceComparisonModal');
    if (modal) modal.remove();
}

/**
 * Enhanced price comparison tab with ML predictions
 */
async function generatePriceComparisonML() {
    const comparisonResults = document.getElementById('comparisonResults');
    if (!comparisonResults) return;
    
    comparisonResults.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading price comparisons...</p></div>';
    
    try {
        const productTypes = ['Blazer', 'Dress Shirt', 'Jeans', 'Dress'];
        const allComparisons = [];
        
        for (const productType of productTypes) {
            const comparison = await priceAPI.comparePrices({
                product_name: productType,
                brand: 'Generic',
                category: productType
            });
            
            if (comparison.success) {
                allComparisons.push({
                    productType,
                    data: comparison
                });
            }
        }
        
        // Display all comparisons
        comparisonResults.innerHTML = '';
        
        allComparisons.forEach(({ productType, data }) => {
            const sectionDiv = document.createElement('div');
            sectionDiv.innerHTML = `<h4 style="margin: 20px 0 15px 0; color: #4a5568;">${productType}</h4>`;
            
            const sortedRetailers = data.comparisons.sort((a, b) => a.predicted_price - b.predicted_price);
            
            sortedRetailers.forEach((item, index) => {
                const isBestDeal = index === 0;
                
                const itemDiv = document.createElement('div');
                itemDiv.className = `comparison-item ${isBestDeal ? 'best-deal' : ''}`;
                itemDiv.innerHTML = `
                    <div class="retailer-info">
                        <div class="retailer-logo">${item.retailer.substring(0, 2)}</div>
                        <div class="product-details">
                            <div class="product-title">${productType}</div>
                            <div class="product-rating-small">
                                <span class="stars">★★★★☆</span>
                                <span>4.0</span>
                            </div>
                            <small style="color: #666;">${item.retailer}</small>
                        </div>
                    </div>
                    <div class="price-section">
                        <div class="current-price">₹${item.predicted_price}</div>
                        ${item.discount > 0 ? `
                            <div class="original-price">₹${(item.predicted_price / (1 - item.discount/100)).toFixed(2)}</div>
                            <div class="discount-badge">${item.discount}% OFF</div>
                        ` : ''}
                        ${isBestDeal ? '<div style="color: #48bb78; font-size: 0.8rem; margin-top: 3px;">Best Deal</div>' : ''}
                    </div>
                `;
                sectionDiv.appendChild(itemDiv);
            });
            
            comparisonResults.appendChild(sectionDiv);
        });
        
    } catch (error) {
        console.error('Error generating ML price comparison:', error);
        // Fallback to original implementation
        generatePriceComparison();
    }
}

/**
 * Initialize ML features when results are shown
 */
function enhanceResultsWithML() {
    // Replace original functions with ML-enhanced versions
    if (typeof generateProductRecommendations !== 'undefined') {
        generateProductRecommendationsWithML();
    }
    
    if (typeof generatePriceComparison !== 'undefined') {
        generatePriceComparisonML();
    }
}

/**
 * Check API connection on page load
 */
async function initializeMLFeatures() {
    try {
        const health = await priceAPI.checkHealth();
        if (health.status === 'healthy') {
            console.log('✅ ML Price Prediction API Connected');
            console.log('Model:', health.model_loaded ? 'Loaded' : 'Not Loaded');
        } else {
            console.warn('⚠️ ML API unhealthy, using fallback prices');
        }
    } catch (error) {
        console.warn('⚠️ ML API not available, using fallback prices');
    }
}

// Initialize on page load
if (typeof window !== 'undefined') {
    window.addEventListener('load', initializeMLFeatures);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FashionPriceAPI, priceAPI };
}

// Helper function to get product icons
function getProductIcon(category) {
    const icons = {
        'dresses': '👗',
        'jeans': '👖',
        'shirts': '👔',
        'blazers': ' Blazers',
        'jackets': '🧥',
        'tops': '👚',
        'skirts': '👗',
        'pants': '👖',
        'suits': '🕴️',
        'hoodies': '🧥',
        'tshirts': '👕',
        'bottoms': '👖'
    };
    return icons[category] || '👕';
}

function generateResults() {
    const bodyTypeInfo = bodyTypeRecommendations[selectedGender][bodyType];
    
    document.getElementById('bodyTypeName').textContent = bodyType;
    document.getElementById('bodyTypeDescription').textContent = bodyTypeInfo.description;
    
    const colorPalette = document.getElementById('colorPalette');
    colorPalette.innerHTML = '';
    dominantColors.forEach(color => {
        const swatch = document.createElement('div');
        swatch.className = 'color-swatch';
        swatch.style.backgroundColor = color;
        colorPalette.appendChild(swatch);
    });
    
    document.getElementById('colorDescription').textContent = 
        userProfile.colorDescription || 'These colors complement your natural features!';
    
    generateStyleRecommendations();
    
    // Use ML-enhanced product recommendations
    generateProductRecommendationsWithML();
}