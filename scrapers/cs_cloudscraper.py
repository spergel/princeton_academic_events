#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
from typing import List, Dict, Any

class CSCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
            delay=10
        )
        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.base_url = "https://www.cs.princeton.edu"
        self.events_url = "https://www.cs.princeton.edu/events"
        self.department_name = "Computer Science"
        self.meta_category = "sciences_engineering"
        
    def scrape_cs_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Computer Science department"""
        print(f"💻 SCRAPING {self.department_name.upper()} EVENTS")
        print("=" * 60)
        
        all_events = []
        
        try:
            print(f"🔍 Scraping events from: {self.events_url}")
            
            response = self.scraper.get(self.events_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find event containers - CS department uses custom_card class
            event_containers = soup.find_all('li', class_='custom_card')
            print(f"    🔍 Found {len(event_containers)} events")
            
            if not event_containers:
                print("    ⚠️  No events found")
                return []
            
            # Extract events from containers
            for container in event_containers:
                event = self._extract_event_from_container(container)
                if event and event.get('title'):
                    # Get additional details from individual event page
                    if event.get('source_url'):
                        detailed_event = self._fetch_event_details(event['source_url'])
                        if detailed_event:
                            event.update(detailed_event)
                    
                    all_events.append(event)
            
            # Remove duplicates and sort by date
            unique_events = self._deduplicate_events(all_events)
            unique_events.sort(key=lambda x: x.get('start_date', ''))
            
            print(f"🎯 Total unique events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping CS events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a container"""
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
            'source_url': '',
            'source_name': f'{self.department_name} Department Events',
            'speaker': '',
            'speaker_affiliation': '',
            'subtitle': '',
            'audience': '',
            'topics': [],
            'departments': [],
            'tags': [],
            'category': '',
            'image_url': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title and URL
        title_elem = container.find('h5', class_='custom_card__heading')
        if title_elem:
            title_link = title_elem.find('a', class_='custom_card__heading-link')
            if title_link:
                event['title'] = title_link.get_text(strip=True)
                href = title_link.get('href')
                if href.startswith('http'):
                    event['source_url'] = href
                else:
                    event['source_url'] = self.base_url + href
                
                event['id'] = f"{self.department_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract event type
        type_elem = container.find('div', class_='field--name-field-event-type')
        if type_elem:
            type_link = type_elem.find('a')
            if type_link:
                event['event_type'] = type_link.get_text(strip=True)
                event['category'] = type_link.get_text(strip=True)
                event['tags'].append(type_link.get_text(strip=True))
        
        # Extract date
        date_elem = container.find('div', class_='event__date_time')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            if date_text:
                # Parse date format like "09-16" or "10-07"
                date_match = re.search(r'(\d{1,2})-(\d{1,2})', date_text)
                if date_match:
                    month = date_match.group(1)
                    day = date_match.group(2)
                    # Assume current year if not specified
                    current_year = datetime.now().year
                    event['start_date'] = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Extract time
        time_elem = container.find('div', class_='event__date_range')
        if time_elem:
            time_text = time_elem.get_text(strip=True)
            if time_text:
                # Extract time information like "12:15 PM - 1:15 PM"
                time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:am|pm))\s*-\s*(\d{1,2}:\d{2}\s*(?:am|pm))', time_text, re.IGNORECASE)
                if time_match:
                    event['time'] = f"{time_match.group(1)} - {time_match.group(2)}"
                else:
                    # Single time
                    single_time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:am|pm))', time_text, re.IGNORECASE)
                    if single_time_match:
                        event['time'] = single_time_match.group(1)
        
        # Extract location
        location_elem = container.find('div', class_='event__location')
        if location_elem:
            location_item = location_elem.find('div', class_='field--name-field-event-location-id')
            if location_item:
                event['location'] = location_item.get_text(strip=True)
        
        # Extract description/summary if available
        snippet_elem = container.find('div', class_='custom_card__snippet')
        if snippet_elem:
            # Remove time and location info to get just the description
            snippet_text = snippet_elem.get_text(strip=True)
            if snippet_text:
                # Clean up the text by removing time and location
                cleaned_text = re.sub(r'\d{1,2}:\d{2}\s*(?:am|pm)(?:\s*-\s*\d{1,2}:\d{2}\s*(?:am|pm))?', '', snippet_text)
                cleaned_text = re.sub(r'[A-Za-z\s]+Hall\s+\d+', '', cleaned_text)
                cleaned_text = cleaned_text.strip()
                if cleaned_text:
                    event['description'] = cleaned_text
        
        # Determine event type and tags
        event['event_type'] = self._determine_event_type(event['title'], event.get('category', ''))
        event['tags'].extend(self._extract_tags(event['title'], event.get('description', ''), event.get('category', '')))
        
        return event
    
    def _fetch_event_details(self, event_url: str) -> Dict[str, Any]:
        """Fetch detailed information from individual event page"""
        try:
            print(f"    🔍 Fetching details from: {event_url}")
            response = self.scraper.get(event_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract description from the specific field
            desc_elem = soup.find('div', class_='field--name-field-event-description')
            if desc_elem:
                # Get the text content and clean it up
                description = desc_elem.get_text(strip=True)
                if description:
                    # Clean up the description
                    description = re.sub(r'\s+', ' ', description).strip()
                    # Remove common footer text
                    description = re.sub(r'(privacy policy|cookie policy|copyright|all rights reserved).*$', '', description, flags=re.IGNORECASE)
                    details['description'] = description
            
            # If no description found, try meta description as fallback
            if not details.get('description'):
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    details['description'] = meta_desc.get('content')
            
            # Extract speaker information
            speaker_elem = soup.find('div', class_='field--name-field-speaker')
            if speaker_elem:
                speaker_text = speaker_elem.get_text(strip=True)
                if speaker_text and 'speaker' not in speaker_text.lower():
                    details['speaker'] = speaker_text
            
            # Extract additional content for tags
            if details.get('description'):
                content_text = details['description'].lower()
                additional_tags = self._extract_content_tags(content_text)
                if additional_tags:
                    details['tags'] = additional_tags
            
            return details
            
        except Exception as e:
            print(f"    ⚠️  Error fetching event details: {e}")
            return {}
    
    def _determine_event_type(self, title: str, category: str) -> str:
        """Determine event type based on title and category"""
        if not title:
            return 'Event'
            
        title_lower = title.lower()
        category_lower = category.lower()
        
        # Check category first
        if 'seminar' in category_lower:
            return 'Seminar'
        elif 'lecture' in category_lower:
            return 'Lecture'
        elif 'colloquium' in category_lower:
            return 'Colloquium'
        
        # Check title keywords
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
            'research': 'Research Presentation',
            'hackathon': 'Hackathon',
            'competition': 'Competition'
        }
        
        for keyword, event_type in type_keywords.items():
            if keyword in title_lower:
                return event_type
        
        return 'Event'
    
    def _extract_tags(self, title: str, description: str, category: str) -> List[str]:
        """Extract relevant tags from title, description, and category"""
        text = (title + ' ' + (description or '') + ' ' + (category or '')).lower()
        tags = []
        
        # Add department-specific tags
        cs_tags = [
            'computer science', 'cs', 'computing', 'programming', 'software',
            'algorithm', 'data structure', 'machine learning', 'ai', 'artificial intelligence',
            'computer vision', 'natural language processing', 'nlp', 'robotics',
            'systems', 'networks', 'security', 'cryptography', 'databases',
            'operating systems', 'compilers', 'theory', 'complexity', 'optimization',
            'human-computer interaction', 'hci', 'user interface', 'ui', 'ux',
            'web development', 'mobile development', 'game development', 'virtual reality',
            'augmented reality', 'blockchain', 'distributed systems', 'parallel computing'
        ]
        
        for tag in cs_tags:
            if tag in text:
                tags.append(tag)
        
        # Add general tags
        general_tags = ['princeton', 'university', 'academic', 'event', 'seminar', 'lecture']
        for tag in general_tags:
            if tag in text and tag not in tags:
                tags.append(tag)
        
        return tags
    
    def _extract_content_tags(self, content_text: str) -> List[str]:
        """Extract additional tags from event content"""
        tags = []
        
        # Look for specific content indicators
        content_keywords = [
            'computer science', 'cs', 'computing', 'programming', 'software',
            'algorithm', 'data structure', 'machine learning', 'ai', 'artificial intelligence',
            'computer vision', 'natural language processing', 'nlp', 'robotics',
            'systems', 'networks', 'security', 'cryptography', 'databases',
            'operating systems', 'compilers', 'theory', 'complexity', 'optimization',
            'human-computer interaction', 'hci', 'user interface', 'ui', 'ux',
            'web development', 'mobile development', 'game development', 'virtual reality',
            'augmented reality', 'blockchain', 'distributed systems', 'parallel computing',
            'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'swift'
        ]
        
        for keyword in content_keywords:
            if keyword in content_text:
                tags.append(keyword)
        
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
            filename = f'{self.department_name.lower().replace(" ", "_")}_cloudscraper_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.events_url,
                'source': f'{self.department_name} CloudScraper',
                'note': f'Scraped from {self.events_url} with individual page details'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    scraper = CSCloudScraper()
    events = scraper.scrape_cs_events()
    scraper.save_events(events)
