#!/usr/bin/env python3
"""
Convert aggregated events data to the format expected by the API.
This script reads the aggregated events.json and converts it to the format
that the Cloudflare Worker API expects.
"""

import json
import os
from datetime import datetime

def convert_events_for_api():
    """Convert aggregated events to API format"""
    print("🔄 CONVERTING EVENTS FOR API")
    print("=" * 50)
    
    # Read the aggregated events
    events_file = "frontend/public/data/events.json"
    if not os.path.exists(events_file):
        print(f"❌ Events file not found: {events_file}")
        return None
    
    with open(events_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    print(f"📄 Found {len(events)} events in aggregated data")
    
    # Convert to API format
    api_events = []
    for event in events:
        api_event = {
            'id': event.get('id', ''),
            'title': event.get('title', ''),
            'description': event.get('description', ''),
            'date': event.get('start_date', ''),  # Convert start_date to date
            'time': event.get('time', ''),
            'location': event.get('location', ''),
            'department': event.get('department', ''),
            'source_url': event.get('source_url', '')
        }
        api_events.append(api_event)
    
    # Create API payload
    api_payload = {
        'events': api_events
    }
    
    # Save to file
    output_file = "api_events.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(api_payload, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Converted {len(api_events)} events to API format")
    print(f"💾 Saved to: {output_file}")
    
    # Show sample
    if api_events:
        print(f"\n📋 Sample event:")
        sample = api_events[0]
        for key, value in sample.items():
            print(f"   {key}: {value}")
    
    return api_payload

if __name__ == "__main__":
    convert_events_for_api()
