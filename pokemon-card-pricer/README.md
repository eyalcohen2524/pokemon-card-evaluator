# Pokemon Card Price Checker

An app that identifies Pokemon cards through camera and provides real-time pricing from auction sites.

## Project Structure

```
pokemon-card-pricer/
├── backend/
│   ├── api/           # FastAPI endpoints  
│   ├── cv/            # Computer vision pipeline
│   ├── data/          # Card database & scraping
│   └── models/        # ML models
├── mobile/            # React Native app
├── data/              # Sample images & datasets
└── tests/             # Test files
```

## Development Phases

### Phase 1: Core Identification ✅ (Current)
- [x] Basic card detection from images
- [x] OCR text extraction
- [x] Simple card database lookup
- [ ] Grade assessment prototype

### Phase 2: Pricing Integration
- [ ] Web scraping for auction sites
- [ ] Price aggregation and caching
- [ ] Real-time API endpoints

### Phase 3: Mobile App
- [ ] React Native camera interface
- [ ] Real-time card identification
- [ ] Results display

### Phase 4: Advanced Features
- [ ] ML-based grade assessment
- [ ] Portfolio tracking
- [ ] Price alerts

## Getting Started

```bash
cd backend
pip install -r requirements.txt
python -m cv.card_identifier test_image.jpg
```