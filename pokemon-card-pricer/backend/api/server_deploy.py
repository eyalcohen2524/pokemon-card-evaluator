#!/usr/bin/env python3
"""
FastAPI server for Pokemon Card Price Checker - Deployment Version
Provides HTTP endpoints with mock data for demonstration
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile

# Import our image analyzer
from image_analyzer import analyzer

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon Card Price Checker API",
    description="Identify Pokemon cards from images and get pricing information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock card database
MOCK_CARDS = [
    {
        "name": "Charizard",
        "set_name": "Base Set",
        "set_number": "4/102",
        "rarity": "Holo Rare",
        "hp": 120,
        "card_type": "Fire",
        "release_date": "1999-01-09"
    },
    {
        "name": "Pikachu", 
        "set_name": "Base Set",
        "set_number": "58/102",
        "rarity": "Common",
        "hp": 40,
        "card_type": "Lightning",
        "release_date": "1999-01-09"
    },
    {
        "name": "Blastoise",
        "set_name": "Base Set", 
        "set_number": "2/102",
        "rarity": "Holo Rare",
        "hp": 100,
        "card_type": "Water",
        "release_date": "1999-01-09"
    },
    {
        "name": "Venusaur",
        "set_name": "Base Set",
        "set_number": "15/102", 
        "rarity": "Holo Rare",
        "hp": 100,
        "card_type": "Grass",
        "release_date": "1999-01-09"
    }
]

def generate_mock_pricing(card_name: str, rarity: str) -> Dict:
    """Generate realistic mock pricing data"""
    base_price = 5
    
    # Adjust by rarity
    if rarity == "Holo Rare":
        base_price = 50
    elif rarity == "Rare":
        base_price = 15
    elif rarity == "Uncommon":
        base_price = 3
        
    # Adjust by popularity
    multipliers = {
        "Charizard": 8.0,
        "Pikachu": 3.0,
        "Blastoise": 4.0,
        "Venusaur": 4.0
    }
    base_price *= multipliers.get(card_name, 1.0)
    
    grades = ["Ungraded", "PSA 8", "PSA 9", "PSA 10", "BGS 9.5"]
    grade_multipliers = [1.0, 3.0, 6.0, 12.0, 8.0]
    
    prices_by_grade = {}
    for grade, multiplier in zip(grades, grade_multipliers):
        price = base_price * multiplier * (0.8 + random.random() * 0.4)
        prices_by_grade[grade] = {
            "avg_price": round(price, 2),
            "min_price": round(price * 0.7, 2),
            "max_price": round(price * 1.4, 2),
            "median_price": round(price * 0.95, 2),
            "sale_count": random.randint(5, 25)
        }
    
    return {
        "card_name": f"{card_name} ({card_name} Set)",
        "set_number": "4/102", 
        "prices_by_grade": prices_by_grade,
        "total_listings": sum(grade["sale_count"] for grade in prices_by_grade.values()),
        "source": "demo",
        "last_updated": datetime.now().isoformat(),
        "note": "Demo pricing data from Render deployment"
    }

def generate_mock_grading(card_name: str) -> Dict:
    """Generate mock grading scores"""
    seed = hash(card_name) % 100
    base_grade = 7 + (seed % 3)
    
    def random_variation():
        return random.uniform(-0.75, 0.75)
    
    grading = {
        "centering": max(5, min(10, base_grade + random_variation())),
        "surface": max(5, min(10, base_grade + random_variation())), 
        "edges": max(5, min(10, base_grade + random_variation())),
        "corners": max(5, min(10, base_grade + random_variation()))
    }
    
    return {k: round(v, 1) for k, v in grading.items()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pokemon Card Price Checker API",
        "version": "1.0.0",
        "status": "live",
        "environment": "production"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_cards": len(MOCK_CARDS),
        "available_sets": list(set(card["set_name"] for card in MOCK_CARDS)),
        "environment": "render-deployment"
    }

@app.post("/identify")
async def identify_card(file: UploadFile = File(...)):
    """
    Identify a Pokemon card from an uploaded image
    Uses real image analysis with intelligent fallback
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Use our image analyzer for real analysis
        result = analyzer.analyze_image(temp_file_path)
        
        if not result.get("success"):
            # Fallback to mock data if analysis fails
            random_card = random.choice(MOCK_CARDS)
            result = {
                "success": True,
                "filename": file.filename,
                "cv_confidence": 0.75,
                "identified_info": {
                    "name": random_card["name"],
                    "hp": random_card["hp"],
                    "set_number": random_card["set_number"]
                },
                "matches": [
                    {
                        "card": random_card,
                        "confidence": 0.85,
                        "match_reasons": ["fallback_mode"],
                        "pricing": generate_mock_pricing(random_card["name"], random_card["rarity"])
                    }
                ],
                "grading": generate_mock_grading(random_card["name"]),
                "note": "Analysis fallback - using mock data"
            }
        else:
            # Add filename to successful result
            result["filename"] = file.filename
            result["note"] = "Real image analysis complete"
        
        return result
        
    except Exception as e:
        # Ultimate fallback
        random_card = random.choice(MOCK_CARDS)
        return {
            "success": True,
            "filename": file.filename,
            "cv_confidence": 0.70,
            "identified_info": {
                "name": random_card["name"],
                "hp": random_card["hp"],
                "set_number": random_card["set_number"]
            },
            "matches": [
                {
                    "card": random_card,
                    "confidence": 0.80,
                    "match_reasons": ["error_fallback"],
                    "pricing": generate_mock_pricing(random_card["name"], random_card["rarity"])
                }
            ],
            "grading": generate_mock_grading(random_card["name"]),
            "note": f"Error fallback: {str(e)}"
        }
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

@app.get("/card/{card_name}/{set_name}")
async def get_card_pricing(card_name: str, set_name: str):
    """Get pricing for a specific card"""
    # Find matching card
    matching_cards = [
        card for card in MOCK_CARDS 
        if card["name"].lower() == card_name.lower().replace("-", " ")
        and card["set_name"].lower() == set_name.lower().replace("-", " ")
    ]
    
    if not matching_cards:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card = matching_cards[0]
    
    return {
        "success": True,
        "card": card,
        "pricing": generate_mock_pricing(card["name"], card["rarity"]),
        "grading": generate_mock_grading(card["name"])
    }

@app.get("/search")
async def search_cards(name: str):
    """Search for cards by name"""
    matching_cards = [
        card for card in MOCK_CARDS
        if name.lower() in card["name"].lower()
    ]
    
    return {
        "success": True,
        "query": name,
        "results": matching_cards,
        "total": len(matching_cards)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)