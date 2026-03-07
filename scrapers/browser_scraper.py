#!/usr/bin/env python3
"""
Browser-based scraper using Playwright to bypass Cloudflare protection.
This scraper uses a real browser to render pages and solve JS challenges.
"""

import asyncio
import json
import re
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("WARNING: Playwright not installed. Run: pip install playwright && playwright install chromium")


class BrowserScraper:
    """Browser-based scraper that can bypass Cloudflare protection"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        """Start the browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        self.playwright = await async_playwright().start()

        # Use chromium with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.3573, 'longitude': -74.6672},  # Princeton, NJ
            permissions=['geolocation'],
            java_script_enabled=True,
        )

        # Add stealth scripts to every page
        await self.context.add_init_script("""
            // Override webdriver detection
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });

            // Override hardwareConcurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });

            // Override deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });

            // Fix chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

    async def close(self):
        """Close the browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def get_page(self, url: str, wait_for: str = 'networkidle', timeout: int = 60000) -> str:
        """
        Fetch a page and return its HTML content.
        Handles Cloudflare challenges by waiting for them to resolve.
        """
        page = await self.context.new_page()

        try:
            # Navigate to page
            print(f"    Navigating to {url}...")
            response = await page.goto(url, wait_until='domcontentloaded', timeout=timeout)

            # Check for Cloudflare challenge
            content = await page.content()
            if 'Just a moment' in content or 'Checking your browser' in content or 'cf-browser-verification' in content:
                print("    Cloudflare challenge detected, waiting...")
                # Wait for challenge to resolve (up to 30 seconds)
                for i in range(30):
                    await asyncio.sleep(1)
                    content = await page.content()
                    if 'Just a moment' not in content and 'Checking your browser' not in content:
                        print(f"    Challenge resolved after {i+1} seconds")
                        break
                else:
                    print("    WARNING: Cloudflare challenge may not have resolved")

            # Wait for page to be fully loaded
            await page.wait_for_load_state(wait_for, timeout=timeout)

            # Small random delay to appear more human
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Get final content
            content = await page.content()
            return content

        finally:
            await page.close()


class BrowserDrupalScraper:
    """Drupal event scraper using browser automation"""

    def __init__(self, department_name: str, base_url: str, events_url: str, meta_category: str):
        self.department_name = department_name
        self.base_url = base_url
        self.events_url = events_url
        self.meta_category = meta_category

    async def scrape_events(self, max_pages: int = 5, headless: bool = True) -> List[Dict[str, Any]]:
        """Scrape events using browser automation"""
        print(f"BROWSER SCRAPING {self.department_name.upper()} EVENTS")
        print("=" * 60)

        all_events = []

        async with BrowserScraper(headless=headless) as browser:
            page = 0
            consecutive_empty = 0

            while page < max_pages and consecutive_empty < 2:
                url = self.events_url if page == 0 else f"{self.events_url}?page={page}"
                print(f"  Page {page}: {url}")

                try:
                    html = await browser.get_page(url)
                    soup = BeautifulSoup(html, 'html.parser')

                    # Check if we got blocked
                    if 'Access denied' in html or 'Error 403' in html:
                        print(f"    ERROR: Access denied on page {page}")
                        break

                    # Extract events
                    events = self._extract_events_from_soup(soup)
                    print(f"    Found {len(events)} events")

                    if events:
                        all_events.extend(events)
                        consecutive_empty = 0
                    else:
                        consecutive_empty += 1

                    page += 1

                    # Random delay between pages
                    await asyncio.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"    ERROR on page {page}: {e}")
                    break

        # Deduplicate
        unique_events = self._deduplicate_events(all_events)
        print(f"Total unique events: {len(unique_events)}")
        return unique_events

    def _extract_events_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract events from parsed HTML"""
        events = []

        # Try multiple container selectors
        containers = []
        selectors = [
            ('div', {'class': 'node--type-event'}),
            ('article', {'class': 'node--type-event'}),
            ('div', {'class': 'content-list-item'}),
            ('div', {'class': 'event-item'}),
            ('article', {'class': 'event'}),
            ('div', {'class': 'views-row'}),
            ('li', {'class': 'event'}),
        ]

        for tag, attrs in selectors:
            found = soup.find_all(tag, attrs)
            if found:
                containers.extend(found)

        # Lambda-based fallbacks
        if not containers:
            containers = soup.find_all('article', class_=lambda x: x and 'node' in str(x))
        if not containers:
            containers = soup.find_all('div', class_=lambda x: x and 'event' in str(x).lower())

        # Dedupe containers
        seen_ids = set()
        unique_containers = []
        for c in containers:
            cid = id(c)
            if cid not in seen_ids:
                seen_ids.add(cid)
                unique_containers.append(c)

        for container in unique_containers:
            event = self._extract_event(container)
            if event and event.get('title'):
                events.append(event)

        return events

    def _extract_event(self, container) -> Dict[str, Any]:
        """Extract event data from a container element"""
        event = {
            'id': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': None,
            'time': '',
            'location': 'Princeton University',
            'event_type': 'Event',
            'department': self.department_name.lower().replace(' ', '_'),
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
        title_link = None

        # Try various title selectors
        for selector in ['h2 a', 'h3 a', '.field--name-title a', '.event-title a', 'a.title']:
            elem = container.select_one(selector)
            if elem:
                title_link = elem
                break

        # Fallback: first link with substantial text
        if not title_link:
            for link in container.find_all('a'):
                text = link.get_text(strip=True)
                if len(text) > 10:
                    title_link = link
                    break

        if title_link:
            # Handle encoding - convert to ASCII-safe version
            raw_title = title_link.get_text(strip=True)
            event['title'] = raw_title.encode('ascii', 'ignore').decode('ascii') or raw_title
            href = title_link.get('href', '')
            if href:
                event['source_url'] = href if href.startswith('http') else self.base_url + href
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', event['title'][:30])
            event['id'] = f"{self.department_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{safe_title}"

        # Extract date
        date_extracted = False

        # Method 1: Date badge
        date_badge = container.find('div', class_='date-badge')
        if date_badge:
            month_elem = date_badge.find('div', class_='month')
            day_elem = date_badge.find('div', class_='day')
            if month_elem and day_elem:
                month = month_elem.get_text(strip=True)
                day = day_elem.get_text(strip=True)
                event['start_date'] = f"{datetime.now().year}-{self._month_to_num(month)}-{day.zfill(2)}"
                date_extracted = True

        # Method 2: Date wrapper
        if not date_extracted:
            date_wrapper = container.find('div', class_='date-wrapper')
            if date_wrapper:
                month_field = date_wrapper.find('div', class_=lambda x: x and 'month' in str(x).lower())
                day_field = date_wrapper.find('div', class_=lambda x: x and 'day' in str(x).lower())
                if month_field and day_field:
                    month = month_field.get_text(strip=True)
                    day = day_field.get_text(strip=True)
                    event['start_date'] = f"{datetime.now().year}-{self._month_to_num(month)}-{day.zfill(2)}"
                    date_extracted = True

        # Method 3: Date field
        if not date_extracted:
            date_elem = container.find('div', class_=lambda x: x and 'date' in str(x).lower())
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                parsed = self._parse_date(date_text)
                if parsed:
                    event['start_date'] = parsed

        # Extract time
        time_elem = container.find('span', class_='time')
        if time_elem:
            event['time'] = time_elem.get_text(strip=True)
        else:
            # Try to extract time from text
            full_text = container.get_text()
            time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:am|pm)(?:\s*[-–]\s*\d{1,2}:\d{2}\s*(?:am|pm))?)', full_text, re.I)
            if time_match:
                event['time'] = time_match.group(1)

        # Extract location
        location_elem = container.find('div', class_=lambda x: x and 'location' in str(x).lower())
        if location_elem:
            event['location'] = location_elem.get_text(strip=True)

        # Extract description
        desc_elem = container.find('div', class_=lambda x: x and ('summary' in str(x).lower() or 'description' in str(x).lower() or 'body' in str(x).lower()))
        if desc_elem:
            event['description'] = desc_elem.get_text(strip=True)[:500]

        # Determine event type
        title_lower = event['title'].lower()
        for keyword, etype in [('seminar', 'Seminar'), ('colloquium', 'Colloquium'), ('lecture', 'Lecture'),
                               ('workshop', 'Workshop'), ('talk', 'Talk'), ('conference', 'Conference')]:
            if keyword in title_lower:
                event['event_type'] = etype
                break

        return event

    def _month_to_num(self, month: str) -> str:
        """Convert month name to number"""
        months = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
            'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
            'january': '01', 'february': '02', 'march': '03', 'april': '04', 'june': '06',
            'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        return months.get(month.lower()[:3], '01')

    def _parse_date(self, text: str) -> str:
        """Parse date from text"""
        # Try "Month Day, Year" format
        match = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', text)
        if match:
            month = self._month_to_num(match.group(1))
            day = match.group(2).zfill(2)
            year = match.group(3)
            return f"{year}-{month}-{day}"
        return ''

    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate events"""
        seen = set()
        unique = []
        for e in events:
            key = f"{e.get('title', '')}_{e.get('start_date', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique


# Department configurations
BROWSER_DEPARTMENTS = [
    # Previously blocked by Cloudflare
    ('anthropology', 'https://anthropology.princeton.edu', 'https://anthropology.princeton.edu/events', 'social_sciences'),
    ('sociology', 'https://sociology.princeton.edu', 'https://sociology.princeton.edu/events', 'social_sciences'),
    ('psychology', 'https://psychology.princeton.edu', 'https://psychology.princeton.edu/events', 'social_sciences'),
    ('history', 'https://history.princeton.edu', 'https://history.princeton.edu/news-events/events', 'arts_humanities'),
    ('english', 'https://english.princeton.edu', 'https://english.princeton.edu/events', 'arts_humanities'),
    ('classics', 'https://classics.princeton.edu', 'https://classics.princeton.edu/events', 'arts_humanities'),
    ('music', 'https://music.princeton.edu', 'https://music.princeton.edu/events', 'arts_humanities'),
    ('art_archaeology', 'https://artandarchaeology.princeton.edu', 'https://artandarchaeology.princeton.edu/events', 'arts_humanities'),
    ('religion', 'https://religion.princeton.edu', 'https://religion.princeton.edu/events', 'arts_humanities'),
    ('comparative_literature', 'https://complit.princeton.edu', 'https://complit.princeton.edu/events', 'arts_humanities'),
    ('near_eastern_studies', 'https://nes.princeton.edu', 'https://nes.princeton.edu/events', 'area_studies'),
    ('cbe', 'https://cbe.princeton.edu', 'https://cbe.princeton.edu/events', 'sciences_engineering'),
    ('orfe', 'https://orfe.princeton.edu', 'https://orfe.princeton.edu/events', 'sciences_engineering'),
    ('ece', 'https://ece.princeton.edu', 'https://ece.princeton.edu/events', 'sciences_engineering'),
    ('molecular_biology', 'https://molbio.princeton.edu', 'https://molbio.princeton.edu/events', 'sciences_engineering'),
    ('citp', 'https://citp.princeton.edu', 'https://citp.princeton.edu/events', 'interdisciplinary'),
]


async def scrape_all_browser_departments(headless: bool = True) -> List[Dict[str, Any]]:
    """Scrape all departments that need browser automation"""
    all_events = []

    for dept_name, base_url, events_url, meta_category in BROWSER_DEPARTMENTS:
        print(f"\n{'='*60}")
        print(f"Scraping {dept_name}...")

        scraper = BrowserDrupalScraper(dept_name, base_url, events_url, meta_category)
        try:
            events = await scraper.scrape_events(max_pages=3, headless=headless)
            all_events.extend(events)
            print(f"SUCCESS: {dept_name} - {len(events)} events")
        except Exception as e:
            print(f"ERROR: {dept_name} - {e}")

        # Delay between departments
        await asyncio.sleep(random.uniform(3, 5))

    return all_events


def run_browser_scraper(headless: bool = True) -> List[Dict[str, Any]]:
    """Synchronous wrapper for the browser scraper"""
    return asyncio.run(scrape_all_browser_departments(headless=headless))


if __name__ == "__main__":
    import sys

    headless = '--visible' not in sys.argv

    if not PLAYWRIGHT_AVAILABLE:
        print("ERROR: Playwright not installed!")
        print("Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    events = run_browser_scraper(headless=headless)

    # Save results
    output = {
        'metadata': {
            'scraper': 'browser_scraper',
            'total_events': len(events),
            'scraped_at': datetime.now().isoformat(),
        },
        'events': events
    }

    with open('browser_scraped_events.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(events)} events to browser_scraped_events.json")
