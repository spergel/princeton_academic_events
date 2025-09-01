#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

class HistoryCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.base_url = "https://history.princeton.edu/events"
        
    def scrape_events(self):
        """Scrape events from History department"""
        print("📚 Scraping History Department Events...")
        
        try:
            # Get the main events page
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            
            # Find all content list items (each represents an event)
            event_items = soup.select('.content-list-item')
            print(f"Found {len(event_items)} event items")
            
            for i, item in enumerate(event_items[:20]):  # Limit to first 20 for testing
                try:
                    event = self.parse_event_item(item, i)
                    if event:
                        events.append(event)
                        print(f"  ✅ Parsed event {i+1}: {event['title'][:50]}...")
                except Exception as e:
                    print(f"  ❌ Error parsing event {i+1}: {str(e)}")
                    continue
            
            print(f"\n📊 History Events Summary:")
            print(f"Total events found: {len(events)}")
            
            return events
            
        except Exception as e:
            print(f"❌ Error scraping History events: {str(e)}")
            return []
    
    def parse_event_item(self, item, index):
        """Parse individual event item"""
        try:
            # Extract title
            title = self.extract_title(item)
            if not title:
                return None
            
            # Extract description
            description = self.extract_description(item)
            
            # Extract date and time
            date_info = self.extract_date_time(item)
            
            # Extract location
            location = self.extract_location(item)
            
            # Extract URL
            url = self.extract_url(item)
            
            # Create event object
            event = {
                'event_id': f"history_{index + 1}_{self.sanitize_title(title)}",
                'title': title,
                'description': description,
                'date': date_info.get('start_date'),
                'time': date_info.get('time'),
                'location': location,
                'department': 'History',
                'url': url,
                'category': 'humanities'
            }
            
            return event
            
        except Exception as e:
            print(f"    Error parsing event item: {str(e)}")
            return None
    
    def extract_title(self, item):
        """Extract event title"""
        # Look for title in the title field
        title_elem = item.select_one('.field--name-title a')
        if title_elem:
            return title_elem.get_text().strip()
        
        # Fallback: look for any heading or link text
        title_elem = item.select_one('h1, h2, h3, h4, h5, h6, a[href*="/events/"]')
        if title_elem:
            return title_elem.get_text().strip()
        
        return None
    
    def extract_description(self, item):
        """Extract event description"""
        # Look for series information
        series_elem = item.select_one('.field--name-field-history-scholarly-series a')
        if series_elem:
            return f"Series: {series_elem.get_text().strip()}"
        
        return ""
    
    def extract_date_time(self, item):
        """Extract date and time information from Drupal date field"""
        # Look for the date field that contains the full date (not the badge)
        # The badge is in .content-list-item-date-badge, we want the one in .content-list-item-fields
        date_field = item.select_one('.content-list-item-fields .field--name-field-ps-events-date')
        if not date_field:
            return {'start_date': None, 'time': None}
        
        # Look for the full date text in the day span
        day_elem = date_field.select_one('span.day')
        time_elem = date_field.select_one('span.time')
        
        start_date = None
        time = ""
        
        if day_elem:
            date_text = day_elem.get_text().strip()
            
            # Parse date like "Monday, September 8, 2025"
            try:
                # Remove day of week and parse
                date_parts = date_text.split(', ')
                if len(date_parts) >= 2:
                    month_day = date_parts[1]  # "September 8"
                    year = date_parts[2] if len(date_parts) > 2 else "2025"
                    
                    # Parse month and day
                    month_map = {
                        'January': '01', 'February': '02', 'March': '03', 'April': '04',
                        'May': '05', 'June': '06', 'July': '07', 'August': '08',
                        'September': '09', 'October': '10', 'November': '11', 'December': '12'
                    }
                    
                    month_day_parts = month_day.split(' ')
                    if len(month_day_parts) == 2:
                        month = month_map.get(month_day_parts[0])
                        day = month_day_parts[1].zfill(2)
                        if month:
                            start_date = f"{year}-{month}-{day}"
            except:
                pass
        
        if time_elem:
            time = time_elem.get_text().strip()
        
        return {
            'start_date': start_date,
            'time': time
        }
    
    def extract_location(self, item):
        """Extract event location"""
        location_field = item.select_one('.field--name-field-ps-events-location-name .field__item')
        if location_field:
            return location_field.get_text().strip()
        
        return "TBD"
    
    def extract_url(self, item):
        """Extract event URL"""
        title_link = item.select_one('.field--name-title a')
        if title_link and title_link.get('href'):
            href = title_link.get('href')
            if href.startswith('/'):
                return f"https://history.princeton.edu{href}"
            return href
        
        return "https://history.princeton.edu/events"
    
    def sanitize_title(self, title):
        """Create a sanitized ID from title"""
        if not title:
            return "unknown"
        # Remove special characters and spaces
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized).lower()
        return sanitized[:50]  # Limit length
    
    def _deduplicate_events(self, events):
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
    scraper = HistoryCloudScraper()
    events = scraper.scrape_events()
    
    # Save to JSON for inspection
    with open('history_events_test.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved {len(events)} events to history_events_test.json")
