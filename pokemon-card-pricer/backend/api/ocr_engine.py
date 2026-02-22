#!/usr/bin/env python3
"""
OCR Engine for Pokemon Card Text Extraction
Uses OCR.space API (free tier: 25,000 calls/month)
"""

import os
import re
import base64
import requests
from typing import Dict, List, Optional, Tuple
from PIL import Image
import io

# OCR.space API configuration
# Free API key - limited but works for demos
# For production, get your own key at https://ocr.space/ocrapi
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "K85119aborud288")  # Free demo key
OCR_SPACE_URL = "https://api.ocr.space/parse/image"


class PokemonCardOCR:
    """
    Extracts text from Pokemon card images using cloud OCR
    Parses extracted text to identify card attributes
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OCR_SPACE_API_KEY
        
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Send image to OCR.space API and extract text
        Returns raw OCR results
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Resize if too large (OCR.space has file size limits)
            image_data = self._optimize_image(image_data)
            
            # Encode to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Call OCR.space API
            payload = {
                'apikey': self.api_key,
                'base64Image': f'data:image/jpeg;base64,{base64_image}',
                'language': 'eng',
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'OCREngine': 2,  # Engine 2 is better for dense text
            }
            
            response = requests.post(
                OCR_SPACE_URL,
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('IsErroredOnProcessing'):
                    return {
                        'success': False,
                        'error': result.get('ErrorMessage', 'OCR processing failed'),
                        'raw_text': ''
                    }
                
                # Extract parsed text
                parsed_results = result.get('ParsedResults', [])
                if parsed_results:
                    raw_text = parsed_results[0].get('ParsedText', '')
                    return {
                        'success': True,
                        'raw_text': raw_text,
                        'confidence': parsed_results[0].get('TextOverlay', {}).get('MeanConfidence', 0)
                    }
                
                return {'success': False, 'error': 'No text found', 'raw_text': ''}
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'raw_text': ''
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'OCR failed: {str(e)}',
                'raw_text': ''
            }
    
    def _optimize_image(self, image_data: bytes, max_size: int = 1024*1024) -> bytes:
        """Resize image if too large for OCR API"""
        if len(image_data) <= max_size:
            return image_data
        
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Reduce size while maintaining aspect ratio
            while True:
                # Reduce dimensions by 20%
                new_width = int(img.width * 0.8)
                new_height = int(img.height * 0.8)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to buffer
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_data = buffer.getvalue()
                
                if len(image_data) <= max_size or img.width < 500:
                    break
            
            return image_data
        except:
            return image_data
    
    def parse_pokemon_card_text(self, raw_text: str) -> Dict:
        """
        Parse OCR text to extract Pokemon card attributes
        Returns structured card information
        """
        result = {
            'name': None,
            'hp': None,
            'set_number': None,
            'card_type': None,
            'attacks': [],
            'stage': None,
            'raw_text': raw_text
        }
        
        # Normalize text
        text = raw_text.upper()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract HP (usually in format "120 HP" or "HP 120")
        hp_patterns = [
            r'(\d+)\s*HP',
            r'HP\s*(\d+)',
            r'(\d{2,3})\s*H\s*P'  # Handle spacing issues
        ]
        for pattern in hp_patterns:
            match = re.search(pattern, text)
            if match:
                result['hp'] = int(match.group(1))
                break
        
        # Extract set number (usually in format "4/102" or similar)
        set_patterns = [
            r'(\d{1,3})\s*/\s*(\d{1,3})',
            r'(\d{1,3})\s*OF\s*(\d{1,3})',
        ]
        for pattern in set_patterns:
            match = re.search(pattern, text)
            if match:
                result['set_number'] = f"{match.group(1)}/{match.group(2)}"
                break
        
        # Extract Pokemon name (usually first significant line)
        # Common Pokemon names to look for
        pokemon_names = [
            'CHARIZARD', 'BLASTOISE', 'VENUSAUR', 'PIKACHU', 'MEWTWO',
            'ALAKAZAM', 'MACHAMP', 'GYARADOS', 'DRAGONITE', 'GENGAR',
            'RAICHU', 'NINETALES', 'ARCANINE', 'POLIWRATH', 'GOLEM',
            'RAPIDASH', 'SLOWBRO', 'MAGNETON', 'CLOYSTER', 'ELECTRODE',
            'CHANSEY', 'HITMONCHAN', 'ZAPDOS', 'ARTICUNO', 'MOLTRES',
            'NIDOKING', 'NIDOQUEEN', 'CLEFAIRY', 'WIGGLYTUFF', 'DUGTRIO',
            'ALAKAZAM', 'VICTREEBEL', 'TENTACRUEL', 'GRAVELER', 'PONYTA',
            'MAGNEMITE', 'DEWGONG', 'MUK', 'GASTLY', 'HAUNTER',
            'ONIX', 'HYPNO', 'KINGLER', 'HITMONLEE', 'WEEZING',
            'TANGELA', 'KANGASKHAN', 'GOLDEEN', 'SEAKING', 'STARYU',
            'STARMIE', 'SCYTHER', 'JYNX', 'ELECTABUZZ', 'MAGMAR',
            'PINSIR', 'TAUROS', 'LAPRAS', 'DITTO', 'EEVEE',
            'VAPOREON', 'JOLTEON', 'FLAREON', 'PORYGON', 'OMANYTE',
            'OMASTAR', 'KABUTO', 'KABUTOPS', 'AERODACTYL', 'SNORLAX',
            'MEW', 'BULBASAUR', 'IVYSAUR', 'CHARMANDER', 'CHARMELEON',
            'SQUIRTLE', 'WARTORTLE', 'CATERPIE', 'METAPOD', 'BEEDRILL',
            'PIDGEY', 'PIDGEOTTO', 'PIDGEOT', 'RATTATA', 'RATICATE',
            'SPEAROW', 'FEAROW', 'EKANS', 'ARBOK', 'SANDSHREW',
            'SANDSLASH', 'NIDORAN', 'NIDORINA', 'NIDORINO', 'CLEFABLE',
            'VULPIX', 'JIGGLYPUFF', 'ZUBAT', 'GOLBAT', 'ODDISH',
            'GLOOM', 'VILEPLUME', 'PARAS', 'PARASECT', 'VENONAT',
            'VENOMOTH', 'DIGLETT', 'MEOWTH', 'PERSIAN', 'PSYDUCK',
            'GOLDUCK', 'MANKEY', 'PRIMEAPE', 'GROWLITHE', 'POLIWAG',
            'POLIWHIRL', 'ABRA', 'KADABRA', 'MACHOP', 'MACHOKE',
            'BELLSPROUT', 'WEEPINBELL', 'GEODUDE', 'SLOWPOKE', 'MAGIKARP',
            'SEEL', 'GRIMER', 'SHELLDER', 'DROWZEE', 'KRABBY',
            'VOLTORB', 'EXEGGCUTE', 'EXEGGUTOR', 'CUBONE', 'MAROWAK',
            'LICKITUNG', 'RHYHORN', 'RHYDON', 'HORSEA', 'SEADRA',
            'ELECTABUZZ', 'DRATINI', 'DRAGONAIR', 'KAKUNA', 'WEEDLE',
            'DODUO', 'KOFFING', 'FARFETCH', "FARFETCH'D"
        ]
        
        # Look for Pokemon name in text
        for pokemon in pokemon_names:
            if pokemon in text:
                result['name'] = pokemon.capitalize()
                break
        
        # If no name found, try to get first line that looks like a name
        if not result['name'] and lines:
            for line in lines[:3]:  # Check first 3 lines
                # Clean the line
                clean_line = re.sub(r'[^A-Z\s]', '', line).strip()
                if clean_line and len(clean_line) > 2:
                    # Check if it's a single word (likely Pokemon name)
                    words = clean_line.split()
                    if 1 <= len(words) <= 2:
                        result['name'] = clean_line.title()
                        break
        
        # Detect stage
        if 'BASIC' in text:
            result['stage'] = 'Basic'
        elif 'STAGE 2' in text:
            result['stage'] = 'Stage 2'
        elif 'STAGE 1' in text or 'STAGE1' in text:
            result['stage'] = 'Stage 1'
        
        # Detect card type from energy symbols or type text
        type_patterns = {
            'Fire': ['FIRE', '🔥', 'FLAME'],
            'Water': ['WATER', '💧', 'HYDRO'],
            'Grass': ['GRASS', '🌿', 'LEAF'],
            'Lightning': ['LIGHTNING', '⚡', 'ELECTRIC', 'THUNDER'],
            'Psychic': ['PSYCHIC', '🔮', 'PSY'],
            'Fighting': ['FIGHTING', '👊', 'FIGHT'],
            'Colorless': ['COLORLESS', 'NORMAL'],
        }
        
        for card_type, patterns in type_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    result['card_type'] = card_type
                    break
            if result['card_type']:
                break
        
        return result
    
    def identify_card(self, image_path: str) -> Dict:
        """
        Full pipeline: OCR → Parse → Match
        Returns complete card identification result
        """
        # Step 1: Extract text with OCR
        ocr_result = self.extract_text_from_image(image_path)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'OCR failed'),
                'ocr_result': ocr_result
            }
        
        # Step 2: Parse the text
        parsed = self.parse_pokemon_card_text(ocr_result['raw_text'])
        
        return {
            'success': True,
            'extracted_name': parsed['name'],
            'extracted_hp': parsed['hp'],
            'extracted_set_number': parsed['set_number'],
            'extracted_stage': parsed['stage'],
            'extracted_type': parsed['card_type'],
            'raw_text': ocr_result['raw_text'],
            'ocr_confidence': ocr_result.get('confidence', 0)
        }


# Global OCR instance
ocr_engine = PokemonCardOCR()