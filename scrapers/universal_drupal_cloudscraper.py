#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
from typing import List, Dict, Any, Optional

class UniversalDrupalCloudScraper:
    def __init__(self, department_name: str, base_url: str, events_url: str, meta_category: str):
        """
        Universal Drupal scraper for Princeton departments
        
        Args:
            department_name: Name of the department (e.g., "History")
            base_url: Base URL of the department (e.g., "https://history.princeton.edu")
            events_url: URL to the events page (e.g., "https://history.princeton.edu/events")
            meta_category: Meta category for the department (e.g., "arts_humanities")
        """
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
        self.department_name = department_name
        self.base_url = base_url
        self.events_url = events_url
        self.meta_category = meta_category
        
    def scrape_events(self, max_pages: int = 10, fetch_details: bool = True) -> List[Dict[str, Any]]:
        """Scrape events from the department"""
        print(f"SCRAPING {self.department_name.upper()} EVENTS")
        print("=" * 60)

        all_events = []
        page = 0

        try:
            while page <= max_pages:
                # Build URL for current page
                if page == 0:
                    url = self.events_url
                else:
                    url = f"{self.events_url}?page={page}"

                print(f"Scraping page {page} from: {url}")
                
                response = self.scraper.get(url, timeout=30)
                response.raise_for_status()

                # Handle encoding issues
                response.encoding = response.apparent_encoding or 'utf-8'
                soup = BeautifulSoup(response.content.decode(response.encoding, errors='replace'), 'html.parser')
                
                # Find event containers - try multiple selectors for different Drupal versions
                event_containers = soup.find_all('div', class_='content-list-item') or \
                                 soup.find_all('div', class_='event-item') or \
                                 soup.find_all('article', class_='event') or \
                                 soup.find_all('div', class_='views-row') or \
                                 soup.find_all('li', class_='event')

                print(f"    Found {len(event_containers)} events on page {page}")

                # Debug: if no events found, check for alternative structures
                if len(event_containers) == 0:
                    # Look for any elements that might contain events
                    possible_containers = [
                        soup.find_all('div', class_=lambda x: x and 'event' in x.lower()),
                        soup.find_all('article'),
                        soup.find_all('li', class_=lambda x: x and ('item' in x.lower() or 'event' in x.lower())),
                        soup.find_all('div', class_=lambda x: x and ('card' in x.lower() or 'item' in x.lower()))
                    ]

                    for i, containers in enumerate(possible_containers):
                        if containers and len(containers) > 0:
                            print(f"    Found {len(containers)} possible event containers (type {i+1})")
                            if len(containers) <= 5:  # Only show if reasonable number
                                for j, container in enumerate(containers[:3]):
                                    print(f"      Container {j+1}: {container.get('class', 'no-class')} - {container.name}")

                if not event_containers:
                    print(f"    No events found on page {page}")
                    break
                
                # Extract events from this page
                for container in event_containers:
                    event = self._extract_event_from_container(container)
                    if event and event.get('title'):
                        # Optionally fetch detailed information from individual event page
                        if fetch_details and event.get('source_url'):
                            detailed_event = self._fetch_event_details(event)
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
            
            print(f"Total unique events found: {len(unique_events)}")
            return unique_events

        except Exception as e:
            print(f"Error scraping {self.department_name} events: {e}")
            return []
    
    def _extract_event_from_container(self, container) -> Dict[str, Any]:
        """Extract event information from a Drupal container"""
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
            'source_name': f'{self.department_name} Events',
            'speaker': '',
            'audience': '',
            'topics': [],
            'departments': [],
            'tags': [],
            'series': '',
            'speaker_affiliation': '',
            'speaker_url': '',
            'image_url': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Extract title and URL
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
                    event['id'] = f"{self.department_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{event['title'][:20].replace(' ', '_')}"
        
        # Extract date from date badge
        date_badge = container.find('div', class_='date-badge')
        if date_badge:
            month_elem = date_badge.find('div', class_='month')
            day_elem = date_badge.find('div', class_='day')
            if month_elem and day_elem:
                month = month_elem.get_text(strip=True)
                day = day_elem.get_text(strip=True)
                # Assume current year if not specified
                current_year = datetime.now().year
                event['start_date'] = f"{current_year}-{self._month_to_number(month)}-{day.zfill(2)}"
        
        # Extract full date and time information
        date_elem = container.find('div', class_='field--name-field-ps-events-date')
        if date_elem:
            # Look for day span
            day_span = date_elem.find('span', class_='day')
            if day_span:
                date_text = day_span.get_text(strip=True)
                # Parse date like "Wed, Sep 24, 2025"
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    event['start_date'] = parsed_date

            # Look for time spans first (preferred method)
            time_spans = date_elem.find_all('span', class_='time')
            if time_spans:
                if len(time_spans) == 1:
                    event['time'] = time_spans[0].get_text(strip=True)
                elif len(time_spans) == 2:
                    # Handle time range like "4:30 pm – 6:00 pm"
                    start_time = time_spans[0].get_text(strip=True)
                    end_time = time_spans[1].get_text(strip=True)
                    event['time'] = f"{start_time} – {end_time}"
            else:
                # Fallback: extract time from the full text content of the date element
                date_text = date_elem.get_text(strip=True)
                # Look for time patterns like "3:00 pm", "4:30 pm – 6:00 pm", etc.
                time_patterns = [
                    r'(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)(?:\s*–\s*\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))?)',  # "3:00 pm – 4:20 pm"
                    r'(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))',  # Single time like "3:00 pm"
                    r'(\d{1,2}\s*(?:am|pm|AM|PM)(?:\s*–\s*\d{1,2}\s*(?:am|pm|AM|PM))?)',  # "3 pm – 4 pm"
                    r'(\d{1,2}\s*(?:am|pm|AM|PM))'  # Single time like "3 pm"
                ]

                for pattern in time_patterns:
                    match = re.search(pattern, date_text, re.IGNORECASE)
                    if match:
                        event['time'] = match.group(1).strip()
                        break
        
        # Extract location
        location_elem = container.find('div', class_='field--name-field-ps-events-location-name')
        if location_elem:
            location_item = location_elem.find('div', class_='field__item')
            if location_item:
                event['location'] = location_item.get_text(strip=True)
        
        # Extract audience information
        audience_elem = container.find('div', class_='field--name-field-ps-events-audience')
        if audience_elem:
            event['audience'] = audience_elem.get_text(strip=True)
        
        # Extract event category/series
        category_elem = container.find('div', class_='field--name-field-ps-events-category')
        if category_elem:
            category_item = category_elem.find('div', class_='field__item')
            if category_item:
                event['series'] = category_item.get_text(strip=True)
        
        # Extract speaker information from title
        if event.get('title'):
            # Look for speaker names in parentheses or after colons
            speaker_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z-]+(?: [A-Z][a-z-]+)?)\s*\(([^)]+)\)', event['title'])
            if speaker_match:
                event['speaker'] = speaker_match.group(1)
                event['speaker_affiliation'] = speaker_match.group(2)
            else:
                # Try to extract speaker from title format like "Title: Speaker Name"
                title_parts = event['title'].split(':')
                if len(title_parts) > 1:
                    potential_speaker = title_parts[-1].strip()
                    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z-]+', potential_speaker):
                        event['speaker'] = potential_speaker
        
        # Extract summary/description
        summary_elem = container.find('div', class_='field--name-field-ps-summary')
        if summary_elem:
            event['description'] = summary_elem.get_text(strip=True)
        
        # Extract image URL
        img_elem = container.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem.get('src')
            if src.startswith('http'):
                event['image_url'] = src
            else:
                event['image_url'] = self.base_url + src
        
        # Determine event type and tags
        event['event_type'] = self._determine_event_type(event['title'], event.get('series', ''))
        event['tags'].extend(self._extract_tags(event['title'], event.get('description', '')))
        
        return event
    
    def _fetch_event_details(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch detailed information from individual event page"""
        try:
            if not event.get('source_url'):
                return None
            
            print(f"    Fetching details for: {event['title'][:50]}...")
            response = self.scraper.get(event['source_url'], timeout=30)
            response.raise_for_status()

            # Handle encoding issues
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content.decode(response.encoding, errors='replace'), 'html.parser')
            details = {}

            # Extract detailed description
            description_elem = soup.find('div', class_='field--name-body') or soup.find('div', class_='field--name-field-ps-events-description')
            if description_elem:
                details['description'] = description_elem.get_text(strip=True)

            # Skip speaker extraction - focus on times only
            # Extract speaker information (minimal/simple version)
            speaker_elem = soup.find('div', class_='field--name-field-ps-events-speaker')
            if speaker_elem:
                # Simple speaker extraction - just get names, no complex parsing
                speaker_names = []
                speaker_links = speaker_elem.find_all('a')
                for link in speaker_links:
                    name = link.get_text(strip=True)
                    if name and len(name) > 2:  # Avoid generic links
                        speaker_names.append(name)

                if speaker_names:
                    details['speaker'] = '; '.join(speaker_names[:3])  # Limit to first 3 speakers

            # Extract time information if not already extracted
            if not event.get('time'):
                date_elem = soup.find('div', class_='field--name-field-ps-events-date')
                if date_elem:
                    # Look for time spans
                    time_spans = date_elem.find_all('span', class_='time')
                    if time_spans:
                        if len(time_spans) == 1:
                            details['time'] = time_spans[0].get_text(strip=True)
                        elif len(time_spans) == 2:
                            # Handle time range like "4:30 pm – 6:00 pm"
                            start_time = time_spans[0].get_text(strip=True)
                            end_time = time_spans[1].get_text(strip=True)
                            details['time'] = f"{start_time} – {end_time}"

            # Extract additional topics/tags
            topics_elem = soup.find('div', class_='field--name-field-ps-events-topics')
            if topics_elem:
                topic_items = topics_elem.find_all('div', class_='field__item')
                topics = [item.get_text(strip=True) for item in topic_items if item.get_text(strip=True)]
                details['topics'] = topics

            time.sleep(1)  # Be respectful
            return details

        except Exception as e:
            print(f"    Could not fetch details for {event['title'][:30]}: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date text like 'Monday, November 10, 2025' or 'Wed, Sep 24, 2025' or 'Sep 8, 2025'"""
        try:
            # Clean the text
            date_text = re.sub(r'\s+', ' ', date_text.strip())

            # Try pattern with full month name and day of week: "Monday, November 10, 2025"
            date_match = re.search(r'\w+,\s+(\w+)\s+(\d{1,2}),\s+(\d{4})', date_text)
            if date_match:
                month = date_match.group(1)
                day = date_match.group(2)
                year = date_match.group(3)

                # Convert month name to number
                month_num = self._month_to_number(month)
                return f"{year}-{month_num}-{day.zfill(2)}"

            # Try pattern with day of week: "Wed, Sep 24, 2025"
            date_match = re.search(r'(\w+),?\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})', date_text)
            if date_match:
                # Skip the day of week if present
                month = date_match.group(2)
                day = date_match.group(3)
                year = date_match.group(4)

                # Convert month abbreviation to number
                month_num = self._month_to_number(month)
                return f"{year}-{month_num}-{day.zfill(2)}"

            # Try pattern without day of week: "Sep 8, 2025"
            date_match = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', date_text)
            if date_match:
                month = date_match.group(1)
                day = date_match.group(2)
                year = date_match.group(3)

                # Convert month abbreviation to number
                month_num = self._month_to_number(month)
                return f"{year}-{month_num}-{day.zfill(2)}"
        except:
            pass

        return ""
    
    def _month_to_number(self, month: str) -> str:
        """Convert month name or abbreviation to number"""
        months = {
            # Abbreviations
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
            # Full names
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        return months.get(month, '01')
    
    def _determine_event_type(self, title: str, series: str) -> str:
        """Determine event type based on title and series"""
        text = (title + ' ' + series).lower()
        
        type_keywords = {
            'seminar': 'Seminar',
            'colloquium': 'Colloquium',
            'lecture': 'Lecture',
            'talk': 'Talk',
            'workshop': 'Workshop',
            'conference': 'Conference',
            'panel': 'Panel',
            'discussion': 'Discussion',
            'symposium': 'Symposium',
            'meeting': 'Meeting',
            'presentation': 'Presentation',
            'kruzhok': 'Kruzhok',
            'artist': 'Artist Talk',
            'exhibition': 'Exhibition',
            'film': 'Film Screening',
            'screening': 'Film Screening'
        }
        
        for keyword, event_type in type_keywords.items():
            if keyword in text:
                return event_type
        
        return 'Event'
    
    def _extract_tags(self, title: str, description: str) -> List[str]:
        """Extract relevant tags from title and description"""
        text = (title + ' ' + description).lower()
        tags = []
        
        # Add department-specific tags based on meta category
        if self.meta_category == 'arts_humanities':
            tags.extend(['humanities', 'arts', 'literature', 'history', 'philosophy', 'culture'])
        elif self.meta_category == 'social_sciences':
            tags.extend(['social sciences', 'sociology', 'politics', 'economics', 'anthropology'])
        elif self.meta_category == 'sciences_engineering':
            tags.extend(['science', 'engineering', 'technology', 'research', 'innovation'])
        elif self.meta_category == 'area_studies':
            tags.extend(['area studies', 'international', 'global', 'cultural studies'])
        elif self.meta_category == 'interdisciplinary':
            tags.extend(['interdisciplinary', 'cross-disciplinary', 'multidisciplinary'])
        
        # Add common academic tags
        common_tags = [
            'princeton', 'university', 'academic', 'event', 'education',
            'seminar', 'colloquium', 'lecture', 'talk', 'workshop',
            'conference', 'presentation', 'discussion', 'symposium'
        ]
        tags.extend(common_tags)
        
        # Filter tags that appear in the text
        filtered_tags = [tag for tag in tags if tag in text and tag not in tags]
        return filtered_tags
    
    def _has_next_page(self, soup, current_page: int) -> bool:
        """Check if there's a next page"""
        # Look for pagination controls
        pagination = soup.find('nav', class_='pager') or soup.find('div', class_='pagination')
        
        if pagination:
            # Check for next page link
            next_link = pagination.find('a', string=re.compile(r'Next', re.I))
            if next_link:
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
            filename = f'{self.department_name.lower().replace(" ", "_")}_universal_drupal_events.json'
        
        output = {
            'metadata': {
                'department': self.department_name,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.events_url,
                'source': f'{self.department_name} Universal Drupal CloudScraper',
                'note': f'Scraped from {self.events_url} using universal Drupal content-list-item structure'
            },
            'events': events
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(events)} events to {filename}")


# Department configurations for easy testing
DEPARTMENT_CONFIGS = {
    'history': {
        'name': 'History',
        'base_url': 'https://history.princeton.edu',
        'events_url': 'https://history.princeton.edu/news-events/events',
        'meta_category': 'arts_humanities'
    },
    'sociology': {
        'name': 'Sociology',
        'base_url': 'https://sociology.princeton.edu',
        'events_url': 'https://sociology.princeton.edu/events',
        'meta_category': 'social_sciences'
    },
    'anthropology': {
        'name': 'Anthropology',
        'base_url': 'https://anthropology.princeton.edu',
        'events_url': 'https://anthropology.princeton.edu/news-events/events',
        'meta_category': 'social_sciences'
    },
    'african_studies': {
        'name': 'African Studies',
        'base_url': 'https://afs.princeton.edu',
        'events_url': 'https://afs.princeton.edu/events',
        'meta_category': 'area_studies'
    },
    'slavic_languages': {
        'name': 'Slavic Languages and Literatures',
        'base_url': 'https://slavic.princeton.edu',
        'events_url': 'https://slavic.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'french_italian': {
        'name': 'French & Italian',
        'base_url': 'https://frit.princeton.edu',
        'events_url': 'https://frit.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'neuroscience': {
        'name': 'Princeton Neuroscience Institute',
        'base_url': 'https://pni.princeton.edu',
        'events_url': 'https://pni.princeton.edu/events',
        'meta_category': 'sciences_engineering'
    },
    'uchv': {
        'name': 'University Center for Human Values',
        'base_url': 'https://uchv.princeton.edu',
        'events_url': 'https://uchv.princeton.edu/events',
        'meta_category': 'interdisciplinary'
    },
    'cbe': {
        'name': 'Chemical and Biological Engineering',
        'base_url': 'https://cbe.princeton.edu',
        'events_url': 'https://cbe.princeton.edu/events',
        'meta_category': 'engineering'
    },
    'orfe': {
        'name': 'Operations Research and Financial Engineering',
        'base_url': 'https://orfe.princeton.edu',
        'events_url': 'https://orfe.princeton.edu/events',
        'meta_category': 'engineering'
    },
    'ece': {
        'name': 'Electrical and Computer Engineering',
        'base_url': 'https://ece.princeton.edu',
        'events_url': 'https://ece.princeton.edu/events',
        'meta_category': 'engineering'
    }
,
    'history': {
        'name': 'History',
        'base_url': 'https://history.princeton.edu',
        'events_url': 'https://history.princeton.edu/news-events/events',
        'meta_category': 'arts_humanities'
    },
    'classics': {
        'name': 'Classics',
        'base_url': 'https://classics.princeton.edu',
        'events_url': 'https://classics.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'english': {
        'name': 'English',
        'base_url': 'https://english.princeton.edu',
        'events_url': 'https://english.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'art_archaeology': {
        'name': 'Art and Archaeology',
        'base_url': 'https://artandarchaeology.princeton.edu',
        'events_url': 'https://artandarchaeology.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'comparative_literature': {
        'name': 'Comparative Literature',
        'base_url': 'https://complit.princeton.edu',
        'events_url': 'https://complit.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'near_eastern_studies': {
        'name': 'Near Eastern Studies',
        'base_url': 'https://nes.princeton.edu',
        'events_url': 'https://nes.princeton.edu/events',
        'meta_category': 'area_studies'
    },
    'east_asian_studies': {
        'name': 'East Asian Studies',
        'base_url': 'https://eas.princeton.edu',
        'events_url': 'https://eas.princeton.edu/events',
        'meta_category': 'area_studies'
    },
    'french_italian': {
        'name': 'French & Italian',
        'base_url': 'https://frit.princeton.edu',
        'events_url': 'https://frit.princeton.edu/events',
        'meta_category': 'arts_humanities'
    },
    'neuroscience': {
        'name': 'Princeton Neuroscience Institute',
        'base_url': 'https://pni.princeton.edu',
        'events_url': 'https://pni.princeton.edu/events',
        'meta_category': 'sciences_engineering'
    },
}


def test_department(department_key: str, max_pages: int = 3, fetch_details: bool = True):
    """Test the universal scraper with a specific department"""
    if department_key not in DEPARTMENT_CONFIGS:
        print(f"❌ Department '{department_key}' not found in configurations")
        print(f"Available departments: {list(DEPARTMENT_CONFIGS.keys())}")
        return
    
    config = DEPARTMENT_CONFIGS[department_key]
    scraper = UniversalDrupalCloudScraper(
        department_name=config['name'],
        base_url=config['base_url'],
        events_url=config['events_url'],
        meta_category=config['meta_category']
    )
    
    events = scraper.scrape_events(max_pages=max_pages, fetch_details=fetch_details)
    scraper.save_events(events)
    return events


if __name__ == "__main__":
    # Test with a specific department
    import sys
    
    if len(sys.argv) > 1:
        department = sys.argv[1]
        test_department(department)
    else:
        # Default test with Sociology
        test_department('sociology')
