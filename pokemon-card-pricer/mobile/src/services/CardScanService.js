import axios from 'axios';

// Backend API configuration
const API_BASE_URL = __DEV__ ? 'https://pokemon-card-evaluator-6zuj.onrender.com' : 'https://pokemon-card-evaluator-6zuj.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for image processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

/**
 * Scan a Pokemon card image and get identification + pricing
 * @param {string} imageUri - Local image URI from camera
 * @returns {Promise<Object>} Scan result with card info and pricing
 */
export async function scanCard(imageUri) {
  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'card_scan.jpg',
    });

    console.log('📤 Uploading image for scanning...');
    
    const response = await api.post('/identify', formData);
    
    if (response.data.success) {
      console.log('✅ Card scan successful');
      
      // Enhance the response with mock grading data for demo
      const enhancedResult = {
        ...response.data,
        grading: generateMockGrading(response.data.identified_info?.name),
      };
      
      return enhancedResult;
    } else {
      console.log('❌ Card scan failed:', response.data.error);
      return {
        success: false,
        error: response.data.error || 'Unknown scan error'
      };
    }
    
  } catch (error) {
    console.error('🚫 Card scan error:', error);
    
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network')) {
      return {
        success: false,
        error: 'Network error. Please check your connection and ensure the backend server is running.'
      };
    }
    
    if (error.code === 'ECONNABORTED') {
      return {
        success: false,
        error: 'Request timed out. Please try again with better lighting.'
      };
    }
    
    // For demo purposes, return mock data when backend is not available
    if (__DEV__ && (error.code === 'ECONNREFUSED' || error.response?.status === 404)) {
      console.log('🔧 Backend not available, returning mock data for demo');
      return generateMockScanResult();
    }
    
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Scan failed'
    };
  }
}

/**
 * Search for cards by name
 * @param {string} cardName - Name to search for
 * @returns {Promise<Object>} Search results
 */
export async function searchCards(cardName) {
  try {
    const response = await api.get('/search', {
      params: { name: cardName }
    });
    
    return response.data;
    
  } catch (error) {
    console.error('Search error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
}

/**
 * Get card details by set number
 * @param {string} setNumber - Card set number (e.g., "4/102")
 * @returns {Promise<Object>} Card details
 */
export async function getCardBySetNumber(setNumber) {
  try {
    const response = await api.get(`/cards/${encodeURIComponent(setNumber)}`);
    
    return response.data;
    
  } catch (error) {
    console.error('Card lookup error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
}

/**
 * Generate mock grading data for demo purposes
 * @param {string} cardName - Name of the card
 * @returns {Object} Mock grading scores
 */
function generateMockGrading(cardName = 'Unknown') {
  // Base grading on card name for consistency
  const seed = cardName.toLowerCase().charCodeAt(0) || 80;
  
  const baseGrade = 7 + (seed % 3); // 7-9 base range
  const variation = () => (Math.random() - 0.5) * 1.5; // ±0.75 variation
  
  const grading = {
    centering: Math.min(10, Math.max(5, baseGrade + variation())),
    surface: Math.min(10, Math.max(5, baseGrade + variation())),
    edges: Math.min(10, Math.max(5, baseGrade + variation())),
    corners: Math.min(10, Math.max(5, baseGrade + variation())),
  };
  
  // Round to 1 decimal place
  Object.keys(grading).forEach(key => {
    grading[key] = Math.round(grading[key] * 10) / 10;
  });
  
  return grading;
}

/**
 * Generate complete mock scan result for demo
 * @returns {Object} Mock scan result
 */
function generateMockScanResult() {
  const mockCards = [
    { name: 'Charizard', set: 'Base Set', number: '4/102', rarity: 'Holo Rare', hp: 120 },
    { name: 'Pikachu', set: 'Base Set', number: '58/102', rarity: 'Common', hp: 40 },
    { name: 'Blastoise', set: 'Base Set', number: '2/102', rarity: 'Holo Rare', hp: 100 },
    { name: 'Venusaur', set: 'Base Set', number: '15/102', rarity: 'Holo Rare', hp: 100 },
    { name: 'Alakazam', set: 'Base Set', number: '1/102', rarity: 'Holo Rare', hp: 80 },
  ];
  
  const randomCard = mockCards[Math.floor(Math.random() * mockCards.length)];
  
  return {
    success: true,
    filename: 'demo_scan.jpg',
    cv_confidence: 0.85 + (Math.random() * 0.15), // 85-100% confidence
    identified_info: {
      name: randomCard.name,
      hp: randomCard.hp,
      set_number: randomCard.number
    },
    matches: [
      {
        card: {
          name: randomCard.name,
          set_name: randomCard.set,
          set_number: randomCard.number,
          rarity: randomCard.rarity,
          hp: randomCard.hp,
          card_type: getCardType(randomCard.name),
          release_date: '1999-01-09'
        },
        confidence: 0.95,
        match_reasons: ['exact_set_number_match'],
        pricing: generateMockPricing(randomCard.name, randomCard.rarity)
      }
    ],
    grading: generateMockGrading(randomCard.name)
  };
}

/**
 * Get card type based on name (for mock data)
 */
function getCardType(name) {
  const types = {
    'Charizard': 'Fire',
    'Pikachu': 'Lightning',
    'Blastoise': 'Water',
    'Venusaur': 'Grass',
    'Alakazam': 'Psychic'
  };
  return types[name] || 'Normal';
}

/**
 * Generate mock pricing data
 */
function generateMockPricing(cardName, rarity) {
  let basePrice = 5;
  
  // Adjust base price by rarity
  if (rarity === 'Holo Rare') basePrice = 50;
  else if (rarity === 'Rare') basePrice = 15;
  else if (rarity === 'Uncommon') basePrice = 3;
  
  // Adjust by card popularity
  const multipliers = {
    'Charizard': 8.0,
    'Pikachu': 3.0,
    'Blastoise': 4.0,
    'Venusaur': 4.0,
    'Alakazam': 2.0
  };
  
  basePrice *= (multipliers[cardName] || 1.0);
  
  const grades = ['Ungraded', 'PSA 8', 'PSA 9', 'PSA 10', 'BGS 9.5'];
  const gradeMultipliers = [1.0, 3.0, 6.0, 12.0, 8.0];
  
  const prices_by_grade = {};
  
  grades.forEach((grade, index) => {
    const price = basePrice * gradeMultipliers[index] * (0.8 + Math.random() * 0.4);
    prices_by_grade[grade] = {
      avg_price: Math.round(price * 100) / 100,
      min_price: Math.round(price * 0.7 * 100) / 100,
      max_price: Math.round(price * 1.4 * 100) / 100,
      median_price: Math.round(price * 0.95 * 100) / 100,
      sale_count: Math.floor(Math.random() * 20) + 5
    };
  });
  
  return {
    card_name: `${cardName} (Base Set)`,
    set_number: '4/102',
    prices_by_grade,
    total_listings: Object.values(prices_by_grade).reduce((sum, grade) => sum + grade.sale_count, 0),
    source: 'mock',
    last_updated: new Date().toISOString(),
    note: 'Demo pricing data - Backend not connected'
  };
}