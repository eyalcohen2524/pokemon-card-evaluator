#!/usr/bin/env python3
"""
Pokemon Card Price Checker - Main Integration Script
Combines computer vision identification with database lookup
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from cv.card_identifier import PokemonCardIdentifier
from data.card_database import CardDatabase, PokemonCard
from data.price_cache import PriceCacheManager

class PokemonCardPricer:
    """Main class that ties together identification and pricing"""
    
    def __init__(self, db_path: str = None):
        self.identifier = PokemonCardIdentifier()
        
        # Smart database path resolution
        if db_path is None:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "data", "pokemon_comprehensive.db")
            
            # Fallback if not found
            if not os.path.exists(db_path):
                db_path = os.path.join(os.path.dirname(current_dir), "data", "pokemon_comprehensive.db")
        
        self.database = CardDatabase(db_path)
        self.price_cache = PriceCacheManager()
        
        # Log database size
        print(f"🎴 Initialized with {len(self.database.cards):,} cards from comprehensive database")
        
        # Initialize with sample data if database is empty
        if not self.database.cards:
            print("⚠️ Comprehensive database empty, falling back to sample data...")
            self._create_sample_fallback()
        
        # Start background price updates
        self.price_cache.start_background_updates()
    
    def identify_and_price_card(self, image_path: str) -> Dict:
        """
        Complete pipeline: identify card from image and get pricing info
        """
        print(f"🔍 Analyzing image: {image_path}")
        
        # Step 1: Computer vision identification
        cv_result = self.identifier.identify_card(image_path)
        
        if 'error' in cv_result:
            return {
                'success': False,
                'error': cv_result['error']
            }
        
        print(f"✅ Card identified with {cv_result['confidence']:.1%} confidence")
        print(f"   Name: {cv_result['name']}")
        print(f"   HP: {cv_result['hp']}")
        print(f"   Set: {cv_result['set_number']}")
        
        # Step 2: Database lookup
        matches = self._find_database_matches(cv_result)
        
        if not matches:
            return {
                'success': False,
                'cv_result': cv_result,
                'error': 'No matching cards found in database'
            }
        
        # Step 3: Format results
        result = {
            'success': True,
            'cv_result': cv_result,
            'matches': []
        }
        
        print(f"\n📚 Found {len(matches)} database matches:")
        
        for match in matches:
            match_info = {
                'card': match['card'].to_dict(),
                'confidence': match['confidence'],
                'match_reasons': match['reasons']
            }
            result['matches'].append(match_info)
            
            card = match['card']
            print(f"   🎯 {card.name} ({card.set_name}) - {card.set_number}")
            print(f"      Confidence: {match['confidence']:.1%}")
            print(f"      Match reasons: {', '.join(match['reasons'])}")
        
        return result
    
    def _find_database_matches(self, cv_result: Dict) -> List[Dict]:
        """Find matching cards in database based on CV results"""
        matches = []
        
        # Primary: Search by set number (most reliable)
        if cv_result.get('set_number'):
            exact_match = self.database.search_by_set_number(cv_result['set_number'])
            if exact_match:
                matches.append({
                    'card': exact_match,
                    'confidence': 0.95,
                    'reasons': ['exact_set_number_match']
                })
                return matches  # Set number should be unique
        
        # Secondary: Search by name
        if cv_result.get('name'):
            name_matches = self.database.search_by_name(cv_result['name'])
            
            for card in name_matches:
                confidence = 0.6  # Base confidence for name match
                reasons = ['name_match']
                
                # Boost confidence if HP matches
                if cv_result.get('hp') and card.hp == cv_result['hp']:
                    confidence += 0.25
                    reasons.append('hp_match')
                
                # Boost confidence if we have partial set info
                if cv_result.get('set_number') and card.set_number:
                    # Check if set numbers are similar
                    cv_set_parts = cv_result['set_number'].split('/')
                    db_set_parts = card.set_number.split('/')
                    
                    if len(cv_set_parts) >= 1 and len(db_set_parts) >= 1:
                        if cv_set_parts[0] == db_set_parts[0]:  # Same card number
                            confidence += 0.2
                            reasons.append('card_number_match')
                
                matches.append({
                    'card': card,
                    'confidence': min(confidence, 0.95),
                    'reasons': reasons
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches
    
    def get_real_pricing(self, card: PokemonCard, use_cache: bool = True) -> Dict:
        """
        Get real pricing data from auction sites and marketplaces
        """
        try:
            # Get pricing from cache or fresh scrape
            pricing_result = self.price_cache.get_pricing(
                card.name, 
                card.set_name, 
                force_refresh=not use_cache
            )
            
            if not pricing_result['success']:
                # Fallback to mock data if scraping fails
                return self._get_fallback_pricing(card)
            
            # Transform the grade_summary into a cleaner format
            prices_by_grade = {}
            
            for grade, data in pricing_result['grade_summary'].items():
                prices_by_grade[grade] = {
                    'avg_price': round(data['avg_price'], 2),
                    'min_price': round(data['min_price'], 2),
                    'max_price': round(data['max_price'], 2),
                    'median_price': round(data['median_price'], 2),
                    'sale_count': data['count']
                }
            
            return {
                'card_name': f"{card.name} ({card.set_name})",
                'set_number': card.set_number,
                'prices_by_grade': prices_by_grade,
                'total_listings': pricing_result['total_listings'],
                'last_updated': pricing_result['last_updated'],
                'source': pricing_result['source'],
                'note': 'Real auction and marketplace pricing data'
            }
            
        except Exception as e:
            print(f"❌ Error getting real pricing for {card.name}: {e}")
            return self._get_fallback_pricing(card)
    
    def _get_fallback_pricing(self, card: PokemonCard) -> Dict:
        """Fallback mock pricing when real data isn't available"""
        import random
        
        # Mock prices based on rarity and name (similar to old logic)
        base_price = 5
        
        if card.rarity == "Holo Rare":
            base_price = 50
        elif card.rarity == "Rare":
            base_price = 15
        elif card.rarity == "Uncommon":
            base_price = 3
        
        # Famous cards get price multipliers
        multipliers = {
            "Charizard": 5.0,
            "Pikachu": 2.0,
            "Blastoise": 3.0,
            "Venusaur": 3.0
        }
        
        multiplier = multipliers.get(card.name, 1.0)
        base_price *= multiplier
        
        # Generate grade-based pricing with realistic structure
        grades = ['Ungraded', 'PSA 8', 'PSA 9', 'PSA 10', 'BGS 9.5']
        multipliers = [1.0, 2.0, 4.0, 8.0, 6.0]
        
        prices_by_grade = {}
        
        for grade, mult in zip(grades, multipliers):
            price = base_price * mult * (0.8 + random.random() * 0.4)
            prices_by_grade[grade] = {
                'avg_price': round(price, 2),
                'min_price': round(price * 0.7, 2),
                'max_price': round(price * 1.4, 2),
                'median_price': round(price * 0.95, 2),
                'sale_count': random.randint(1, 10)
            }
        
        return {
            'card_name': f"{card.name} ({card.set_name})",
            'set_number': card.set_number,
            'prices_by_grade': prices_by_grade,
            'total_listings': sum(g['sale_count'] for g in prices_by_grade.values()),
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback',
            'note': 'Fallback pricing - real data unavailable'
        }
    
    def _create_sample_fallback(self):
        """Create sample cards if comprehensive database fails"""
        try:
            from data.card_database import PokemonCard
            
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
                )
            ]
            
            self.database.cards = sample_cards
            print(f"📦 Created {len(sample_cards)} fallback cards")
            
        except Exception as e:
            print(f"❌ Error creating fallback cards: {e}")

def main():
    """Test the complete pipeline"""
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_path>")
        print("\nExample: python main.py ../data/sample_charizard.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Initialize the pricer
    pricer = PokemonCardPricer()
    
    # Run complete identification and pricing
    result = pricer.identify_and_price_card(image_path)
    
    if not result['success']:
        print(f"❌ Failed: {result['error']}")
        if 'cv_result' in result:
            print(f"CV extracted text: {result['cv_result'].get('extracted_text', {})}")
        sys.exit(1)
    
    # Show pricing for best match
    if result['matches']:
        best_match = result['matches'][0]
        card = PokemonCard(**best_match['card'])
        
        print(f"\n💰 Real Pricing for best match:")
        pricing = pricer.get_real_pricing(card)
        
        print(f"Card: {pricing['card_name']}")
        print(f"Data source: {pricing['source']}")
        print(f"Total listings: {pricing['total_listings']}")
        print("Prices by grade:")
        
        for grade, data in pricing['prices_by_grade'].items():
            if isinstance(data, dict):
                print(f"  {grade:12}: ${data['avg_price']:7.2f} avg (${data['min_price']:.2f}-${data['max_price']:.2f}, {data['sale_count']} sales)")
            else:
                # Fallback for old format
                print(f"  {grade:12}: ${data:7.2f}")
        
        print(f"\n{pricing['note']}")
        print(f"Last updated: {pricing['last_updated']}")
    
    # Save detailed results
    output_file = "identification_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()