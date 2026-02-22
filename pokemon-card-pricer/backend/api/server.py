#!/usr/bin/env python3
"""
FastAPI server for Pokemon Card Price Checker
Provides HTTP endpoints for card identification and pricing
"""

import os
import sys
import tempfile
from typing import Dict, List, Optional
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import PokemonCardPricer
from data.card_database import PokemonCard

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon Card Price Checker API",
    description="Identify Pokemon cards from images and get pricing information",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the card pricer
pricer = PokemonCardPricer()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Pokemon Card Price Checker API",
        "version": "1.0.0",
        "endpoints": {
            "identify": "POST /identify - Upload image to identify card",
            "search": "GET /search?name={name} - Search cards by name",
            "health": "GET /health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_cards": len(pricer.database.cards),
        "available_sets": pricer.database.get_all_sets()
    }

@app.post("/identify")
async def identify_card(file: UploadFile = File(...)):
    """
    Identify a Pokemon card from an uploaded image
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Run identification
        result = pricer.identify_and_price_card(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if not result['success']:
            raise HTTPException(status_code=422, detail=result['error'])
        
        # Add pricing information for matches
        enhanced_matches = []
        for match in result['matches']:
            card = PokemonCard(**match['card'])
            pricing = pricer.get_real_pricing(card)
            
            enhanced_match = {
                **match,
                'pricing': pricing
            }
            enhanced_matches.append(enhanced_match)
        
        return {
            "success": True,
            "filename": file.filename,
            "cv_confidence": result['cv_result']['confidence'],
            "identified_info": {
                "name": result['cv_result']['name'],
                "hp": result['cv_result']['hp'],
                "set_number": result['cv_result']['set_number']
            },
            "matches": enhanced_matches,
            "match_count": len(enhanced_matches)
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/search")
async def search_cards(name: str):
    """
    Search for cards by name
    """
    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
    
    matches = pricer.database.search_by_name(name.strip())
    
    if not matches:
        return {
            "success": True,
            "query": name,
            "matches": [],
            "count": 0
        }
    
    # Add pricing for each match
    enhanced_matches = []
    for card in matches:
        pricing = pricer.get_real_pricing(card)
        enhanced_matches.append({
            "card": card.to_dict(),
            "pricing": pricing
        })
    
    return {
        "success": True,
        "query": name,
        "matches": enhanced_matches,
        "count": len(enhanced_matches)
    }

@app.get("/sets")
async def list_sets():
    """Get list of all card sets in database"""
    sets = pricer.database.get_all_sets()
    return {
        "sets": sorted(sets),
        "count": len(sets)
    }

@app.get("/cards/{set_number}")
async def get_card_by_set_number(set_number: str):
    """Get specific card by set number"""
    card = pricer.database.search_by_set_number(set_number)
    
    if not card:
        raise HTTPException(status_code=404, detail=f"Card not found: {set_number}")
    
    pricing = pricer.get_real_pricing(card)
    
    return {
        "card": card.to_dict(),
        "pricing": pricing
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors gracefully"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pokemon Card Price Checker API Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', default=8000, type=int, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    print("🚀 Starting Pokemon Card Price Checker API")
    print(f"📡 Server: http://{args.host}:{args.port}")
    print(f"📊 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 Database: {len(pricer.database.cards)} cards loaded")
    
    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()