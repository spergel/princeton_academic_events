#!/usr/bin/env python3
import json
import importlib
from datetime import datetime
from typing import List, Dict, Any
from universal_drupal_cloudscraper import UniversalDrupalCloudScraper

# Working individual scrapers (these have their own modules)
INDIVIDUAL_SCRAPERS = [
    ('math_ics_scraper', 'MathICSScraper', 'scrape_math_events'),
    ('philosophy_ics_scraper', 'PhilosophyICSScraper', 'scrape_philosophy_events'),
    ('physics_json_scraper', 'PhysicsJSONScraper', 'scrape_physics_events'),
    ('geosciences_json_scraper', 'GeosciencesJSONScraper', 'scrape_geosciences_events'),
    ('cs_cloudscraper', 'CSCloudScraper', 'scrape_cs_events'),
]

# Departments to scrape with universal Drupal scraper
UNIVERSAL_DRUPAL_DEPARTMENTS = [
    # Social Sciences
    ('sociology', 'https://sociology.princeton.edu', 'https://sociology.princeton.edu/events', 'social_sciences'),
    ('politics', 'https://politics.princeton.edu', 'https://politics.princeton.edu/events', 'social_sciences'),
    ('economics', 'https://economics.princeton.edu', 'https://economics.princeton.edu/events', 'social_sciences'),
    ('spia', 'https://spia.princeton.edu', 'https://spia.princeton.edu/events', 'social_sciences'),
    ('psychology', 'https://psychology.princeton.edu', 'https://psychology.princeton.edu/events', 'social_sciences'),
    ('anthropology', 'https://anthropology.princeton.edu', 'https://anthropology.princeton.edu/events', 'social_sciences'),
    
    # Humanities & Arts
    ('history', 'https://history.princeton.edu', 'https://history.princeton.edu/news-events/events', 'arts_humanities'),
    ('english', 'https://english.princeton.edu', 'https://english.princeton.edu/events', 'arts_humanities'),
    ('classics', 'https://classics.princeton.edu', 'https://classics.princeton.edu/events', 'arts_humanities'),
    ('comparative_literature', 'https://complit.princeton.edu', 'https://complit.princeton.edu/events', 'arts_humanities'),
    ('music', 'https://music.princeton.edu', 'https://music.princeton.edu/events', 'arts_humanities'),
    ('art_archaeology', 'https://artandarchaeology.princeton.edu', 'https://artandarchaeology.princeton.edu/events', 'arts_humanities'),
    ('religion', 'https://religion.princeton.edu', 'https://religion.princeton.edu/events', 'arts_humanities'),
    ('slavic_languages', 'https://slavic.princeton.edu', 'https://slavic.princeton.edu/events', 'arts_humanities'),
    ('french_italian', 'https://frit.princeton.edu', 'https://frit.princeton.edu/events', 'arts_humanities'),
    ('gender_sexuality_studies', 'https://gss.princeton.edu', 'https://gss.princeton.edu/events', 'arts_humanities'),
    ('humanities_council', 'https://humanities.princeton.edu', 'https://humanities.princeton.edu/events', 'arts_humanities'),
    ('medieval_studies', 'https://medieval.princeton.edu', 'https://medieval.princeton.edu/events', 'arts_humanities'),
    
    # Area Studies
    ('african_studies', 'https://africanstudies.princeton.edu', 'https://africanstudies.princeton.edu/events', 'area_studies'),
    ('east_asian_studies', 'https://eastasianstudies.princeton.edu', 'https://eastasianstudies.princeton.edu/events', 'area_studies'),
    ('south_asian_studies', 'https://southasianstudies.princeton.edu', 'https://southasianstudies.princeton.edu/events', 'area_studies'),
    ('near_eastern_studies', 'https://nes.princeton.edu', 'https://nes.princeton.edu/events', 'area_studies'),
    ('latin_american_studies', 'https://plas.princeton.edu', 'https://plas.princeton.edu/events', 'area_studies'),
    ('russian_east_european_eurasian_studies', 'https://rees.princeton.edu', 'https://rees.princeton.edu/events', 'area_studies'),
    ('hellenic_studies', 'https://hellenic.princeton.edu', 'https://hellenic.princeton.edu/events', 'area_studies'),
    
    # Sciences & Engineering
    ('cbe', 'https://cbe.princeton.edu', 'https://cbe.princeton.edu/events', 'sciences_engineering'),
    ('orfe', 'https://orfe.princeton.edu', 'https://orfe.princeton.edu/events', 'sciences_engineering'),
    ('ece', 'https://ece.princeton.edu', 'https://ece.princeton.edu/events', 'sciences_engineering'),
    ('astrophysical_sciences', 'https://astro.princeton.edu', 'https://astro.princeton.edu/events', 'sciences_engineering'),
    ('molecular_biology', 'https://molbio.princeton.edu', 'https://molbio.princeton.edu/events', 'sciences_engineering'),
    ('ecology_evolutionary_biology', 'https://eeb.princeton.edu', 'https://eeb.princeton.edu/events', 'sciences_engineering'),
    ('civil_environmental_engineering', 'https://cee.princeton.edu', 'https://cee.princeton.edu/events', 'sciences_engineering'),
    ('mechanical_aerospace_engineering', 'https://mae.princeton.edu', 'https://mae.princeton.edu/events', 'sciences_engineering'),
    
    # Other Programs
    ('citp', 'https://citp.princeton.edu', 'https://citp.princeton.edu/events', 'interdisciplinary'),
    ('pacm', 'https://pacm.princeton.edu', 'https://pacm.princeton.edu/events', 'sciences_engineering'),
    ('environmental_studies', 'https://environment.princeton.edu', 'https://environment.princeton.edu/events', 'interdisciplinary'),
]

def run_individual_scraper(scraper_name: str, class_name: str, method_name: str) -> List[Dict[str, Any]]:
    """Run a single individual scraper and return its events"""
    try:
        print(f"Running {scraper_name}...")
        scraper_module = importlib.import_module(scraper_name)
        scraper_class = getattr(scraper_module, class_name)
        scraper = scraper_class()
        scrape_method = getattr(scraper, method_name)
        events = scrape_method()
        print(f"SUCCESS: {scraper_name}: {len(events)} events found")
        return events
    except Exception as e:
        print(f"ERROR: {scraper_name}: {e}")
        return []

def run_universal_drupal_scraper(dept_name: str, base_url: str, events_url: str, meta_category: str) -> List[Dict[str, Any]]:
    """Run the universal Drupal scraper for a department"""
    try:
        print(f"Running universal Drupal scraper for {dept_name}...")
        scraper = UniversalDrupalCloudScraper(dept_name, base_url, events_url, meta_category)
        events = scraper.scrape_events(max_pages=5, fetch_details=True)
        print(f"SUCCESS: {dept_name}: {len(events)} events found")
        return events
    except Exception as e:
        print(f"ERROR: {dept_name}: {e}")
        return []

def combine_all_events():
    """Combine events from all working scrapers"""
    print("COMBINING ALL CLOUDSCRAPER EVENTS")
    print("=" * 60)
    
    all_events = []
    successful_scrapers = 0
    total_events = 0
    
    # Run individual scrapers
    for scraper_name, class_name, method_name in INDIVIDUAL_SCRAPERS:
        events = run_individual_scraper(scraper_name, class_name, method_name)
        if events:
            all_events.extend(events)
            successful_scrapers += 1
            total_events += len(events)
    
    # Run universal Drupal scraper for multiple departments
    for dept_name, base_url, events_url, meta_category in UNIVERSAL_DRUPAL_DEPARTMENTS:
        events = run_universal_drupal_scraper(dept_name, base_url, events_url, meta_category)
        if events:
            all_events.extend(events)
            successful_scrapers += 1
            total_events += len(events)
    
    # Add metadata
    total_scrapers = len(INDIVIDUAL_SCRAPERS) + len(UNIVERSAL_DRUPAL_DEPARTMENTS)
    combined_data = {
        "metadata": {
            "total_events": len(all_events),
            "successful_scrapers": successful_scrapers,
            "total_scrapers": total_scrapers,
            "combined_at": datetime.now().isoformat(),
            "individual_scrapers_used": len(INDIVIDUAL_SCRAPERS),
            "universal_drupal_departments_used": len(UNIVERSAL_DRUPAL_DEPARTMENTS)
        },
        "events": all_events
    }
    
    # Save combined data
    output_file = "all_princeton_academic_events.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print("\nCOMBINATION RESULTS")
    print("=" * 60)
    print(f"SUCCESS: Successful scrapers: {successful_scrapers}/{total_scrapers}")
    print(f"Total events: {total_events}")
    print(f"Saved to: {output_file}")
    
    # Show breakdown by department
    department_counts = {}
    for event in all_events:
        dept = event.get('department', 'Unknown')
        department_counts[dept] = department_counts.get(dept, 0) + 1
    
    print("\nEVENTS BY DEPARTMENT:")
    for dept, count in sorted(department_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dept}: {count} events")
    
    return combined_data

if __name__ == "__main__":
    combine_all_events()
