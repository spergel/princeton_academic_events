#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class SPIACloudScraperNew:
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
        self.base_url = "https://spia.princeton.edu"
        
    def scrape_spia_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the SPIA department using the new HTML structure with pagination"""
        print("🏛️ SCRAPING SPIA EVENTS (NEW SCRAPER WITH PAGINATION)")
        print("=" * 60)
        
        all_events = []
        page = 0  # SPIA uses 0-based pagination
        max_pages = 10  # Safety limit
        
        try:
            while page <= max_pages:
                print(f"🔍 Scraping page {page + 1} from: {self.base_url}/events")
                
                if page == 0:
                    url = f"{self.base_url}/events"
                else:
                    # Use the working pagination parameter we discovered
                    url = f"{self.base_url}/events?page={page}"
                
                response = self.scraper.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for event containers - they have class 'event-card'
                event_containers = soup.find_all('div', class_='event-card')
                print(f"    🔍 Found {len(event_containers)} events on page {page + 1}")
                
                if not event_containers:
                    print(f"    ⚠️  No events found on page {page + 1}")
                    break
                
                # Extract events from this page
                for i, container in enumerate(event_containers):
                    try:
                        event = self._extract_event_from_container(container)
                        if event and event.get('title') and len(event['title']) > 5:
                            all_events.append(event)
                            print(f"      ✅ Added: {event['title'][:50]}... on {event.get('start_date', 'No date')}")
                            
                            # Optionally fetch detailed information from individual event page
                            if event.get('source_url') and 'spia.princeton.edu' in event['source_url']:
                                detailed_event = self._fetch_event_details(event['source_url'])
                                if detailed_event:
                                    # Merge detailed info with basic info
                                    event.update(detailed_event)
                                    print(f"        📄 Fetched detailed info: {detailed_event.get('speaker', 'No speaker')} | {detailed_event.get('audience', 'No audience')}")
                        else:
                            print(f"      ⚠️  Skipped event {i+1}: insufficient data")
                    except Exception as e:
                        print(f"      ❌ Error extracting event {i+1}: {e}")
                        continue
                
                # Check if we've reached the end by looking for pagination controls
                pagination = soup.find('nav', class_='pager')
                if pagination:
                    # Check if we're on the last page by looking at page numbers
                    page_links = pagination.find_all('a', href=True)
                    if page_links:
                        page_numbers = []
                        for link in page_links:
                            href = link.get('href', '')
                            if 'page=' in href:
                                page_match = re.search(r'page=(\d+)', href)
                                if page_match:
                                    page_numbers.append(int(page_match.group(1)))
                        
                        # If we're on the last page, stop
                        if page_numbers and page >= max(page_numbers):
                            print(f"    📄 Reached last page {page + 1}, stopping")
                            break
                        
                        # Also check if we're on the last page by looking for "Last »" link
                        last_page_link = pagination.find('a', string=re.compile(r'Last', re.I))
                        if last_page_link:
                            last_href = last_page_link.get('href', '')
                            last_match = re.search(r'page=(\d+)', last_href)
                            if last_match and page >= int(last_match.group(1)):
                                print(f"    📄 Reached last page {page + 1}, stopping")
                                break
                else:
                    print(f"    ⚠️  No pagination controls found, stopping at page {page + 1}")
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
            print(f"❌ Error scraping SPIA events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from an event-card container"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': 'Princeton University',
            'event_type': 'Event',
            'department': 'SPIA',
            'meta_category': 'social_sciences',
            'source_url': f"{self.base_url}/events",
            'source_name': 'SPIA Department Events',
            'speaker': '',
            'audience': '',
            'topics': [],
            'departments': [],
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title from the title div
        title_elem = container.find('div', class_='title')
        if title_elem:
            event['title'] = title_elem.get_text(strip=True)
            # Generate ID
            event['id'] = f"spia_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract URL from the event card link
        link_elem = container.find('a', class_='event-card__link')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            if href.startswith('http'):
                event['source_url'] = href
            else:
                event['source_url'] = self.base_url + href
        
        # Extract date from month-day div
        month_day_elem = container.find('div', class_='event-card__month-day')
        if month_day_elem:
            month_elem = month_day_elem.find('div', class_='month')
            day_elem = month_day_elem.find('div', class_='day')
            
            if month_elem and day_elem:
                month = month_elem.get_text(strip=True)
                day = day_elem.get_text(strip=True)
                # Assume current year for now
                year = datetime.now().year
                date_str = f"{month} {day}, {year}"
                
                try:
                    event['start_date'] = datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
                except:
                    event['start_date'] = ""
        
        # Extract time from location-time div
        location_time_elem = container.find('div', class_='event-card__location-time')
        if location_time_elem:
            time_elem = location_time_elem.find('div', class_='time')
            if time_elem:
                event['time'] = time_elem.get_text(strip=True)
        
        # Extract location from location-time div
        if location_time_elem:
            location_elem = location_time_elem.find('div', class_='location')
            if location_elem:
                event['location'] = location_elem.get_text(strip=True)
        
        # Determine event type based on title
        event['event_type'] = self._determine_event_type(event['title'])
        
        # Extract tags
        event['tags'] = self._extract_tags(event['title'])
        
        return event
    
    def _fetch_event_details(self, event_url: str) -> Dict[str, Any]:
        """Fetch detailed information from individual event page"""
        try:
            print(f"        🔍 Fetching details from: {event_url}")
            response = self.scraper.get(event_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}
            
            # Extract speaker information
            speaker_elem = soup.find('div', class_='speaker')
            if speaker_elem:
                speaker_items = speaker_elem.find_all('span')
                if len(speaker_items) > 1:
                    speaker_text = speaker_items[1].get_text(strip=True)
                    details['speaker'] = speaker_text
            
            # Extract audience information
            audience_elem = soup.find('div', class_='audience')
            if audience_elem:
                audience_items = audience_elem.find_all('span')
                if len(audience_items) > 1:
                    audience_text = audience_items[1].get_text(strip=True)
                    details['audience'] = audience_text
            
            # Extract topics
            topics_elem = soup.find('div', class_='topics')
            if topics_elem:
                topic_links = topics_elem.find_all('a')
                topics = []
                for link in topic_links:
                    topic_text = link.get_text(strip=True)
                    if topic_text:
                        topics.append(topic_text)
                if topics:
                    details['topics'] = topics
            
            # Extract departments
            dept_elem = soup.find('div', class_='department')
            if dept_elem:
                dept_links = dept_elem.find_all('a')
                departments = []
                for link in dept_links:
                    dept_text = link.get_text(strip=True)
                    if dept_text:
                        departments.append(dept_text)
                if departments:
                    details['departments'] = departments
            
            # Extract description from content body
            content_body = soup.find('div', class_='node--content-body')
            if content_body:
                description_text = content_body.get_text(strip=True)
                if description_text:
                    details['description'] = description_text
            
            return details
            
        except Exception as e:
            print(f"        ⚠️  Error fetching event details: {e}")
            return {}
    
    def _determine_event_type(self, title: str) -> str:
        """Determine event type based on title"""
        title_lower = title.lower()
        
        if 'summit' in title_lower:
            return 'Summit'
        elif 'seminar' in title_lower:
            return 'Seminar'
        elif 'workshop' in title_lower:
            return 'Workshop'
        elif 'talk' in title_lower:
            return 'Talk'
        elif 'lecture' in title_lower:
            return 'Lecture'
        elif 'conference' in title_lower:
            return 'Conference'
        elif 'panel' in title_lower:
            return 'Panel'
        elif 'discussion' in title_lower:
            return 'Discussion'
        else:
            return 'Event'  # Default
    
    def _extract_tags(self, title: str) -> List[str]:
        """Extract relevant tags"""
        text = title.lower()
        tags = []
        
        spia_tags = [
            'spia', 'public', 'international', 'affairs', 'policy', 'summit', 'seminar',
            'workshop', 'talk', 'lecture', 'conference', 'panel', 'discussion',
            'research', 'academic', 'university', 'princeton', 'event'
        ]
        
        for tag in spia_tags:
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
    
    def save_events(self, events: List[Dict[str, Any]], filename: str = 'spia_cloudscraper_new_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'department': 'SPIA',
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': f"{self.base_url}/events",
                'source': 'SPIA CloudScraper New (WITH PAGINATION)',
                'note': 'Scraped from spia.princeton.edu/events using new HTML structure with pagination and detailed page scraping'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} SPIA events to {filename}")

if __name__ == "__main__":
    scraper = SPIACloudScraperNew()
    events = scraper.scrape_spia_events()
    scraper.save_events(events)
