#!/usr/bin/env python3
"""
Price Cache System for Pokemon Card Price Checker
Manages cached pricing data and refresh schedules
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
from dataclasses import dataclass, asdict

try:
    from .price_scraper import PokemonPriceScraper
except ImportError:
    from price_scraper import PokemonPriceScraper

@dataclass
class CachedPrice:
    """Cached pricing data with metadata"""
    card_name: str
    set_name: str
    grade_summary: Dict
    total_listings: int
    last_updated: str
    cache_expires: str
    raw_data: List[Dict]
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        expire_time = datetime.fromisoformat(self.cache_expires.replace('Z', '+00:00'))
        return datetime.now() > expire_time.replace(tzinfo=None)
    
    def to_dict(self) -> Dict:
        return asdict(self)

class PriceCacheManager:
    """Manages price caching and background updates"""
    
    def __init__(self, cache_dir: str = "data/price_cache"):
        self.cache_dir = cache_dir
        self.cache_duration_hours = 6  # Cache expires after 6 hours
        self.popular_cards_refresh_hours = 2  # Popular cards refresh more often
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize scraper
        self.scraper = PokemonPriceScraper()
        
        # Background update thread
        self.update_thread = None
        self.shutdown_flag = threading.Event()
        
        # Popular cards that get updated more frequently
        self.popular_cards = [
            ("Charizard", "Base Set"),
            ("Pikachu", "Base Set"), 
            ("Blastoise", "Base Set"),
            ("Venusaur", "Base Set"),
            ("Charizard", "Evolutions"),
            ("Pikachu", "Promo"),
            ("Mewtwo", "Base Set"),
            ("Mew", "Promo")
        ]
    
    def _get_cache_path(self, card_name: str, set_name: str) -> str:
        """Get cache file path for a card"""
        safe_name = f"{card_name}_{set_name}".replace(" ", "_").replace("/", "_")
        return os.path.join(self.cache_dir, f"{safe_name}.json")
    
    def _load_cached_price(self, card_name: str, set_name: str) -> Optional[CachedPrice]:
        """Load cached price data if it exists and is valid"""
        cache_path = self._get_cache_path(card_name, set_name)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            cached_price = CachedPrice(**data)
            
            # Check if expired
            if cached_price.is_expired():
                print(f"💭 Cache expired for {card_name} ({set_name})")
                return None
            
            print(f"✅ Cache hit for {card_name} ({set_name})")
            return cached_price
            
        except Exception as e:
            print(f"❌ Error loading cache for {card_name}: {e}")
            return None
    
    def _save_cached_price(self, pricing_data: Dict) -> CachedPrice:
        """Save pricing data to cache"""
        card_name = pricing_data['card_name']
        set_name = pricing_data.get('set_name', '')
        
        # Calculate expiration time
        is_popular = (card_name, set_name) in self.popular_cards
        cache_hours = self.popular_cards_refresh_hours if is_popular else self.cache_duration_hours
        
        expire_time = datetime.now() + timedelta(hours=cache_hours)
        
        cached_price = CachedPrice(
            card_name=card_name,
            set_name=set_name,
            grade_summary=pricing_data['grade_summary'],
            total_listings=pricing_data['total_listings'],
            last_updated=pricing_data['last_updated'],
            cache_expires=expire_time.isoformat(),
            raw_data=pricing_data['raw_data']
        )
        
        # Save to file
        cache_path = self._get_cache_path(card_name, set_name)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cached_price.to_dict(), f, indent=2)
            
            cache_type = "popular" if is_popular else "standard"
            print(f"💾 Cached pricing for {card_name} ({cache_type}, expires in {cache_hours}h)")
            
        except Exception as e:
            print(f"❌ Error saving cache for {card_name}: {e}")
        
        return cached_price
    
    def get_pricing(self, card_name: str, set_name: str = "", force_refresh: bool = False) -> Dict:
        """
        Get pricing data (from cache or fresh scrape)
        """
        print(f"🔍 Getting pricing for: {card_name} ({set_name})")
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached = self._load_cached_price(card_name, set_name)
            if cached:
                return {
                    'success': True,
                    'source': 'cache',
                    'card_name': cached.card_name,
                    'set_name': cached.set_name,
                    'grade_summary': cached.grade_summary,
                    'total_listings': cached.total_listings,
                    'last_updated': cached.last_updated,
                    'cache_expires': cached.cache_expires
                }
        
        # Cache miss or force refresh - scrape fresh data
        print(f"🕷️  Scraping fresh pricing data...")
        
        try:
            pricing_data = self.scraper.get_comprehensive_pricing(card_name, set_name)
            
            # Cache the results
            cached = self._save_cached_price(pricing_data)
            
            return {
                'success': True,
                'source': 'fresh',
                'card_name': cached.card_name,
                'set_name': cached.set_name,
                'grade_summary': cached.grade_summary,
                'total_listings': cached.total_listings,
                'last_updated': cached.last_updated,
                'cache_expires': cached.cache_expires
            }
            
        except Exception as e:
            print(f"❌ Error getting pricing for {card_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def preload_popular_cards(self):
        """Preload pricing data for popular cards"""
        print(f"🔥 Preloading {len(self.popular_cards)} popular cards...")
        
        for card_name, set_name in self.popular_cards:
            try:
                result = self.get_pricing(card_name, set_name)
                if result['success']:
                    print(f"   ✅ {card_name} ({set_name})")
                else:
                    print(f"   ❌ {card_name} ({set_name}): {result.get('error', 'Unknown error')}")
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ {card_name} ({set_name}): {e}")
        
        print("🎉 Preloading complete!")
    
    def start_background_updates(self):
        """Start background thread to keep popular cards updated"""
        if self.update_thread and self.update_thread.is_alive():
            print("⚠️  Background updates already running")
            return
        
        print("🔄 Starting background price updates...")
        self.shutdown_flag.clear()
        self.update_thread = threading.Thread(target=self._background_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop_background_updates(self):
        """Stop background update thread"""
        if self.update_thread and self.update_thread.is_alive():
            print("🛑 Stopping background updates...")
            self.shutdown_flag.set()
            self.update_thread.join(timeout=10)
    
    def _background_update_loop(self):
        """Background loop that updates expired popular cards"""
        print("🔄 Background update loop started")
        
        while not self.shutdown_flag.is_set():
            try:
                # Check popular cards for expired cache
                for card_name, set_name in self.popular_cards:
                    if self.shutdown_flag.is_set():
                        break
                    
                    cached = self._load_cached_price(card_name, set_name)
                    
                    # If expired or doesn't exist, refresh
                    if not cached or cached.is_expired():
                        print(f"🔄 Background refresh: {card_name} ({set_name})")
                        self.get_pricing(card_name, set_name, force_refresh=True)
                        
                        # Wait between updates to be respectful
                        time.sleep(5)
                
                # Sleep for an hour before next check
                for _ in range(3600):  # 1 hour = 3600 seconds
                    if self.shutdown_flag.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Background update error: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        print("🔄 Background update loop stopped")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached data"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        total_cached = len(cache_files)
        expired_count = 0
        popular_cached = 0
        
        for filename in cache_files:
            try:
                with open(os.path.join(self.cache_dir, filename), 'r') as f:
                    data = json.load(f)
                
                cached_price = CachedPrice(**data)
                
                if cached_price.is_expired():
                    expired_count += 1
                
                if (cached_price.card_name, cached_price.set_name) in self.popular_cards:
                    popular_cached += 1
                    
            except Exception:
                continue
        
        return {
            'total_cached_cards': total_cached,
            'expired_entries': expired_count,
            'popular_cards_cached': popular_cached,
            'total_popular_cards': len(self.popular_cards),
            'cache_directory': self.cache_dir
        }
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        removed_count = 0
        
        for filename in cache_files:
            filepath = os.path.join(self.cache_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                cached_price = CachedPrice(**data)
                
                if cached_price.is_expired():
                    os.remove(filepath)
                    removed_count += 1
                    print(f"🗑️  Removed expired cache: {cached_price.card_name}")
                    
            except Exception as e:
                print(f"❌ Error checking cache file {filename}: {e}")
        
        print(f"🧹 Cleaned up {removed_count} expired cache entries")

def main():
    """Test the price cache system"""
    cache_manager = PriceCacheManager()
    
    # Test cache functionality
    test_cards = [
        ("Charizard", "Base Set"),
        ("Pikachu", "Base Set")
    ]
    
    print("🧪 Testing price cache system")
    print("="*50)
    
    for card_name, set_name in test_cards:
        print(f"\nTesting: {card_name} ({set_name})")
        
        # First request (should be fresh)
        result1 = cache_manager.get_pricing(card_name, set_name)
        print(f"First request source: {result1.get('source', 'unknown')}")
        
        # Second request (should be cached)
        result2 = cache_manager.get_pricing(card_name, set_name)
        print(f"Second request source: {result2.get('source', 'unknown')}")
        
        # Force refresh
        result3 = cache_manager.get_pricing(card_name, set_name, force_refresh=True)
        print(f"Force refresh source: {result3.get('source', 'unknown')}")
    
    # Show cache stats
    print(f"\n📊 Cache Statistics:")
    stats = cache_manager.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test preloading
    print(f"\n🔥 Testing preload...")
    cache_manager.preload_popular_cards()

if __name__ == "__main__":
    main()