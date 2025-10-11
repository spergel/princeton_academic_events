#!/usr/bin/env python3
"""
Test script to run the universal Drupal scraper on all configured departments
"""

from universal_drupal_cloudscraper import UniversalDrupalCloudScraper, DEPARTMENT_CONFIGS
import json
from datetime import datetime

def test_all_drupal_departments(max_pages: int = 3, fetch_details: bool = False):
    """Test the universal scraper on all configured departments"""
    print("🚀 TESTING UNIVERSAL DRUPAL SCRAPER ON ALL DEPARTMENTS")
    print("=" * 80)
    
    results = {}
    total_events = 0
    
    for dept_key, config in DEPARTMENT_CONFIGS.items():
        print(f"\n{'='*20} TESTING {config['name'].upper()} {'='*20}")
        
        try:
            scraper = UniversalDrupalCloudScraper(
                department_name=config['name'],
                base_url=config['base_url'],
                events_url=config['events_url'],
                meta_category=config['meta_category']
            )
            
            events = scraper.scrape_events(max_pages=max_pages, fetch_details=fetch_details)
            
            results[dept_key] = {
                'department': config['name'],
                'success': True,
                'event_count': len(events),
                'events': events[:3] if events else [],  # Store first 3 events as sample
                'meta_category': config['meta_category']
            }
            
            total_events += len(events)
            print(f"✅ {config['name']}: {len(events)} events")
            
        except Exception as e:
            results[dept_key] = {
                'department': config['name'],
                'success': False,
                'error': str(e),
                'event_count': 0,
                'meta_category': config['meta_category']
            }
            print(f"❌ {config['name']}: {e}")
    
    # Generate summary report
    print(f"\n{'='*20} SUMMARY REPORT {'='*20}")
    successful_departments = [k for k, v in results.items() if v['success']]
    failed_departments = [k for k, v in results.items() if not v['success']]
    
    print(f"✅ Successful departments: {len(successful_departments)}")
    print(f"❌ Failed departments: {len(failed_departments)}")
    print(f"📊 Total events collected: {total_events}")
    
    if successful_departments:
        print(f"\n✅ Working departments:")
        for dept in successful_departments:
            config = DEPARTMENT_CONFIGS[dept]
            event_count = results[dept]['event_count']
            print(f"   - {config['name']}: {event_count} events")
    
    if failed_departments:
        print(f"\n❌ Failed departments:")
        for dept in failed_departments:
            config = DEPARTMENT_CONFIGS[dept]
            error = results[dept]['error']
            print(f"   - {config['name']}: {error}")
    
    # Save results to file
    output_file = f"universal_drupal_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_summary': {
                'total_departments': len(DEPARTMENT_CONFIGS),
                'successful_departments': len(successful_departments),
                'failed_departments': len(failed_departments),
                'total_events': total_events,
                'test_timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return results

def test_specific_departments(department_keys: list, max_pages: int = 3, fetch_details: bool = False):
    """Test specific departments only"""
    print(f"🎯 TESTING SPECIFIC DEPARTMENTS: {', '.join(department_keys)}")
    print("=" * 80)
    
    results = {}
    total_events = 0
    
    for dept_key in department_keys:
        if dept_key not in DEPARTMENT_CONFIGS:
            print(f"❌ Department '{dept_key}' not found in configurations")
            continue
        
        config = DEPARTMENT_CONFIGS[dept_key]
        print(f"\n{'='*20} TESTING {config['name'].upper()} {'='*20}")
        
        try:
            scraper = UniversalDrupalCloudScraper(
                department_name=config['name'],
                base_url=config['base_url'],
                events_url=config['events_url'],
                meta_category=config['meta_category']
            )
            
            events = scraper.scrape_events(max_pages=max_pages, fetch_details=fetch_details)
            
            results[dept_key] = {
                'department': config['name'],
                'success': True,
                'event_count': len(events),
                'events': events[:3] if events else [],  # Store first 3 events as sample
                'meta_category': config['meta_category']
            }
            
            total_events += len(events)
            print(f"✅ {config['name']}: {len(events)} events")
            
        except Exception as e:
            results[dept_key] = {
                'department': config['name'],
                'success': False,
                'error': str(e),
                'event_count': 0,
                'meta_category': config['meta_category']
            }
            print(f"❌ {config['name']}: {e}")
    
    print(f"\n📊 Total events collected: {total_events}")
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # Test all departments
            test_all_drupal_departments()
        else:
            # Test specific departments
            departments = sys.argv[1:]
            test_specific_departments(departments)
    else:
        # Default: test a few key departments
        test_departments = ['sociology', 'african_studies', 'cbe', 'orfe', 'ece']
        test_specific_departments(test_departments)
