#!/usr/bin/env python3
"""
Cleanup script to remove excess files accumulated during testing.
This script removes duplicate scrapers and old test files while keeping the essential ones.
"""

import os
import shutil
from pathlib import Path

def cleanup_scrapers_directory():
    """Clean up the scrapers directory by removing duplicate and test files"""
    print("🧹 CLEANING UP SCRAPERS DIRECTORY")
    print("=" * 50)
    
    scrapers_dir = "scrapers"
    
    # Files to keep (essential scrapers and documentation)
    keep_files = {
        # Documentation
        "SCRAPER_BEST_PRACTICES.md",
        "EVENTS_SOURCES_TODO.md",
        "CLEANUP_SUMMARY.md",
        
        # Universal scraper (our new consolidated approach)
        "universal_drupal_cloudscraper.py",
        "test_all_drupal_departments.py",
        
        # Essential individual scrapers (non-Drupal ones)
        "art_archaeology_cloudscraper.py",
        "classics_cloudscraper.py", 
        "comparative_literature_cloudscraper.py",
        "cs_cloudscraper.py",
        "english_cloudscraper.py",
        "geosciences_json_scraper.py",
        "history_cloudscraper.py",
        "math_ics_scraper.py",
        "medieval_studies_cloudscraper.py",
        "near_eastern_studies_cloudscraper.py",
        "neuroscience_cloudscraper.py",
        "philosophy_ics_scraper.py",
        "physics_cloudscraper.py",
        "physics_json_scraper.py",
        "politics_cloudscraper_new.py",
        "spia_cloudscraper_new.py",
        "economics_cloudscraper_new.py",
        "sociology_cloudscraper_new.py",
        "french_italian_cloudscraper.py",
        "east_asian_studies_cloudscraper.py",
        
        # Combined events file
        "all_princeton_academic_events.json",
        "combine_cloudscraper_events.py"
    }
    
    # Files to remove (duplicates, old versions, test files)
    remove_patterns = [
        # Duplicate Drupal scrapers (replaced by universal scraper)
        "*_cloudscraper.py",  # Individual Drupal scrapers
        "*_cloudscraper_events.json",  # Individual event files
        "*_universal_drupal_events.json",  # Test universal scraper outputs
        
        # Old/duplicate files
        "chemistry_cloudscraper.py",
        "chemistry_cloudscraper_events.json",
        "computer_science_events_cloudscraper.py",
        "computer_science_events_cloudscraper_events.json",
        "anthropology_cloudscraper.py",
        "anthropology_cloudscraper_events.json",
        "african_studies_cloudscraper.py",
        "african_studies_cloudscraper_events.json",
        "slavic_languages_cloudscraper.py",
        "slavic_languages_and_literatures_cloudscraper_events.json",
        "uchv_cloudscraper.py",
        "university_center_for_human_values_cloudscraper_events.json",
        "mathematics_machine_learning_cloudscraper.py",
        "mathematics_and_machine_learning_cloudscraper_events.json",
        "chemical_biological_engineering_cloudscraper.py",
        "chemical_and_biological_engineering_cloudscraper_events.json",
        "orfe_cloudscraper.py",
        "operations_research_and_financial_engineering_cloudscraper_events.json",
        "ece_cloudscraper.py",
        "electrical_and_computer_engineering_cloudscraper_events.json",
        "sociology_cloudscraper.py",
        "sociology_cloudscraper_events.json",
        "sociology_universal_drupal_events.json",
        "african_studies_universal_drupal_events.json",
        "chemical_and_biological_engineering_universal_drupal_events.json",
        
        # Archive directory (old scrapers)
        "archive_working_scrapers_20250903_100457"
    ]
    
    removed_count = 0
    kept_count = 0
    
    # Process all files in scrapers directory
    for file_path in Path(scrapers_dir).iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            # Check if we should keep this file
            if filename in keep_files:
                print(f"✅ Keeping: {filename}")
                kept_count += 1
            else:
                # Check if it matches any removal pattern
                should_remove = False
                for pattern in remove_patterns:
                    if pattern.startswith("*") and pattern.endswith("*"):
                        # Wildcard pattern
                        if pattern[1:-1] in filename:
                            should_remove = True
                            break
                    elif pattern == filename:
                        # Exact match
                        should_remove = True
                        break
                
                if should_remove:
                    print(f"🗑️  Removing: {filename}")
                    file_path.unlink()
                    removed_count += 1
                else:
                    print(f"❓ Unknown file: {filename} (keeping for safety)")
                    kept_count += 1
    
    # Remove archive directory if it exists
    archive_dir = Path(scrapers_dir) / "archive_working_scrapers_20250903_100457"
    if archive_dir.exists():
        print(f"🗑️  Removing archive directory: {archive_dir.name}")
        shutil.rmtree(archive_dir)
        removed_count += 1
    
    print(f"\n📊 CLEANUP SUMMARY")
    print(f"   Files kept: {kept_count}")
    print(f"   Files removed: {removed_count}")
    
    return removed_count

def cleanup_frontend_directory():
    """Clean up the frontend directory"""
    print("\n🧹 CLEANING UP FRONTEND DIRECTORY")
    print("=" * 50)
    
    frontend_dir = "frontend"
    
    # Remove old frontend if it exists
    old_frontend = "frontend-old"
    if Path(old_frontend).exists():
        print(f"🗑️  Removing old frontend: {old_frontend}")
        shutil.rmtree(old_frontend)
        return 1
    
    return 0

def cleanup_root_directory():
    """Clean up root directory"""
    print("\n🧹 CLEANING UP ROOT DIRECTORY")
    print("=" * 50)
    
    # Files to remove from root
    remove_files = [
        "all_princeton_academic_events.json",  # Moved to scrapers/
    ]
    
    removed_count = 0
    for filename in remove_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"🗑️  Removing: {filename}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def main():
    """Main cleanup function"""
    print("🧹 PRINCETON ACADEMIC EVENTS - CLEANUP")
    print("=" * 60)
    print("This script will remove excess files accumulated during testing:")
    print("- Duplicate Drupal scrapers (replaced by universal scraper)")
    print("- Old test event JSON files")
    print("- Archive directories")
    print("- Old frontend versions")
    print("=" * 60)
    
    total_removed = 0
    
    # Clean up each directory
    total_removed += cleanup_scrapers_directory()
    total_removed += cleanup_frontend_directory()
    total_removed += cleanup_root_directory()
    
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"   Total items removed: {total_removed}")
    print(f"   📁 Scrapers directory cleaned")
    print(f"   📁 Frontend directory cleaned")
    print(f"   📁 Root directory cleaned")
    print(f"\n💡 The universal Drupal scraper can now handle all Drupal-based departments!")

if __name__ == "__main__":
    main()
