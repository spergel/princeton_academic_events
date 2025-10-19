#!/usr/bin/env python3
"""
Sociology Department Stealth CloudScraper
Uses advanced headers and techniques to bypass 403 Forbidden
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Any
import time
import random


class SociologyStealthScraper:
    def __init__(self):
        self.department_name = "Sociology"
        self.base_url = "https://sociology.princeton.edu"
        self.events_url = "https://sociology.princeton.edu/events"
        self.meta_category = "social_sciences"
        
    def scrape_sociology_events(self) -> List[Dict[str, Any]]:
        """Scrape events from Sociology department with stealth techniques"""
        print("STEALTH SCRAPING SOCIOLOGY EVENTS")
        print("=" * 60)
        print(f"Scraping events from: {self.events_url}")
        
        try:
            # Advanced headers to mimic real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Referer': 'https://www.google.com/',
            }
            
            # Add random delay to seem more human
            time.sleep(random.uniform(1, 3))
            
            # Use session to maintain cookies
            session = requests.Session()
            session.headers.update(headers)
            
            # First, visit the main page to get cookies
            print("    Getting initial cookies...")
            main_response = session.get(self.base_url, timeout=30)
            main_response.raise_for_status()
            
            # Wait a bit before making the actual request
            time.sleep(random.uniform(2, 4))
            
            # Now try to access the events page
            print("    Accessing events page...")
            response = session.get(self.events_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            events = []
            
            # Find all event items
            event_items = soup.find_all('div', class_='content-list-item')
            print(f"    Found {len(event_items)} events on page")
            
            for item in event_items:
                event = self._parse_event_item(item)
                if event:
                    events.append(event)
                    print(f"    Parsed: {event['title'][:50]}...")
                    # Add small delay between parsing events
                    time.sleep(random.uniform(0.1, 0.3))
            
            # Remove duplicates
            events = self._deduplicate_events(events)
            
            print(f"Total unique events found: {len(events)}")
            return events
            
        except Exception as e:
            print(f"Error scraping Sociology events: {e}")
            return []
    
    def _parse_event_item(self, item) -> Dict[str, Any]:
        """Parse individual event item"""
        try:
            event = {
                'title': '',
                'description': '',
                'start_date': '',
                'end_date': '',
                'time': '',
                'location': '',
                'url': '',
                'department': self.department_name,
                'meta_category': self.meta_category,
                'event_type': 'Event',
                'tags': [],
                'speaker': '',
                'audience': '',
                'topics': [],
                'departments': [self.department_name],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract title and URL
            title_link = item.find('a', href=True)
            if title_link:
                event['title'] = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                if href.startswith('http'):
                    event['url'] = href
                else:
                    event['url'] = self.base_url + href
            
            # Extract date and time
            date_field = item.find('div', class_='field--name-field-ps-events-date')
            if date_field:
                date_text = date_field.get_text(strip=True)
                event['start_date'], event['time'] = self._parse_date_time(date_text)
            
            # Extract description
            summary_field = item.find('div', class_='field--name-field-ps-summary')
            if summary_field:
                event['description'] = summary_field.get_text(strip=True)
            
            # Extract location
            location_field = item.find('div', class_='field--name-field-ps-events-location-name')
            if location_field:
                location_item = location_field.find('div', class_='field__item')
                if location_item:
                    event['location'] = location_item.get_text(strip=True)
            
            # Extract speaker information
            speaker_field = item.find('div', class_='field--name-field-ps-events-speaker')
            if speaker_field:
                speaker_name = speaker_field.find('div', class_='field--name-field-ps-event-speaker-name')
                if speaker_name:
                    event['speaker'] = speaker_name.get_text(strip=True)
                
                speaker_affil = speaker_field.find('div', class_='field--name-field-ps-event-speaker-affil')
                if speaker_affil:
                    affiliation = speaker_affil.find('div', class_='field__item')
                    if affiliation:
                        event['speaker'] += f" ({affiliation.get_text(strip=True)})"
            
            # Determine event type
            event['event_type'] = self._determine_event_type(event['title'])
            
            # Extract tags
            event['tags'] = self._extract_tags(event['title'], event['description'])
            
            return event if event['title'] else None
            
        except Exception as e:
            print(f"Error parsing event item: {e}")
            return None
    
    def _parse_date_time(self, date_text: str) -> tuple:
        """Parse date and time from text"""
        try:
            # Extract date part (e.g., "Mon, Oct 20, 2025")
            date_match = re.search(r'([A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4})', date_text)
            if date_match:
                date_str = date_match.group(1)
                # Convert to YYYY-MM-DD format
                dt = datetime.strptime(date_str, '%a, %b %d, %Y')
                formatted_date = dt.strftime('%Y-%m-%d')
            else:
                formatted_date = ''
            
            # Extract time part (e.g., "12:00 pm – 1:15 pm")
            time_match = re.search(r'(\d{1,2}:\d{2} [ap]m)', date_text)
            if time_match:
                time_str = time_match.group(1)
                # Convert to 24-hour format
                try:
                    time_obj = datetime.strptime(time_str, '%I:%M %p')
                    formatted_time = time_obj.strftime('%H:%M')
                except:
                    formatted_time = time_str
            else:
                formatted_time = ''
            
            return formatted_date, formatted_time
            
        except Exception as e:
            print(f"Error parsing date/time: {e}")
            return '', ''
    
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
            'recitation': 'Recitation',
            'series': 'Series'
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
        sociology_tags = [
            'sociology', 'social', 'society', 'inequality', 'race', 'gender',
            'class', 'migration', 'immigration', 'urban', 'rural', 'family',
            'education', 'health', 'crime', 'deviance', 'social movements',
            'social policy', 'social change', 'social theory', 'methodology'
        ]
        
        for tag in sociology_tags:
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
            filename = f'{self.department_name.lower()}_stealth_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.events_url,
                'source': f'{self.department_name} Department Events (Stealth)',
                'note': f'Scraped from {self.events_url} using stealth techniques'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            import json
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(events)} events to {filename}")


if __name__ == "__main__":
    scraper = SociologyStealthScraper()
    events = scraper.scrape_sociology_events()
    scraper.save_events(events)
