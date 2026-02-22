#!/usr/bin/env python3
"""
Research comprehensive Pokemon card databases and APIs
"""

import requests
import json
import time
import csv
from typing import Dict, List

def test_pokemon_tcg_api():
    """Test the Pokemon TCG API - largest free database"""
    print("🔍 Testing Pokemon TCG API (pokemontcg.io)")
    print("=" * 50)
    
    try:
        # Test basic connection and get total count
        response = requests.get('https://api.pokemontcg.io/v2/cards?pageSize=1', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_cards = data.get('totalCount', 0)
            
            print(f"✅ API accessible")
            print(f"📊 Total cards available: {total_cards:,}")
            
            if total_cards > 0 and data.get('data'):
                sample_card = data['data'][0]
                print(f"📋 Sample card: {sample_card.get('name')} ({sample_card.get('set', {}).get('name')})")
                
                # Show available fields
                fields = list(sample_card.keys())
                print(f"🏷️ Available fields ({len(fields)}): {', '.join(fields[:10])}...")
                
                # Test sets endpoint
                sets_response = requests.get('https://api.pokemontcg.io/v2/sets?pageSize=5', timeout=10)
                if sets_response.status_code == 200:
                    sets_data = sets_response.json()
                    total_sets = sets_data.get('totalCount', 0)
                    sets = sets_data.get('data', [])
                    
                    print(f"📚 Total sets: {total_sets}")
                    print("🎯 Sample sets:")
                    for s in sets:
                        print(f"   • {s.get('name')} ({s.get('releaseDate')}) - {s.get('total', 0)} cards")
                
                return True, total_cards, sample_card
        else:
            print(f"❌ API error: {response.status_code}")
            return False, 0, None
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, 0, None

def test_tcgplayer_public():
    """Test TCGPlayer public data access"""
    print("\n🔍 Testing TCGPlayer public access")
    print("=" * 40)
    
    try:
        # Test public product search
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get('https://shop.tcgplayer.com/pokemon', headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ TCGPlayer accessible")
            print("💰 Has pricing data but requires scraping or API key")
            return True
        else:
            print(f"❌ TCGPlayer access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ TCGPlayer test failed: {e}")
        return False

def test_scryfall_equivalent():
    """Look for Pokemon equivalent of Scryfall (Magic cards)"""
    print("\n🔍 Looking for Pokemon card APIs")
    print("=" * 35)
    
    apis_to_test = [
        ('PokemonTCG.io', 'https://api.pokemontcg.io/v2/cards'),
        ('TCGPlayer API', 'https://api.tcgplayer.com/'),  # Requires auth
        ('PTCGO API', 'https://ptcgo-legends.com/api/'),   # Fan site
    ]
    
    working_apis = []
    
    for name, url in apis_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401]:  # 401 means API exists but needs auth
                working_apis.append((name, url, response.status_code))
                print(f"✅ {name}: Available (status: {response.status_code})")
            else:
                print(f"❌ {name}: Not accessible ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {name}: Failed ({e})")
    
    return working_apis

def explore_pokemon_tcg_data():
    """Deep dive into Pokemon TCG API data structure"""
    print("\n🔬 Deep dive: Pokemon TCG API data")
    print("=" * 40)
    
    try:
        # Get sample cards from different sets
        response = requests.get('https://api.pokemontcg.io/v2/cards?pageSize=10&q=name:charizard', timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            cards = data.get('data', [])
            
            print(f"🎯 Found {len(cards)} Charizard variants")
            
            for i, card in enumerate(cards[:5]):  # Show first 5
                print(f"\n[{i+1}] {card.get('name')} - {card.get('set', {}).get('name', 'Unknown Set')}")
                print(f"    ID: {card.get('id')}")
                print(f"    Number: {card.get('number')}")
                print(f"    Rarity: {card.get('rarity')}")
                print(f"    HP: {card.get('hp', 'N/A')}")
                
                # Check for pricing data
                tcgplayer = card.get('tcgplayer', {})
                if tcgplayer:
                    prices = tcgplayer.get('prices', {})
                    if prices:
                        print(f"    💰 Pricing available: {list(prices.keys())}")
                        
                        # Show sample pricing
                        for condition, price_data in list(prices.items())[:2]:
                            if isinstance(price_data, dict):
                                market_price = price_data.get('market')
                                if market_price:
                                    print(f"       {condition}: ${market_price}")
                
                # Check for images
                images = card.get('images', {})
                if images:
                    print(f"    🖼️ Images: {list(images.keys())}")
            
            return True, cards
        else:
            print(f"❌ Deep dive failed: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"❌ Deep dive error: {e}")
        return False, []

def create_database_import_plan():
    """Create a plan for importing large card database"""
    print("\n📋 Database Import Strategy")
    print("=" * 30)
    
    plan = {
        'primary_source': 'Pokemon TCG API',
        'endpoint': 'https://api.pokemontcg.io/v2/cards',
        'estimated_cards': '15,000+',
        'rate_limits': 'Unknown - test needed',
        'import_strategy': [
            '1. Fetch all sets first (/v2/sets)',
            '2. Import cards by set (easier to manage)',
            '3. Store in PostgreSQL with full-text search',
            '4. Cache images locally or use CDN URLs',
            '5. Build fuzzy matching index for OCR results'
        ],
        'required_fields': [
            'id', 'name', 'set.name', 'number', 'rarity',
            'hp', 'types', 'images.large', 'tcgplayer.prices'
        ],
        'batch_size': 250,  # Cards per request
        'estimated_time': '~30 minutes for full import'
    }
    
    for key, value in plan.items():
        if isinstance(value, list):
            print(f"{key.replace('_', ' ').title()}:")
            for item in value:
                print(f"   {item}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    return plan

def generate_import_script():
    """Generate actual import script"""
    print("\n💻 Generating import script...")
    
    script = '''#!/usr/bin/env python3
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
        
        print(f"\\n[{i}/{len(sets_to_import)}] {set_name} ({set_total} cards)")
        
        imported = importer.import_set(set_id, set_name, args.limit)
        total_cards += imported
        
        if args.limit and total_cards >= args.limit:
            break
    
    print(f"\\n🎉 Import complete! {total_cards:,} cards imported")
    print(f"💾 Database: {importer.db_path}")

if __name__ == "__main__":
    main()
'''
    
    with open('import_pokemon_cards.py', 'w') as f:
        f.write(script)
    
    print("✅ Import script generated: import_pokemon_cards.py")
    return True

def main():
    print("🔍 Pokemon Card Database Research")
    print("=" * 60)
    
    # Test Pokemon TCG API
    api_works, total_cards, sample = test_pokemon_tcg_api()
    
    # Test other sources
    tcg_works = test_tcgplayer_public()
    
    # Find other APIs
    working_apis = test_scryfall_equivalent()
    
    # Deep dive into structure
    if api_works:
        explore_success, cards = explore_pokemon_tcg_data()
    
    # Create import plan
    plan = create_database_import_plan()
    
    # Generate actual import script
    generate_import_script()
    
    print("\n" + "=" * 60)
    print("🏁 RESEARCH SUMMARY")
    print("=" * 60)
    
    if api_works:
        print(f"✅ PRIMARY SOURCE: Pokemon TCG API")
        print(f"   📊 {total_cards:,} cards available")
        print(f"   💰 Pricing data included")
        print(f"   🖼️ High-quality images")
        print(f"   🚀 Ready for bulk import")
    
    print(f"\n📋 RECOMMENDED APPROACH:")
    print(f"   1. Use Pokemon TCG API as primary source")
    print(f"   2. Import {total_cards:,} cards with full metadata")
    print(f"   3. Add real pricing from our eBay scraper") 
    print(f"   4. Enable fuzzy search for OCR matching")
    
    print(f"\n💻 NEXT STEPS:")
    print(f"   • Run: python import_pokemon_cards.py --popular-only")
    print(f"   • This will import ~2,000 popular cards")
    print(f"   • Full import: ~{total_cards:,} cards in ~30 minutes")
    
    return api_works

if __name__ == '__main__':
    main()