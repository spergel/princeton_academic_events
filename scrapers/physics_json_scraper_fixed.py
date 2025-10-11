#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import re
from typing import List, Dict, Any
import pytz

class PhysicsJSONScraper:
    def __init__(self):
        self.base_url = "https://phy.princeton.edu"
        self.json_url = "https://phy.princeton.edu/feeds/events/calendar.json"
        self.department_name = "Physics"
        self.meta_category = "sciences_engineering"
        
    def scrape_physics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Physics department using their JSON calendar feed"""
        print(f"⚛️ SCRAPING {self.department_name.upper()} EVENTS FROM JSON FEED")
        print("=" * 60)
        
        try:
            print(f"🔍 Fetching JSON feed from: {self.json_url}")
            
            # Set up parameters for the JSON request
            params = {
                'uuid': '2cea06c3-31b5-478b-b470-477cf35c7a4d',
                'et': 'node',
                'ei': '7896',
                'start': '2025-01-01T00:00:00',  # Get events from start of year
                'end': '2025-12-31T23:59:59',    # Get events until end of year
                'timeZone': 'America/New_York'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://phy.princeton.edu/',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = requests.get(self.json_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the JSON content
            data = response.json()
            
            all_events = []
            
            # Extract events from the JSON response
            if isinstance(data, list):
                for event_data in data:
                    event = self._extract_event_from_json(event_data)
                    if event and event.get('title'):
                        all_events.append(event)
            elif isinstance(data, dict) and 'events' in data:
                for event_data in data['events']:
                    event = self._extract_event_from_json(event_data)
                    if event and event.get('title'):
                        all_events.append(event)
            
            # Remove duplicates and sort by date
            unique_events = self._deduplicate_events(all_events)
            unique_events.sort(key=lambda x: x.get('start_date', ''))
            
            print(f"🎯 Total events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Physics events: {e}")
            return []
    
    def _extract_event_from_json(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract event information from JSON data"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': 'Princeton University',
            'event_type': 'Event',
            'department': self.department_name,
            'meta_category': self.meta_category,
            'source_url': f"{self.base_url}/events",
            'source_name': f'{self.department_name} Department Events',
            'speaker': '',
            'audience': '',
            'topics': [],
            'departments': [],
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title
        if event_data.get('title'):
            event['title'] = str(event_data['title'])
            event['id'] = f"{self.department_name.lower()}_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract description
        if event_data.get('description'):
            event['description'] = str(event_data['description'])
        
        # Extract start date and time
        if event_data.get('start'):
            start_str = str(event_data['start'])
            start_dt = self._parse_datetime(start_str)
            if start_dt:
                event['start_date'] = start_dt.strftime('%Y-%m-%d')
                event['time'] = start_dt.strftime('%I:%M %p')
        
        # Extract end date and time
        if event_data.get('end'):
            end_str = str(event_data['end'])
            end_dt = self._parse_datetime(end_str)
            if end_dt:
                event['end_date'] = end_dt.strftime('%Y-%m-%d')
                # If same day, add end time
                if event.get('start_date') == event['end_date']:
                    if event.get('time'):
                        event['time'] += f" - {end_dt.strftime('%I:%M %p')}"
        
        # Extract location
        if event_data.get('location'):
            location = str(event_data['location'])
            if location and location.strip():
                event['location'] = location
        
        # Extract URL if available
        if event_data.get('url'):
            url = str(event_data['url'])
            if url and url.startswith('http'):
                event['source_url'] = url
        
        # Extract additional fields that might be available
        if event_data.get('speaker'):
            event['speaker'] = str(event_data['speaker'])
        
        if event_data.get('category'):
            event['tags'].append(str(event_data['category']))
        
        # Determine event type and tags
        event['event_type'] = self._determine_event_type(event['title'])
        event['tags'].extend(self._extract_tags(event['title'], event.get('description', '')))
        
        return event
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string from Physics JSON feed"""
        try:
            # Handle timezone-aware datetime strings (e.g., "2025-01-01T00:00:00-05:00")
            if 'T' in datetime_str and ('+' in datetime_str or datetime_str.count('-') > 2):
                # Parse ISO format with timezone
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                # Convert to Princeton timezone
                princeton_tz = pytz.timezone('America/New_York')
                dt = dt.astimezone(princeton_tz)
                return dt
            
            # Try different datetime formats for non-timezone strings
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(datetime_str, fmt)
                    # Convert to Princeton timezone if it's timezone-aware
                    if dt.tzinfo:
                        princeton_tz = pytz.timezone('America/New_York')
                        dt = dt.astimezone(princeton_tz)
                    return dt
                except ValueError:
                    continue
            
            return None
        except Exception:
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


