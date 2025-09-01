import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class EastAsianStudiesCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://eas.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_east_asian_studies_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Program in East Asian Studies"""
        events = []
        
        try:
            print(f"Scraping East Asian Studies events from: {self.events_url}")
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for specific East Asian studies event patterns
            eas_keywords = ['lecture', 'seminar', 'colloquium', 'workshop', 'conference', 'symposium', 'talk', 'presentation', 'forum', 'panel', 'discussion', 'reading']
            
            # Look for text content that contains East Asian studies event keywords
            all_text = soup.get_text()
            
            # Split by lines and look for event-like content
            lines = all_text.split('\n')
            current_event = None
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                
                # Look for lines that contain East Asian studies event keywords
                if any(keyword in line.lower() for keyword in eas_keywords):
                    # This might be an event title or series
                    if current_event:
                        events.append(current_event)
                    
                    current_event = {
                        'title': line,
                        'department': 'Program in East Asian Studies',
                        'category': 'arts_humanities',
                        'event_type': 'lecture',
                        'url': self.events_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                
                # Look for date patterns
                elif current_event and not current_event.get('date'):
                    date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', line)
                    if date_match:
                        current_event['date'] = date_match.group()
                
                # Look for time patterns
                elif current_event and not current_event.get('time'):
                    time_match = re.search(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', line)
                    if time_match:
                        current_event['time'] = time_match.group()
                
                # Look for location patterns
                elif current_event and not current_event.get('location'):
                    if any(loc in line for loc in ['Jones Hall', 'Room', 'Auditorium', 'Building', 'East Asian']):
                        current_event['location'] = line
            
            # Add the last event if exists
            if current_event:
                events.append(current_event)
            
            # Also look for any links that contain East Asian studies event information
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                link_text = link.get_text(strip=True)
                if (len(link_text) > 20 and 
                    any(keyword in link_text.lower() for keyword in eas_keywords) and
                    not any(skip_word in link_text.lower() for skip_word in ['search', 'menu', 'navigation', 'about', 'people', 'courses'])):
                    
                    event = {
                        'title': link_text,
                        'department': 'Program in East Asian Studies',
                        'category': 'arts_humanities',
                        'event_type': 'lecture',
                        'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                        'scraped_at': datetime.now().isoformat()
                    }
                    events.append(event)
            
            # Remove duplicates
            unique_events = self._deduplicate_events(events)
            
            print(f"Found {len(unique_events)} East Asian Studies events")
            return unique_events
            
        except Exception as e:
            print(f"Error scraping East Asian Studies events: {e}")
            return []
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title"""
        seen_titles = set()
        unique_events = []
        
        for event in events:
            title = event.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_events.append(event)
        
        return unique_events

if __name__ == "__main__":
    scraper = EastAsianStudiesCloudScraper()
    events = scraper.scrape_east_asian_studies_events()
    
    # Save to file
    with open('east_asian_studies_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(events)} events from East Asian Studies")
    for event in events[:3]:  # Show first 3 events
        print(f"- {event.get('title', 'No title')}")
