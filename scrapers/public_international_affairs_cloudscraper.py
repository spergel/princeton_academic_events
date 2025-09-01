import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class PublicInternationalAffairsCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://spia.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_public_international_affairs_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Public and International Affairs department"""
        events = []
        
        try:
            print(f"Scraping Public and International Affairs events from: {self.events_url}")
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for actual event containers - SPIA uses specific patterns
            event_containers = soup.find_all('div', class_=lambda x: x and 'event' in x.lower())
            
            for container in event_containers:
                # Skip containers that are clearly not events (like navigation, search, etc.)
                text = container.get_text().lower()
                if any(skip_word in text for skip_word in ['search', 'navigation', 'menu', 'utility', 'pagination', 'header', 'footer']):
                    continue
                
                # Look for containers that have date-like patterns
                if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', text):
                    event = self._extract_event_from_container(container)
                    if event and event.get('title') and len(event['title']) > 10:
                        events.append(event)
            
            # Also look for any links that contain event-like text
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                link_text = link.get_text(strip=True)
                if (len(link_text) > 20 and 
                    any(keyword in link_text.lower() for keyword in ['seminar', 'talk', 'lecture', 'event', 'series', 'conference']) and
                    not any(skip_word in link_text.lower() for skip_word in ['search', 'menu', 'navigation'])):
                    
                    event = self._extract_event_from_link(link)
                    if event:
                        events.append(event)
            
            # Remove duplicates and clean up
            unique_events = self._deduplicate_events(events)
            
            print(f"Found {len(unique_events)} Public and International Affairs events")
            return unique_events
            
        except Exception as e:
            print(f"Error scraping Public and International Affairs events: {e}")
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
            'department': 'Public and International Affairs',
            'category': 'social_sciences',
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
            r'\b(?:Wallace Hall|Robertson Hall|Sherrerd Hall|Richardson Auditorium|Julis Romo Rabinowitz Building|Princeton Public Library)\s*[A-Z0-9\s]*\b',
            r'\b[A-Z]{2,4}\s+\d{3,4}\b',  # Building codes like "GSL 101"
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, text_content)
            if location_match:
                event['location'] = location_match.group().strip()
                break
        
        # Extract title - look for the longest meaningful text line
        lines = text_content.split('\n')
        potential_titles = []
        for line in lines:
            line = line.strip()
            if (len(line) > 20 and len(line) < 200 and 
                not any(skip_word in line.lower() for skip_word in ['search', 'menu', 'navigation', 'utility', 'pagination']) and
                not re.match(r'^\d+$', line) and  # Skip pure numbers
                not re.match(r'^[A-Z\s]+$', line)):  # Skip all caps navigation
                potential_titles.append(line)
        
        if potential_titles:
            # Choose the longest line that looks like a title
            title = max(potential_titles, key=len)
            
            # Clean up the title by removing date/location prefixes
            # Remove date patterns from the beginning
            title = re.sub(r'^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2}\s*', '', title)
            # Remove time patterns
            title = re.sub(r'\s*\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\s*', ' ', title)
            # Remove location patterns
            title = re.sub(r'^(?:Wallace Hall|Robertson Hall|Sherrerd Hall|Richardson Auditorium|Julis Romo Rabinowitz Building|Princeton Public Library)\s*', '', title)
            # Clean up extra spaces
            title = re.sub(r'\s+', ' ', title).strip()
            
            event['title'] = title
        
        # Extract description - use the text after the title
        if event['title']:
            title_index = text_content.find(event['title'])
            if title_index != -1:
                description_start = title_index + len(event['title'])
                description = text_content[description_start:].strip()
                if description and len(description) > 20:
                    event['description'] = description[:500]  # Limit description length
        
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
    
    def _extract_event_from_link(self, link) -> Dict[str, Any]:
        """Extract event information from a link element"""
        event = {
            'title': link.get_text(strip=True),
            'department': 'Public and International Affairs',
            'category': 'social_sciences',
            'event_type': 'seminar',
            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
            'scraped_at': datetime.now().isoformat()
        }
        
        return event if event.get('title') else None
    
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
    scraper = PublicInternationalAffairsCloudScraper()
    events = scraper.scrape_public_international_affairs_events()
    
    # Save to file
    with open('public_international_affairs_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(events)} events from Public and International Affairs")
    for event in events[:3]:  # Show first 3 events
        print(f"- {event.get('title', 'No title')}")
