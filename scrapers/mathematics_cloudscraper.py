import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class MathematicsCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://math.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_mathematics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Mathematics department"""
        events = []
        
        try:
            print(f"Scraping Mathematics events from: {self.events_url}")
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all event cards
            event_cards = soup.find_all('div', class_='event-card')
            
            print(f"Found {len(event_cards)} event cards")
            
            for card in event_cards:
                try:
                    # Extract date from thumbnail
                    date_thumbnail = card.find('div', class_='event-card__date-thumbnail')
                    if not date_thumbnail:
                        continue
                        
                    month_elem = date_thumbnail.find('div', class_='event-card__big-month')
                    day_elem = date_thumbnail.find('div', class_='event-card__big-day')
                    
                    if not month_elem or not day_elem:
                        continue
                        
                    month = month_elem.get_text(strip=True)
                    day = day_elem.get_text(strip=True)
                    
                    # Convert month abbreviation to number
                    month_map = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    
                    month_num = month_map.get(month)
                    if not month_num:
                        continue
                        
                    # Use current year (2025) for dates
                    year = "2025"
                    date_str = f"{year}-{month_num}-{day.zfill(2)}"
                    
                    # Extract event title
                    title_elem = card.find('a', class_='event-card__title')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract event body/description
                    body_elem = card.find('div', class_='event-card__body')
                    description = body_elem.get_text(strip=True) if body_elem else None
                    
                    # Extract time
                    time_elem = card.find('time')
                    time_str = None
                    if time_elem and time_elem.get('datetime'):
                        # Parse ISO datetime to get time
                        datetime_str = time_elem.get('datetime')
                        try:
                            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            time_str = dt.strftime('%I:%M %p')
                        except:
                            time_str = time_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = card.find('div', class_='event-card__location')
                    location = None
                    if location_elem:
                        # Get text content, excluding SVG icons
                        location_text = location_elem.get_text(strip=True)
                        if location_text and location_text not in ['TBD', 'TBA']:
                            location = location_text
                    
                    # Extract URL
                    url = None
                    if title_elem and title_elem.get('href'):
                        href = title_elem.get('href')
                        if href.startswith('http'):
                            url = href
                        else:
                            url = self.base_url + href
                    
                    # Extract seminar type
                    seminar_elem = card.find('span', class_='event-seminar-thumbnail')
                    seminar_type = None
                    if seminar_elem:
                        seminar_type_elem = seminar_elem.find('div', class_='field--name-name')
                        if seminar_type_elem:
                            seminar_type = seminar_type_elem.get_text(strip=True)
                    
                    # Create event object
                    event = {
                        'title': title,
                        'description': description,
                        'date': date_str,
                        'time': time_str,
                        'location': location,
                        'department': 'Mathematics',
                        'url': url,
                        'seminar_type': seminar_type,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Only add if we have essential data
                    if event['title'] and event['date']:
                        events.append(event)
                        print(f"  ✅ Added: {title} on {date_str}")
                    
                except Exception as e:
                    print(f"  ❌ Error parsing event card: {e}")
                    continue
            
            # Remove duplicates based on title and date
            unique_events = self._deduplicate_events(events)
            
            print(f"Found {len(unique_events)} Mathematics events")
            return unique_events
            
        except Exception as e:
            print(f"Error scraping Mathematics events: {e}")
            return []
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title and date"""
        seen = set()
        unique_events = []
        
        for event in events:
            key = (event['title'], event['date'])
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events

# Test the scraper
if __name__ == "__main__":
    scraper = MathematicsCloudScraper()
    events = scraper.scrape_mathematics_events()
    
    print(f"\n📊 SCRAPING RESULTS:")
    print(f"Total events found: {len(events)}")
    
    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event['title']}")
        print(f"   Date: {event['date']}")
        print(f"   Time: {event['time']}")
        print(f"   Location: {event['location']}")
        print(f"   Type: {event['seminar_type']}")
    
    # Save to JSON for inspection
    with open('mathematics_events_test.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"\n💾 Saved to: mathematics_events_test.json")
