import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class AnthropologyCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://anthropology.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_anthropology_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Anthropology department"""
        events = []
        
        try:
            print(f"Scraping Anthropology events from: {self.events_url}")
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event containers - Anthropology typically uses structured event listings
            event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event|seminar|talk|lecture', re.I))
            
            if not event_containers:
                # Try alternative selectors
                event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'item|entry|post|listing', re.I))
            
            if not event_containers:
                # Look for any divs that might contain event information
                event_containers = soup.find_all('div', class_=True)
                event_containers = [div for div in event_containers if any(keyword in div.get_text().lower() 
                                                                        for keyword in ['seminar', 'talk', 'lecture', 'event', 'presentation', 'colloquium'])]
            
            for container in event_containers:
                try:
                    event = self._extract_event_from_container(container)
                    if event:
                        events.append(event)
                except Exception as e:
                    print(f"Error extracting event from container: {e}")
                    continue
            
            # If no events found with containers, try parsing the entire page
            if not events:
                events = self._parse_page_for_events(soup)
            
            print(f"Found {len(events)} Anthropology events")
            return events
            
        except Exception as e:
            print(f"Error scraping Anthropology events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a container element"""
        event = {
            'title': '',
            'description': '',
            'date': '',
            'time': '',
            'location': '',
            'event_type': 'seminar',
            'department': 'Anthropology',
            'category': 'social_sciences',
            'url': self.events_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract title
        title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if title_elem:
            event['title'] = title_elem.get_text(strip=True)
        
        # Extract date
        date_elem = container.find(['time', 'span', 'div'], class_=re.compile(r'date|time', re.I))
        if date_elem:
            event['date'] = date_elem.get_text(strip=True)
        
        # Extract location
        location_elem = container.find(['span', 'div'], class_=re.compile(r'location|venue|room', re.I))
        if location_elem:
            event['location'] = location_elem.get_text(strip=True)
        
        # Extract description
        desc_elem = container.find(['p', 'div'], class_=re.compile(r'description|summary|excerpt', re.I))
        if desc_elem:
            event['description'] = desc_elem.get_text(strip=True)
        
        # Extract link
        link_elem = container.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if href.startswith('/'):
                event['url'] = self.base_url + href
            elif href.startswith('http'):
                event['url'] = href
        
        # Clean up empty fields
        event = {k: v for k, v in event.items() if v}
        
        return event if event.get('title') else None
    
    def _parse_page_for_events(self, soup) -> List[Dict[str, Any]]:
        """Parse the entire page for event information when containers aren't found"""
        events = []
        
        # Look for patterns that might indicate events
        text_content = soup.get_text()
        
        # Split by common event separators
        potential_events = re.split(r'\n\s*\n|\r\n\s*\r\n', text_content)
        
        for event_text in potential_events:
            if len(event_text.strip()) < 50:  # Skip very short text
                continue
                
            # Look for event-like patterns
            if any(keyword in event_text.lower() for keyword in ['seminar', 'talk', 'lecture', 'presentation', 'event', 'colloquium']):
                event = {
                    'title': self._extract_title_from_text(event_text),
                    'description': event_text.strip()[:500],  # First 500 chars as description
                    'date': self._extract_date_from_text(event_text),
                    'time': self._extract_time_from_text(event_text),
                    'location': self._extract_location_from_text(event_text),
                    'event_type': 'seminar',
                    'department': 'Anthropology',
                    'category': 'social_sciences',
                    'url': self.events_url,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Clean up empty fields
                event = {k: v for k, v in event.items() if v}
                
                if event.get('title'):
                    events.append(event)
        
        return events
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract a potential title from text"""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                # Remove common prefixes
                line = re.sub(r'^[0-9]+\.\s*', '', line)
                line = re.sub(r'^[-•*]\s*', '', line)
                return line
        return ''
    
    def _extract_date_from_text(self, text: str) -> str:
        """Extract date from text"""
        # Look for common date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return ''
    
    def _extract_time_from_text(self, text: str) -> str:
        """Extract time from text"""
        time_pattern = r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
        match = re.search(time_pattern, text)
        return match.group() if match else ''
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from text"""
        # Look for common location indicators
        location_patterns = [
            r'(?:Room|Auditorium|Hall|Building|Center|Institute)\s+[A-Z0-9\s]+',
            r'\b[A-Z]{2,4}\s+\d{3,4}\b',  # Building codes like "GSL 101"
            r'\b\d{3,4}\s+[A-Z]{2,4}\b'   # Room numbers like "101 GSL"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return ''

if __name__ == "__main__":
    scraper = AnthropologyCloudScraper()
    events = scraper.scrape_anthropology_events()
    
    # Save to file
    with open('anthropology_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(events)} events from Anthropology")
    for event in events[:3]:  # Show first 3 events
        print(f"- {event.get('title', 'No title')}")
