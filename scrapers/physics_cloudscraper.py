#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
from typing import List, Dict, Any

class PhysicsCloudScraper:
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
        self.base_url = "https://phy.princeton.edu"
        self.events_url = "https://phy.princeton.edu/events"
        self.department_name = "Physics"
        self.meta_category = "sciences_engineering"
        
    def scrape_physics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Physics department using their FullCalendar widget"""
        print(f"⚛️ SCRAPING {self.department_name.upper()} EVENTS")
        print("=" * 60)
        
        all_events = []
        
        try:
            print(f"🔍 Fetching events from: {self.events_url}")
            
            # First, let's try to get the page with CloudScraper
            response = self.scraper.get(self.events_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we got a Cloudflare challenge page
            if "Just a moment" in response.text or "Cloudflare" in response.text:
                print("⚠️  Cloudflare challenge detected, trying alternative approach...")
                # Try to find any event-related content
                all_text = soup.get_text()
                if "fc-events-list" in all_text:
                    print("✅ Found calendar content in page")
                else:
                    print("❌ No calendar content found")
                    return []
            
            # Find the FullCalendar events list
            events_list = soup.find('ul', class_='fc-events-list')
            if not events_list:
                print("🔍 Looking for alternative event containers...")
                # Try to find any event-like content
                event_containers = soup.find_all(['div', 'li'], class_=lambda x: x and any(word in str(x).lower() for word in ['event', 'calendar', 'fc-']))
                if event_containers:
                    print(f"🔍 Found {len(event_containers)} potential event containers")
                    # Try to extract events from these containers
                    for container in event_containers:
                        event = self._extract_event_from_alternative_container(container)
                        if event and event.get('title'):
                            all_events.append(event)
                else:
                    print("❌ No events list or alternative containers found")
                    print("📄 Page content preview:", soup.get_text()[:500])
                    return []
            else:
                # Extract events from the list
                event_items = events_list.find_all('li')
                print(f"🔍 Found {len(event_items)} events in calendar list")
                
                for item in event_items:
                    event = self._extract_event_from_item(item)
                    if event and event.get('title'):
                        # Get additional details from individual event page
                        if event.get('source_url'):
                            detailed_event = self._fetch_event_details(event['source_url'])
                            if detailed_event:
                                event.update(detailed_event)
                        
                        all_events.append(event)
            
            # Remove duplicates and sort by date
            unique_events = self._deduplicate_events(all_events)
            unique_events.sort(key=lambda x: x.get('start_date', ''))
            
            print(f"🎯 Total unique events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Physics events: {e}")
            return []
    
    def _extract_event_from_item(self, item) -> Dict[str, Any]:
        """Extract event information from a FullCalendar list item"""
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
            'image_url': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title and URL
        title_elem = item.find('div', class_='fc-event-title')
        if title_elem:
            title_link = title_elem.find('a')
            if title_link:
                event['title'] = title_link.get_text(strip=True)
                href = title_link.get('href')
                if href.startswith('http'):
                    event['source_url'] = href
                else:
                    event['source_url'] = self.base_url + href
                
                event['id'] = f"{self.department_name.lower()}_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract date and time
        date_elem = item.find('div', class_='fc-event-date')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            # Remove "Date:" prefix if present
            date_text = re.sub(r'^Date:\s*', '', date_text)
            
            # Parse the date and time
            parsed_info = self._parse_physics_date(date_text)
            if parsed_info:
                event['start_date'] = parsed_info.get('date', '')
                event['time'] = parsed_info.get('time', '')
                event['end_time'] = parsed_info.get('end_time', '')
        
        # Extract series information from title
        if event.get('title'):
            event['series'] = self._extract_series_from_title(event['title'])
            event['event_type'] = self._determine_event_type(event['title'])
            event['tags'].extend(self._extract_tags(event['title'], event.get('series', '')))
        
        return event
    
    def _extract_event_from_alternative_container(self, container) -> Dict[str, Any]:
        """Extract event information from alternative containers when calendar is not available"""
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
            'image_url': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Try to extract any text that might be event-related
        text = container.get_text(strip=True)
        if len(text) > 10 and any(word in text.lower() for word in ['seminar', 'colloquium', 'lecture', 'event']):
            event['title'] = text[:100]  # Use first 100 chars as title
            event['id'] = f"{self.department_name.lower()}_{datetime.now().strftime('%Y%m%d')}_{text[:20].replace(' ', '_')}"
            event['tags'].extend(self._extract_tags(text, ''))
        
        return event
    
    def _parse_physics_date(self, date_text: str) -> Dict[str, str]:
        """Parse Physics department date format: 'Sep 8, 2025, 12:30 p.m. – 1:30 p.m.'"""
        try:
            # Pattern: "Sep 8, 2025, 12:30 p.m. – 1:30 p.m."
            pattern = r'(\w+)\s+(\d{1,2}),?\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)\s*–\s*(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)'
            match = re.search(pattern, date_text)
            
            if match:
                month, day, year, start_hour, start_min, start_ampm, end_hour, end_min, end_ampm = match.groups()
                
                # Convert month abbreviation to number
                month_num = self._month_to_number(month)
                
                # Format date
                date = f"{year}-{month_num}-{day.zfill(2)}"
                
                # Format start time
                start_time = self._format_time(start_hour, start_min, start_ampm)
                
                # Format end time
                end_time = self._format_time(end_hour, end_min, end_ampm)
                
                # Combine times
                time_range = f"{start_time} - {end_time}"
                
                return {
                    'date': date,
                    'time': time_range,
                    'end_time': end_time
                }
            
            # Try simpler pattern without end time: "Sep 8, 2025, 12:30 p.m."
            simple_pattern = r'(\w+)\s+(\d{1,2}),?\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)'
            simple_match = re.search(simple_pattern, date_text)
            
            if simple_match:
                month, day, year, hour, minute, ampm = simple_match.groups()
                month_num = self._month_to_number(month)
                date = f"{year}-{month_num}-{day.zfill(2)}"
                time = self._format_time(hour, minute, ampm)
                
                return {
                    'date': date,
                    'time': time,
                    'end_time': ''
                }
            
        except Exception as e:
            print(f"    ⚠️  Error parsing date: {date_text} - {e}")
        
        return {}
    
    def _format_time(self, hour: str, minute: str, ampm: str) -> str:
        """Format time from hour, minute, and AM/PM"""
        hour_int = int(hour)
        minute_int = int(minute)
        
        # Convert to 12-hour format
        if ampm.lower() == 'p.m.' and hour_int != 12:
            hour_int += 12
        elif ampm.lower() == 'a.m.' and hour_int == 12:
            hour_int = 0
        
        return f"{hour_int:02d}:{minute_int:02d}"
    
    def _month_to_number(self, month: str) -> str:
        """Convert month abbreviation to number"""
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return months.get(month, '01')
    
    def _extract_series_from_title(self, title: str) -> str:
        """Extract series information from event title"""
        # Physics department uses patterns like "CPBF Seminar Series | ..."
        series_patterns = [
            r'^([^|]+)\s*\|',  # Everything before the first |
            r'^([^:]+):',      # Everything before the first :
            r'^([^(]+)\s*\(',  # Everything before the first (
        ]
        
        for pattern in series_patterns:
            match = re.search(pattern, title)
            if match:
                series = match.group(1).strip()
                # Clean up common series names
                if 'seminar' in series.lower():
                    return series
                elif 'colloquium' in series.lower():
                    return series
                elif 'lecture' in series.lower():
                    return series
        
        return ""
    
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
            'exam': 'Exam',
            'office hours': 'Office Hours',
            'fpo': 'PhD Defense',
            'distinguished lecture': 'Distinguished Lecture'
        }
        
        for keyword, event_type in type_keywords.items():
            if keyword in title_lower:
                return event_type
        
        return 'Event'
    
    def _extract_tags(self, title: str, series: str) -> List[str]:
        """Extract relevant tags from title and series"""
        text = (title + ' ' + series).lower()
        tags = []
        
        # Add department-specific tags
        physics_tags = [
            'physics', 'physical', 'quantum', 'particle', 'nuclear', 'astrophysics',
            'biophysics', 'condensed matter', 'high energy', 'theoretical', 'experimental',
            'mathematical physics', 'cosmology', 'gravity', 'atomic', 'molecular',
            'statistical mechanics', 'phenomenology', 'cpbf', 'het', 'pcts', 'pqi'
        ]
        
        for tag in physics_tags:
            if tag in text:
                tags.append(tag)
        
        # Add general tags
        general_tags = ['princeton', 'university', 'academic', 'event', 'research']
        for tag in general_tags:
            if tag in text and tag not in tags:
                tags.append(tag)
        
        return tags
    
    def _fetch_event_details(self, event_url: str) -> Dict[str, Any]:
        """Fetch detailed information from individual event page"""
        try:
            print(f"    🔍 Fetching details from: {event_url}")
            response = self.scraper.get(event_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract description
            desc_elem = soup.find('meta', {'name': 'description'})
            if desc_elem and desc_elem.get('content'):
                details['description'] = desc_elem.get('content')
            
            # Extract location if available
            location_elem = soup.find('div', class_='field--name-field-ps-events-location-name')
            if location_elem:
                details['location'] = location_elem.get_text(strip=True)
            
            # Extract speaker if available
            speaker_elem = soup.find('div', class_='field--name-field-ps-events-speaker')
            if speaker_elem:
                speaker_name = speaker_elem.find('div', class_='field--name-field-ps-event-speaker-name')
                if speaker_name:
                    details['speaker'] = speaker_name.get_text(strip=True)
                
                speaker_affil = speaker_elem.find('div', class_='field--name-field-ps-event-speaker-affil')
                if speaker_affil:
                    details['speaker_affiliation'] = speaker_affil.get_text(strip=True)
            
            # Extract audience if available
            audience_elem = soup.find('div', class_='field--name-field-ps-events-audience')
            if audience_elem:
                details['audience'] = audience_elem.get_text(strip=True)
            
            # Extract additional tags from content
            content_elem = soup.find('div', class_='node__content')
            if content_elem:
                content_text = content_elem.get_text().lower()
                additional_tags = self._extract_content_tags(content_text)
                if additional_tags:
                    details['tags'] = additional_tags
            
            return details
            
        except Exception as e:
            print(f"    ⚠️  Error fetching event details: {e}")
            return {}
    
    def _extract_content_tags(self, content_text: str) -> List[str]:
        """Extract additional tags from event content"""
        tags = []
        
        # Look for specific content indicators
        content_keywords = [
            'quantum', 'particle', 'nuclear', 'astrophysics', 'biophysics',
            'condensed matter', 'high energy', 'theoretical', 'experimental',
            'mathematical physics', 'cosmology', 'gravity', 'atomic', 'molecular',
            'statistical mechanics', 'phenomenology', 'research', 'scholarship',
            'academic', 'faculty', 'students', 'postdocs', 'fellows'
        ]
        
        for keyword in content_keywords:
            if keyword in content_text:
                tags.append(keyword)
        
        return tags
    
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
            filename = f'{self.department_name.lower()}_cloudscraper_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.events_url,
                'source': f'{self.department_name} CloudScraper',
                'note': f'Scraped from {self.events_url} FullCalendar widget with individual page details'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} events to {filename}")

if __name__ == "__main__":
    scraper = PhysicsCloudScraper()
    events = scraper.scrape_physics_events()
    scraper.save_events(events)
