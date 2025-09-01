import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class ChemistryCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://chemistry.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_chemistry_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Chemistry department"""
        events = []
        
        try:
            print(f"Scraping Chemistry events from: {self.events_url}")
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for chemistry event patterns
            chem_keywords = ['seminar', 'lecture', 'colloquium', 'symposium', 'workshop', 'conference', 'talk']
            
            # Look for event containers
            event_containers = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and any(word in x.lower() for word in ['event', 'seminar', 'lecture', 'item']))
            
            for container in event_containers:
                # Skip containers that are clearly not events
                text = container.get_text().lower()
                if any(skip_word in text for skip_word in ['search', 'navigation', 'menu', 'utility', 'pagination', 'header', 'footer']):
                    continue
                
                # Look for containers that have date-like patterns
                if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', text):
                    event = self._extract_event_from_container(container)
                    if event and event.get('title') and len(event['title']) > 10:
                        events.append(event)
            
            # Also look for any links that contain chemistry event information
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                link_text = link.get_text(strip=True)
                if (len(link_text) > 20 and 
                    any(keyword in link_text.lower() for keyword in chem_keywords) and
                    not any(skip_word in link_text.lower() for skip_word in ['search', 'menu', 'navigation', 'about', 'people', 'courses'])):
                    
                    event = self._extract_event_from_link(link)
                    if event:
                        events.append(event)
            
            # Remove duplicates
            unique_events = self._deduplicate_events(events)
            
            print(f"Found {len(unique_events)} Chemistry events")
            return unique_events
            
        except Exception as e:
            print(f"Error scraping Chemistry events: {e}")
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
            'department': 'Chemistry',
            'category': 'science_engineering',
            'url': self.events_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Get all text content
        text_content = container.get_text()
        
        # Extract date - look for month/day patterns
        date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', text_content)
        if date_match:
            event['date'] = date_match.group()
        
        # Extract time - look for time patterns
        time_match = re.search(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', text_content)
        if time_match:
            event['time'] = time_match.group()
        
        # Extract location - look for building/room patterns
        location_patterns = [
            r'\b(?:Frick Chemistry Laboratory|Frick Lab|Taylor Auditorium|Room \d+)\b',
            r'\b[A-Z]{2,4}\s+\d{3,4}\b',  # Building codes
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, text_content)
            if location_match:
                event['location'] = location_match.group().strip()
                break
        
        # Extract title - look for the longest meaningful text line
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not any(skip in line.lower() for skip in ['date', 'time', 'location', 'room']):
                event['title'] = line
                break
        
        return event
    
    def _extract_event_from_link(self, link) -> Dict[str, Any]:
        """Extract event information from a link element"""
        event = {
            'title': link.get_text(strip=True),
            'description': '',
            'date': '',
            'time': '',
            'location': '',
            'event_type': 'seminar',
            'department': 'Chemistry',
            'category': 'science_engineering',
            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
            'scraped_at': datetime.now().isoformat()
        }
        
        # Try to extract additional info from parent elements
        parent = link.parent
        if parent:
            parent_text = parent.get_text()
            
            # Extract date
            date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', parent_text)
            if date_match:
                event['date'] = date_match.group()
            
            # Extract time
            time_match = re.search(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', parent_text)
            if time_match:
                event['time'] = time_match.group()
        
        return event
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title"""
        seen_titles = set()
        unique_events = []
        
        for event in events:
            title = event.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_events.append(event)
        
        return unique_events

if __name__ == "__main__":
    scraper = ChemistryCloudScraper()
    events = scraper.scrape_chemistry_events()
    print(f"Found {len(events)} Chemistry events")
