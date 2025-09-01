#!/usr/bin/env python3
import json
import importlib
from datetime import datetime
from typing import List, Dict, Any

# Updated list of all working scrapers
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
    ('hellenic_studies_cloudscraper', 'HellenicStudiesCloudScraper', 'scrape_hellenic_studies_events'),
    # Additional new scrapers
    ('astrophysical_sciences_cloudscraper', 'AstrophysicalSciencesCloudScraper', 'scrape_astrophysical_sciences_events')
]

def run_scraper(scraper_name: str, class_name: str, method_name: str) -> List[Dict[str, Any]]:
    """Run a single scraper and return its events"""
    try:
        print(f"🔍 Running {scraper_name}...")
        scraper_module = importlib.import_module(scraper_name)
        scraper_class = getattr(scraper_module, class_name)
        scraper = scraper_class()
        scrape_method = getattr(scraper, method_name)
        events = scrape_method()
        print(f"✅ {scraper_name}: {len(events)} events found")
        return events
    except Exception as e:
        print(f"❌ {scraper_name}: Error - {e}")
        return []

def combine_all_events():
    """Combine events from all working scrapers"""
    print("COMBINING ALL CLOUDSCRAPER EVENTS")
    print("=" * 60)
    
    all_events = []
    successful_scrapers = 0
    total_events = 0
    
    for scraper_name, class_name, method_name in WORKING_SCRAPERS:
        events = run_scraper(scraper_name, class_name, method_name)
        if events:
            all_events.extend(events)
            successful_scrapers += 1
            total_events += len(events)
    
    # Add metadata
    combined_data = {
        "metadata": {
            "total_events": len(all_events),
            "successful_scrapers": successful_scrapers,
            "total_scrapers": len(WORKING_SCRAPERS),
            "combined_at": datetime.now().isoformat(),
            "scrapers_used": [scraper[0] for scraper in WORKING_SCRAPERS[:successful_scrapers]]
        },
        "events": all_events
    }
    
    # Save combined data
    output_file = "all_princeton_academic_events.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print("\n📊 COMBINATION RESULTS")
    print("=" * 60)
    print(f"✅ Successful scrapers: {successful_scrapers}/{len(WORKING_SCRAPERS)}")
    print(f"📈 Total events: {total_events}")
    print(f"💾 Saved to: {output_file}")
    
    # Show breakdown by department
    department_counts = {}
    for event in all_events:
        dept = event.get('department', 'Unknown')
        department_counts[dept] = department_counts.get(dept, 0) + 1
    
    print("\n📋 EVENTS BY DEPARTMENT:")
    for dept, count in sorted(department_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dept}: {count} events")
    
    return combined_data

if __name__ == "__main__":
    combine_all_events()
