#!/usr/bin/env python3
"""
Universal ICS calendar scraper for Princeton departments.
All Princeton Drupal sites expose /feeds/events/ical.ics which bypasses
Cloudflare bot protection (it's a calendar feed endpoint, not a browser page).
"""
import requests
import json
from datetime import datetime
import re
from typing import List, Dict, Any
from icalendar import Calendar
import pytz

# All departments confirmed to have working ICS feeds
ICS_DEPARTMENTS = [
    # name, domain, meta_category
    ('Anthropology',              'anthropology.princeton.edu',       'social_sciences'),
    ('English',                   'english.princeton.edu',             'arts_humanities'),
    ('Classics',                  'classics.princeton.edu',            'arts_humanities'),
    ('Comparative Literature',    'complit.princeton.edu',             'arts_humanities'),
    ('Music',                     'music.princeton.edu',               'arts_humanities'),
    ('Art & Archaeology',         'artandarchaeology.princeton.edu',   'arts_humanities'),
    ('Religion',                  'religion.princeton.edu',            'arts_humanities'),
    ('Slavic Languages',          'slavic.princeton.edu',              'arts_humanities'),
    ('Gender & Sexuality Studies','gss.princeton.edu',                 'interdisciplinary'),
    ('Near Eastern Studies',      'nes.princeton.edu',                 'area_studies'),
    ('Hellenic Studies',          'hellenic.princeton.edu',            'area_studies'),
    ('African American Studies',  'aas.princeton.edu',                 'area_studies'),
    ('CBE',                       'cbe.princeton.edu',                 'sciences_engineering'),
    ('ORFE',                      'orfe.princeton.edu',                'sciences_engineering'),
    ('ECE',                       'ece.princeton.edu',                 'sciences_engineering'),
    ('Molecular Biology',         'molbio.princeton.edu',              'sciences_engineering'),
    ('EEB',                       'eeb.princeton.edu',                 'sciences_engineering'),
    ('CEE',                       'cee.princeton.edu',                 'sciences_engineering'),
    ('MAE',                       'mae.princeton.edu',                 'sciences_engineering'),
    ('CITP',                      'citp.princeton.edu',                'interdisciplinary'),
    ('Sociology',                 'sociology.princeton.edu',           'social_sciences'),
    ('Psychology',                'psychology.princeton.edu',          'social_sciences'),
    ('History',                   'history.princeton.edu',             'arts_humanities'),
    ('Neuroscience (PNI)',        'pni.princeton.edu',                 'sciences_engineering'),
    ('UCHV',                      'uchv.princeton.edu',                'interdisciplinary'),
]


class UniversalICSScraper:
    """Scrapes events from a Princeton department's ICS calendar feed."""

    def __init__(self, department_name: str, domain: str, meta_category: str):
        self.department_name = department_name
        self.domain = domain
        self.base_url = f'https://{domain}'
        self.ics_url = f'https://{domain}/feeds/events/ical.ics'
        self.meta_category = meta_category
        self.princeton_tz = pytz.timezone('America/New_York')

    def scrape_events(self) -> List[Dict[str, Any]]:
        print(f'Scraping {self.department_name} from {self.ics_url}')
        try:
            resp = requests.get(
                self.ics_url,
                headers={'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'},
                timeout=20,
            )
            resp.raise_for_status()
            cal = Calendar.from_ical(resp.content)
            events = []
            for component in cal.walk():
                if component.name == 'VEVENT':
                    event = self._parse_component(component)
                    if event and event.get('title'):
                        events.append(event)
            events = self._deduplicate(events)
            events.sort(key=lambda x: x.get('start_date', ''))
            print(f'  {self.department_name}: {len(events)} events')
            return events
        except Exception as e:
            print(f'  ERROR {self.department_name}: {e}')
            return []

    def _parse_component(self, component) -> Dict[str, Any]:
        title = str(component.get('summary', '')).strip()
        if not title:
            return {}

        start_date = ''
        event_time = ''
        end_date = None

        dtstart = component.get('dtstart')
        if dtstart and hasattr(dtstart, 'dt'):
            dt = dtstart.dt
            if isinstance(dt, datetime):
                if dt.tzinfo:
                    dt = dt.astimezone(self.princeton_tz)
                start_date = dt.strftime('%Y-%m-%d')
                event_time = dt.strftime('%I:%M %p').lstrip('0')
            else:
                start_date = dt.strftime('%Y-%m-%d')

        dtend = component.get('dtend')
        if dtend and hasattr(dtend, 'dt'):
            dt = dtend.dt
            if isinstance(dt, datetime):
                if dt.tzinfo:
                    dt = dt.astimezone(self.princeton_tz)
                end_date = dt.strftime('%Y-%m-%d')
                if start_date == end_date and event_time:
                    end_time = dt.strftime('%I:%M %p').lstrip('0')
                    event_time = f'{event_time} - {end_time}'
            else:
                end_date = dt.strftime('%Y-%m-%d')

        description = str(component.get('description', '') or '').strip()
        location = str(component.get('location', '') or 'Princeton University').strip()
        if not location:
            location = 'Princeton University'

        url = str(component.get('url', '') or '').strip()
        if url and not url.startswith('http'):
            url = self.base_url + url
        if not url:
            url = f'{self.base_url}/events'

        uid = str(component.get('uid', '') or '')
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title[:20])
        dept_slug = re.sub(r'[^a-zA-Z0-9]', '_', self.department_name.lower()[:15])
        event_id = f'ics_{dept_slug}_{uid or safe_title}'

        return {
            'id': event_id,
            'title': title,
            'description': description[:1000],
            'start_date': start_date,
            'end_date': end_date,
            'time': event_time,
            'location': location,
            'event_type': self._determine_event_type(title, description),
            'department': self.department_name,
            'meta_category': self.meta_category,
            'source_url': url,
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
            'updated_at': datetime.now().isoformat(),
        }

    def _determine_event_type(self, title: str, description: str = '') -> str:
        text = (title + ' ' + description).lower()
        for keyword, etype in [
            ('colloquium', 'Colloquium'), ('seminar', 'Seminar'),
            ('lecture', 'Lecture'), ('workshop', 'Workshop'),
            ('conference', 'Conference'), ('symposium', 'Symposium'),
            ('panel', 'Panel'), ('talk', 'Talk'),
            ('dissertation', 'Dissertation Defense'), ('defense', 'Dissertation Defense'),
            ('fpo', 'Dissertation Defense'), ('concert', 'Concert'),
            ('recital', 'Recital'), ('performance', 'Performance'),
            ('exhibition', 'Exhibition'), ('screening', 'Film Screening'),
            ('reading', 'Reading'), ('meeting', 'Meeting'),
        ]:
            if keyword in text:
                return etype
        return 'Event'

    def _deduplicate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for e in events:
            key = f"{e.get('title', '')}|{e.get('start_date', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique


def scrape_all_ics_departments() -> List[Dict[str, Any]]:
    """Scrape all Princeton departments that have ICS feeds."""
    all_events = []
    for name, domain, category in ICS_DEPARTMENTS:
        scraper = UniversalICSScraper(name, domain, category)
        events = scraper.scrape_events()
        all_events.extend(events)
    return all_events


if __name__ == '__main__':
    events = scrape_all_ics_departments()
    output = {
        'metadata': {
            'source': 'Princeton Department ICS Feeds',
            'total_events': len(events),
            'scraped_at': datetime.now().isoformat(),
        },
        'events': events,
    }
    with open('universal_ics_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f'\nTotal: {len(events)} events saved to universal_ics_events.json')
