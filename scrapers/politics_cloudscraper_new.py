#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class PoliticsCloudScraperNew:
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
        self.base_url = "https://politics.princeton.edu"
        
    def scrape_politics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Politics department using the new HTML structure"""
        print("🗳️ SCRAPING POLITICS EVENTS (NEW SCRAPER)")
        print("=" * 60)
        
        events = []
        
        try:
            print(f"🔍 Scraping Politics events from: {self.base_url}/events")
            response = self.scraper.get(f"{self.base_url}/events", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event containers based on the HTML structure provided
            event_containers = soup.find_all('div', class_='node--type-event')
            print(f"    🔍 Found {len(event_containers)} event containers")
            
            if not event_containers:
                # Fallback: look for any divs with event-like content
                event_containers = soup.find_all('div', class_=re.compile(r'event|node', re.I))
                print(f"    🔍 Fallback: Found {len(event_containers)} potential containers")
            
            for i, container in enumerate(event_containers):
                try:
                    event = self._extract_event_from_container(container)
                    if event and event.get('title') and len(event['title']) > 10:
                        events.append(event)
                        print(f"      ✅ Added: {event['title'][:50]}... on {event.get('start_date', 'No date')}")
                    else:
                        print(f"      ⚠️  Skipped event {i+1}: insufficient data")
                except Exception as e:
                    print(f"      ❌ Error extracting event {i+1}: {e}")
                    continue
            
            # Remove duplicates
            unique_events = self._deduplicate_events(events)
            
            print(f"🎯 Total events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Politics events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a container element using the specific HTML structure"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': '',
            'event_type': 'Colloquium',
            'department': 'Politics',
            'meta_category': 'social_sciences',
            'source_url': f"{self.base_url}/events",
            'source_name': 'Politics Department Events',
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title from the specific HTML structure
        title_elem = container.find('div', class_='field--name-node-title')
        if title_elem:
            title_link = title_elem.find('a')
            if title_link:
                title = title_link.get_text(strip=True)
                if title and len(title) > 5:
                    event['title'] = title
                    # Extract URL for source_url
                    href = title_link.get('href')
                    if href:
                        if href.startswith('/'):
                            event['source_url'] = self.base_url + href
                        elif href.startswith('http'):
                            event['source_url'] = href
                    # Generate ID
                    event['id'] = f"politics_{datetime.now().strftime('%Y%m%d')}_{title[:20].replace(' ', '_')}"
        
        # Extract date from the specific HTML structure
        month_elem = container.find('div', class_='field--name-dynamic-token-fieldnode-event-month')
        day_elem = container.find('div', class_='field--name-dynamic-token-fieldnode-event-day')
        
        if month_elem and day_elem:
            month = month_elem.get_text(strip=True)
            day = day_elem.get_text(strip=True)
            if month and day:
                # Assume current year for now
                current_year = datetime.now().year
                date_str = f"{month} {day}, {current_year}"
                event['start_date'] = self._parse_date(date_str)
        
        # Extract time from the specific HTML structure
        time_elem = container.find('div', class_='field--name-dynamic-token-fieldnode-start-time-only')
        if time_elem:
            event['time'] = time_elem.get_text(strip=True)
        
        # Extract location from the specific HTML structure
        location_elem = container.find('div', class_='field--name-field-event-location')
        if location_elem:
            event['location'] = location_elem.get_text(strip=True)
        else:
            # Check for location in body field as fallback
            body_elem = container.find('div', class_='field--name-body')
            if body_elem:
                body_text = body_elem.get_text(strip=True)
                # Look for location patterns in body text
                location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Hall|Building|Room|Center))', body_text)
                if location_match:
                    event['location'] = location_match.group(1)
                else:
                    event['location'] = 'Princeton University'
        
        # Extract description from body field
        body_elem = container.find('div', class_='field--name-body')
        if body_elem:
            event['description'] = body_elem.get_text(strip=True)
        
        # Extract event series for additional context
        series_elem = container.find('div', class_='field--name-field-related-event-series')
        if series_elem:
            series_link = series_elem.find('a')
            if series_link:
                series_text = series_link.get_text(strip=True)
                if series_text:
                    # Add series to description if no description exists
                    if not event['description']:
                        event['description'] = f"Part of the {series_text} series"
                    # Determine event type based on series
                    if 'colloquium' in series_text.lower():
                        event['event_type'] = 'Colloquium'
                    elif 'seminar' in series_text.lower():
                        event['event_type'] = 'Seminar'
                    elif 'lecture' in series_text.lower():
                        event['event_type'] = 'Lecture'
                    elif 'conference' in series_text.lower():
                        event['event_type'] = 'Conference'
        
        # Determine event type from title if not set
        if event['title'] and not event['event_type']:
            title_lower = event['title'].lower()
            if 'colloquium' in title_lower:
                event['event_type'] = 'Colloquium'
            elif 'seminar' in title_lower:
                event['event_type'] = 'Seminar'
            elif 'lecture' in title_lower:
                event['event_type'] = 'Lecture'
            elif 'conference' in title_lower:
                event['event_type'] = 'Conference'
            elif 'workshop' in title_lower:
                event['event_type'] = 'Workshop'
            else:
                event['event_type'] = 'Colloquium'  # Default for Politics
        
        # Extract tags
        event['tags'] = self._extract_tags(event['title'], event['description'])
        
        return event
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date text to YYYY-MM-DD format"""
        try:
            # Try different date formats
            date_formats = [
                '%b %d, %Y',    # Sep 15, 2025
                '%B %d, %Y',    # September 15, 2025
                '%b %d %Y',     # Sep 15 2025
                '%B %d %Y'      # September 15 2025
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_text, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
            
            return ""
        except:
            return ""
    
    def _extract_tags(self, title: str, description: str) -> List[str]:
        """Extract relevant tags"""
        text = (title + ' ' + description).lower()
        tags = []
        
        politics_tags = [
            'politics', 'political', 'colloquium', 'seminar', 'lecture', 'conference',
            'international relations', 'ir', 'csdp', 'american politics', 'comparative politics',
            'political theory', 'political economy', 'public policy', 'governance'
        ]
        
        for tag in politics_tags:
            if tag in text:
                tags.append(tag)
        
        return tags
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events"""
        seen = set()
        unique_events = []
        
        for event in events:
            key = f"{event.get('title', '')}_{event.get('start_date', '')}"
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def save_events(self, events: List[Dict[str, Any]], filename: str = 'politics_cloudscraper_new_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'department': 'Politics',
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': f"{self.base_url}/events",
                'source': 'Politics CloudScraper New',
                'note': 'Scraped from politics.princeton.edu/events using new HTML structure'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} Politics events to {filename}")

if __name__ == "__main__":
    scraper = PoliticsCloudScraperNew()
    events = scraper.scrape_politics_events()
    scraper.save_events(events)
