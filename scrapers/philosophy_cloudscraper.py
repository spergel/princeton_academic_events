#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

class PhilosophyCloudScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.base_url = "https://philosophy.princeton.edu"
        self.events_url = f"{self.base_url}/events"
        
    def scrape_events(self):
        """Scrape events from Philosophy department"""
        print("🤔 Scraping Philosophy Department Events...")
        
        try:
            # Get the main events page
            response = self.scraper.get(self.events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save raw HTML for debugging
            with open('philosophy_cloudscraper_content.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            events = []
            
            # Look for event containers - Philosophy uses specific structure
            # Find all elements that contain event information
            event_containers = soup.find_all(['div', 'article'], class_=lambda x: x and 'event' in x.lower() if x else False)
            
            if not event_containers:
                # Fallback: look for any div that might contain event info
                event_containers = soup.find_all('div')
            
            print(f"Found {len(event_containers)} potential event containers")
            
            # Process each container to find events
            for container in event_containers:
                try:
                    # Look for date patterns in this container
                    date_spans = container.find_all('span', class_=lambda x: x and 'day-time-separator' in x if x else False)
                    
                    if date_spans:
                        # This container has date information, extract the event
                        event = self.extract_event_from_container(container)
                        if event:
                            events.append(event)
                            print(f"  ✅ Added: {event['title'][:50]}... on {event.get('start_date', 'NO DATE')}")
                
                except Exception as e:
                    continue
            
            # If we didn't find events with the structured approach, try a different method
            if len(events) < 5:
                print("  🔍 Trying alternative event extraction method...")
                events.extend(self.extract_events_alternative(soup))
            
            # Remove duplicates
            unique_events = self._deduplicate_events(events)
            
            print(f"\n📊 Philosophy Events Summary:")
            print(f"Total events found: {len(unique_events)}")
            
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Philosophy events: {str(e)}")
            return []
    
    def extract_event_from_container(self, container):
        """Extract event information from a container with date information"""
        try:
            # Extract date
            date_span = container.find('span', class_=lambda x: x and 'day-time-separator' in x if x else False)
            if not date_span:
                return None
            
            # Get the text content around the date span
            date_text = date_span.get_text(strip=True)
            if not date_text:
                return None
            
            # Parse date like "Fri, Sep 19, 2025"
            date_match = re.search(r'(\w+), (\w+) (\d{1,2}), (\d{4})', date_text)
            if not date_match:
                return None
            
            day_of_week, month, day, year = date_match.groups()
            
            # Convert month abbreviation to number
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            
            month_num = month_map.get(month)
            if not month_num:
                return None
            
            start_date = f"{year}-{month_num}-{day.zfill(2)}"
            
            # Extract time
            time_spans = container.find_all('span', class_=lambda x: x and 'date-range-separator' in x if x else False)
            time_str = ""
            if time_spans:
                # Get the text between time spans
                time_text = container.get_text()
                time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)\s*–\s*(\d{1,2}:\d{2}\s*[ap]m)', time_text, re.IGNORECASE)
                if time_match:
                    time_str = f"{time_match.group(1)} – {time_match.group(2)}"
            
            # Extract title - look for links or headings
            title = None
            title_elem = container.find('a', href=True)
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            if not title:
                # Look for any text that might be a title
                text_content = container.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in lines:
                    if len(line) > 10 and not any(skip in line.lower() for skip in ['filters', 'event category', 'upcoming', 'location', 'affiliation']):
                        title = line
                        break
            
            if not title or len(title) < 5:
                return None
            
            # Extract location
            location = None
            location_elem = container.find(text=re.compile(r'Fine Hall|Room|Auditorium|Building', re.IGNORECASE))
            if location_elem:
                location = location_elem.strip()
            
            # Extract URL
            url = None
            if title_elem and title_elem.get('href'):
                href = title_elem.get('href')
                if href.startswith('http'):
                    url = href
                else:
                    url = self.base_url + href
            
            # Create event object
            event = {
                'title': title,
                'start_date': start_date,
                'time': time_str,
                'location': location,
                'department': 'Philosophy',
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            return event
            
        except Exception as e:
            return None
    
    def extract_events_alternative(self, soup):
        """Alternative method to extract events if the structured approach fails"""
        events = []
        
        try:
            # Look for any text that contains date patterns
            all_text = soup.get_text()
            
            # Find date patterns like "Fri, Sep 19, 2025"
            date_pattern = r'(\w+), (\w+) (\d{1,2}), (\d{4})'
            date_matches = re.finditer(date_pattern, all_text)
            
            for match in date_matches:
                try:
                    day_of_week, month, day, year = match.groups()
                    
                    # Convert month abbreviation to number
                    month_map = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    
                    month_num = month_map.get(month)
                    if not month_num:
                        continue
                    
                    start_date = f"{year}-{month_num}-{day.zfill(2)}"
                    
                    # Get surrounding text to find title
                    start_pos = max(0, match.start() - 300)
                    end_pos = min(len(all_text), match.end() + 300)
                    context = all_text[start_pos:end_pos]
                    
                    # Look for potential titles in context - be more selective
                    lines = [line.strip() for line in context.split('\n') if line.strip()]
                    title = None
                    
                    for line in lines:
                        # More strict filtering to avoid corrupted titles
                        if (len(line) > 15 and len(line) < 80 and  # Reasonable title length
                            not any(skip in line.lower() for skip in [
                                'filters', 'event category', 'upcoming', 'location', 
                                'affiliation', 'department of', 'september', 'october',
                                'november', 'december', 'january', 'february', 'march',
                                'april', 'may', 'june', 'july', 'august'
                            ]) and
                            not line.isdigit() and
                            not re.match(r'^\d{1,2}:\d{2}', line) and  # Not time
                            not re.match(r'^[A-Z][a-z]{2}, \w+ \d{1,2}, \d{4}', line) and  # Not date
                            not line.startswith('i, ') and  # Not corrupted fragments
                            not line.startswith('hout ') and
                            not line.startswith('an ') and
                            line[0].isupper()):  # Should start with capital letter
                            title = line
                            break
                    
                    if title and len(title) < 100:  # Reasonable title length
                        event = {
                            'title': title,
                            'start_date': start_date,
                            'time': None,
                            'location': None,
                            'department': 'Philosophy',
                            'url': self.events_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                        events.append(event)
                
                except Exception as e:
                    continue
            
        except Exception as e:
            pass
        
        return events
    
    def _deduplicate_events(self, events):
        """Remove duplicate events based on title and date"""
        seen = set()
        unique_events = []
        
        for event in events:
            key = (event['title'], event.get('start_date'))
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events

# Test the scraper
if __name__ == "__main__":
    scraper = PhilosophyCloudScraper()
    events = scraper.scrape_events()
    
    print(f"\n📊 SCRAPING RESULTS:")
    print(f"Total events found: {len(events)}")
    
    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event['title']}")
        print(f"   Date: {event.get('start_date', 'NO DATE')}")
        print(f"   Time: {event.get('time', 'NO TIME')}")
        print(f"   Location: {event.get('location', 'NO LOCATION')}")
    
    # Save to JSON for inspection
    with open('philosophy_events_test.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"\n💾 Saved to: philosophy_events_test.json")
