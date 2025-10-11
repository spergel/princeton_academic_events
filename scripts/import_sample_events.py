#!/usr/bin/env python3
"""
Import a sample of events to test the API.
This script imports the first 50 events from our aggregated data.
"""

import json
import requests

def import_sample_events():
    """Import a sample of events to the API"""
    print("📥 IMPORTING SAMPLE EVENTS TO API")
    print("=" * 50)
    
    # Read the API events file
    with open('api_events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_events = data['events']
    print(f"📄 Found {len(all_events)} total events")
    
    # Take first 50 events as sample
    sample_events = all_events[:50]
    print(f"📊 Importing {len(sample_events)} sample events")
    
    # Prepare payload
    payload = {
        'events': sample_events
    }
    
    # Import to API
    api_url = "https://princeton-academic-events.spergel-joshua.workers.dev/api/import"
    
    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully imported {result['count']} events")
            print(f"📊 Departments: {result['summary']['departments']}")
            print(f"🕐 Timestamp: {result['timestamp']}")
        else:
            print(f"❌ Import failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error importing events: {e}")

if __name__ == "__main__":
    import_sample_events()
