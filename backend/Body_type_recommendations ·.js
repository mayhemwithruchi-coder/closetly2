/**
 * Highly Specific Body-Type Fashion Recommendations
 * Detailed, differentiated guidance for each body type
 */

const BodyTypeRecommendations = {
    women: {
        'Hourglass': {
            description: 'You have a balanced, proportionate silhouette with a well-defined waist. Your bust and hips are roughly equal in measurement, creating beautiful curves.',
            
            detailedAnalysis: {
                strengths: 'Naturally balanced proportions, defined waistline, feminine curves',
                challenges: 'Avoiding shapeless clothing that hides curves, finding proper fit',
                goal: 'Emphasize waist, maintain balance between top and bottom'
            },
            
            specificItems: {
                tops: [
                    { item: 'Wrap tops in fitted styles', why: 'Cinches waist and follows natural curves', avoid: 'Boxy, oversized tops' },
                    { item: 'V-neck and sweetheart necklines', why: 'Balances proportions and elongates torso', avoid: 'High crew necks that shorten torso' },
                    { item: 'Peplum tops', why: 'Emphasizes waist while adding subtle volume', avoid: 'Shapeless tunics' },
                    { item: 'Fitted button-down shirts', why: 'Shows curves without being tight', avoid: 'Baggy boyfriend shirts' }
                ],
                
                bottoms: [
                    { item: 'High-waisted jeans and trousers', why: 'Accentuates smallest part of waist', avoid: 'Low-rise or mid-rise styles' },
                    { item: 'Pencil skirts with belt', why: 'Highlights curves and defines waist', avoid: 'A-line skirts that hide curves' },
                    { item: 'Bootcut or flared jeans', why: 'Balances hips and creates elegant line', avoid: 'Baggy straight-leg pants' },
                    { item: 'Bodycon midi skirts', why: 'Celebrates your curves tastefully', avoid: 'Pleated or gathered skirts at waist' }
                ],
                
                dresses: [
                    { item: 'Wrap dresses in knee-length', why: 'The wrap style is made for your figure', avoid: 'Shift dresses that hide waist' },
                    { item: 'Fit-and-flare with defined waist', why: 'Shows curves while staying balanced', avoid: 'Empire waist that hides your best feature' },
                    { item: 'Bodycon dresses with structure', why: 'Celebrates proportions when well-made', avoid: 'Oversized maxi dresses' },
                    { item: 'Sheath dresses with belt', why: 'Streamlined with waist emphasis', avoid: 'Sack-style dresses' }
                ],
                
                outerwear: [
                    { item: 'Belted trench coats', why: 'Cinches waist even in outerwear', avoid: 'Straight-cut coats' },
                    { item: 'Cropped jackets hitting at waist', why: 'Shows your proportions', avoid: 'Hip-length jackets' },
                    { item: 'Wrap coats', why: 'Creates that signature cinched look', avoid: 'Boxy peacoats' }
                ]
            },
            
            fabricsAndPatterns: {
                best: ['Structured knits', 'Medium-weight fabrics', 'Vertical stripes', 'Small to medium prints'],
                avoid: ['Overly stiff fabrics', 'Large horizontal stripes', 'Busy all-over patterns']
            },
            
            stylingTips: [
                'Always define your waist - use belts strategically',
                'Choose fitted styles over loose ones',
                'Balance top and bottom - if wearing volume on top, keep bottom fitted',
                'V-necks and scoop necks are your best friends',
                'High-waisted everything to show off that waist'
            ],
            
            celebrityInspiration: ['Salma Hayek', 'Sofia Vergara', 'Priyanka Chopra', 'Marilyn Monroe'],
            
            shoppingPriorities: ['Fit at waist', 'Quality over quantity', 'Tailoring investment', 'Belt collection']
        },
        
        'Pear': {
            description: 'You have narrower shoulders and bust with fuller hips and thighs. Your lower body is your curvier area, creating a feminine silhouette.',
            
            detailedAnalysis: {
                strengths: 'Defined waist, feminine lower curves, delicate shoulders',
                challenges: 'Balancing proportions, finding pants that fit waist and hips',
                goal: 'Draw attention upward, balance shoulders with hips'
            },
            
            specificItems: {
                tops: [
                    { item: 'Boat neck and off-shoulder tops', why: 'Broadens shoulder line to balance hips', avoid: 'Narrow tank tops' },
                    { item: 'Statement sleeve blouses', why: 'Adds visual weight to upper body', avoid: 'Sleeveless with no detail' },
                    { item: 'Bright colored tops', why: 'Draws eye upward', avoid: 'Dark tops with light bottoms' },
                    { item: 'Embellished necklines', why: 'Creates focal point at shoulders', avoid: 'Plain, simple necklines' },
                    { item: 'Horizontal striped tops', why: 'Widens upper body visually', avoid: 'Vertical stripes on top' }
                ],
                
                bottoms: [
                    { item: 'Dark-wash bootcut jeans', why: 'Dark color minimizes, bootcut balances', avoid: 'Light-colored skinny jeans' },
                    { item: 'A-line skirts in dark colors', why: 'Skims over hips without clinging', avoid: 'Tight pencil skirts' },
                    { item: 'Straight-leg trousers', why: 'Creates clean line without emphasizing hips', avoid: 'Tapered ankle pants' },
                    { item: 'Flared pants in structured fabric', why: 'Balances hip width', avoid: 'Cargo pants with pockets' }
                ],
                
                dresses: [
                    { item: 'A-line dresses with detailed bodice', why: 'Eye goes to top, skirt skims hips', avoid: 'Body-con styles' },
                    { item: 'Fit-and-flare with embellished top', why: 'Balances proportions perfectly', avoid: 'Fitted throughout' },
                    { item: 'Wrap dresses with V-neck', why: 'Draws attention to neckline and waist', avoid: 'Empire waist styles' },
                    { item: 'Dresses with structured shoulders', why: 'Creates balance', avoid: 'Spaghetti straps' }
                ],
                
                outerwear: [
                    { item: 'Structured blazers with shoulder pads', why: 'Creates balance across shoulders', avoid: 'Boyfriend blazers' },
                    { item: 'Jackets ending at hip', why: 'Doesn\'t cut across widest point', avoid: 'Cropped jackets at hip level' },
                    { item: 'Detailed lapels and collars', why: 'Draws eye upward', avoid: 'Plain, simple outerwear' }
                ]
            },
            
            fabricsAndPatterns: {
                best: ['Textured fabrics on top', 'Smooth fabrics on bottom', 'Patterns on upper body', 'Solid darks below'],
                avoid: ['Shiny/clingy fabrics on bottom', 'Horizontal stripes below waist', 'Large prints on bottom']
            },
            
            stylingTips: [
                'Invest in statement necklaces and earrings',
                'Wear scarves and accessories near face',
                'Choose interesting sleeves and necklines',
                'Dark colors on bottom, bright colors on top',
                'Structured shoulders are your secret weapon',
                'Find a good tailor for perfect-fit pants'
            ],
            
            celebrityInspiration: ['Jennifer Lopez', 'Beyoncé', 'Shakira', 'Rihanna'],
            
            shoppingPriorities: ['Statement tops', 'Dark wash jeans', 'Accessories', 'Structured blazers']
        },
        
        'Apple': {
            description: 'You carry weight in your midsection with broader shoulders and a less defined waist. Your legs are often slim, and you may have a fuller bust.',
            
            detailedAnalysis: {
                strengths: 'Great legs, nice shoulders, balanced overall look',
                challenges: 'Creating waist definition, finding comfortable fits at midsection',
                goal: 'Create vertical lines, define waistline, show off legs'
            },
            
            specificItems: {
                tops: [
                    { item: 'Empire waist tops', why: 'Defines line above natural waist', avoid: 'Tight fitted tops at waist' },
                    { item: 'V-neck tunics', why: 'Elongates torso vertically', avoid: 'Crew necks that widen' },
                    { item: 'Wrap tops with draping', why: 'Creates diagonal lines, flattering drape', avoid: 'Clingy knits' },
                    { item: 'Tops with vertical details', why: 'Lengthens torso visually', avoid: 'Horizontal stripes' },
                    { item: 'Flowy blouses with structure', why: 'Skims without clinging', avoid: 'Tight-fitted shirts' }
                ],
                
                bottoms: [
                    { item: 'Straight-leg jeans', why: 'Clean line, shows off legs', avoid: 'Wide-leg that overwhelms' },
                    { item: 'Bootcut in dark wash', why: 'Balances proportions', avoid: 'High-rise that emphasizes middle' },
                    { item: 'Pencil skirts', why: 'Shows off slimmer lower half', avoid: 'Gathered waists' },
                    { item: 'Slim ankle pants', why: 'Highlights great legs', avoid: 'Baggy boyfriend styles' }
                ],
                
                dresses: [
                    { item: 'A-line dresses', why: 'Skims over midsection gracefully', avoid: 'Belted at natural waist' },
                    { item: 'Shift dresses with interest below bust', why: 'Flows from bustline', avoid: 'Bodycon styles' },
                    { item: 'Wrap dresses in soft fabric', why: 'Adjustable fit, flattering drape', avoid: 'Tight sheaths' },
                    { item: 'Maxi dresses with empire waist', why: 'Flows beautifully, comfortable', avoid: 'Fitted waistlines' }
                ],
                
                outerwear: [
                    { item: 'Long open cardigans', why: 'Creates vertical line', avoid: 'Cropped boleros' },
                    { item: 'Longline blazers', why: 'Elongates without cutting torso', avoid: 'Cropped jackets' },
                    { item: 'Waterfall cardigans', why: 'Flowing vertical lines', avoid: 'Belted coats' }
                ]
            },
            
            fabricsAndPatterns: {
                best: ['Flowing fabrics', 'Vertical stripes', 'Small prints', 'Structured but not stiff'],
                avoid: ['Clingy materials', 'Horizontal stripes', 'Large bold patterns at midsection']
            },
            
            stylingTips: [
                'Monochromatic outfits create long vertical lines',
                'Show off those legs with skirts and dresses',
                'Layer with long pieces - cardigans, dusters',
                'V-necks are your most flattering neckline',
                'Strategic draping is your best friend',
                'Don\'t hide under baggy clothes - skimming is better'
            ],
            
            celebrityInspiration: ['Drew Barrymore', 'Queen Latifah', 'Catherine Zeta-Jones', 'Angelina Jolie'],
            
            shoppingPriorities: ['V-neck collection', 'Empire waist pieces', 'Long cardigans', 'Show-off-legs pieces']
        },
        
        'Rectangle': {
            description: 'You have a straight, athletic build with shoulders, waist, and hips of similar width. Your silhouette is streamlined with minimal curves.',
            
            detailedAnalysis: {
                strengths: 'Athletic build, can wear many styles, balanced proportions',
                challenges: 'Creating curves and waist definition',
                goal: 'Add curves, create waist illusion, add femininity'
            },
            
            specificItems: {
                tops: [
                    { item: 'Peplum tops', why: 'Creates curve at waist', avoid: 'Straight boxy tops' },
                    { item: 'Ruffled blouses', why: 'Adds dimension and femininity', avoid: 'Plain tank tops' },
                    { item: 'Wrap tops', why: 'Creates diagonal lines and curve suggestion', avoid: 'Tube tops' },
                    { item: 'Belted tunics', why: 'Defines waist where there isn\'t one', avoid: 'Straight shift tops' }
                ],
                
                bottoms: [
                    { item: 'High-waisted with belt', why: 'Creates waist definition', avoid: 'Low-rise straight styles' },
                    { item: 'Cargo pants with pockets', why: 'Adds volume at hips', avoid: 'Plain straight-leg' },
                    { item: 'Flared jeans', why: 'Creates curve at hip and leg', avoid: 'Skinny jeans without detail' },
                    { item: 'Pleated skirts', why: 'Adds volume and movement', avoid: 'Straight pencil skirts' }
                ],
                
                dresses: [
                    { item: 'Fit-and-flare with belt', why: 'Creates waist and adds curves', avoid: 'Straight shift dresses' },
                    { item: 'Tiered dresses', why: 'Adds dimension through layers', avoid: 'Column dresses' },
                    { item: 'Dresses with ruching at waist', why: 'Creates shape where needed', avoid: 'Sack dresses' },
                    { item: 'Wrap dresses belted', why: 'Adjustable waist definition', avoid: 'Straight cuts' }
                ],
                
                outerwear: [
                    { item: 'Belted trench coats', why: 'Creates waist in outerwear', avoid: 'Straight peacoats' },
                    { item: 'Peplum jackets', why: 'Adds curve at waist', avoid: 'Boxy boyfriend blazers' },
                    { item: 'Structured blazers with belts', why: 'Defines shape', avoid: 'Unstructured long coats' }
                ]
            },
            
            fabricsAndPatterns: {
                best: ['Textured fabrics', 'Bold prints', 'Layered looks', 'Color blocking at waist'],
                avoid: ['Super smooth fabrics', 'Vertical stripes only', 'Minimalist plain styles']
            },
            
            stylingTips: [
                'Belts are your best accessory - use them everywhere',
                'Layer to create dimension',
                'Textured and embellished pieces add curves',
                'Color blocking at waist creates definition',
                'Don\'t be afraid of ruffles, pleats, and details',
                'Crop tops with high-waisted bottoms work great'
            ],
            
            celebrityInspiration: ['Cameron Diaz', 'Kate Hudson', 'Nicole Kidman', 'Keira Knightley'],
            
            shoppingPriorities: ['Belt collection', 'Peplum styles', 'Textured pieces', 'High-waisted bottoms']
        },
        
        'Inverted Triangle': {
            description: 'You have broader shoulders and bust with narrower hips. Your athletic upper body is your strongest feature, with a well-defined shoulder line.',
            
            detailedAnalysis: {
                strengths: 'Athletic shoulders, defined upper body, great for statement pieces',
                challenges: 'Balancing proportions, not over-emphasizing shoulders',
                goal: 'Balance upper body with lower, add volume to hips, soften shoulders'
            },
            
            specificItems: {
                tops: [
                    { item: 'V-neck tees', why: 'Softens and elongates neckline', avoid: 'Boat necks that widen' },
                    { item: 'Scoop neck blouses', why: 'Creates softer upper line', avoid: 'Off-shoulder styles' },
                    { item: 'Wrap tops in dark colors', why: 'Streamlines upper body', avoid: 'Shoulder pad styles' },
                    { item: 'Raglan sleeves', why: 'De-emphasizes shoulder width', avoid: 'Cap sleeves' },
                    { item: 'Flowy unstructured tops', why: 'Softens shoulder line', avoid: 'Structured blazers with pads' }
                ],
                
                bottoms: [
                    { item: 'Wide-leg trousers', why: 'Adds volume to balance shoulders', avoid: 'Skinny jeans' },
                    { item: 'Flared jeans in light wash', why: 'Creates volume at bottom', avoid: 'Dark slim-fit' },
                    { item: 'Pleated skirts', why: 'Adds fullness to lower half', avoid: 'Straight pencil skirts' },
                    { item: 'Palazzo pants', why: 'Dramatic volume balances top', avoid: 'Leggings alone' },
                    { item: 'A-line skirts with details', why: 'Adds curves to hips', avoid: 'Plain fitted skirts' }
                ],
                
                dresses: [
                    { item: 'A-line dresses', why: 'Perfect proportion balancing', avoid: 'Fitted sheaths' },
                    { item: 'Fit-and-flare', why: 'Shows waist, adds volume below', avoid: 'Shift dresses' },
                    { item: 'Wrap dresses with fuller skirt', why: 'Balances top and bottom', avoid: 'Bodycon styles' },
                    { item: 'Dresses with detailed skirts', why: 'Draws eye downward', avoid: 'Embellished necklines' }
                ],
                
                outerwear: [
                    { item: 'Unstructured long cardigans', why: 'Doesn\'t add shoulder bulk', avoid: 'Structured shoulder pad blazers' },
                    { item: 'Waterfall draping coats', why: 'Soft lines, no shoulder emphasis', avoid: 'Military-style jackets' },
                    { item: 'A-line coats', why: 'Balances proportions in outerwear', avoid: 'Cropped jackets' }
                ]
            },
            
            fabricsAndPatterns: {
                best: ['Soft flowy fabrics on top', 'Bold patterns on bottom', 'Light colors below', 'Dark colors above'],
                avoid: ['Shoulder details', 'Horizontal stripes on top', 'Stiff structured fabrics above']
            },
            
            stylingTips: [
                'Dark on top, light on bottom is your formula',
                'Avoid anything that adds shoulder width',
                'Show off your great legs with detailed bottoms',
                'V-necks are more flattering than wide necklines',
                'Add volume and interest to your lower half',
                'Accessories: focus on hip-level, avoid big statement necklaces'
            ],
            
            celebrityInspiration: ['Demi Moore', 'Naomi Campbell', 'Renée Zellweger', 'Angelina Jolie'],
            
            shoppingPriorities: ['Wide-leg pants', 'A-line skirts', 'Flared jeans', 'V-neck collection']
        }
    },
    
    // Add men's and unisex categories as needed...
    men: {
        // Similar detailed structure for men's body types
    },
    
    unisex: {
        // Similar detailed structure for non-binary/fluid styles
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BodyTypeRecommendations;
}
