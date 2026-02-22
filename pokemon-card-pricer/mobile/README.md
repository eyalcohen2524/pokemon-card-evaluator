# Pokemon Card Price Checker - Mobile App

React Native mobile app built with Expo for scanning and pricing Pokemon cards.

## ✨ Features

- **📱 Instant AI Grading:** Camera-based card scanning with real-time condition assessment
- **💰 Valuation Tracking:** Live market pricing from auction sites
- **🗄️ Digital Vault Management:** Save and organize your card collection
- **📊 Condition Visualization:** Radar charts showing card quality breakdown
- **📈 Market Awareness:** Trending cards and price movements

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Expo CLI (`npm install -g @expo/cli`)
- iOS Simulator (Mac) or Android Emulator
- Pokemon Card Price Checker Backend running on `localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start the development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator  
npm run android

# Run in web browser (limited functionality)
npm run web
```

### Backend Connection

The app expects the backend API to be running on:
- **Development:** `http://localhost:8000`
- **Production:** Configure in `src/services/CardScanService.js`

If the backend is not available, the app will show mock data for demonstration.

## 📱 App Structure

```
src/
├── screens/
│   ├── Scanner/           # Camera scanning & results
│   ├── Vault/            # Collection management
│   ├── Market/           # Trending cards & pricing
│   └── Profile/          # Settings & stats
├── components/
│   ├── RadarChart.js     # Condition visualization
│   └── GradeReveal.js    # Gamified grade reveal
└── services/
    ├── CardScanService.js # Backend API integration
    └── VaultService.js    # Local storage management
```

## 🎯 Key User Stories

### 1. Instant AI Grading
- Use phone camera to scan Pokemon cards
- Get immediate estimates for centering, surface, edges, corners
- No waiting for mail-in grading services

### 2. Valuation Tracking  
- See estimated market value based on recent sales
- Grade-dependent pricing (Ungraded vs PSA 10)
- Make informed buy/sell/hold decisions

### 3. Digital Vault Management
- Save scanned results to personal "Vault"
- Track total collection value
- Digital record of card conditions

### 4. Condition Visualization
- Radar charts show card quality "shape"
- Quickly identify strengths/weaknesses
- Visual breakdown of sub-grades

### 5. Market Awareness
- "Movers & Shakers" trending cards
- Market insights and news
- Price change notifications

## 🎮 Gamified Experience

- **Grade Reveal Animation:** Unboxing-style excitement with glow effects
- **Visual Feedback:** Haptic responses and smooth animations
- **Achievement System:** Collection milestones and rare card discoveries

## 🔧 Configuration

### API Endpoints

Edit `src/services/CardScanService.js`:

```javascript
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000' 
  : 'https://your-production-api.com';
```

### Demo Mode

If backend is unavailable, the app automatically switches to demo mode with:
- Mock card identification
- Sample pricing data  
- Realistic grading scores
- Fake market trends

## 📊 Data Storage

- **Local Storage:** AsyncStorage for vault data
- **Image Caching:** Card photos stored locally
- **Export/Import:** JSON backup functionality
- **Privacy:** No data leaves device without consent

## 🎨 Design System

- **Color Palette:** Dark theme with green accents (#4CAF50)
- **Typography:** Clean, readable fonts with visual hierarchy
- **Cards:** Distinct containers with subtle borders
- **Gradients:** Enhance visual appeal and grade indicators

## 📱 Platform Support

- **iOS:** Full camera and haptic support
- **Android:** Full camera and haptic support  
- **Web:** Limited (no camera access)

## 🚧 Development Notes

### Mock Data

When backend is unavailable, the app generates realistic mock data:
- Consistent card identification based on image hash
- Grade-appropriate pricing variations
- Popular card multipliers (Charizard, Pikachu, etc.)

### Performance

- **Image Processing:** Optimized for mobile performance
- **Caching:** Smart price caching reduces API calls
- **Navigation:** React Navigation with gesture support

## 🔍 Testing

```bash
# Test on physical device via Expo Go app
expo start

# Scan QR code with Expo Go app
# Or use iOS/Android simulators
```

## 📦 Building for Production

```bash
# Build for iOS App Store
expo build:ios

# Build for Google Play Store  
expo build:android

# Or use EAS Build (recommended)
eas build --platform all
```

## 🐛 Known Issues

- Camera permissions required on first launch
- Backend connection needed for real pricing data
- Haptic feedback iOS-only in simulator

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test on iOS and Android
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Made with ❤️ for Pokemon card collectors**