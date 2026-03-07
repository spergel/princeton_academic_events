#!/usr/bin/env python3
"""
Princeton Localist Events API Scraper
Scrapes events from Princeton's central events calendar (events.princeton.edu)
which uses the Localist platform. This covers many departments that are
Cloudflare-blocked on their individual sites.
"""

import requests
import json
from datetime import datetime
import re
import time
from typing import List, Dict, Any, Optional

# Academic department group names to prioritize (partial matches)
ACADEMIC_KEYWORDS = [
    'department', 'dept', 'program', 'institute', 'center', 'school',
    'mathematics', 'physics', 'chemistry', 'biology', 'computer science',
    'engineering', 'economics', 'politics', 'history', 'english', 'philosophy',
    'psychology', 'sociology', 'anthropology', 'art', 'music', 'religion',
    'classics', 'neuroscience', 'geosciences', 'astrophysics', 'molecular',
    'ecology', 'environmental', 'civil', 'electrical', 'mechanical', 'chemical',
    'operations research', 'finance', 'public affairs', 'humanities',
    'slavic', 'near eastern', 'east asian', 'comparative literature',
    'gender', 'latin american', 'hellenic', 'african', 'medieval',
    'french', 'italian', 'spanish', 'portuguese', 'linguistics',
    'neuroscience', 'pacm', 'citp', 'piirs', 'andlinger',
]

# Map group names to meta_category
META_CATEGORY_MAP = {
    'mathematics': 'sciences_engineering',
    'physics': 'sciences_engineering',
    'chemistry': 'sciences_engineering',
    'biology': 'sciences_engineering',
    'molecular biology': 'sciences_engineering',
    'geosciences': 'sciences_engineering',
    'astrophysical': 'sciences_engineering',
    'computer science': 'sciences_engineering',
    'electrical': 'sciences_engineering',
    'mechanical': 'sciences_engineering',
    'chemical': 'sciences_engineering',
    'civil': 'sciences_engineering',
    'operations research': 'sciences_engineering',
    'neuroscience': 'sciences_engineering',
    'ecology': 'sciences_engineering',
    'environmental': 'sciences_engineering',
    'pacm': 'sciences_engineering',
    'andlinger': 'sciences_engineering',
    'economics': 'social_sciences',
    'politics': 'social_sciences',
    'sociology': 'social_sciences',
    'psychology': 'social_sciences',
    'anthropology': 'social_sciences',
    'public affairs': 'social_sciences',
    'spia': 'social_sciences',
    'finance': 'social_sciences',
    'piirs': 'social_sciences',
    'history': 'arts_humanities',
    'english': 'arts_humanities',
    'philosophy': 'arts_humanities',
    'art': 'arts_humanities',
    'music': 'arts_humanities',
    'religion': 'arts_humanities',
    'classics': 'arts_humanities',
    'slavic': 'arts_humanities',
    'comparative literature': 'arts_humanities',
    'humanities': 'arts_humanities',
    'medieval': 'arts_humanities',
    'french': 'arts_humanities',
    'italian': 'arts_humanities',
    'spanish': 'arts_humanities',
    'portuguese': 'arts_humanities',
    'linguistics': 'arts_humanities',
    'near eastern': 'area_studies',
    'east asian': 'area_studies',
    'latin american': 'area_studies',
    'hellenic': 'area_studies',
    'african': 'area_studies',
    'gender': 'interdisciplinary',
    'citp': 'interdisciplinary',
}


class PrincetonLocalistScraper:
    """
    Scrapes Princeton's central events calendar at events.princeton.edu
    Uses the Localist REST API for reliable, structured data access.
    """

    def __init__(self):
        self.base_url = 'https://events.princeton.edu'
        self.api_base = f'{self.base_url}/api/2'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def fetch_groups(self) -> List[Dict[str, Any]]:
        """Fetch all department/group listings from the Localist API"""
        groups = []
        page = 1
        while True:
            try:
                resp = self.session.get(
                    f'{self.api_base}/groups',
                    params={'page': page, 'pp': 100},
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json()
                batch = data.get('groups', [])
                if not batch:
                    break
                groups.extend(batch)
                total_pages = data.get('page', {}).get('total', 1)
                if page >= total_pages:
                    break
                page += 1
                time.sleep(0.5)
            except Exception as e:
                print(f'  Error fetching groups page {page}: {e}')
                break
        return groups

    def fetch_events_page(self, page: int, pp: int = 100, group_id: Optional[int] = None,
                          days: int = 365) -> Dict[str, Any]:
        """Fetch a single page of events from the Localist API"""
        params = {'page': page, 'pp': pp, 'days': days}
        if group_id:
            params['group_id'] = group_id
        resp = self.session.get(f'{self.api_base}/events', params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def scrape_events(self, days: int = 365) -> List[Dict[str, Any]]:
        """Scrape all academic events from the Princeton Localist calendar"""
        print('SCRAPING PRINCETON LOCALIST EVENTS CALENDAR')
        print('=' * 60)
        print(f'Source: {self.base_url}')

        all_events = []
        page = 1
        total_pages = None

        while True:
            try:
                print(f'  Fetching page {page}{"/" + str(total_pages) if total_pages else ""}...')
                data = self.fetch_events_page(page=page, pp=100, days=days)

                raw_events = data.get('events', [])
                if not raw_events:
                    print('  No more events found, stopping.')
                    break

                page_info = data.get('page', {})
                if total_pages is None:
                    total_pages = page_info.get('total', 1)

                for raw in raw_events:
                    event = self._parse_event(raw)
                    if event:
                        all_events.append(event)

                print(f'    Got {len(raw_events)} events (total so far: {len(all_events)})')

                if page >= total_pages:
                    break
                page += 1
                time.sleep(0.5)

            except Exception as e:
                print(f'  Error on page {page}: {e}')
                break

        unique = self._deduplicate(all_events)
        unique.sort(key=lambda x: x.get('start_date', ''))
        print(f'Total unique events from Localist: {len(unique)}')
        return unique

    def _parse_event(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a Localist API event object into our standard format"""
        try:
            # Localist wraps event data under 'event' key
            ev = raw.get('event', raw)

            title = ev.get('title', '').strip()
            if not title:
                return None

            # Extract dates
            start_date = ''
            end_date = None
            event_time = ''

            first_date = ev.get('first_date', '') or ev.get('start', '')
            last_date = ev.get('last_date', '') or ev.get('end', '')

            if first_date:
                start_date = self._parse_date(first_date)
                event_time = self._parse_time(first_date)
            if last_date:
                end_date = self._parse_date(last_date)
                end_time = self._parse_time(last_date)
                if end_time and event_time and start_date == end_date:
                    event_time = f'{event_time} - {end_time}'

            # Extract location
            location = (ev.get('location_name') or ev.get('location') or
                        ev.get('venue', {}).get('name') if isinstance(ev.get('venue'), dict) else None or
                        'Princeton University')
            if not location:
                location = 'Princeton University'

            # Extract department/group
            group = ev.get('group', {}) or {}
            if isinstance(group, dict):
                dept_name = group.get('name', '')
                group_id = group.get('id', '')
            else:
                dept_name = ''
                group_id = ''

            if not dept_name:
                # Try filters
                filters = ev.get('filters', {}) or {}
                depts = filters.get('departments', []) or []
                if depts and isinstance(depts[0], dict):
                    dept_name = depts[0].get('name', '')
                elif depts and isinstance(depts[0], str):
                    dept_name = depts[0]

            meta_category = self._get_meta_category(dept_name)

            # Extract description (strip HTML)
            description = ev.get('description_text', '') or ev.get('description', '') or ''
            if '<' in description:
                description = re.sub(r'<[^>]+>', ' ', description)
                description = re.sub(r'\s+', ' ', description).strip()

            # Build event URL
            url_path = ev.get('url', '') or ''
            if url_path and not url_path.startswith('http'):
                source_url = self.base_url + url_path
            elif url_path:
                source_url = url_path
            else:
                event_id = ev.get('id', '')
                source_url = f'{self.base_url}/event/{event_id}' if event_id else self.base_url

            # Event ID
            event_id = ev.get('id', '')
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title[:20])
            dept_slug = re.sub(r'[^a-zA-Z0-9]', '_', dept_name.lower()[:20]) if dept_name else 'princeton'
            combined_id = f'localist_{dept_slug}_{event_id or safe_title}'

            # Tags from Localist filters/tags
            tags = []
            for tag in (ev.get('tags', []) or []):
                if isinstance(tag, dict):
                    tags.append(tag.get('name', ''))
                elif isinstance(tag, str):
                    tags.append(tag)
            tags = [t for t in tags if t]

            # Event type
            event_type = self._determine_event_type(title, description)

            # Speaker
            speaker = ev.get('speaker', '') or ''

            return {
                'id': combined_id,
                'title': title,
                'description': description[:1000] if description else '',
                'start_date': start_date,
                'end_date': end_date,
                'time': event_time,
                'location': location,
                'event_type': event_type,
                'department': dept_name or 'Princeton University',
                'meta_category': meta_category,
                'source_url': source_url,
                'source_name': 'Princeton Events Calendar',
                'speaker': speaker,
                'audience': ev.get('audience', '') or '',
                'topics': [],
                'departments': [dept_name] if dept_name else [],
                'tags': tags,
                'series': ev.get('event_instances', [{}])[0].get('event_instance', {}).get('subtitle', '') if ev.get('event_instances') else '',
                'speaker_affiliation': '',
                'speaker_url': '',
                'image_url': ev.get('photo_url', '') or '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }

        except Exception as e:
            print(f'  Error parsing event: {e}')
            return None

    def _parse_date(self, date_str: str) -> str:
        """Extract YYYY-MM-DD from an ISO datetime string or date string"""
        if not date_str:
            return ''
        # Match YYYY-MM-DD at the start
        m = re.match(r'(\d{4}-\d{2}-\d{2})', str(date_str))
        if m:
            return m.group(1)
        return ''

    def _parse_time(self, datetime_str: str) -> str:
        """Extract HH:MM time from an ISO datetime string"""
        if not datetime_str:
            return ''
        m = re.search(r'T(\d{2}):(\d{2})', str(datetime_str))
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2))
            ampm = 'AM' if hour < 12 else 'PM'
            display_hour = hour % 12 or 12
            return f'{display_hour}:{minute:02d} {ampm}'
        return ''

    def _get_meta_category(self, dept_name: str) -> str:
        """Map department name to meta_category"""
        lower = dept_name.lower()
        for keyword, category in META_CATEGORY_MAP.items():
            if keyword in lower:
                return category
        return 'interdisciplinary'

    def _determine_event_type(self, title: str, description: str = '') -> str:
        """Determine event type from title/description"""
        text = (title + ' ' + description).lower()
        type_keywords = {
            'colloquium': 'Colloquium',
            'seminar': 'Seminar',
            'lecture': 'Lecture',
            'workshop': 'Workshop',
            'conference': 'Conference',
            'symposium': 'Symposium',
            'panel': 'Panel',
            'talk': 'Talk',
            'discussion': 'Discussion',
            'presentation': 'Presentation',
            'dissertation': 'Dissertation Defense',
            'defense': 'Dissertation Defense',
            'fpo': 'Dissertation Defense',
            'concert': 'Concert',
            'recital': 'Recital',
            'performance': 'Performance',
            'exhibition': 'Exhibition',
            'screening': 'Film Screening',
            'meeting': 'Meeting',
        }
        for keyword, event_type in type_keywords.items():
            if keyword in text:
                return event_type
        return 'Event'

    def _deduplicate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events by title + date"""
        seen = set()
        unique = []
        for e in events:
            key = f"{e.get('title', '')}|{e.get('start_date', '')}|{e.get('department', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique

    def save_events(self, events: List[Dict[str, Any]], filename: str = 'princeton_localist_events.json'):
        """Save events to JSON file"""
        output = {
            'metadata': {
                'source': 'Princeton Localist Events Calendar',
                'source_url': self.base_url,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat(),
            },
            'events': events
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f'Saved {len(events)} events to {filename}')


if __name__ == '__main__':
    scraper = PrincetonLocalistScraper()
    events = scraper.scrape_events(days=365)
    scraper.save_events(events)
