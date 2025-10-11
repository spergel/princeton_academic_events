#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import re
from typing import List, Dict, Any
from icalendar import Calendar
import pytz

class MathICSScraper:
    def __init__(self):
        self.base_url = "https://www.math.princeton.edu"
        self.ics_url = "https://www.math.princeton.edu/events-feed.ics"
        self.department_name = "Mathematics"
        self.meta_category = "sciences_engineering"
        
    def scrape_math_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Mathematics department using their ICS calendar feed"""
        print(f"🔢 SCRAPING {self.department_name.upper()} EVENTS FROM ICS FEED")
        print("=" * 60)
        
        try:
            print(f"🔍 Fetching ICS feed from: {self.ics_url}")
            
            response = requests.get(self.ics_url, timeout=30)
            response.raise_for_status()
            
            # Parse the ICS content
            cal = Calendar.from_ical(response.content)
            
            all_events = []
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event = self._extract_event_from_ics(component)
                    if event and event.get('title'):
                        all_events.append(event)
            
            # Remove duplicates and sort by date
            unique_events = self._deduplicate_events(all_events)
            unique_events.sort(key=lambda x: x.get('start_date', ''))
            
            print(f"🎯 Total events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Mathematics events: {e}")
            return []
    
    def _extract_event_from_ics(self, component) -> Dict[str, Any]:
        """Extract event information from an ICS component"""
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
        if component.get('summary'):
            title = str(component.get('summary'))
            event['title'] = title
            event['id'] = f"{self.department_name.lower()}_{datetime.now().strftime('%Y%m%d')}_{title[:20].replace(' ', '_')}"
        
        # Extract description
        if component.get('description'):
            description = str(component.get('description'))
            event['description'] = description
        
        # Extract start date and time
        if component.get('dtstart'):
            dtstart = component.get('dtstart')
            if hasattr(dtstart, 'dt'):
                start_dt = dtstart.dt
                if isinstance(start_dt, datetime):
                    # Convert to Princeton timezone if it's timezone-aware
                    if start_dt.tzinfo:
                        princeton_tz = pytz.timezone('America/New_York')
                        start_dt = start_dt.astimezone(princeton_tz)
                    
                    event['start_date'] = start_dt.strftime('%Y-%m-%d')
                    event['time'] = start_dt.strftime('%I:%M %p')
                else:
                    event['start_date'] = start_dt.strftime('%Y-%m-%d')
        
        # Extract end date and time
        if component.get('dtend'):
            dtend = component.get('dtend')
            if hasattr(dtend, 'dt'):
                end_dt = dtend.dt
                if isinstance(end_dt, datetime):
                    if end_dt.tzinfo:
                        princeton_tz = pytz.timezone('America/New_York')
                        end_dt = end_dt.astimezone(princeton_tz)
                    
                    event['end_date'] = end_dt.strftime('%Y-%m-%d')
                    # If same day, add end time
                    if event.get('start_date') == event['end_date']:
                        if event.get('time'):
                            event['time'] += f" - {end_dt.strftime('%I:%M %p')}"
                else:
                    event['end_date'] = end_dt.strftime('%Y-%m-%d')
        
        # Extract location
        if component.get('location'):
            location = str(component.get('location'))
            if location and location.strip():
                event['location'] = location
        
        # Extract URL if available
        if component.get('url'):
            url = str(component.get('url'))
            if url and url.startswith('http'):
                event['source_url'] = url
        
        # Determine event type and tags
        event['event_type'] = self._determine_event_type(event['title'])
        event['tags'] = self._extract_tags(event['title'], event['description'])
        
        return event
    
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
            'recital': 'Recital',
            'concert': 'Concert',
            'performance': 'Performance',
            'meeting': 'Meeting',
            'exam': 'Exam',
            'office hours': 'Office Hours'
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
        math_tags = [
            'mathematics', 'math', 'mathematical', 'algebra', 'analysis', 'geometry',
            'topology', 'number theory', 'combinatorics', 'probability', 'statistics',
            'differential equations', 'optimization', 'numerical analysis', 'applied math',
            'pure math', 'theoretical computer science', 'mathematical physics'
        ]
        
        for tag in math_tags:
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
            filename = f'{self.department_name.lower()}_ics_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.ics_url,
                'source': f'{self.department_name} ICS Calendar Feed',
                'note': f'Scraped from {self.ics_url}'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    scraper = MathICSScraper()
    events = scraper.scrape_math_events()
    scraper.save_events(events)
