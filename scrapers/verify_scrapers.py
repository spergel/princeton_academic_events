#!/usr/bin/env python3
"""
Princeton Academic Events - Scraper Verification Script
Tests all working scrapers to ensure they're functioning correctly.
"""

import json
import importlib
import sys
from datetime import datetime

# List of working scrapers to test (with their actual class names and method names)
WORKING_SCRAPERS = [
    ('politics_cloudscraper', 'PoliticsCloudScraper', 'scrape_politics_events'),
    ('philosophy_cloudscraper', 'PhilosophyCloudScraper', 'scrape_events'),
    ('history_cloudscraper', 'HistoryCloudScraper', 'scrape_events'),
    ('english_cloudscraper', 'EnglishCloudScraper', 'scrape_events'),
    ('psychology_cloudscraper', 'PsychologyCloudScraper', 'scrape_psychology_events'),
    ('physics_cloudscraper', 'PhysicsCloudScraper', 'scrape_events'),
    ('classics_cloudscraper', 'ClassicsCloudScraper', 'scrape_classics_events'),
    ('geosciences_cloudscraper', 'GeosciencesCloudScraper', 'scrape_geosciences_events'),
    ('computer_science_cloudscraper', 'ComputerScienceCloudScraper', 'scrape_cs_events'),
    ('economics_cloudscraper', 'EconomicsCloudScraper', 'scrape_economics_events'),
    ('sociology_cloudscraper', 'SociologyCloudScraper', 'scrape_sociology_events'),
    # New scrapers
    ('molecular_biology_cloudscraper', 'MolecularBiologyCloudScraper', 'scrape_molecular_biology_events'),
    ('ecology_evolutionary_biology_cloudscraper', 'EcologyEvolutionaryBiologyCloudScraper', 'scrape_ecology_evolutionary_biology_events'),
    ('chemical_biological_engineering_cloudscraper', 'ChemicalBiologicalEngineeringCloudScraper', 'scrape_chemical_biological_engineering_events'),
    ('civil_environmental_engineering_cloudscraper', 'CivilEnvironmentalEngineeringCloudScraper', 'scrape_civil_environmental_engineering_events'),
    ('electrical_computer_engineering_cloudscraper', 'ElectricalComputerEngineeringCloudScraper', 'scrape_electrical_computer_engineering_events'),
    ('operations_research_financial_engineering_cloudscraper', 'OperationsResearchFinancialEngineeringCloudScraper', 'scrape_operations_research_financial_engineering_events'),
    ('anthropology_cloudscraper', 'AnthropologyCloudScraper', 'scrape_anthropology_events'),
    ('public_international_affairs_cloudscraper', 'PublicInternationalAffairsCloudScraper', 'scrape_public_international_affairs_events'),
    # Additional new scrapers
    ('mathematics_cloudscraper', 'MathematicsCloudScraper', 'scrape_mathematics_events'),
    ('music_cloudscraper', 'MusicCloudScraper', 'scrape_music_events'),
    ('art_archaeology_cloudscraper', 'ArtArchaeologyCloudScraper', 'scrape_art_archaeology_events'),
    ('religion_cloudscraper', 'ReligionCloudScraper', 'scrape_religion_events'),
    # Additional new scrapers
    ('comparative_literature_cloudscraper', 'ComparativeLiteratureCloudScraper', 'scrape_comparative_literature_events'),
    ('citp_cloudscraper', 'CITPCloudScraper', 'scrape_citp_events'),
    ('pacm_cloudscraper', 'PACMCloudScraper', 'scrape_pacm_events'),
    # Additional new scrapers
    ('environmental_studies_cloudscraper', 'EnvironmentalStudiesCloudScraper', 'scrape_environmental_studies_events'),
    ('latin_american_studies_cloudscraper', 'LatinAmericanStudiesCloudScraper', 'scrape_latin_american_studies_events'),
    ('gender_sexuality_studies_cloudscraper', 'GenderSexualityStudiesCloudScraper', 'scrape_gender_sexuality_studies_events'),
    # Additional new scrapers
    ('african_studies_cloudscraper', 'AfricanStudiesCloudScraper', 'scrape_african_studies_events'),
    ('near_eastern_studies_cloudscraper', 'NearEasternStudiesCloudScraper', 'scrape_near_eastern_studies_events'),
    ('russian_east_european_eurasian_studies_cloudscraper', 'RussianEastEuropeanEurasianStudiesCloudScraper', 'scrape_russian_east_european_eurasian_studies_events'),
    # Additional new scrapers
    ('east_asian_studies_cloudscraper', 'EastAsianStudiesCloudScraper', 'scrape_east_asian_studies_events'),
    ('south_asian_studies_cloudscraper', 'SouthAsianStudiesCloudScraper', 'scrape_south_asian_studies_events'),
    ('hellenic_studies_cloudscraper', 'HellenicStudiesCloudScraper', 'scrape_hellenic_studies_events')
]

def test_scraper(scraper_name, class_name, method_name):
    """Test a single scraper and return results"""
    try:
        # Import the scraper module
        scraper_module = importlib.import_module(scraper_name)
        
        # Get the scraper class
        scraper_class = getattr(scraper_module, class_name)
        
        # Create scraper instance
        scraper = scraper_class()
        
        # Get the scraping method
        scrape_method = getattr(scraper, method_name)
        
        # Test scraping
        print(f"🔍 Testing {scraper_name}...")
        events = scrape_method()
        
        if events:
            print(f"✅ {scraper_name}: {len(events)} events found")
            return {
                'scraper': scraper_name,
                'status': 'success',
                'event_count': len(events),
                'sample_event': events[0] if events else None
            }
        else:
            print(f"⚠️  {scraper_name}: No events found")
            return {
                'scraper': scraper_name,
                'status': 'no_events',
                'event_count': 0,
                'sample_event': None
            }
            
    except Exception as e:
        print(f"❌ {scraper_name}: Error - {str(e)}")
        return {
            'scraper': scraper_name,
            'status': 'error',
            'error': str(e),
            'event_count': 0,
            'sample_event': None
        }

def main():
    """Main verification function"""
    print("🔍 PRINCETON ACADEMIC EVENTS - SCRAPER VERIFICATION")
    print("=" * 60)
    print(f"Testing {len(WORKING_SCRAPERS)} working scrapers...")
    print()
    
    results = []
    total_events = 0
    successful_scrapers = 0
    
    for scraper_name, class_name, method_name in WORKING_SCRAPERS:
        result = test_scraper(scraper_name, class_name, method_name)
        results.append(result)
        
        if result['status'] == 'success':
            successful_scrapers += 1
            total_events += result['event_count']
    
    print()
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Total scrapers tested: {len(WORKING_SCRAPERS)}")
    print(f"Successful scrapers: {successful_scrapers}")
    print(f"Total events found: {total_events}")
    print()
    
    # Summary by status
    success_count = len([r for r in results if r['status'] == 'success'])
    no_events_count = len([r for r in results if r['status'] == 'no_events'])
    error_count = len([r for r in results if r['status'] == 'error'])
    
    print("📈 STATUS BREAKDOWN:")
    print(f"✅ Working: {success_count}")
    print(f"⚠️  No events: {no_events_count}")
    print(f"❌ Errors: {error_count}")
    print()
    
    # Show errors if any
    errors = [r for r in results if r['status'] == 'error']
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error['scraper']}: {error['error']}")
        print()
    
    # Show scrapers with no events
    no_events = [r for r in results if r['status'] == 'no_events']
    if no_events:
        print("⚠️  SCRAPERS WITH NO EVENTS:")
        for scraper in no_events:
            print(f"  - {scraper['scraper']}")
        print()
    
    # Show successful scrapers
    successful = [r for r in results if r['status'] == 'success']
    if successful:
        print("✅ WORKING SCRAPERS:")
        for scraper in successful:
            print(f"  - {scraper['scraper']}: {scraper['event_count']} events")
        print()
    
    # Save results
    verification_results = {
        'timestamp': datetime.now().isoformat(),
        'total_scrapers': len(WORKING_SCRAPERS),
        'successful_scrapers': successful_scrapers,
        'total_events': total_events,
        'results': results
    }
    
    with open('scraper_verification_results.json', 'w') as f:
        json.dump(verification_results, f, indent=2)
    
    print(f"📄 Results saved to: scraper_verification_results.json")
    
    # Overall status
    if error_count == 0 and no_events_count == 0:
        print("🎉 ALL SCRAPERS WORKING PERFECTLY!")
        return True
    elif error_count == 0:
        print("✅ All scrapers functional (some may have no current events)")
        return True
    else:
        print("⚠️  Some scrapers have issues - check errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
