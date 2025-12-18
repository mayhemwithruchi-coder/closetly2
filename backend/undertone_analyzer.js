/**
 * Advanced Skin Undertone Analysis Algorithm
 * Uses multiple factors for highly accurate undertone detection
 */

class UndertoneAnalyzer {
    constructor() {
        this.weights = {
            veinColor: 0.35,
            jewelryPreference: 0.20,
            sunReaction: 0.15,
            whiteClothingEffect: 0.15,
            naturalHairEyeColor: 0.15
        };
    }

    /**
     * Analyze skin undertone from image using advanced color analysis
     * @param {ImageData} imageData - Canvas image data
     * @param {Object} userInputs - User-provided data for verification
     * @returns {Object} - Undertone analysis results
     */
    analyzeFromImage(imageData, userInputs = {}) {
        const skinTones = this.extractSkinTones(imageData);
        const rgbAnalysis = this.analyzeRGBRatios(skinTones);
        const labAnalysis = this.analyzeLabColor(skinTones);
        
        let score = {
            warm: 0,
            cool: 0,
            neutral: 0
        };

        // RGB-based analysis (30% weight)
        if (rgbAnalysis.warmth > 0.6) {
            score.warm += 0.30;
        } else if (rgbAnalysis.warmth < 0.4) {
            score.cool += 0.30;
        } else {
            score.neutral += 0.30;
        }

        // LAB color space analysis (40% weight)
        if (labAnalysis.aValue > 5) { // More red = warm
            score.warm += 0.40 * (labAnalysis.aValue / 15);
            score.cool += 0.40 * (1 - labAnalysis.aValue / 15);
        }
        
        if (labAnalysis.bValue > 5) { // More yellow = warm
            score.warm += 0.40 * (labAnalysis.bValue / 20);
        } else if (labAnalysis.bValue < -5) { // More blue = cool
            score.cool += 0.40;
        }

        // User input verification (30% weight)
        if (userInputs.veinColor) {
            const veinScore = this.analyzeVeinColor(userInputs.veinColor);
            score.warm += veinScore.warm * 0.30;
            score.cool += veinScore.cool * 0.30;
            score.neutral += veinScore.neutral * 0.30;
        }

        // Normalize scores
        const total = score.warm + score.cool + score.neutral;
        score.warm = (score.warm / total) * 100;
        score.cool = (score.cool / total) * 100;
        score.neutral = (score.neutral / total) * 100;

        // Determine primary undertone
        let undertone = 'neutral';
        let confidence = 'medium';
        
        if (score.warm > 60) {
            undertone = 'warm';
            confidence = score.warm > 75 ? 'high' : 'medium';
        } else if (score.cool > 60) {
            undertone = 'cool';
            confidence = score.cool > 75 ? 'high' : 'medium';
        } else if (Math.abs(score.warm - score.cool) < 15) {
            undertone = 'neutral';
            confidence = 'high';
        }

        // Determine color season
        const colorSeason = this.determineColorSeason(undertone, labAnalysis.lValue, score);

        return {
            undertone,
            confidence,
            scores: score,
            colorSeason,
            analysis: {
                rgb: rgbAnalysis,
                lab: labAnalysis
            }
        };
    }

    /**
     * Extract skin tone pixels from image
     */
    extractSkinTones(imageData) {
        const pixels = [];
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            // Filter for skin tones using expanded criteria
            if (this.isSkinTone(r, g, b)) {
                pixels.push({ r, g, b });
            }
        }
        
        return pixels;
    }

    /**
     * Check if RGB values represent skin tone
     */
    isSkinTone(r, g, b) {
        // Expanded skin tone detection for diverse skin tones
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        
        // Basic skin tone criteria
        if (r > 95 && g > 40 && b > 20 &&
            max - min > 15 &&
            Math.abs(r - g) > 15 &&
            r > g && r > b) {
            return true;
        }
        
        // Dark skin tones
        if (r > 40 && r < 95 && 
            g > 20 && g < 80 &&
            b > 15 && b < 70 &&
            r > g && g >= b) {
            return true;
        }
        
        return false;
    }

    /**
     * Analyze RGB ratios for warmth/coolness
     */
    analyzeRGBRatios(pixels) {
        if (pixels.length === 0) {
            return { warmth: 0.5, saturation: 0 };
        }

        let totalR = 0, totalG = 0, totalB = 0;
        
        pixels.forEach(pixel => {
            totalR += pixel.r;
            totalG += pixel.g;
            totalB += pixel.b;
        });
        
        const avgR = totalR / pixels.length;
        const avgG = totalG / pixels.length;
        const avgB = totalB / pixels.length;
        
        // Calculate warmth index (higher = warmer)
        const warmth = (avgR + avgG) / (avgR + avgG + 2 * avgB);
        
        // Calculate saturation
        const max = Math.max(avgR, avgG, avgB);
        const min = Math.min(avgR, avgG, avgB);
        const saturation = max > 0 ? (max - min) / max : 0;
        
        return {
            warmth,
            saturation,
            avgR,
            avgG,
            avgB
        };
    }

    /**
     * Convert RGB to LAB color space for better analysis
     */
    analyzeLabColor(pixels) {
        if (pixels.length === 0) {
            return { lValue: 50, aValue: 0, bValue: 0 };
        }

        // Average RGB
        let avgR = 0, avgG = 0, avgB = 0;
        pixels.forEach(p => {
            avgR += p.r;
            avgG += p.g;
            avgB += p.b;
        });
        avgR /= pixels.length;
        avgG /= pixels.length;
        avgB /= pixels.length;

        // Convert to LAB
        const lab = this.rgbToLab(avgR, avgG, avgB);
        
        return lab;
    }

    /**
     * RGB to LAB conversion
     */
    rgbToLab(r, g, b) {
        // Normalize RGB
        r = r / 255;
        g = g / 255;
        b = b / 255;

        // Convert to XYZ
        r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
        g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
        b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

        let x = (r * 0.4124 + g * 0.3576 + b * 0.1805) * 100;
        let y = (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100;
        let z = (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100;

        // Convert XYZ to LAB
        x = x / 95.047;
        y = y / 100.000;
        z = z / 108.883;

        x = x > 0.008856 ? Math.pow(x, 1/3) : (7.787 * x) + 16/116;
        y = y > 0.008856 ? Math.pow(y, 1/3) : (7.787 * y) + 16/116;
        z = z > 0.008856 ? Math.pow(z, 1/3) : (7.787 * z) + 16/116;

        const lValue = (116 * y) - 16;
        const aValue = 500 * (x - y);
        const bValue = 200 * (y - z);

        return { lValue, aValue, bValue };
    }

    /**
     * Analyze vein color (user input)
     */
    analyzeVeinColor(veinColor) {
        const scores = {
            'green': { warm: 0.9, cool: 0.05, neutral: 0.05 },
            'blue': { warm: 0.05, cool: 0.9, neutral: 0.05 },
            'blue-green': { warm: 0.4, cool: 0.4, neutral: 0.2 },
            'purple': { warm: 0.1, cool: 0.8, neutral: 0.1 },
            'unsure': { warm: 0.33, cool: 0.33, neutral: 0.34 }
        };
        
        return scores[veinColor] || scores['unsure'];
    }

    /**
     * Determine seasonal color analysis
     */
    determineColorSeason(undertone, lValue, scores) {
        // Spring: Warm + Light
        // Summer: Cool + Light
        // Autumn: Warm + Deep
        // Winter: Cool + Deep
        
        const isLight = lValue > 60;
        
        if (undertone === 'warm') {
            return isLight ? 'spring' : 'autumn';
        } else if (undertone === 'cool') {
            return isLight ? 'summer' : 'winter';
        } else {
            // Neutral can be soft summer or soft autumn
            return scores.cool > scores.warm ? 'summer' : 'autumn';
        }
    }

    /**
     * Get recommended colors based on analysis
     */
    getRecommendedColors(colorSeason, undertone) {
        const colorPalettes = {
            spring: {
                colors: ['#FFD700', '#FF6B6B', '#FFA07A', '#98D8C8', '#F7DC6F', '#85C1E2', '#FFDAB9', '#FF69B4'],
                description: 'Warm, bright colors with yellow undertones. Think coral, peach, golden yellow, and warm pink.',
                avoid: ['Black', 'Pure white', 'Navy', 'Dark purple']
            },
            summer: {
                colors: ['#B4A7D6', '#87CEEB', '#DDA0DD', '#F0E68C', '#E6E6FA', '#AFEEEE', '#C4C4E8', '#FFB6C1'],
                description: 'Cool, soft colors with blue undertones. Lavender, powder blue, soft pink, and dusty rose.',
                avoid: ['Orange', 'Warm browns', 'Golden yellows', 'Bright warm colors']
            },
            autumn: {
                colors: ['#CD853F', '#D2691E', '#8B4513', '#DAA520', '#B8860B', '#BC8F8F', '#A0522D', '#8B6508'],
                description: 'Warm, rich earthy tones. Rust, olive, camel, burgundy, and warm browns.',
                avoid: ['Bright pink', 'Cool blues', 'Icy pastels', 'Pure black']
            },
            winter: {
                colors: ['#000080', '#8B0000', '#4B0082', '#2F4F4F', '#DC143C', '#1C1C1C', '#191970', '#800020'],
                description: 'Cool, vivid colors and true neutrals. Navy, burgundy, pure black, pure white, and jewel tones.',
                avoid: ['Orange', 'Golden yellow', 'Warm browns', 'Muted earth tones']
            }
        };
        
        return colorPalettes[colorSeason] || colorPalettes.autumn;
    }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UndertoneAnalyzer;
}
