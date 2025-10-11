#!/usr/bin/env python3
"""
Test script for individual scrapers (JSON, ICS, etc.)
"""

import sys
import importlib
from datetime import datetime

def test_physics_scraper():
    """Test the Physics JSON scraper"""
    print("⚛️ TESTING PHYSICS JSON SCRAPER")
    print("=" * 50)
    
    try:
        from physics_json_scraper import PhysicsJSONScraper
        scraper = PhysicsJSONScraper()
        events = scraper.scrape_physics_events()
        
        print(f"✅ Physics: {len(events)} events found")
        if events:
            print("Sample events:")
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.get('title', 'No title')}: {event.get('start_date', 'No date')} {event.get('time', 'No time')}")
        
        return events
    except Exception as e:
        print(f"❌ Physics scraper failed: {e}")
        return []

def test_geosciences_scraper():
    """Test the Geosciences JSON scraper"""
    print("\n🌍 TESTING GEOSCIENCES JSON SCRAPER")
    print("=" * 50)
    
    try:
        from geosciences_json_scraper import GeosciencesJSONScraper
        scraper = GeosciencesJSONScraper()
        events = scraper.scrape_geosciences_events()
        
        print(f"✅ Geosciences: {len(events)} events found")
        if events:
            print("Sample events:")
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.get('title', 'No title')}: {event.get('start_date', 'No date')} {event.get('time', 'No time')}")
        
        return events
    except Exception as e:
        print(f"❌ Geosciences scraper failed: {e}")
        return []

def test_philosophy_scraper():
    """Test the Philosophy ICS scraper"""
    print("\n🤔 TESTING PHILOSOPHY ICS SCRAPER")
    print("=" * 50)
    
    try:
        from philosophy_ics_scraper import PhilosophyICSScraper
        scraper = PhilosophyICSScraper()
        events = scraper.scrape_philosophy_events()
        
        print(f"✅ Philosophy: {len(events)} events found")
        if events:
            print("Sample events:")
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.get('title', 'No title')}: {event.get('start_date', 'No date')} {event.get('time', 'No time')}")
        
        return events
    except Exception as e:
        print(f"❌ Philosophy scraper failed: {e}")
        return []

def test_math_scraper():
    """Test the Math ICS scraper"""
    print("\n🔢 TESTING MATH ICS SCRAPER")
    print("=" * 50)
    
    try:
        from math_ics_scraper import MathICSScraper
        scraper = MathICSScraper()
        events = scraper.scrape_math_events()
        
        print(f"✅ Math: {len(events)} events found")
        if events:
            print("Sample events:")
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.get('title', 'No title')}: {event.get('start_date', 'No date')} {event.get('time', 'No time')}")
        
        return events
    except Exception as e:
        print(f"❌ Math scraper failed: {e}")
        return []

def test_orfe_scraper():
    """Test the ORFE Drupal scraper"""
    print("\n📊 TESTING ORFE DRUPAL SCRAPER")
    print("=" * 50)
    
    try:
        from universal_drupal_cloudscraper import UniversalDrupalCloudScraper
        scraper = UniversalDrupalCloudScraper(
            'ORFE', 
            'https://orfe.princeton.edu', 
            'https://orfe.princeton.edu/events', 
            'sciences_engineering'
        )
        events = scraper.scrape_events(max_pages=2)
        
        print(f"✅ ORFE: {len(events)} events found")
        if events:
            print("Sample events:")
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.get('title', 'No title')}: {event.get('start_date', 'No date')} {event.get('time', 'No time')}")
        
        return events
    except Exception as e:
        print(f"❌ ORFE scraper failed: {e}")
        return []

def test_all_individual_scrapers():
    """Test all individual scrapers"""
    print("🚀 TESTING ALL INDIVIDUAL SCRAPERS")
    print("=" * 80)
    
    results = {}
    total_events = 0
    
    # Test each scraper
    scrapers = [
        ("Physics", test_physics_scraper),
        ("Geosciences", test_geosciences_scraper),
        ("Philosophy", test_philosophy_scraper),
        ("Math", test_math_scraper),
        ("ORFE", test_orfe_scraper),
    ]
    
    for name, test_func in scrapers:
        try:
            events = test_func()
            results[name] = {
                'success': True,
                'event_count': len(events),
                'events': events[:2] if events else []  # Store first 2 events as sample
            }
            total_events += len(events)
        except Exception as e:
            results[name] = {
                'success': False,
                'error': str(e),
                'event_count': 0
            }
    
    # Summary
    print(f"\n{'='*20} SUMMARY {'='*20}")
    successful = [name for name, result in results.items() if result['success']]
    failed = [name for name, result in results.items() if not result['success']]
    
    print(f"✅ Successful scrapers: {len(successful)}")
    print(f"❌ Failed scrapers: {len(failed)}")
    print(f"📊 Total events collected: {total_events}")
    
    if successful:
        print(f"\n✅ Working scrapers:")
        for name in successful:
            event_count = results[name]['event_count']
            print(f"   - {name}: {event_count} events")
    
    if failed:
        print(f"\n❌ Failed scrapers:")
        for name in failed:
            error = results[name]['error']
            print(f"   - {name}: {error}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scraper_name = sys.argv[1].lower()
        
        if scraper_name == "physics":
            test_physics_scraper()
        elif scraper_name == "geosciences":
            test_geosciences_scraper()
        elif scraper_name == "philosophy":
            test_philosophy_scraper()
        elif scraper_name == "math":
            test_math_scraper()
        elif scraper_name == "orfe":
            test_orfe_scraper()
        elif scraper_name == "all":
            test_all_individual_scrapers()
        else:
            print(f"Unknown scraper: {scraper_name}")
            print("Available scrapers: physics, geosciences, philosophy, math, orfe, all")
    else:
        # Default: test all scrapers
        test_all_individual_scrapers()

