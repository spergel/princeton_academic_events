#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

class PhysicsCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.base_url = "https://physics.princeton.edu/events"
        
    def scrape_events(self):
        """Scrape events from Physics department"""
        print("🔬 Scraping Physics Department Events...")
        
        try:
            # Get the main events page
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save raw HTML for debugging
            with open('physics_cloudscraper_content.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            events = []
            
            # Look for event containers - Physics typically uses different selectors
            event_selectors = [
                '.event', '.events', '.calendar-event', '.seminar',
                '.lecture', '.colloquium', '.talk', '.workshop',
                '[class*="event"]', '[class*="seminar"]', '[class*="lecture"]',
                'article', '.node', '.content-item'
            ]
            
            event_elements = []
            for selector in event_selectors:
                elements = soup.select(selector)
                if elements:
                    event_elements.extend(elements)
                    print(f"Found {len(elements)} elements with selector: {selector}")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_elements = []
            for element in event_elements:
                element_str = str(element)
                if element_str not in seen:
                    seen.add(element_str)
                    unique_elements.append(element)
            
            print(f"Processing {len(unique_elements)} unique event elements...")
            
            for i, element in enumerate(unique_elements[:20]):  # Limit to first 20 for testing
                try:
                    event = self.parse_event_element(element, i)
                    if event:
                        events.append(event)
                        print(f"  ✅ Parsed event {i+1}: {event['title'][:50]}...")
                except Exception as e:
                    print(f"  ❌ Error parsing event {i+1}: {str(e)}")
                    continue
            
            print(f"\n📊 Physics Events Summary:")
            print(f"Total events found: {len(events)}")
            
            return events
            
        except Exception as e:
            print(f"❌ Error scraping Physics events: {str(e)}")
            return []
    
    def parse_event_element(self, element, index):
        """Parse individual event element"""
        try:
            # Extract title
            title = self.extract_title(element)
            if not title:
                return None
            
            # Extract description
            description = self.extract_description(element)
            
            # Extract date and time
            date_info = self.extract_date_time(element)
            
            # Extract location
            location = self.extract_location(element)
            
            # Extract event type
            event_type = self.extract_event_type(element, title)
            
            # Extract tags
            tags = self.extract_tags(element, title, description)
            
            # Create event object
            event = {
                'id': f"physics_{index}_{self.sanitize_id(title)}",
                'title': title,
                'description': description,
                'start_date': date_info.get('start_date'),
                'end_date': date_info.get('end_date'),
                'time': date_info.get('time'),
                'location': location,
                'event_type': event_type,
                'department': 'Physics',
                'meta_category': 'science_engineering',
                'source_url': self.base_url,
                'source_name': 'Physics Department Events',
                'tags': tags,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            return event
            
        except Exception as e:
            print(f"    Error parsing event element: {str(e)}")
            return None
    
    def extract_title(self, element):
        """Extract event title"""
        # Try multiple selectors for title
        title_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '.title', '.event-title', '.seminar-title',
            '[class*="title"]', '[class*="name"]'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 3:
                    return title
        
        # Fallback: get first text content
        text = element.get_text().strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            return lines[0][:100]  # Limit length
        
        return None
    
    def extract_description(self, element):
        """Extract event description"""
        # Try to find description in paragraphs or divs
        desc_selectors = [
            'p', '.description', '.summary', '.abstract',
            '[class*="description"]', '[class*="summary"]'
        ]
        
        descriptions = []
        for selector in desc_selectors:
            desc_elems = element.select(selector)
            for desc_elem in desc_elems:
                text = desc_elem.get_text().strip()
                if text and len(text) > 10:
                    descriptions.append(text)
        
        if descriptions:
            return ' '.join(descriptions[:3])  # Combine first 3 descriptions
        
        return ""
    
    def extract_date_time(self, element):
        """Extract date and time information"""
        # Look for date/time patterns in text
        text = element.get_text()
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\w+ \d{1,2},? \d{4})',
            r'(\d{1,2} \w+ \d{4})'
        ]
        
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*[AP]M)',
            r'(\d{1,2}:\d{2})'
        ]
        
        start_date = None
        time = ""
        
        # Find date
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse the date
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            start_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    elif '-' in date_str:
                        start_date = date_str
                    break
                except:
                    continue
        
        # Find time
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                time = match.group(1)
                break
        
        return {
            'start_date': start_date,
            'end_date': None,
            'time': time
        }
    
    def extract_location(self, element):
        """Extract event location"""
        text = element.get_text()
        
        # Look for common location indicators
        location_indicators = [
            'Room', 'Hall', 'Building', 'Center', 'Auditorium',
            'Lecture Hall', 'Seminar Room', 'Conference Room'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(indicator in line for indicator in location_indicators):
                return line
        
        return "TBD"
    
    def extract_event_type(self, element, title):
        """Extract event type from title and content"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['seminar', 'seminars']):
            return 'Seminar'
        elif any(word in title_lower for word in ['lecture', 'lectures']):
            return 'Lecture'
        elif any(word in title_lower for word in ['colloquium', 'colloquia']):
            return 'Colloquium'
        elif any(word in title_lower for word in ['talk', 'talks']):
            return 'Talk'
        elif any(word in title_lower for word in ['workshop', 'workshops']):
            return 'Workshop'
        elif any(word in title_lower for word in ['conference', 'conferences']):
            return 'Conference'
        else:
            return 'Academic Event'
    
    def extract_tags(self, element, title, description):
        """Extract relevant tags"""
        text = (title + ' ' + description).lower()
        
        tags = []
        
        # Physics-specific tags
        physics_tags = [
            'quantum', 'particle', 'condensed matter', 'astrophysics',
            'cosmology', 'plasma', 'nuclear', 'optics', 'biophysics',
            'theoretical', 'experimental', 'computational'
        ]
        
        for tag in physics_tags:
            if tag in text:
                tags.append(tag)
        
        return tags
    
    def sanitize_id(self, title):
        """Create a sanitized ID from title"""
        # Remove special characters and limit length
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:30].lower()
    
    def save_events(self, events, filename='physics_cloudscraper_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'department': 'Physics',
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.base_url,
                'source': 'Physics CloudScraper',
                'note': 'Scraped from physics.princeton.edu/events using cloudscraper'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} Physics events to {filename}")

if __name__ == "__main__":
    scraper = PhysicsCloudScraper()
    events = scraper.scrape_events()
    scraper.save_events(events)
