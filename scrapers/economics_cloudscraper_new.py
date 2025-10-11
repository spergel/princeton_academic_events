#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class EconomicsCloudScraperNew:
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
        self.base_url = "https://economics.princeton.edu"
        
    def scrape_economics_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Economics department using the new HTML structure with pagination"""
        print("💰 SCRAPING ECONOMICS EVENTS (NEW SCRAPER WITH PAGINATION)")
        print("=" * 60)
        
        all_events = []
        page = 1
        max_pages = 10  # Safety limit
        
        try:
            while page <= max_pages:
                print(f"🔍 Scraping page {page} from: {self.base_url}/events/upcoming-seminars/")
                
                if page == 1:
                    url = f"{self.base_url}/events/upcoming-seminars/"
                else:
                    # Use the working pagination parameter we discovered
                    url = f"{self.base_url}/events/upcoming-seminars/?paged={page}"
                
                response = self.scraper.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for the main event list container
                event_list_container = soup.find('div', class_='posts event-list')
                if not event_list_container:
                    print(f"    ⚠️  No event list container found on page {page}")
                    break
                
                # Find individual events - they are divs with no class inside the event-list
                event_divs = []
                for div in event_list_container.find_all('div', recursive=False):
                    # Check if this div contains event elements
                    if div.find('div', class_='interior'):
                        event_divs.append(div)
                
                print(f"    🔍 Found {len(event_divs)} events on page {page}")
                
                if not event_divs:
                    print(f"    ⚠️  No events found on page {page}")
                    break
                
                # Extract events from this page
                for i, event_div in enumerate(event_divs):
                    try:
                        event = self._extract_event_from_container(event_div)
                        if event and event.get('title') and len(event['title']) > 5:
                            all_events.append(event)
                            print(f"      ✅ Added: {event['title'][:50]}... on {event.get('start_date', 'No date')}")
                        else:
                            print(f"      ⚠️  Skipped event {i+1}: insufficient data")
                    except Exception as e:
                        print(f"      ❌ Error extracting event {i+1}: {e}")
                        continue
                
                # Check if we've reached the end by looking for pagination controls
                pagination = soup.find('div', class_='pagination')
                if pagination:
                    # Check if there's a next page
                    next_page_link = pagination.find('a', class_='next-page')
                    if not next_page_link or 'hidden' in next_page_link.get('class', []):
                        print(f"    📄 No more pages found, stopping at page {page}")
                        break
                    
                    # Check if we're on the last page by looking at page numbers
                    page_links = pagination.find_all('a', class_='page')
                    if page_links:
                        page_numbers = []
                        for link in page_links:
                            text = link.get_text(strip=True)
                            if text.isdigit():
                                page_numbers.append(int(text))
                        
                        if page_numbers and page >= max(page_numbers):
                            print(f"    📄 Reached last page {page}, stopping")
                            break
                else:
                    print(f"    ⚠️  No pagination controls found, stopping at page {page}")
                    break
                
                page += 1
                # Add delay between pages
                import time
                time.sleep(2)
            
            # Remove duplicates
            unique_events = self._deduplicate_events(all_events)
            
            print(f"🎯 Total events found across {page} pages: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Economics events: {e}")
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
            'location': 'Princeton University',
            'event_type': 'Seminar',
            'department': 'Economics',
            'meta_category': 'social_sciences',
            'source_url': f"{self.base_url}/events/upcoming-seminars/",
            'source_name': 'Economics Department Events',
            'audience': '',
            'series': '',
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Find the interior div that contains all the event details
        interior_div = container.find('div', class_='interior')
        if not interior_div:
            return None
        
        # Extract title from the specific HTML structure
        title_elem = interior_div.find('div', class_='event-title')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            if title_text and len(title_text) > 3:
                event['title'] = title_text
                # Generate ID
                event['id'] = f"economics_{datetime.now().strftime('%Y%m%d')}_{title_text[:20].replace(' ', '_')}"
        
        # Extract subtitle/description
        subtitle_elem = interior_div.find('div', class_='event-subtitle')
        if subtitle_elem:
            subtitle_text = subtitle_elem.get_text(strip=True)
            if subtitle_text:
                event['description'] = subtitle_text
        
        # Extract date and time from the specific HTML structure
        date_elem = interior_div.find('div', class_='event-date')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            if date_text:
                # Parse date and time
                date_time_info = self._parse_date_time(date_text)
                event['start_date'] = date_time_info.get('date', '')
                event['time'] = date_time_info.get('time', '')
        
        # Extract audience information
        audience_elem = interior_div.find('div', class_='audience')
        if audience_elem:
            audience_text = audience_elem.get_text(strip=True)
            if audience_text:
                event['audience'] = audience_text
                # Add audience to description if no description exists
                if not event['description']:
                    event['description'] = f"Audience: {audience_text}"
                else:
                    event['description'] += f" | Audience: {audience_text}"
        
        # Extract event series
        series_elem = interior_div.find('div', class_='event-series')
        if series_elem:
            series_label = series_elem.find('label')
            series_div = series_elem.find('div')
            if series_label and series_div:
                series_text = series_div.get_text(strip=True)
                if series_text:
                    event['series'] = series_text
                    # Add series to description
                    if not event['description']:
                        event['description'] = f"Series: {series_text}"
                    else:
                        event['description'] += f" | Series: {series_text}"
                    
                    # Determine event type based on series
                    series_lower = series_text.lower()
                    if 'seminar' in series_lower:
                        event['event_type'] = 'Seminar'
                    elif 'colloquium' in series_lower:
                        event['event_type'] = 'Colloquium'
                    elif 'workshop' in series_lower:
                        event['event_type'] = 'Workshop'
                    elif 'lecture' in series_lower:
                        event['event_type'] = 'Lecture'
                    elif 'conference' in series_lower:
                        event['event_type'] = 'Conference'
        
        # Extract URL for source_url
        link_elem = interior_div.find('a', class_='post-link')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            if href.startswith('http'):
                event['source_url'] = href
            else:
                event['source_url'] = self.base_url + href
        
        # Determine event type from title if not set
        if event['title'] and not event['event_type']:
            title_lower = event['title'].lower()
            if 'seminar' in title_lower:
                event['event_type'] = 'Seminar'
            elif 'colloquium' in title_lower:
                event['event_type'] = 'Colloquium'
            elif 'workshop' in title_lower:
                event['event_type'] = 'Workshop'
            elif 'lecture' in title_lower:
                event['event_type'] = 'Lecture'
            elif 'conference' in title_lower:
                event['event_type'] = 'Conference'
            else:
                event['event_type'] = 'Seminar'  # Default for Economics
        
        # Extract tags
        event['tags'] = self._extract_tags(event['title'], event['description'], event['series'])
        
        return event
    
    def _parse_date_time(self, date_time_text: str) -> Dict[str, str]:
        """Parse date and time text to separate date and time fields"""
        try:
            # Remove <br> tags and clean up
            clean_text = re.sub(r'<br\s*/?>', ' ', date_time_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Look for date pattern
            date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', clean_text)
            date_str = date_match.group(1) if date_match else ""
            
            # Look for time pattern
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m(?:\s*-\s*\d{1,2}:\d{2}\s*[ap]m)?)', clean_text)
            time_str = time_match.group(1) if time_match else ""
            
            # Parse date to YYYY-MM-DD format
            parsed_date = ""
            if date_str:
                try:
                    parsed_date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
                except:
                    try:
                        parsed_date = datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
                    except:
                        parsed_date = ""
            
            return {
                'date': parsed_date,
                'time': time_str
            }
            
        except Exception as e:
            print(f"      ⚠️  Error parsing date/time: {e}")
            return {'date': '', 'time': ''}
    
    def _extract_tags(self, title: str, description: str, series: str) -> List[str]:
        """Extract relevant tags"""
        text = (title + ' ' + description + ' ' + series).lower()
        tags = []
        
        economics_tags = [
            'economics', 'economic', 'seminar', 'colloquium', 'workshop', 'lecture',
            'econometrics', 'microeconomic', 'macroeconomic', 'international trade',
            'development economics', 'behavioral economics', 'experimental economics',
            'finance', 'industrial organization', 'applied econometrics', 'political economy'
        ]
        
        for tag in economics_tags:
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
    
    def save_events(self, events: List[Dict[str, Any]], filename: str = 'economics_cloudscraper_new_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'department': 'Economics',
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': f"{self.base_url}/events/upcoming-seminars/",
                'source': 'Economics CloudScraper New (WITH PAGINATION)',
                'note': 'Scraped from economics.princeton.edu/events/upcoming-seminars/ using new HTML structure and pagination'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} Economics events to {filename}")

if __name__ == "__main__":
    scraper = EconomicsCloudScraperNew()
    events = scraper.scrape_economics_events()
    scraper.save_events(events)
