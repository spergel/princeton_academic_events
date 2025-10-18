#!/usr/bin/env python3
"""
Physics Department JSON Scraper
Scrapes events from Physics Department JSON calendar feed
"""

import json
import requests
from datetime import datetime
import pytz
from typing import List, Dict, Any


class PhysicsJSONScraper:
    def __init__(self):
        self.department_name = "Physics"
        self.json_url = "https://physics.princeton.edu/feeds/events/calendar.json"
        
    def scrape_physics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from Physics JSON feed"""
        print("🔬 SCRAPING PHYSICS EVENTS FROM JSON FEED")
        print("=" * 60)
        print(f"🔍 Fetching JSON feed from: {self.json_url}")
        
        try:
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            events = []
            
            # Parse events from JSON feed
            for event_data in data.get('events', []):
                event = self._parse_event(event_data)
                if event:
                    events.append(event)
            
            # Remove duplicates
            events = self._deduplicate_events(events)
            
            print(f"🎯 Total events found: {len(events)}")
            return events
            
        except Exception as e:
            print(f"❌ Error scraping Physics events: {e}")
            return []
    
    def _parse_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual event from JSON data"""
        try:
            event = {
                'title': str(event_data.get('title', '')),
                'description': str(event_data.get('description', '')),
                'start_date': str(event_data.get('start_date', '')),
                'end_date': str(event_data.get('end_date', '')),
                'time': str(event_data.get('time', '')),
                'location': str(event_data.get('location', '')),
                'url': str(event_data.get('url', '')),
                'department': self.department_name,
                'meta_category': 'sciences_engineering',
                'event_type': 'Event',
                'tags': [],
                'speaker': str(event_data.get('speaker', '')),
                'category': str(event_data.get('category', ''))
            }
            
            # Determine event type and tags
            event['event_type'] = self._determine_event_type(event['title'])
            event['tags'].extend(self._extract_tags(event['title'], event.get('description', '')))
            
            return event
            
        except Exception as e:
            print(f"❌ Error parsing event: {e}")
            return None
    
    def _determine_event_type(self, title: str) -> str:
        """Determine event type based on title"""
        if not title:
            return 'Event'
            
        title_lower = title.lower()
        
        type_keywords = {
            'colloquium': 'Colloquium',
            'seminar': 'Seminar',
            'workshop': 'Workshop',
            'talk': 'Talk',
            'lecture': 'Lecture',
            'conference': 'Conference',
            'panel': 'Panel',
            'discussion': 'Discussion',
            'symposium': 'Symposium',
            'meeting': 'Meeting',
            'exam': 'Exam',
            'office hours': 'Office Hours',
            'lab': 'Lab Session',
            'tutorial': 'Tutorial',
            'recitation': 'Recitation'
        }
        
        for keyword, event_type in type_keywords.items():
            if keyword in title_lower:
                return event_type
        
        return 'Event'
    
    def _extract_tags(self, title: str, description: str) -> List[str]:
        """Extract relevant tags from title and description"""
        text = (title + ' ' + (description or '')).lower()
        tags = []
        
        # Add department-specific tags
        physics_tags = [
            'physics', 'physical', 'mechanics', 'thermodynamics', 'electromagnetism',
            'optics', 'quantum', 'particle', 'nuclear', 'astrophysics', 'cosmology',
            'condensed matter', 'plasma', 'fluid dynamics', 'statistical mechanics',
            'relativity', 'string theory', 'quantum field theory', 'quantum mechanics'
        ]
        
        for tag in physics_tags:
            if tag in text:
                tags.append(tag)
        
        # Add general tags
        general_tags = ['princeton', 'university', 'academic', 'event', 'colloquium', 'seminar']
        for tag in general_tags:
            if tag in text and tag not in tags:
                tags.append(tag)
        
        return tags
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events"""
        seen = set()
        unique_events = []
        
        for event in events:
            key = f"{event.get('title', '')}_{event.get('start_date', '')}_{event.get('time', '')}"
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def save_events(self, events: List[Dict[str, Any]], filename: str = None):
        """Save events to JSON file"""
        if not filename:
            filename = f'{self.department_name.lower()}_json_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.json_url,
                'source': f'{self.department_name} JSON Calendar Feed',
                'note': f'Scraped from {self.json_url}'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} events to {filename}")


if __name__ == "__main__":
    scraper = PhysicsJSONScraper()
    events = scraper.scrape_physics_events()
    scraper.save_events(events)