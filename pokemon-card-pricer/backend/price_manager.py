#!/usr/bin/env python3
"""
Pokemon Card Price Manager CLI
Command-line interface for managing price data and cache
"""

import argparse
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.append('.')

from data.price_cache import PriceCacheManager
from data.price_scraper import PokemonPriceScraper

def main():
    parser = argparse.ArgumentParser(description='Pokemon Card Price Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Get pricing for a specific card')
    price_parser.add_argument('name', help='Card name')
    price_parser.add_argument('--set', default='', help='Set name (optional)')
    price_parser.add_argument('--force', action='store_true', help='Force fresh scrape (ignore cache)')
    price_parser.add_argument('--save', help='Save results to file')
    
    # Cache command
    cache_parser = subparsers.add_parser('cache', help='Manage price cache')
    cache_subparsers = cache_parser.add_subparsers(dest='cache_action', help='Cache actions')
    
    cache_subparsers.add_parser('stats', help='Show cache statistics')
    cache_subparsers.add_parser('clear', help='Clear expired cache entries')
    cache_subparsers.add_parser('preload', help='Preload popular cards')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Direct scraping (bypass cache)')
    scrape_parser.add_argument('name', help='Card name')
    scrape_parser.add_argument('--set', default='', help='Set name (optional)')
    scrape_parser.add_argument('--source', choices=['ebay', 'tcgplayer', 'pwcc', 'all'], 
                               default='all', help='Scraping source')
    scrape_parser.add_argument('--limit', type=int, default=20, help='Limit results per source')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test the pricing system')
    test_parser.add_argument('--quick', action='store_true', help='Quick test with popular cards')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'price':
        cmd_price(args)
    elif args.command == 'cache':
        cmd_cache(args)
    elif args.command == 'scrape':
        cmd_scrape(args)
    elif args.command == 'test':
        cmd_test(args)

def cmd_price(args):
    """Get pricing for a card"""
    print(f"💰 Getting pricing for: {args.name} ({args.set})")
    print("=" * 60)
    
    cache_manager = PriceCacheManager()
    
    result = cache_manager.get_pricing(
        args.name, 
        args.set, 
        force_refresh=args.force
    )
    
    if not result['success']:
        print(f"❌ Failed to get pricing: {result.get('error', 'Unknown error')}")
        return
    
    # Display results
    print(f"Card: {result['card_name']} ({result['set_name']})")
    print(f"Source: {result['source']}")
    print(f"Total listings: {result['total_listings']}")
    print(f"Last updated: {result['last_updated']}")
    print(f"Cache expires: {result.get('cache_expires', 'N/A')}")
    print()
    
    print("Pricing by Grade:")
    print("-" * 40)
    
    for grade, data in result['grade_summary'].items():
        print(f"{grade}:")
        print(f"  Count: {data['count']} sales")
        print(f"  Average: ${data['avg_price']:.2f}")
        print(f"  Range: ${data['min_price']:.2f} - ${data['max_price']:.2f}")
        print(f"  Median: ${data['median_price']:.2f}")
        print()
    
    # Save to file if requested
    if args.save:
        with open(args.save, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Results saved to: {args.save}")

def cmd_cache(args):
    """Manage cache"""
    cache_manager = PriceCacheManager()
    
    if args.cache_action == 'stats':
        print("📊 Cache Statistics")
        print("=" * 30)
        
        stats = cache_manager.get_cache_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    elif args.cache_action == 'clear':
        print("🧹 Clearing expired cache entries...")
        cache_manager.clear_expired_cache()
    
    elif args.cache_action == 'preload':
        print("🔥 Preloading popular cards...")
        cache_manager.preload_popular_cards()
    
    else:
        print("Available cache actions: stats, clear, preload")

def cmd_scrape(args):
    """Direct scraping"""
    print(f"🕷️  Scraping pricing for: {args.name} ({args.set})")
    print(f"Source: {args.source}")
    print("=" * 60)
    
    scraper = PokemonPriceScraper()
    search_term = f"{args.name} {args.set}".strip()
    
    all_results = []
    
    if args.source in ['ebay', 'all']:
        print("Scraping eBay...")
        ebay_results = scraper.scrape_ebay_sold(search_term, args.limit)
        all_results.extend(ebay_results)
    
    if args.source in ['tcgplayer', 'all']:
        print("Scraping TCGPlayer...")
        tcg_results = scraper.scrape_tcgplayer(search_term, args.limit)
        all_results.extend(tcg_results)
    
    if args.source in ['pwcc', 'all']:
        print("Scraping PWCC...")
        pwcc_results = scraper.scrape_pwcc(search_term, args.limit)
        all_results.extend(pwcc_results)
    
    print(f"\n📊 Results Summary:")
    print(f"Total results: {len(all_results)}")
    
    # Group by marketplace
    by_marketplace = {}
    for result in all_results:
        marketplace = result.marketplace
        if marketplace not in by_marketplace:
            by_marketplace[marketplace] = []
        by_marketplace[marketplace].append(result)
    
    for marketplace, results in by_marketplace.items():
        prices = [r.price for r in results]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"{marketplace}: {len(results)} results, avg ${avg_price:.2f}")
    
    # Show some sample results
    if all_results:
        print(f"\nSample Results:")
        for i, result in enumerate(all_results[:5]):
            print(f"{i+1}. {result.marketplace}: {result.title[:60]}... - ${result.price:.2f} ({result.grade})")

def cmd_test(args):
    """Test the pricing system"""
    if args.quick:
        test_cards = [("Charizard", "Base Set"), ("Pikachu", "Base Set")]
    else:
        test_cards = [
            ("Charizard", "Base Set"),
            ("Pikachu", "Base Set"),
            ("Blastoise", "Base Set"),
            ("Venusaur", "Base Set")
        ]
    
    print(f"🧪 Testing pricing system with {len(test_cards)} cards")
    print("=" * 60)
    
    cache_manager = PriceCacheManager()
    
    for i, (card_name, set_name) in enumerate(test_cards, 1):
        print(f"\n[{i}/{len(test_cards)}] Testing: {card_name} ({set_name})")
        
        try:
            result = cache_manager.get_pricing(card_name, set_name)
            
            if result['success']:
                print(f"✅ Success - {result['source']} ({result['total_listings']} listings)")
                
                # Show top grades
                top_grades = list(result['grade_summary'].keys())[:3]
                for grade in top_grades:
                    data = result['grade_summary'][grade]
                    print(f"   {grade}: ${data['avg_price']:.2f} avg ({data['count']} sales)")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Test complete!")

if __name__ == "__main__":
    main()