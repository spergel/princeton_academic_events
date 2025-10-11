#!/usr/bin/env python3
"""
Aggregate all department event JSON files into static data files for the frontend.
This script combines all individual scraper outputs into consolidated JSON files.
"""

import json
import os
import glob
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

def load_events_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load events from a single JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'events' in data:
                return data['events']
            elif isinstance(data, list):
                return data
            else:
                print(f"⚠️  Unexpected format in {file_path}")
                return []
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return []

def aggregate_all_events(scrapers_dir: str = "scrapers") -> Dict[str, Any]:
    """Aggregate all events from all scraper output files"""
    print("🔄 AGGREGATING ALL EVENTS")
    print("=" * 50)
    
    all_events = []
    department_stats = {}
    total_files = 0
    successful_files = 0
    
    # Find all JSON files in the scrapers directory
    json_files = glob.glob(os.path.join(scrapers_dir, "*_events.json"))
    json_files.extend(glob.glob(os.path.join(scrapers_dir, "*_cloudscraper_events.json")))
    json_files.extend(glob.glob(os.path.join(scrapers_dir, "*_universal_drupal_events.json")))
    
    print(f"📁 Found {len(json_files)} event files")
    
    for file_path in json_files:
        total_files += 1
        filename = os.path.basename(file_path)
        print(f"📄 Processing: {filename}")
        
        events = load_events_from_file(file_path)
        if events:
            successful_files += 1
            all_events.extend(events)
            
            # Track department statistics
            for event in events:
                dept = event.get('department', 'Unknown')
                if dept not in department_stats:
                    department_stats[dept] = {
                        'name': dept,
                        'meta_category': event.get('meta_category', 'other'),
                        'event_count': 0,
                        'is_selected': False
                    }
                department_stats[dept]['event_count'] += 1
            
            print(f"    ✅ {len(events)} events from {filename}")
        else:
            print(f"    ⚠️  No events found in {filename}")
    
    # Remove duplicates based on title, date, and time
    unique_events = deduplicate_events(all_events)
    
    print(f"\n📊 AGGREGATION SUMMARY")
    print(f"   Total files processed: {total_files}")
    print(f"   Successful files: {successful_files}")
    print(f"   Total events found: {len(all_events)}")
    print(f"   Unique events after deduplication: {len(unique_events)}")
    print(f"   Departments represented: {len(department_stats)}")
    
    return {
        'events': unique_events,
        'departments': list(department_stats.values()),
        'metadata': {
            'total_events': len(unique_events),
            'total_departments': len(department_stats),
            'files_processed': total_files,
            'successful_files': successful_files,
            'aggregated_at': datetime.now().isoformat(),
            'deduplication_removed': len(all_events) - len(unique_events)
        }
    }

def deduplicate_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate events based on title, date, and time"""
    seen = set()
    unique_events = []
    
    for event in events:
        # Create a key for deduplication
        key = f"{event.get('title', '')}_{event.get('start_date', '')}_{event.get('time', '')}"
        
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    return unique_events

def create_departments_file(departments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create departments metadata file"""
    # Sort departments by meta category and name
    meta_categories = {
        'arts_humanities': 'Arts & Humanities',
        'social_sciences': 'Social Sciences', 
        'sciences_engineering': 'Sciences & Engineering',
        'area_studies': 'Area Studies',
        'interdisciplinary': 'Interdisciplinary'
    }
    
    # Group departments by meta category
    departments_by_category = {}
    for dept in departments:
        category = dept.get('meta_category', 'other')
        if category not in departments_by_category:
            departments_by_category[category] = []
        departments_by_category[category].append(dept)
    
    # Sort departments within each category
    for category in departments_by_category:
        departments_by_category[category].sort(key=lambda x: x['name'])
    
    return {
        'departments': departments,
        'departments_by_category': departments_by_category,
        'meta_categories': meta_categories,
        'total_departments': len(departments),
        'generated_at': datetime.now().isoformat()
    }

def create_meta_file(total_events: int, total_departments: int) -> Dict[str, Any]:
    """Create site metadata file"""
    return {
        'site_info': {
            'name': 'Princeton Academic Events',
            'description': 'Academic events across Princeton University',
            'version': '1.0.0'
        },
        'stats': {
            'total_events': total_events,
            'total_departments': total_departments,
            'last_updated': datetime.now().isoformat()
        },
        'build_info': {
            'build_date': datetime.now().isoformat(),
            'data_source': 'Princeton University Department Websites',
            'update_frequency': 'Weekly'
        }
    }

def save_json_file(data: Dict[str, Any], file_path: str):
    """Save data to JSON file with proper formatting"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved: {file_path}")

def main():
    """Main aggregation function"""
    print("🚀 PRINCETON ACADEMIC EVENTS - DATA AGGREGATION")
    print("=" * 60)
    
    # Aggregate all events
    aggregated_data = aggregate_all_events()
    
    # Create output directory
    output_dir = "frontend/public/data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save consolidated events file
    events_data = {
        'events': aggregated_data['events'],
        'metadata': aggregated_data['metadata']
    }
    save_json_file(events_data, os.path.join(output_dir, "events.json"))
    
    # Save departments file
    departments_data = create_departments_file(aggregated_data['departments'])
    save_json_file(departments_data, os.path.join(output_dir, "departments.json"))
    
    # Save metadata file
    meta_data = create_meta_file(
        aggregated_data['metadata']['total_events'],
        aggregated_data['metadata']['total_departments']
    )
    save_json_file(meta_data, os.path.join(output_dir, "meta.json"))
    
    print(f"\n✅ AGGREGATION COMPLETE!")
    print(f"   📁 Output directory: {output_dir}")
    print(f"   📄 Files created:")
    print(f"      - events.json ({len(aggregated_data['events'])} events)")
    print(f"      - departments.json ({len(aggregated_data['departments'])} departments)")
    print(f"      - meta.json (site metadata)")
    
    return aggregated_data

if __name__ == "__main__":
    main()
