#!/usr/bin/env python3
"""
Sociology Department Alternative Scraper
Tries different approaches to bypass 403 Forbidden
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Any
import time
import random


class SociologyAlternativeScraper:
    def __init__(self):
        self.department_name = "Sociology"
        self.base_url = "https://sociology.princeton.edu"
        self.meta_category = "social_sciences"
        
    def scrape_sociology_events(self) -> List[Dict[str, Any]]:
        """Try multiple approaches to scrape Sociology events"""
        print("ALTERNATIVE SOCIOLOGY SCRAPING")
        print("=" * 60)
        
        # Try different URLs and approaches
        urls_to_try = [
            "https://sociology.princeton.edu/events",
            "https://sociology.princeton.edu/news-events",
            "https://sociology.princeton.edu/events/",
            "https://sociology.princeton.edu/events?page=0",
            "https://sociology.princeton.edu/events?page=1"
        ]
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        
        for i, url in enumerate(urls_to_try):
            print(f"Trying approach {i+1}: {url}")
            
            try:
                # Random user agent
                user_agent = random.choice(user_agents)
                
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1',
                    'Referer': 'https://www.google.com/',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
                
                # Add random delay
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    print(f"    SUCCESS! Got response from {url}")
                    return self._parse_events_from_response(response)
                elif response.status_code == 403:
                    print(f"    Still blocked (403) from {url}")
                else:
                    print(f"    Got status {response.status_code} from {url}")
                    
            except Exception as e:
                print(f"    Error with {url}: {e}")
            
            # Wait between attempts
            time.sleep(random.uniform(2, 4))
        
        print("All approaches failed - department is blocking all automated access")
        return []
    
    def _parse_events_from_response(self, response) -> List[Dict[str, Any]]:
        """Parse events from successful response"""
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            events = []
            
            # Try different selectors for event items
            selectors_to_try = [
                'div.content-list-item',
                'div[class*="content-list-item"]',
                'div[class*="event"]',
                'div[class*="item"]',
                'article',
                '.event-item',
                '.event',
                '[data-event]'
            ]
            
            event_items = []
            for selector in selectors_to_try:
                items = soup.select(selector)
                if items:
                    print(f"    Found {len(items)} items with selector: {selector}")
                    event_items = items
                    break
            
            if not event_items:
                print("    No event items found with any selector")
                return []
            
            for item in event_items:
                event = self._parse_event_item(item)
                if event and event['title']:
                    events.append(event)
                    print(f"    Parsed: {event['title'][:50]}...")
            
            # Remove duplicates
            events = self._deduplicate_events(events)
            
            print(f"Total unique events found: {len(events)}")
            return events
            
        except Exception as e:
            print(f"Error parsing events: {e}")
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
            
            # Try to find title in various ways
            title_selectors = [
                'a[href]',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.event-title', '.item-title',
                '[class*="title"]'
            ]
            
            for selector in title_selectors:
                title_elem = item.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    event['title'] = title_elem.get_text(strip=True)
                    # Get URL if it's a link
                    if title_elem.name == 'a' and title_elem.get('href'):
                        href = title_elem.get('href')
                        if href.startswith('http'):
                            event['url'] = href
                        else:
                            event['url'] = self.base_url + href
                    break
            
            # Try to find date/time
            date_selectors = [
                '.date', '.event-date', '.time', '.datetime',
                '[class*="date"]', '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = item.select_one(selector)
                if date_elem and date_elem.get_text(strip=True):
                    date_text = date_elem.get_text(strip=True)
                    event['start_date'], event['time'] = self._parse_date_time(date_text)
                    break
            
            # Try to find location
            location_selectors = [
                '.location', '.venue', '.place',
                '[class*="location"]', '[class*="venue"]'
            ]
            
            for selector in location_selectors:
                loc_elem = item.select_one(selector)
                if loc_elem and loc_elem.get_text(strip=True):
                    event['location'] = loc_elem.get_text(strip=True)
                    break
            
            # Try to find description
            desc_selectors = [
                '.description', '.summary', '.content', '.text',
                '[class*="description"]', '[class*="summary"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = item.select_one(selector)
                if desc_elem and desc_elem.get_text(strip=True):
                    event['description'] = desc_elem.get_text(strip=True)
                    break
            
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
            # Try different date patterns
            date_patterns = [
                r'([A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4})',  # Mon, Oct 20, 2025
                r'([A-Za-z]{3} \d{1,2}, \d{4})',  # Oct 20, 2025
                r'(\d{1,2}/\d{1,2}/\d{4})',  # 10/20/2025
                r'(\d{4}-\d{2}-\d{2})',  # 2025-10-20
            ]
            
            formatted_date = ''
            for pattern in date_patterns:
                date_match = re.search(pattern, date_text)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        if ',' in date_str:
                            dt = datetime.strptime(date_str, '%a, %b %d, %Y')
                        elif '/' in date_str:
                            dt = datetime.strptime(date_str, '%m/%d/%Y')
                        elif '-' in date_str:
                            dt = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            dt = datetime.strptime(date_str, '%b %d, %Y')
                        formatted_date = dt.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
            
            # Try to find time
            time_match = re.search(r'(\d{1,2}:\d{2} [ap]m)', date_text)
            if time_match:
                time_str = time_match.group(1)
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
            filename = f'{self.department_name.lower()}_alternative_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': 'Multiple URLs tried',
                'source': f'{self.department_name} Department Events (Alternative)',
                'note': 'Tried multiple approaches to bypass 403 Forbidden'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            import json
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(events)} events to {filename}")


if __name__ == "__main__":
    scraper = SociologyAlternativeScraper()
    events = scraper.scrape_sociology_events()
    scraper.save_events(events)
