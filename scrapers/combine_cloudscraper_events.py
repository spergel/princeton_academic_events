#!/usr/bin/env python3
import json
import importlib
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from universal_drupal_cloudscraper import UniversalDrupalCloudScraper
from universal_ics_scraper import scrape_all_ics_departments

# Check if browser scraper is available
BROWSER_SCRAPER_AVAILABLE = False
try:
    from browser_scraper import run_browser_scraper, BROWSER_DEPARTMENTS
    BROWSER_SCRAPER_AVAILABLE = True
except ImportError:
    print("NOTE: Browser scraper not available (playwright not installed)")

# Working individual scrapers (these have their own modules)
INDIVIDUAL_SCRAPERS = [
    ('math_ics_scraper', 'MathICSScraper', 'scrape_math_events'),
    ('philosophy_ics_scraper', 'PhilosophyICSScraper', 'scrape_philosophy_events'),
    ('physics_cloudscraper', 'PhysicsCloudScraper', 'scrape_physics_events'),
    ('geosciences_json_scraper', 'GeosciencesJSONScraper', 'scrape_geosciences_events'),
    ('cs_cloudscraper', 'CSCloudScraper', 'scrape_cs_events'),
    ('economics_cloudscraper_new', 'EconomicsCloudScraperNew', 'scrape_economics_events'),
    ('spia_cloudscraper_new', 'SPIACloudScraperNew', 'scrape_spia_events'),
]

# Departments to scrape with universal Drupal scraper
UNIVERSAL_DRUPAL_DEPARTMENTS = [
    ('politics', 'https://politics.princeton.edu', 'https://politics.princeton.edu/events', 'social_sciences'),
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
        # Increased max_pages to 10 to get more events, fetch_details=True for full info
        events = scraper.scrape_events(max_pages=10, fetch_details=True)
        print(f"SUCCESS: {dept_name}: {len(events)} events found")
        return events
    except Exception as e:
        print(f"ERROR: {dept_name}: {e}")
        import traceback
        traceback.print_exc()
        return []

def combine_all_events(use_browser: bool = True):
    """Combine events from all working scrapers"""
    print("COMBINING ALL PRINCETON ACADEMIC EVENTS")
    print("=" * 60)

    all_events = []
    successful_scrapers = 0
    total_events = 0
    browser_events = 0

    # Run universal ICS scraper for all departments with ICS feeds
    print("\n--- UNIVERSAL ICS SCRAPER (25 departments) ---")
    try:
        ics_events = scrape_all_ics_departments()
        if ics_events:
            all_events.extend(ics_events)
            successful_scrapers += 1
            total_events += len(ics_events)
            print(f"SUCCESS: ICS scraper: {len(ics_events)} events from {len(set(e['department'] for e in ics_events))} departments")
    except Exception as e:
        print(f"ERROR: ICS scraper: {e}")

    # Run individual scrapers
    print("\n--- INDIVIDUAL SCRAPERS ---")
    for scraper_name, class_name, method_name in INDIVIDUAL_SCRAPERS:
        events = run_individual_scraper(scraper_name, class_name, method_name)
        if events:
            all_events.extend(events)
            successful_scrapers += 1
            total_events += len(events)

    # Run universal Drupal scraper for non-Cloudflare departments
    print("\n--- UNIVERSAL DRUPAL SCRAPER ---")
    for dept_name, base_url, events_url, meta_category in UNIVERSAL_DRUPAL_DEPARTMENTS:
        events = run_universal_drupal_scraper(dept_name, base_url, events_url, meta_category)
        if events:
            all_events.extend(events)
            successful_scrapers += 1
            total_events += len(events)

    # Run browser scraper for Cloudflare-protected departments
    if use_browser and BROWSER_SCRAPER_AVAILABLE:
        print("\n--- BROWSER SCRAPER (Cloudflare bypass) ---")
        try:
            browser_scraped = run_browser_scraper(headless=True)
            if browser_scraped:
                all_events.extend(browser_scraped)
                browser_events = len(browser_scraped)
                total_events += browser_events
                # Count successful browser departments
                browser_depts = set(e.get('department', '') for e in browser_scraped)
                successful_scrapers += len(browser_depts)
                print(f"SUCCESS: Browser scraper found {browser_events} events from {len(browser_depts)} departments")
        except Exception as e:
            print(f"ERROR: Browser scraper failed: {e}")
    elif use_browser and not BROWSER_SCRAPER_AVAILABLE:
        print("\nWARNING: Browser scraper requested but not available")
        print("Install with: pip install playwright && playwright install chromium")

    # Deduplicate across all sources
    seen_keys = set()
    deduped_events = []
    for event in all_events:
        key = f"{event.get('title', '').strip().lower()}|{event.get('start_date', '')}"
        if key not in seen_keys:
            seen_keys.add(key)
            deduped_events.append(event)
    all_events = deduped_events

    # Calculate totals
    total_scrapers = len(INDIVIDUAL_SCRAPERS) + len(UNIVERSAL_DRUPAL_DEPARTMENTS)
    if BROWSER_SCRAPER_AVAILABLE:
        total_scrapers += len(BROWSER_DEPARTMENTS)

    # Add metadata
    combined_data = {
        "metadata": {
            "total_events": len(all_events),
            "successful_scrapers": successful_scrapers,
            "total_scrapers": total_scrapers,
            "combined_at": datetime.now().isoformat(),
            "individual_scrapers_used": len(INDIVIDUAL_SCRAPERS),
            "universal_drupal_departments_used": len(UNIVERSAL_DRUPAL_DEPARTMENTS),
            "browser_scraped_events": browser_events
        },
        "events": all_events
    }

    # Save combined data
    output_file = "all_princeton_academic_events.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("COMBINATION RESULTS")
    print("=" * 60)
    print(f"Successful scrapers: {successful_scrapers}/{total_scrapers}")
    print(f"Total events (after dedup): {len(all_events)}")
    print(f"  - From individual/Drupal scrapers: {total_events - browser_events}")
    print(f"  - From browser scraper: {browser_events}")
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
    # Browser scraper disabled - ICS feeds cover all those departments
    combine_all_events(use_browser=False)
