#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Any

class SociologyCloudScraperNew:
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
        self.base_url = "https://sociology.princeton.edu"
        
    def scrape_sociology_events(self) -> List[Dict[str, Any]]:
        """Scrape events from the Sociology department using the new HTML structure"""
        print("🏛️ SCRAPING SOCIOLOGY EVENTS (NEW SCRAPER)")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/events"
            print(f"🔍 Fetching: {url}")
            
            response = self.scraper.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event containers - they have class 'content-list-item'
            event_containers = soup.find_all('div', class_='content-list-item')
            print(f"🔍 Found {len(event_containers)} event containers")
            
            if not event_containers:
                print("❌ No event containers found")
                return []
            
            events = []
            for i, container in enumerate(event_containers):
                try:
                    event = self._extract_event_from_container(container)
                    if event and event.get('title') and len(event['title']) > 5:
                        events.append(event)
                        print(f"  ✅ Added: {event['title'][:50]}... on {event.get('start_date', 'No date')}")
                    else:
                        print(f"  ⚠️  Skipped event {i+1}: insufficient data")
                except Exception as e:
                    print(f"  ❌ Error extracting event {i+1}: {e}")
                    continue
            
            # Remove duplicates
            unique_events = self._deduplicate_events(events)
            
            print(f"🎯 Total unique events found: {len(unique_events)}")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Sociology events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a content-list-item container"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': 'Princeton University',
            'event_type': 'Colloquium',
            'department': 'Sociology',
            'meta_category': 'social_sciences',
            'source_url': f"{self.base_url}/events",
            'source_name': 'Sociology Department Events',
            'speaker': '',
            'speaker_affiliation': '',
            'presentation_title': '',
            'tags': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title from the title field
        title_elem = container.find('span', class_='field--name-title')
        if title_elem:
            title_link = title_elem.find('a')
            if title_link:
                event['title'] = title_link.get_text(strip=True)
                href = title_link.get('href')
                if href:
                    if href.startswith('http'):
                        event['source_url'] = href
                    else:
                        event['source_url'] = self.base_url + href
                
                # Generate ID
                event['id'] = f"sociology_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract date and time from the date field
        date_elem = container.find('div', class_='field--name-field-ps-events-date')
        if date_elem:
            date_time_info = self._parse_date_time(date_elem)
            event['start_date'] = date_time_info.get('date', '')
            event['time'] = date_time_info.get('time', '')
        
        # Extract location
        location_elem = container.find('div', class_='field--name-field-ps-events-location-name')
        if location_elem:
            location_item = location_elem.find('div', class_='field__item')
            if location_item:
                event['location'] = location_item.get_text(strip=True)
        
        # Extract speaker information
        speaker_elem = container.find('div', class_='field--name-field-ps-events-speaker')
        if speaker_elem:
            speaker_info = self._extract_speaker_info(speaker_elem)
            event['speaker'] = speaker_info.get('name', '')
            event['speaker_affiliation'] = speaker_info.get('affiliation', '')
            event['presentation_title'] = speaker_info.get('presentation', '')
            
            # Add speaker info to description
            if event['speaker']:
                if not event['description']:
                    event['description'] = f"Speaker: {event['speaker']}"
                else:
                    event['description'] += f" | Speaker: {event['speaker']}"
                
                if event['speaker_affiliation']:
                    event['description'] += f" ({event['speaker_affiliation']})"
                
                if event['presentation_title']:
                    event['description'] += f" | Presentation: {event['presentation_title']}"
        
        # Extract description/summary
        summary_elem = container.find('div', class_='field--name-field-ps-summary')
        if summary_elem:
            summary_text = summary_elem.get_text(strip=True)
            if summary_text:
                if not event['description']:
                    event['description'] = summary_text
                else:
                    event['description'] += f" | {summary_text}"
        
        # Determine event type based on title and series
        event['event_type'] = self._determine_event_type(event['title'], event['description'])
        
        # Extract tags
        event['tags'] = self._extract_tags(event['title'], event['description'], event['speaker'])
        
        return event
    
    def _parse_date_time(self, date_elem) -> Dict[str, str]:
        """Parse date and time from the Sociology date field structure"""
        try:
            # Look for the date badge first (month/day format)
            date_badge = date_elem.find('div', class_='date-badge')
            if date_badge:
                month_elem = date_badge.find('div', class_='month')
                day_elem = date_badge.find('div', class_='day')
                
                if month_elem and day_elem:
                    month = month_elem.get_text(strip=True)
                    day = day_elem.get_text(strip=True)
                    # Assume current year for now
                    year = datetime.now().year
                    date_str = f"{month} {day}, {year}"
                    
                    try:
                        parsed_date = datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
                    except:
                        parsed_date = ""
            else:
                # Look for the full date text
                date_text = date_elem.get_text(strip=True)
                date_match = re.search(r'([A-Z][a-z]{2}, [A-Z][a-z]+ \d{1,2}, \d{4})', date_text)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        parsed_date = datetime.strptime(date_str, '%a, %b %d, %Y').strftime('%Y-%m-%d')
                    except:
                        parsed_date = ""
                else:
                    parsed_date = ""
            
            # Extract time
            time_text = date_elem.get_text(strip=True)
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)', time_text)
            time_str = time_match.group(1) if time_match else ""
            
            # Look for time range
            time_range_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)\s*–\s*(\d{1,2}:\d{2}\s*[ap]m)', time_text)
            if time_range_match:
                start_time = time_range_match.group(1)
                end_time = time_range_match.group(2)
                time_str = f"{start_time} - {end_time}"
            
            return {
                'date': parsed_date,
                'time': time_str
            }
            
        except Exception as e:
            print(f"      ⚠️  Error parsing date/time: {e}")
            return {'date': '', 'time': ''}
    
    def _extract_speaker_info(self, speaker_elem) -> Dict[str, str]:
        """Extract speaker name, affiliation, and presentation title"""
        speaker_info = {
            'name': '',
            'affiliation': '',
            'presentation': ''
        }
        
        try:
            # Extract speaker name
            name_elem = speaker_elem.find('div', class_='field--name-field-ps-event-speaker-name')
            if name_elem:
                name_link = name_elem.find('a')
                if name_link:
                    speaker_info['name'] = name_link.get_text(strip=True)
                else:
                    # Sometimes the name is just text, not a link
                    speaker_info['name'] = name_elem.get_text(strip=True)
            
            # Extract speaker affiliation
            affiliation_elem = speaker_elem.find('div', class_='field--name-field-ps-event-speaker-affil')
            if affiliation_elem:
                affiliation_item = affiliation_elem.find('div', class_='field__item')
                if affiliation_item:
                    affiliation_link = affiliation_item.find('a')
                    if affiliation_link:
                        speaker_info['affiliation'] = affiliation_link.get_text(strip=True)
                    else:
                        speaker_info['affiliation'] = affiliation_item.get_text(strip=True)
            
            # Extract presentation title
            presentation_elem = speaker_elem.find('div', class_='field--name-field-ps-event-speaker-pres')
            if presentation_elem:
                presentation_item = presentation_elem.find('div', class_='field__item')
                if presentation_item:
                    presentation_span = presentation_item.find('span')
                    if presentation_span:
                        speaker_info['presentation'] = presentation_span.get_text(strip=True)
                    else:
                        speaker_info['presentation'] = presentation_item.get_text(strip=True)
        
        except Exception as e:
            print(f"      ⚠️  Error extracting speaker info: {e}")
        
        return speaker_info
    
    def _determine_event_type(self, title: str, description: str) -> str:
        """Determine event type based on title and description"""
        text = (title + ' ' + description).lower()
        
        if 'colloquium' in text:
            return 'Colloquium'
        elif 'seminar' in text:
            return 'Seminar'
        elif 'workshop' in text:
            return 'Workshop'
        elif 'lecture' in text:
            return 'Lecture'
        elif 'conference' in text:
            return 'Conference'
        elif 'talk' in text:
            return 'Talk'
        elif 'discussion' in text:
            return 'Discussion'
        else:
            return 'Event'  # Default
    
    def _extract_tags(self, title: str, description: str, speaker: str) -> List[str]:
        """Extract relevant tags"""
        text = (title + ' ' + description + ' ' + speaker).lower()
        tags = []
        
        sociology_tags = [
            'sociology', 'social', 'colloquium', 'seminar', 'workshop', 'lecture',
            'talk', 'discussion', 'research', 'academic', 'university', 'princeton',
            'speaker', 'presentation', 'event'
        ]
        
        for tag in sociology_tags:
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
    
    def save_events(self, events: List[Dict[str, Any]], filename: str = 'sociology_cloudscraper_new_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'department': 'Sociology',
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': f"{self.base_url}/events",
                'source': 'Sociology CloudScraper New',
                'note': 'Scraped from sociology.princeton.edu/events using new HTML structure'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(events)} Sociology events to {filename}")

if __name__ == "__main__":
    scraper = SociologyCloudScraperNew()
    events = scraper.scrape_sociology_events()
    scraper.save_events(events)
