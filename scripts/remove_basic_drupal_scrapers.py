#!/usr/bin/env python3
"""
Remove basic Drupal scrapers that can be replaced by the universal Drupal scraper.
This script identifies and removes individual Drupal scrapers that use the standard
content-list-item structure, as they can all be handled by the universal scraper.
"""

import os
import shutil
from pathlib import Path

def identify_basic_drupal_scrapers():
    """Identify which scrapers are basic Drupal scrapers"""
    basic_drupal_scrapers = [
        # These all use content-list-item structure and can be replaced by universal scraper
        "history_cloudscraper.py",
        "classics_cloudscraper.py", 
        "english_cloudscraper.py",
        "art_archaeology_cloudscraper.py",
        "comparative_literature_cloudscraper.py",
        "near_eastern_studies_cloudscraper.py",
        "east_asian_studies_cloudscraper.py",
        "french_italian_cloudscraper.py",
        "neuroscience_cloudscraper.py"
    ]
    
    return basic_drupal_scrapers

def get_department_configs_for_removed_scrapers():
    """Get the department configurations for the scrapers we're removing"""
    configs = {
        'history': {
            'name': 'History',
            'base_url': 'https://history.princeton.edu',
            'events_url': 'https://history.princeton.edu/graduate/phd-history-science/events',
            'meta_category': 'arts_humanities'
        },
        'classics': {
            'name': 'Classics',
            'base_url': 'https://classics.princeton.edu',
            'events_url': 'https://classics.princeton.edu/events',
            'meta_category': 'arts_humanities'
        },
        'english': {
            'name': 'English',
            'base_url': 'https://english.princeton.edu',
            'events_url': 'https://english.princeton.edu/events',
            'meta_category': 'arts_humanities'
        },
        'art_archaeology': {
            'name': 'Art and Archaeology',
            'base_url': 'https://artandarchaeology.princeton.edu',
            'events_url': 'https://artandarchaeology.princeton.edu/events',
            'meta_category': 'arts_humanities'
        },
        'comparative_literature': {
            'name': 'Comparative Literature',
            'base_url': 'https://complit.princeton.edu',
            'events_url': 'https://complit.princeton.edu/events',
            'meta_category': 'arts_humanities'
        },
        'near_eastern_studies': {
            'name': 'Near Eastern Studies',
            'base_url': 'https://nes.princeton.edu',
            'events_url': 'https://nes.princeton.edu/events',
            'meta_category': 'area_studies'
        },
        'east_asian_studies': {
            'name': 'East Asian Studies',
            'base_url': 'https://eas.princeton.edu',
            'events_url': 'https://eas.princeton.edu/events',
            'meta_category': 'area_studies'
        },
        'french_italian': {
            'name': 'French & Italian',
            'base_url': 'https://frit.princeton.edu',
            'events_url': 'https://frit.princeton.edu/events',
            'meta_category': 'arts_humanities'
        },
        'neuroscience': {
            'name': 'Princeton Neuroscience Institute',
            'base_url': 'https://pni.princeton.edu',
            'events_url': 'https://pni.princeton.edu/events',
            'meta_category': 'sciences_engineering'
        }
    }
    
    return configs

def update_universal_scraper_configs():
    """Update the universal scraper to include the departments from removed scrapers"""
    universal_scraper_path = "scrapers/universal_drupal_cloudscraper.py"
    
    if not os.path.exists(universal_scraper_path):
        print(f"❌ Universal scraper not found at {universal_scraper_path}")
        return False
    
    # Read the current universal scraper
    with open(universal_scraper_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the DEPARTMENT_CONFIGS section and add the new departments
    new_configs = get_department_configs_for_removed_scrapers()
    
    # Create the new config entries
    new_config_entries = []
    for key, config in new_configs.items():
        entry = f"""    '{key}': {{
        'name': '{config['name']}',
        'base_url': '{config['base_url']}',
        'events_url': '{config['events_url']}',
        'meta_category': '{config['meta_category']}'
    }},"""
        new_config_entries.append(entry)
    
    # Find where to insert the new configs (after the existing ones)
    if "DEPARTMENT_CONFIGS = {" in content:
        # Find the end of the existing configs
        start_marker = "DEPARTMENT_CONFIGS = {"
        end_marker = "}"
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find the matching closing brace
            brace_count = 0
            end_idx = start_idx
            for i, char in enumerate(content[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            # Insert new configs before the closing brace
            new_content = (
                content[:end_idx] + 
                ",\n" + "\n".join(new_config_entries) + "\n" +
                content[end_idx:]
            )
            
            # Write the updated file
            with open(universal_scraper_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated universal scraper with {len(new_configs)} new department configs")
            return True
    
    print("❌ Could not find DEPARTMENT_CONFIGS section in universal scraper")
    return False

def remove_basic_drupal_scrapers():
    """Remove the basic Drupal scrapers"""
    print("🗑️  REMOVING BASIC DRUPAL SCRAPERS")
    print("=" * 50)
    
    scrapers_to_remove = identify_basic_drupal_scrapers()
    scrapers_dir = "scrapers"
    
    removed_count = 0
    for scraper_file in scrapers_to_remove:
        file_path = Path(scrapers_dir) / scraper_file
        if file_path.exists():
            print(f"🗑️  Removing: {scraper_file}")
            file_path.unlink()
            removed_count += 1
        else:
            print(f"⚠️  File not found: {scraper_file}")
    
    print(f"\n📊 Removed {removed_count} basic Drupal scrapers")
    return removed_count

def main():
    """Main cleanup function"""
    print("🧹 REMOVING BASIC DRUPAL SCRAPERS")
    print("=" * 60)
    print("This script will:")
    print("1. Remove individual Drupal scrapers that use content-list-item structure")
    print("2. Update the universal Drupal scraper with the removed departments")
    print("3. Keep specialized scrapers (ICS, TEC, custom HTML)")
    print("=" * 60)
    
    # Step 1: Remove basic Drupal scrapers
    removed_count = remove_basic_drupal_scrapers()
    
    # Step 2: Update universal scraper
    if removed_count > 0:
        print(f"\n🔄 UPDATING UNIVERSAL SCRAPER")
        print("=" * 50)
        update_success = update_universal_scraper_configs()
        
        if update_success:
            print(f"\n🎉 CLEANUP COMPLETE!")
            print(f"   Removed {removed_count} basic Drupal scrapers")
            print(f"   Updated universal scraper with new departments")
            print(f"   💡 The universal scraper can now handle all Drupal sites!")
        else:
            print(f"\n⚠️  Cleanup partially complete")
            print(f"   Removed {removed_count} scrapers but failed to update universal scraper")
    else:
        print(f"\n✅ No basic Drupal scrapers found to remove")

if __name__ == "__main__":
    main()
