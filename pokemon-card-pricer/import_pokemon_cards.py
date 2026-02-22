#!/usr/bin/env python3
"""
Import Pokemon cards from Pokemon TCG API into our database
Usage: python import_cards.py [--limit 1000] [--set-name "Base Set"]
"""

import requests
import json
import time
import argparse
from datetime import datetime
import sqlite3
import os

class PokemonCardImporter:
    def __init__(self, db_path="data/pokemon_cards.db"):
        self.api_base = "https://api.pokemontcg.io/v2"
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokemon Card Price Checker v1.0'
        })
        
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cards table with all important fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                set_name TEXT,
                set_id TEXT,
                number TEXT,
                rarity TEXT,
                hp INTEGER,
                types TEXT,  -- JSON array
                subtypes TEXT,  -- JSON array  
                supertype TEXT,
                artist TEXT,
                release_date TEXT,
                image_small TEXT,
                image_large TEXT,
                tcgplayer_url TEXT,
                prices TEXT,  -- JSON object
                market_price REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id)
            )
        """)
        
        # Create search indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON cards(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_set ON cards(set_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_number ON cards(number)")
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def fetch_all_sets(self):
        """Get all Pokemon card sets"""
        print("📚 Fetching all sets...")
        
        try:
            response = self.session.get(f"{self.api_base}/sets?pageSize=250")
            response.raise_for_status()
            
            data = response.json()
            sets = data.get('data', [])
            
            print(f"✅ Found {len(sets)} sets")
            return sets
            
        except Exception as e:
            print(f"❌ Error fetching sets: {e}")
            return []
    
    def import_set(self, set_id, set_name, limit=None):
        """Import all cards from a specific set"""
        print(f"🎯 Importing set: {set_name} ({set_id})")
        
        page = 1
        page_size = 250
        total_imported = 0
        
        while True:
            try:
                url = f"{self.api_base}/cards?q=set.id:{set_id}&pageSize={page_size}&page={page}"
                response = self.session.get(url)
                response.raise_for_status()
                
                data = response.json()
                cards = data.get('data', [])
                
                if not cards:
                    break
                
                # Import this batch
                imported = self.save_cards(cards)
                total_imported += imported
                
                print(f"   📦 Page {page}: {imported} cards imported")
                
                if limit and total_imported >= limit:
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error importing page {page}: {e}")
                break
        
        print(f"✅ Set complete: {total_imported} cards imported")
        return total_imported
    
    def save_cards(self, cards):
        """Save cards to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        for card in cards:
            try:
                # Extract pricing data
                tcgplayer = card.get('tcgplayer', {})
                prices = tcgplayer.get('prices', {})
                market_price = None
                
                if prices:
                    # Try to get market price from any condition
                    for condition_data in prices.values():
                        if isinstance(condition_data, dict):
                            market_price = condition_data.get('market')
                            if market_price:
                                break
                
                # Insert card
                cursor.execute("""
                    INSERT OR REPLACE INTO cards (
                        id, name, set_name, set_id, number, rarity, hp,
                        types, subtypes, supertype, artist, release_date,
                        image_small, image_large, tcgplayer_url, prices, market_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    card.get('id'),
                    card.get('name'),
                    card.get('set', {}).get('name'),
                    card.get('set', {}).get('id'),
                    card.get('number'),
                    card.get('rarity'),
                    card.get('hp'),
                    json.dumps(card.get('types', [])),
                    json.dumps(card.get('subtypes', [])),
                    card.get('supertype'),
                    card.get('artist'),
                    card.get('set', {}).get('releaseDate'),
                    card.get('images', {}).get('small'),
                    card.get('images', {}).get('large'),
                    tcgplayer.get('url'),
                    json.dumps(prices) if prices else None,
                    market_price
                ))
                
                imported_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Error saving card {card.get('name', 'Unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return imported_count

def main():
    parser = argparse.ArgumentParser(description='Import Pokemon cards from API')
    parser.add_argument('--limit', type=int, help='Limit number of cards to import')
    parser.add_argument('--set-name', help='Import specific set only')
    parser.add_argument('--popular-only', action='store_true', help='Import only popular sets')
    
    args = parser.parse_args()
    
    importer = PokemonCardImporter()
    
    # Get all sets
    sets = importer.fetch_all_sets()
    if not sets:
        print("❌ Could not fetch sets")
        return
    
    # Popular sets for quick start
    popular_sets = [
        'Base', 'Jungle', 'Fossil', 'Team Rocket', 'Gym Heroes', 
        'Gym Challenge', 'Neo Genesis', 'Neo Discovery', 'Evolutions'
    ]
    
    sets_to_import = sets
    
    if args.set_name:
        sets_to_import = [s for s in sets if args.set_name.lower() in s.get('name', '').lower()]
        print(f"🎯 Filtering to sets matching '{args.set_name}': {len(sets_to_import)} found")
    elif args.popular_only:
        sets_to_import = [s for s in sets if any(pop in s.get('name', '') for pop in popular_sets)]
        print(f"🔥 Importing popular sets only: {len(sets_to_import)} sets")
    
    total_cards = 0
    
    for i, set_info in enumerate(sets_to_import, 1):
        set_id = set_info.get('id')
        set_name = set_info.get('name')
        set_total = set_info.get('total', 0)
        
        print(f"\n[{i}/{len(sets_to_import)}] {set_name} ({set_total} cards)")
        
        imported = importer.import_set(set_id, set_name, args.limit)
        total_cards += imported
        
        if args.limit and total_cards >= args.limit:
            break
    
    print(f"\n🎉 Import complete! {total_cards:,} cards imported")
    print(f"💾 Database: {importer.db_path}")

if __name__ == "__main__":
    main()
