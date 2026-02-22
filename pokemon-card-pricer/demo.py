#!/usr/bin/env python3
"""
Pokemon Card Price Checker Demo
Shows the complete pipeline working together
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append('backend')

def demo_pricing_only():
    """Demo just the pricing system without computer vision"""
    print("🎯 DEMO: Real Pokemon Card Pricing System")
    print("=" * 60)
    
    from data.price_cache import PriceCacheManager
    
    cache_manager = PriceCacheManager()
    
    # Test cards with different popularity levels
    test_cards = [
        ("Charizard", "Base Set"),      # Very popular
        ("Pikachu", "Base Set"),        # Popular  
        ("Alakazam", "Base Set"),       # Less popular
        ("Energy", "Base Set")          # Should be cheap
    ]
    
    results = []
    
    for card_name, set_name in test_cards:
        print(f"\n🔍 Getting pricing for: {card_name} ({set_name})")
        
        try:
            result = cache_manager.get_pricing(card_name, set_name)
            
            if result['success']:
                print(f"✅ Found pricing data!")
                print(f"   Source: {result['source']}")
                print(f"   Total listings: {result['total_listings']}")
                
                # Show top 3 grades
                grade_items = list(result['grade_summary'].items())[:3]
                print("   Top grades:")
                
                for grade, data in grade_items:
                    avg_price = data['avg_price']
                    count = data['count']
                    print(f"     {grade}: ${avg_price:.2f} avg ({count} sales)")
                
                results.append(result)
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Save all results
    if results:
        output_file = f"demo_pricing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 All results saved to: {output_file}")
    
    # Show cache stats
    print(f"\n📊 Cache Statistics:")
    stats = cache_manager.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

def demo_identification_system():
    """Demo the card identification without real images"""
    print("\n🎯 DEMO: Card Identification System")
    print("=" * 60)
    
    from data.card_database import CardDatabase
    from main import PokemonCardPricer
    
    # Create a sample "identified" card info (simulating CV results)
    mock_cv_results = [
        {
            'name': 'Charizard',
            'hp': 120,
            'set_number': '4/102',
            'confidence': 0.95
        },
        {
            'name': 'Pikachu', 
            'hp': 40,
            'set_number': '58/102',
            'confidence': 0.88
        },
        {
            'name': 'Unknown Pokemon',  # This should fail to match
            'hp': 90,
            'set_number': '999/999',
            'confidence': 0.65
        }
    ]
    
    pricer = PokemonCardPricer()
    
    for i, cv_result in enumerate(mock_cv_results, 1):
        print(f"\n[{i}/{len(mock_cv_results)}] Processing CV Result:")
        print(f"   Identified: {cv_result['name']} (HP: {cv_result['hp']}, #{cv_result['set_number']})")
        print(f"   Confidence: {cv_result['confidence']:.1%}")
        
        # Find database matches (this is what the real system does)
        matches = pricer._find_database_matches(cv_result)
        
        if matches:
            print(f"✅ Found {len(matches)} database matches:")
            
            for match in matches:
                card = match['card']
                confidence = match['confidence']
                reasons = match['reasons']
                
                print(f"   🎯 {card.name} ({card.set_name}) - #{card.set_number}")
                print(f"      Match confidence: {confidence:.1%}")
                print(f"      Reasons: {', '.join(reasons)}")
                
                # Get pricing for best match
                if match == matches[0]:  # Best match
                    print(f"   💰 Getting pricing...")
                    try:
                        pricing = pricer.get_real_pricing(card)
                        
                        print(f"      Total listings: {pricing['total_listings']}")
                        print(f"      Data source: {pricing['source']}")
                        
                        # Show a few grades
                        grade_items = list(pricing['prices_by_grade'].items())[:2]
                        for grade, data in grade_items:
                            if isinstance(data, dict):
                                print(f"      {grade}: ${data['avg_price']:.2f} avg")
                            else:
                                print(f"      {grade}: ${data:.2f}")
                    
                    except Exception as e:
                        print(f"      ❌ Pricing error: {e}")
        else:
            print(f"❌ No database matches found")

def demo_api_structure():
    """Show what the API responses look like"""
    print("\n🎯 DEMO: API Response Structure")  
    print("=" * 60)
    
    # Sample API response structure
    sample_response = {
        "success": True,
        "filename": "charizard_card.jpg",
        "cv_confidence": 0.95,
        "identified_info": {
            "name": "Charizard",
            "hp": 120,
            "set_number": "4/102"
        },
        "matches": [
            {
                "card": {
                    "name": "Charizard",
                    "set_name": "Base Set",
                    "set_number": "4/102",
                    "rarity": "Holo Rare",
                    "hp": 120
                },
                "confidence": 0.95,
                "match_reasons": ["exact_set_number_match"],
                "pricing": {
                    "card_name": "Charizard (Base Set)",
                    "set_number": "4/102",
                    "prices_by_grade": {
                        "Ungraded": {
                            "avg_price": 150.00,
                            "min_price": 80.00,
                            "max_price": 250.00,
                            "sale_count": 25
                        },
                        "PSA 9": {
                            "avg_price": 800.00,
                            "min_price": 600.00,
                            "max_price": 1200.00,
                            "sale_count": 15
                        },
                        "PSA 10": {
                            "avg_price": 2500.00,
                            "min_price": 1800.00,
                            "max_price": 4000.00,
                            "sale_count": 8
                        }
                    },
                    "total_listings": 48,
                    "source": "cache",
                    "note": "Real auction and marketplace pricing data"
                }
            }
        ]
    }
    
    print("Sample /identify API response:")
    print(json.dumps(sample_response, indent=2))

def main():
    print("🎮 Pokemon Card Price Checker - Complete Demo")
    print("=" * 70)
    print()
    print("This demo shows our Pokemon card price checker system:")
    print("1. Real pricing data from auction sites")
    print("2. Card identification and database matching")  
    print("3. API response structures")
    print()
    
    try:
        # Demo 1: Pricing system
        demo_pricing_only()
        
        # Demo 2: Identification system  
        demo_identification_system()
        
        # Demo 3: API structure
        demo_api_structure()
        
        print("\n" + "=" * 70)
        print("🎉 Demo completed successfully!")
        print()
        print("Next steps to try:")
        print("1. Run the API server: cd backend && python -m api.server")
        print("2. Test pricing CLI: cd backend && python price_manager.py price Charizard --set 'Base Set'")
        print("3. Add real Pokemon card images and test full pipeline")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nThis might be due to missing dependencies.")
        print("Try running: cd pokemon-card-pricer && python setup.py")

if __name__ == "__main__":
    main()