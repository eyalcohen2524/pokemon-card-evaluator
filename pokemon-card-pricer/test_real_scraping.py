#!/usr/bin/env python3
"""
Test real data scraping for Pokemon cards
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
import json

def test_real_ebay_scraping():
    print('🔍 Testing eBay sold listings scraper with real data...')
    
    # Test with a popular Pokemon card
    search_term = 'Charizard Base Set PSA 10'
    query = urllib.parse.quote_plus(search_term + ' pokemon card')
    url = f'https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1&LH_Complete=1&_sop=13'
    
    print(f'🌐 URL: {url}')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=15)
        print(f'✅ eBay response: {response.status_code}')
        print(f'📄 Content length: {len(response.content)} bytes')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Check what we got
            title = soup.find('title')
            if title:
                print(f'📋 Page title: {title.get_text()[:100]}...')
            
            # Look for different possible selectors
            selectors_to_try = [
                {'items': 'div.s-item', 'price': 'span.s-item__price', 'title': 'a.s-item__link'},
                {'items': '.s-item', 'price': '.s-item__price', 'title': '.s-item__title'},
                {'items': '[data-view]', 'price': '.notranslate', 'title': '.it-ttl'},
                {'items': 'div[data-view*="mi:"]', 'price': 'span.notranslate', 'title': 'h3'},
            ]
            
            results = []
            
            for i, selectors in enumerate(selectors_to_try):
                print(f'\n🔎 Trying selector set {i+1}...')
                
                items = soup.select(selectors['items'])
                print(f'📦 Found {len(items)} items with selector: {selectors["items"]}')
                
                if len(items) > 0:
                    for j, item in enumerate(items[:5]):  # Try first 5 items
                        try:
                            price_elem = item.select_one(selectors['price'])
                            title_elem = item.select_one(selectors['title'])
                            
                            if price_elem and title_elem:
                                price_text = price_elem.get_text(strip=True)
                                
                                # Handle title element (could be link or text)
                                if hasattr(title_elem, 'get_text'):
                                    title_text = title_elem.get_text(strip=True)
                                elif title_elem.get('href'):
                                    title_text = title_elem.get('href', '')[:60]
                                else:
                                    title_text = str(title_elem)[:60]
                                
                                # Extract numerical price
                                price_match = re.search(r'\$([0-9,]+(?:\.[0-9]{2})?)', price_text)
                                if price_match:
                                    price_value = float(price_match.group(1).replace(',', ''))
                                    
                                    results.append({
                                        'title': title_text[:80],
                                        'price': price_value,
                                        'price_text': price_text
                                    })
                                    
                                    print(f'💰 [{j+1}] {title_text[:50]}... - ${price_value:.2f}')
                                
                        except Exception as e:
                            continue
                
                if results:
                    break  # Found working selectors
            
            if results:
                print(f'\n🎉 Successfully extracted {len(results)} real eBay prices!')
                avg_price = sum(r['price'] for r in results) / len(results)
                min_price = min(r['price'] for r in results)
                max_price = max(r['price'] for r in results)
                
                print(f'📊 Price Analysis for {search_term}:')
                print(f'   Average: ${avg_price:.2f}')
                print(f'   Range: ${min_price:.2f} - ${max_price:.2f}')
                print(f'   Sample count: {len(results)}')
                return True, results
            else:
                print('❌ No prices extracted - eBay may be blocking or page structure changed')
                
                # Debug: Show some of the HTML structure
                print('\n🔍 Page structure sample:')
                sample_divs = soup.find_all('div', limit=10)
                for div in sample_divs[:5]:
                    classes = div.get('class', [])
                    if classes:
                        print(f'   <div class="{" ".join(classes)[:50]}...">')
                
                return False, []
        else:
            print(f'❌ eBay returned status {response.status_code}')
            if response.status_code == 429:
                print('   Rate limited - eBay is blocking requests')
            elif response.status_code == 403:
                print('   Access forbidden - eBay detected bot')
            return False, []
            
    except Exception as e:
        print(f'❌ Error scraping eBay: {e}')
        return False, []

def test_tcgplayer_api():
    """
    Test TCGPlayer public API access
    """
    print('\n🔍 Testing TCGPlayer API access...')
    
    try:
        # Try accessing TCGPlayer's public search endpoint
        search_url = 'https://shop.tcgplayer.com/pokemon'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f'✅ TCGPlayer response: {response.status_code}')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            if title:
                print(f'📋 Page title: {title.get_text()[:80]}...')
            
            # Look for product listings
            product_links = soup.find_all('a', href=re.compile(r'/pokemon/.*'))
            print(f'📦 Found {len(product_links)} Pokemon product links')
            
            if len(product_links) > 0:
                print('🎉 TCGPlayer access successful!')
                return True
        
        return False
        
    except Exception as e:
        print(f'❌ TCGPlayer test failed: {e}')
        return False

def test_comprehensive_scraping():
    """
    Test our actual price scraper with real data
    """
    print('\n🚀 Testing comprehensive price scraping...')
    
    # Import our actual scraper
    import sys
    sys.path.append('backend')
    
    try:
        from data.price_scraper import PokemonPriceScraper
        
        scraper = PokemonPriceScraper()
        
        # Test with different popular cards
        test_cards = [
            ('Charizard', 'Base Set'),
            ('Pikachu', 'Base Set'),
            ('Blastoise', 'Base Set')
        ]
        
        for card_name, set_name in test_cards:
            print(f'\n📊 Testing: {card_name} ({set_name})')
            
            try:
                result = scraper.get_comprehensive_pricing(card_name, set_name)
                
                if result['total_listings'] > 0:
                    print(f'✅ Found {result["total_listings"]} total listings')
                    
                    # Show grade summary
                    for grade, data in list(result['grade_summary'].items())[:3]:
                        print(f'   {grade}: ${data["avg_price"]:.2f} avg ({data["count"]} sales)')
                else:
                    print('❌ No listings found')
                
                # Add delay between requests
                time.sleep(2)
                
            except Exception as e:
                print(f'❌ Error scraping {card_name}: {e}')
        
        return True
        
    except ImportError as e:
        print(f'❌ Could not import price scraper: {e}')
        return False

def main():
    print('🎯 Pokemon Card Real Data Scraping Test')
    print('=' * 50)
    
    # Test 1: eBay scraping
    ebay_success, ebay_results = test_real_ebay_scraping()
    
    # Test 2: TCGPlayer access
    tcg_success = test_tcgplayer_api()
    
    # Test 3: Full scraper
    scraper_success = test_comprehensive_scraping()
    
    print('\n' + '=' * 50)
    print('🏁 Test Results Summary:')
    print(f'   eBay scraping: {"✅ Working" if ebay_success else "❌ Failed"}')
    print(f'   TCGPlayer access: {"✅ Working" if tcg_success else "❌ Failed"}')
    print(f'   Full scraper: {"✅ Working" if scraper_success else "❌ Failed"}')
    
    if ebay_success and ebay_results:
        print(f'\n💎 Real pricing data available!')
        print(f'   Sample: {len(ebay_results)} eBay sold listings')
        return True
    else:
        print(f'\n⚠️  Falling back to mock data for demo')
        return False

if __name__ == '__main__':
    success = main()