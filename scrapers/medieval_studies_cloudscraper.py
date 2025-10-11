#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
from typing import List, Dict, Any

class MedievalStudiesCloudScraper:
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
        self.base_url = "https://medievalstudies.princeton.edu"
        self.events_url = "https://medievalstudies.princeton.edu/events"
        self.department_name = "Medieval Studies"
        self.meta_category = "arts_humanities"
        
    def scrape_medieval_studies_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Medieval Studies department using The Events Calendar"""
        print(f"🏰 SCRAPING {self.department_name.upper()} EVENTS")
        print("=" * 60)
        
        all_events = []
        page = 1
        max_pages = 10  # Safety limit
        
        try:
            while page <= max_pages:
                # Build URL for current page
                if page == 1:
                    url = self.events_url
                else:
                    url = f"{self.events_url}/page/{page}/"
                
                print(f"🔍 Scraping page {page} from: {url}")
                
                response = self.scraper.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find event containers - Medieval Studies uses tribe-events-calendar-list__event-row
                event_containers = soup.find_all('div', class_='tribe-events-calendar-list__event-row')
                print(f"    🔍 Found {len(event_containers)} events on page {page}")
                
                if not event_containers:
                    print(f"    ⚠️  No events found on page {page}")
                    break
                
                # Extract events from this page
                for container in event_containers:
                    event = self._extract_event_from_container(container)
                    if event and event.get('title'):
                        # Get additional details from individual event page
                        if event.get('source_url'):
                            detailed_event = self._fetch_event_details(event['source_url'])
                            if detailed_event:
                                event.update(detailed_event)
                        
                        all_events.append(event)
                
                # Check for pagination
                if not self._has_next_page(soup, page):
                    break
                
                page += 1
                time.sleep(2)  # Be respectful
            
            # Remove duplicates and sort by date
            unique_events = self._deduplicate_events(all_events)
            unique_events.sort(key=lambda x: x.get('start_date', ''))
            
            print(f"🎯 Total unique events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Medieval Studies events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a container"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': 'Princeton University',
            'event_type': 'Event',
            'department': self.department_name,
            'meta_category': self.meta_category,
            'source_url': '',
            'source_name': f'{self.department_name} Department Events',
            'speaker': '',
            'audience': '',
            'topics': [],
            'departments': [],
            'tags': [],
            'series': '',
            'sponsor': '',
            'image_url': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title and URL
        title_elem = container.find('h3', class_='tribe-events-calendar-list__event-title')
        if title_elem:
            title_link = title_elem.find('a')
            if title_link:
                event['title'] = title_link.get_text(strip=True)
                href = title_link.get('href')
                if href:
                    event['source_url'] = href
                    event['id'] = f"{self.department_name.lower()}_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract date and time from tribe-event-schedule-details
        schedule_elem = container.find('div', class_='tribe-event-schedule-details')
        if schedule_elem:
            time_elem = schedule_elem.find('time', class_='tribe-events-calendar-list__event-datetime')
            if time_elem:
                # Extract datetime attribute
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        # Parse ISO datetime
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        event['start_date'] = dt.strftime('%Y-%m-%d')
                        event['time'] = dt.strftime('%I:%M %p')
                    except:
                        pass
                
                # Also extract the display text
                date_span = time_elem.find('span', class_='tribe-event-date-start')
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    # Parse date text like "Tue, 9/9 · 4:30 pm"
                    parsed_date = self._parse_date_text(date_text)
                    if parsed_date:
                        event['start_date'] = parsed_date['date']
                        event['time'] = parsed_date['time']
        
        # Extract location from tribe-events-calendar-list__event-venue
        venue_elem = container.find('address', class_='tribe-events-calendar-list__event-venue')
        if venue_elem:
            venue_title = venue_elem.find('span', class_='tribe-events-calendar-list__event-venue-title')
            if venue_title:
                event['location'] = venue_title.get_text(strip=True)
        
        # Extract sponsor information
        sponsor_elem = container.find('h5', class_='tribe-event-sponsor')
        if sponsor_elem:
            event['sponsor'] = sponsor_elem.get_text(strip=True)
            event['tags'].append(sponsor_elem.get_text(strip=True))
        
        # Extract image URL
        img_elem = container.find('img', class_='tribe-events-calendar-list__event-featured-image')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src')
            if src:
                event['image_url'] = src
        
        # Determine event type and tags
        event['event_type'] = self._determine_event_type(event['title'])
        event['tags'].extend(self._extract_tags(event['title'], event.get('sponsor', '')))
        
        return event
    
    def _parse_date_text(self, date_text: str) -> Dict[str, str]:
        """Parse date text like 'Tue, 9/9 · 4:30 pm'"""
        try:
            # Split by the bullet point
            parts = date_text.split('·')
            if len(parts) >= 2:
                date_part = parts[0].strip()
                time_part = parts[1].strip()
                
                # Parse date part (e.g., "Tue, 9/9")
                date_match = re.search(r'(\d{1,2})/(\d{1,2})', date_part)
                if date_match:
                    month = date_match.group(1)
                    day = date_match.group(2)
                    # Assume current year
                    current_year = datetime.now().year
                    formatted_date = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    return {
                        'date': formatted_date,
                        'time': time_part
                    }
        except:
            pass
        
        return None
    
    def _fetch_event_details(self, event_url: str) -> Dict[str, Any]:
        """Fetch detailed information from individual event page"""
        try:
            print(f"    🔍 Fetching details from: {event_url}")
            response = self.scraper.get(event_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract description from meta tag or content
            desc_elem = soup.find('meta', {'name': 'description'})
            if desc_elem and desc_elem.get('content'):
                details['description'] = desc_elem.get('content')
            
            # Try to find description in structured data
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, list) and len(data) > 0:
                        event_data = data[0]
                        if 'description' in event_data:
                            details['description'] = event_data['description']
                        if 'startDate' in event_data:
                            # Parse ISO datetime
                            start_dt = datetime.fromisoformat(event_data['startDate'].replace('Z', '+00:00'))
                            details['start_date'] = start_dt.strftime('%Y-%m-%d')
                            details['time'] = start_dt.strftime('%I:%M %p')
                        if 'endDate' in event_data:
                            end_dt = datetime.fromisoformat(event_data['endDate'].replace('Z', '+00:00'))
                            details['end_date'] = end_dt.strftime('%Y-%m-%d')
                        if 'location' in event_data and 'name' in event_data['location']:
                            details['location'] = event_data['location']['name']
                except:
                    pass
            
            # Extract additional content from the page
            content_elem = soup.find('div', class_='tribe-events-single-event-description')
            if content_elem:
                content_text = content_elem.get_text().lower()
                additional_tags = self._extract_content_tags(content_text)
                if additional_tags:
                    details['tags'] = additional_tags
            
            return details
            
        except Exception as e:
            print(f"    ⚠️  Error fetching event details: {e}")
            return {}
    
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
            'book club': 'Book Club',
            'reception': 'Reception',
            'welcome': 'Welcome Event',
            'study group': 'Study Group',
            'reading group': 'Reading Group'
        }
        
        for keyword, event_type in type_keywords.items():
            if keyword in title_lower:
                return event_type
        
        return 'Event'
    
    def _extract_tags(self, title: str, sponsor: str) -> List[str]:
        """Extract relevant tags from title and sponsor"""
        text = (title + ' ' + sponsor).lower()
        tags = []
        
        # Add department-specific tags
        medieval_tags = [
            'medieval', 'medieval studies', 'csla', 'committee for the study of late antiquity',
            'late antiquity', 'medieval book club', 'medieval studies book club',
            'princeton', 'university', 'academic', 'event', 'humanities'
        ]
        
        for tag in medieval_tags:
            if tag in text and tag not in tags:
                tags.append(tag)
        
        # Add general tags
        general_tags = ['princeton', 'university', 'academic', 'event']
        for tag in general_tags:
            if tag in text and tag not in tags:
                tags.append(tag)
        
        return tags
    
    def _extract_content_tags(self, content_text: str) -> List[str]:
        """Extract additional tags from event content"""
        tags = []
        
        # Look for specific content indicators
        content_keywords = [
            'medieval', 'medieval studies', 'late antiquity', 'csla',
            'book club', 'reading group', 'study group', 'reception',
            'welcome', 'faculty', 'students', 'graduate', 'undergraduate',
            'research', 'scholarship', 'academic', 'humanities'
        ]
        
        for keyword in content_keywords:
            if keyword in content_text and keyword not in tags:
                tags.append(keyword)
        
        return tags
    
    def _has_next_page(self, soup, current_page: int) -> bool:
        """Check if there's a next page"""
        # Look for pagination controls
        pagination = soup.find('nav', class_='tribe-events-nav-pagination') or soup.find('div', class_='tribe-events-pagination')
        
        if pagination:
            # Check for next page link
            next_link = pagination.find('a', string=re.compile(r'Next', re.I))
            if next_link:
                return True
            
            # Check page numbers
            page_links = pagination.find_all('a', href=True)
            page_numbers = []
            for link in page_links:
                href = link.get('href', '')
                if '/page/' in href:
                    page_match = re.search(r'/page/(\d+)/', href)
                    if page_match:
                        page_numbers.append(int(page_match.group(1)))
            
            if page_numbers and current_page < max(page_numbers):
                return True
        
        return False
    
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
            filename = f'{self.department_name.lower().replace(" ", "_")}_cloudscraper_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.events_url,
                'source': f'{self.department_name} CloudScraper',
                'note': f'Scraped from {self.events_url} using The Events Calendar'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    scraper = MedievalStudiesCloudScraper()
    events = scraper.scrape_medieval_studies_events()
    scraper.save_events(events)
