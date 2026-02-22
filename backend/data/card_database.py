import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PokemonCard:
    """Data class representing a Pokemon card"""
    name: str
    set_name: str
    set_number: str
    rarity: str
    hp: Optional[int] = None
    card_type: str = ""
    artist: str = ""
    release_date: Optional[str] = None
    tcg_player_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'set_name': self.set_name,
            'set_number': self.set_number,
            'rarity': self.rarity,
            'hp': self.hp,
            'card_type': self.card_type,
            'artist': self.artist,
            'release_date': self.release_date,
            'tcg_player_id': self.tcg_player_id
        }

@dataclass 
class PricePoint:
    """Data class for price information"""
    marketplace: str  # 'ebay', 'tcgplayer', etc.
    grade: str       # 'ungraded', 'PSA 10', 'BGS 9.5', etc.
    price: float
    sale_date: str
    listing_url: Optional[str] = None

class CardDatabase:
    """Comprehensive SQLite-based card database"""
    
    def __init__(self, db_path: str = "data/pokemon_comprehensive.db"):
        self.db_path = db_path
        self.cards = self._load_database()
        
    def _load_database(self) -> List[PokemonCard]:
        """Load cards from SQLite database"""
        if not os.path.exists(self.db_path):
            print(f"Database not found: {self.db_path}")
            return []
            
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT card_id, name, set_name, number, rarity, hp, card_type, 
                       subtype, artist, release_date, market_price
                FROM cards
                LIMIT 10000
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            cards = []
            for row in rows:
                card_id, name, set_name, number, rarity, hp, card_type, subtype, artist, release_date, market_price = row
                
                cards.append(PokemonCard(
                    name=name,
                    set_name=set_name,
                    set_number=number or "Unknown",
                    rarity=rarity or "Unknown",
                    hp=hp,
                    card_type=card_type or "Unknown",
                    artist=artist or "",
                    release_date=release_date or "",
                    tcg_player_id=card_id
                ))
            
            print(f"Loaded {len(cards):,} cards from comprehensive database")
            return cards
            
        except Exception as e:
            print(f"Error loading database: {e}")
            return []
    
    def save_database(self):
        """Save cards to JSON file"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with open(self.db_path, 'w') as f:
            json.dump([card.to_dict() for card in self.cards], f, indent=2)
    
    def add_card(self, card: PokemonCard):
        """Add a card to the database"""
        self.cards.append(card)
        self.save_database()
    
    def search_by_name(self, name: str, fuzzy: bool = True) -> List[PokemonCard]:
        """Search for cards by name using database query"""
        if not os.path.exists(self.db_path):
            # Fallback to in-memory search
            results = []
            name_lower = name.lower().strip()
            
            for card in self.cards:
                card_name_lower = card.name.lower()
                
                if fuzzy:
                    if name_lower in card_name_lower or card_name_lower in name_lower:
                        results.append(card)
                else:
                    if card_name_lower == name_lower:
                        results.append(card)
            
            return results
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if fuzzy:
                # Fuzzy search with SQL LIKE
                cursor.execute("""
                    SELECT card_id, name, set_name, number, rarity, hp, card_type, 
                           subtype, artist, release_date, market_price
                    FROM cards
                    WHERE name LIKE ? OR name LIKE ?
                    ORDER BY 
                        CASE WHEN name LIKE ? THEN 1 ELSE 2 END,
                        market_price DESC
                    LIMIT 20
                """, (f"%{name}%", f"{name}%", f"{name}%"))
            else:
                # Exact search
                cursor.execute("""
                    SELECT card_id, name, set_name, number, rarity, hp, card_type, 
                           subtype, artist, release_date, market_price
                    FROM cards
                    WHERE LOWER(name) = LOWER(?)
                    ORDER BY market_price DESC
                    LIMIT 10
                """, (name,))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                card_id, card_name, set_name, number, rarity, hp, card_type, subtype, artist, release_date, market_price = row
                
                results.append(PokemonCard(
                    name=card_name,
                    set_name=set_name,
                    set_number=number or "Unknown",
                    rarity=rarity or "Unknown",
                    hp=hp,
                    card_type=card_type or "Unknown",
                    artist=artist or "",
                    release_date=release_date or "",
                    tcg_player_id=card_id
                ))
            
            return results
            
        except Exception as e:
            print(f"Error searching database: {e}")
            return []
    
    def search_by_set_number(self, set_number: str) -> Optional[PokemonCard]:
        """Search for card by set number using database query"""
        if not os.path.exists(self.db_path):
            # Fallback to in-memory search
            for card in self.cards:
                if card.set_number == set_number:
                    return card
            return None
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT card_id, name, set_name, number, rarity, hp, card_type, 
                       subtype, artist, release_date, market_price
                FROM cards
                WHERE number = ?
                LIMIT 1
            """, (set_number,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                card_id, card_name, set_name, number, rarity, hp, card_type, subtype, artist, release_date, market_price = row
                
                return PokemonCard(
                    name=card_name,
                    set_name=set_name,
                    set_number=number or "Unknown",
                    rarity=rarity or "Unknown",
                    hp=hp,
                    card_type=card_type or "Unknown",
                    artist=artist or "",
                    release_date=release_date or "",
                    tcg_player_id=card_id
                )
            
            return None
            
        except Exception as e:
            print(f"Error searching by set number: {e}")
            return None
    
    def get_all_sets(self) -> List[str]:
        """Get list of all unique set names"""
        return list(set(card.set_name for card in self.cards))
    
    def populate_sample_data(self):
        """Add some sample Pokemon cards for testing"""
        sample_cards = [
            PokemonCard(
                name="Charizard",
                set_name="Base Set",
                set_number="4/102",
                rarity="Holo Rare",
                hp=120,
                card_type="Fire",
                release_date="1999-01-09"
            ),
            PokemonCard(
                name="Pikachu",
                set_name="Base Set",
                set_number="58/102",
                rarity="Common",
                hp=40,
                card_type="Lightning",
                release_date="1999-01-09"
            ),
            PokemonCard(
                name="Blastoise",
                set_name="Base Set",
                set_number="2/102",
                rarity="Holo Rare",
                hp=100,
                card_type="Water",
                release_date="1999-01-09"
            ),
            PokemonCard(
                name="Venusaur",
                set_name="Base Set",
                set_number="15/102",
                rarity="Holo Rare",
                hp=100,
                card_type="Grass",
                release_date="1999-01-09"
            ),
            PokemonCard(
                name="Charizard",
                set_name="Evolutions",
                set_number="11/108",
                rarity="Holo Rare",
                hp=150,
                card_type="Fire",
                release_date="2016-11-02"
            )
        ]
        
        for card in sample_cards:
            self.add_card(card)
        
        print(f"Added {len(sample_cards)} sample cards to database")

def main():
    """Test the card database"""
    db = CardDatabase("../data/test_cards.json")
    
    # Populate with sample data
    db.populate_sample_data()
    
    # Test searches
    print("\n=== Search Tests ===")
    
    # Search by name
    charizard_cards = db.search_by_name("Charizard")
    print(f"\nFound {len(charizard_cards)} Charizard cards:")
    for card in charizard_cards:
        print(f"  - {card.name} ({card.set_name}) - {card.set_number}")
    
    # Search by set number
    base_charizard = db.search_by_set_number("4/102")
    if base_charizard:
        print(f"\nFound card 4/102: {base_charizard.name} from {base_charizard.set_name}")
    
    # List all sets
    sets = db.get_all_sets()
    print(f"\nAll sets in database: {sets}")

if __name__ == "__main__":
    main()