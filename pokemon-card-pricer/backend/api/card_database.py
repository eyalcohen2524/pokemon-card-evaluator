#!/usr/bin/env python3
"""
Pokemon Card Database - Base Set (102 cards)
Complete database for card identification
"""

from typing import Dict, List, Optional
from difflib import SequenceMatcher
import re

# Complete Base Set Database (102 cards)
BASE_SET_CARDS = [
    # Holo Rares (16 cards)
    {"name": "Alakazam", "set_number": "1/102", "rarity": "Holo Rare", "hp": 80, "card_type": "Psychic", "stage": "Stage 2"},
    {"name": "Blastoise", "set_number": "2/102", "rarity": "Holo Rare", "hp": 100, "card_type": "Water", "stage": "Stage 2"},
    {"name": "Chansey", "set_number": "3/102", "rarity": "Holo Rare", "hp": 120, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Charizard", "set_number": "4/102", "rarity": "Holo Rare", "hp": 120, "card_type": "Fire", "stage": "Stage 2"},
    {"name": "Clefairy", "set_number": "5/102", "rarity": "Holo Rare", "hp": 40, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Gyarados", "set_number": "6/102", "rarity": "Holo Rare", "hp": 100, "card_type": "Water", "stage": "Stage 1"},
    {"name": "Hitmonchan", "set_number": "7/102", "rarity": "Holo Rare", "hp": 70, "card_type": "Fighting", "stage": "Basic"},
    {"name": "Machamp", "set_number": "8/102", "rarity": "Holo Rare", "hp": 100, "card_type": "Fighting", "stage": "Stage 2"},
    {"name": "Magneton", "set_number": "9/102", "rarity": "Holo Rare", "hp": 60, "card_type": "Lightning", "stage": "Stage 1"},
    {"name": "Mewtwo", "set_number": "10/102", "rarity": "Holo Rare", "hp": 60, "card_type": "Psychic", "stage": "Basic"},
    {"name": "Nidoking", "set_number": "11/102", "rarity": "Holo Rare", "hp": 90, "card_type": "Grass", "stage": "Stage 2"},
    {"name": "Ninetales", "set_number": "12/102", "rarity": "Holo Rare", "hp": 80, "card_type": "Fire", "stage": "Stage 1"},
    {"name": "Poliwrath", "set_number": "13/102", "rarity": "Holo Rare", "hp": 90, "card_type": "Water", "stage": "Stage 2"},
    {"name": "Raichu", "set_number": "14/102", "rarity": "Holo Rare", "hp": 80, "card_type": "Lightning", "stage": "Stage 1"},
    {"name": "Venusaur", "set_number": "15/102", "rarity": "Holo Rare", "hp": 100, "card_type": "Grass", "stage": "Stage 2"},
    {"name": "Zapdos", "set_number": "16/102", "rarity": "Holo Rare", "hp": 90, "card_type": "Lightning", "stage": "Basic"},
    
    # Rares (16 cards)
    {"name": "Beedrill", "set_number": "17/102", "rarity": "Rare", "hp": 80, "card_type": "Grass", "stage": "Stage 2"},
    {"name": "Dragonair", "set_number": "18/102", "rarity": "Rare", "hp": 60, "card_type": "Colorless", "stage": "Stage 1"},
    {"name": "Dugtrio", "set_number": "19/102", "rarity": "Rare", "hp": 70, "card_type": "Fighting", "stage": "Stage 1"},
    {"name": "Electabuzz", "set_number": "20/102", "rarity": "Rare", "hp": 70, "card_type": "Lightning", "stage": "Basic"},
    {"name": "Electrode", "set_number": "21/102", "rarity": "Rare", "hp": 80, "card_type": "Lightning", "stage": "Stage 1"},
    {"name": "Pidgeotto", "set_number": "22/102", "rarity": "Rare", "hp": 60, "card_type": "Colorless", "stage": "Stage 1"},
    {"name": "Arcanine", "set_number": "23/102", "rarity": "Uncommon", "hp": 100, "card_type": "Fire", "stage": "Stage 1"},
    {"name": "Charmeleon", "set_number": "24/102", "rarity": "Uncommon", "hp": 80, "card_type": "Fire", "stage": "Stage 1"},
    {"name": "Dewgong", "set_number": "25/102", "rarity": "Uncommon", "hp": 80, "card_type": "Water", "stage": "Stage 1"},
    {"name": "Dratini", "set_number": "26/102", "rarity": "Uncommon", "hp": 40, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Farfetch'd", "set_number": "27/102", "rarity": "Uncommon", "hp": 50, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Growlithe", "set_number": "28/102", "rarity": "Uncommon", "hp": 60, "card_type": "Fire", "stage": "Basic"},
    {"name": "Haunter", "set_number": "29/102", "rarity": "Uncommon", "hp": 60, "card_type": "Psychic", "stage": "Stage 1"},
    {"name": "Ivysaur", "set_number": "30/102", "rarity": "Uncommon", "hp": 60, "card_type": "Grass", "stage": "Stage 1"},
    {"name": "Jynx", "set_number": "31/102", "rarity": "Uncommon", "hp": 70, "card_type": "Psychic", "stage": "Basic"},
    {"name": "Kadabra", "set_number": "32/102", "rarity": "Uncommon", "hp": 60, "card_type": "Psychic", "stage": "Stage 1"},
    {"name": "Kakuna", "set_number": "33/102", "rarity": "Uncommon", "hp": 80, "card_type": "Grass", "stage": "Stage 1"},
    {"name": "Machoke", "set_number": "34/102", "rarity": "Uncommon", "hp": 80, "card_type": "Fighting", "stage": "Stage 1"},
    {"name": "Magikarp", "set_number": "35/102", "rarity": "Uncommon", "hp": 30, "card_type": "Water", "stage": "Basic"},
    {"name": "Magmar", "set_number": "36/102", "rarity": "Uncommon", "hp": 50, "card_type": "Fire", "stage": "Basic"},
    {"name": "Nidorino", "set_number": "37/102", "rarity": "Uncommon", "hp": 60, "card_type": "Grass", "stage": "Stage 1"},
    {"name": "Poliwhirl", "set_number": "38/102", "rarity": "Uncommon", "hp": 60, "card_type": "Water", "stage": "Stage 1"},
    {"name": "Porygon", "set_number": "39/102", "rarity": "Uncommon", "hp": 30, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Raticate", "set_number": "40/102", "rarity": "Uncommon", "hp": 60, "card_type": "Colorless", "stage": "Stage 1"},
    {"name": "Seel", "set_number": "41/102", "rarity": "Uncommon", "hp": 60, "card_type": "Water", "stage": "Basic"},
    {"name": "Wartortle", "set_number": "42/102", "rarity": "Uncommon", "hp": 70, "card_type": "Water", "stage": "Stage 1"},
    
    # Commons (32 cards)
    {"name": "Abra", "set_number": "43/102", "rarity": "Common", "hp": 30, "card_type": "Psychic", "stage": "Basic"},
    {"name": "Bulbasaur", "set_number": "44/102", "rarity": "Common", "hp": 40, "card_type": "Grass", "stage": "Basic"},
    {"name": "Caterpie", "set_number": "45/102", "rarity": "Common", "hp": 40, "card_type": "Grass", "stage": "Basic"},
    {"name": "Charmander", "set_number": "46/102", "rarity": "Common", "hp": 50, "card_type": "Fire", "stage": "Basic"},
    {"name": "Diglett", "set_number": "47/102", "rarity": "Common", "hp": 30, "card_type": "Fighting", "stage": "Basic"},
    {"name": "Doduo", "set_number": "48/102", "rarity": "Common", "hp": 50, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Drowzee", "set_number": "49/102", "rarity": "Common", "hp": 50, "card_type": "Psychic", "stage": "Basic"},
    {"name": "Gastly", "set_number": "50/102", "rarity": "Common", "hp": 30, "card_type": "Psychic", "stage": "Basic"},
    {"name": "Koffing", "set_number": "51/102", "rarity": "Common", "hp": 50, "card_type": "Grass", "stage": "Basic"},
    {"name": "Machop", "set_number": "52/102", "rarity": "Common", "hp": 50, "card_type": "Fighting", "stage": "Basic"},
    {"name": "Magnemite", "set_number": "53/102", "rarity": "Common", "hp": 40, "card_type": "Lightning", "stage": "Basic"},
    {"name": "Metapod", "set_number": "54/102", "rarity": "Common", "hp": 70, "card_type": "Grass", "stage": "Stage 1"},
    {"name": "Nidoran♂", "set_number": "55/102", "rarity": "Common", "hp": 40, "card_type": "Grass", "stage": "Basic"},
    {"name": "Onix", "set_number": "56/102", "rarity": "Common", "hp": 90, "card_type": "Fighting", "stage": "Basic"},
    {"name": "Pidgey", "set_number": "57/102", "rarity": "Common", "hp": 40, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Pikachu", "set_number": "58/102", "rarity": "Common", "hp": 40, "card_type": "Lightning", "stage": "Basic"},
    {"name": "Poliwag", "set_number": "59/102", "rarity": "Common", "hp": 40, "card_type": "Water", "stage": "Basic"},
    {"name": "Ponyta", "set_number": "60/102", "rarity": "Common", "hp": 40, "card_type": "Fire", "stage": "Basic"},
    {"name": "Rattata", "set_number": "61/102", "rarity": "Common", "hp": 30, "card_type": "Colorless", "stage": "Basic"},
    {"name": "Sandshrew", "set_number": "62/102", "rarity": "Common", "hp": 40, "card_type": "Fighting", "stage": "Basic"},
    {"name": "Squirtle", "set_number": "63/102", "rarity": "Common", "hp": 40, "card_type": "Water", "stage": "Basic"},
    {"name": "Starmie", "set_number": "64/102", "rarity": "Common", "hp": 60, "card_type": "Water", "stage": "Stage 1"},
    {"name": "Staryu", "set_number": "65/102", "rarity": "Common", "hp": 40, "card_type": "Water", "stage": "Basic"},
    {"name": "Tangela", "set_number": "66/102", "rarity": "Common", "hp": 50, "card_type": "Grass", "stage": "Basic"},
    {"name": "Voltorb", "set_number": "67/102", "rarity": "Common", "hp": 40, "card_type": "Lightning", "stage": "Basic"},
    {"name": "Vulpix", "set_number": "68/102", "rarity": "Common", "hp": 50, "card_type": "Fire", "stage": "Basic"},
    {"name": "Weedle", "set_number": "69/102", "rarity": "Common", "hp": 40, "card_type": "Grass", "stage": "Basic"},
    
    # Trainer Cards
    {"name": "Clefairy Doll", "set_number": "70/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Computer Search", "set_number": "71/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Devolution Spray", "set_number": "72/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Impostor Professor Oak", "set_number": "73/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Item Finder", "set_number": "74/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Lass", "set_number": "75/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Pokemon Breeder", "set_number": "76/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Pokemon Trader", "set_number": "77/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Scoop Up", "set_number": "78/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Super Energy Removal", "set_number": "79/102", "rarity": "Rare", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Defender", "set_number": "80/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Energy Retrieval", "set_number": "81/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Full Heal", "set_number": "82/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Maintenance", "set_number": "83/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "PlusPower", "set_number": "84/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Pokemon Center", "set_number": "85/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Pokemon Flute", "set_number": "86/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Pokedex", "set_number": "87/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Professor Oak", "set_number": "88/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Revive", "set_number": "89/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Super Potion", "set_number": "90/102", "rarity": "Uncommon", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Bill", "set_number": "91/102", "rarity": "Common", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Energy Removal", "set_number": "92/102", "rarity": "Common", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Gust of Wind", "set_number": "93/102", "rarity": "Common", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Potion", "set_number": "94/102", "rarity": "Common", "hp": None, "card_type": "Trainer", "stage": None},
    {"name": "Switch", "set_number": "95/102", "rarity": "Common", "hp": None, "card_type": "Trainer", "stage": None},
    
    # Energy Cards
    {"name": "Double Colorless Energy", "set_number": "96/102", "rarity": "Uncommon", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Fighting Energy", "set_number": "97/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Fire Energy", "set_number": "98/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Grass Energy", "set_number": "99/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Lightning Energy", "set_number": "100/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Psychic Energy", "set_number": "101/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
    {"name": "Water Energy", "set_number": "102/102", "rarity": "Common", "hp": None, "card_type": "Energy", "stage": None},
]

# Add set name to all cards
for card in BASE_SET_CARDS:
    card["set_name"] = "Base Set"
    card["release_date"] = "1999-01-09"


class CardMatcher:
    """
    Matches OCR-extracted text to cards in the database
    Uses fuzzy string matching for robustness
    """
    
    def __init__(self):
        self.cards = BASE_SET_CARDS
        self._build_search_index()
    
    def _build_search_index(self):
        """Build search indices for fast matching"""
        self.name_index = {}
        self.hp_index = {}
        self.set_number_index = {}
        
        for card in self.cards:
            # Name index (lowercase for matching)
            name_lower = card["name"].lower()
            self.name_index[name_lower] = card
            
            # Also index without special characters
            clean_name = re.sub(r'[^a-z0-9]', '', name_lower)
            self.name_index[clean_name] = card
            
            # HP index
            if card["hp"]:
                hp_key = str(card["hp"])
                if hp_key not in self.hp_index:
                    self.hp_index[hp_key] = []
                self.hp_index[hp_key].append(card)
            
            # Set number index
            self.set_number_index[card["set_number"]] = card
    
    def match_by_name(self, extracted_name: str, threshold: float = 0.6) -> Optional[Dict]:
        """Match card by name with fuzzy matching"""
        if not extracted_name:
            return None
        
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', extracted_name).lower().strip()
        
        # Exact match first
        if clean_name in self.name_index:
            return self.name_index[clean_name]
        
        # Fuzzy match
        best_match = None
        best_score = 0
        
        for card in self.cards:
            card_name_clean = re.sub(r'[^a-zA-Z0-9\s]', '', card["name"]).lower()
            
            # Check if extracted name contains card name or vice versa
            if card_name_clean in clean_name or clean_name in card_name_clean:
                score = 0.9
            else:
                score = SequenceMatcher(None, clean_name, card_name_clean).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = card
        
        return best_match
    
    def match_by_hp(self, hp: int) -> List[Dict]:
        """Get all cards with matching HP"""
        return self.hp_index.get(str(hp), [])
    
    def match_by_set_number(self, set_number: str) -> Optional[Dict]:
        """Match card by exact set number"""
        # Normalize set number format
        normalized = set_number.strip().replace(" ", "")
        return self.set_number_index.get(normalized)
    
    def match_card(self, name: str = None, hp: int = None, set_number: str = None) -> Dict:
        """
        Match a card using all available information
        Returns best match with confidence score
        """
        candidates = []
        
        # Try set number first (most reliable)
        if set_number:
            match = self.match_by_set_number(set_number)
            if match:
                return {"card": match, "confidence": 0.98, "match_type": "set_number"}
        
        # Try name matching
        if name:
            match = self.match_by_name(name)
            if match:
                candidates.append({"card": match, "confidence": 0.85, "match_type": "name"})
        
        # Try HP cross-reference
        if hp and name:
            hp_matches = self.match_by_hp(hp)
            for hp_match in hp_matches:
                # Check if name also matches
                name_score = SequenceMatcher(
                    None, 
                    name.lower(), 
                    hp_match["name"].lower()
                ).ratio()
                if name_score > 0.5:
                    candidates.append({
                        "card": hp_match, 
                        "confidence": 0.7 + (name_score * 0.2),
                        "match_type": "hp_name_combo"
                    })
        
        # Return best candidate
        if candidates:
            candidates.sort(key=lambda x: x["confidence"], reverse=True)
            return candidates[0]
        
        return {"card": None, "confidence": 0, "match_type": "no_match"}
    
    def search(self, query: str) -> List[Dict]:
        """Search cards by name (partial match)"""
        query_lower = query.lower()
        results = []
        
        for card in self.cards:
            if query_lower in card["name"].lower():
                results.append(card)
        
        return results
    
    def get_all_cards(self) -> List[Dict]:
        """Return all cards in database"""
        return self.cards
    
    def get_card_count(self) -> int:
        """Return total number of cards"""
        return len(self.cards)


# Global matcher instance
card_matcher = CardMatcher()