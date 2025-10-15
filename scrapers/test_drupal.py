#!/usr/bin/env python3
from universal_drupal_cloudscraper import UniversalDrupalCloudScraper

# Test politics department
scraper = UniversalDrupalCloudScraper('politics', 'https://politics.princeton.edu', 'https://politics.princeton.edu/events', 'social_sciences')

# Let's check what containers are found
import cloudscraper
from bs4 import BeautifulSoup

scraper_obj = scraper.scraper
response = scraper_obj.get(scraper.events_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Look for event containers
containers = soup.find_all('div', class_=lambda x: x and 'event' in x.lower())
print(f"Found {len(containers)} potential event containers")

# Check the first few containers
for i, container in enumerate(containers[:3]):
    print(f"\nContainer {i} classes: {container.get('class')}")
    print(f"Container {i} HTML: {str(container)[:200]}...")

    # Try different title selectors
    title_elem = container.find('span', class_='field--name-title')
    if title_elem:
        print(f"  Found field--name-title span")
        title_link = title_elem.find('a')
        if title_link:
            title = title_link.get_text(strip=True)[:50]
            print(f"  Title: {title}")
    else:
        print("  No field--name-title span found")

    # Try h3 or other selectors
    h3_elem = container.find('h3')
    if h3_elem:
        h3_link = h3_elem.find('a')
        if h3_link:
            title = h3_link.get_text(strip=True)[:50]
            print(f"  H3 Title: {title}")

    # Try any link
    any_link = container.find('a')
    if any_link and any_link.get_text(strip=True):
        title = any_link.get_text(strip=True)[:50]
        print(f"  Any link title: {title}")

# Check date extraction for the first event
if containers and len(containers) > 1:
    event_container = containers[1]  # The actual event container
    print(f"\nDate extraction test for first event:")

    # Check date badge
    date_badge = event_container.find('div', class_='date-badge')
    if date_badge:
        print("Found date-badge")
        month_elem = date_badge.find('div', class_='month')
        day_elem = date_badge.find('div', class_='day')
        if month_elem and day_elem:
            print(f"Month: {month_elem.get_text(strip=True)}, Day: {day_elem.get_text(strip=True)}")

    # Check date field
    date_elem = event_container.find('div', class_='field--name-field-ps-events-date')
    if date_elem:
        print("Found field--name-field-ps-events-date")
        day_span = date_elem.find('span', class_='day')
        if day_span:
            print(f"Day span text: '{day_span.get_text(strip=True)}'")
        time_spans = date_elem.find_all('span', class_='time')
        if time_spans:
            print(f"Time spans: {[t.get_text(strip=True) for t in time_spans]}")

    # Check for any date-related elements
    all_divs = event_container.find_all('div')
    date_divs = [div for div in all_divs if 'date' in ' '.join(div.get('class', [])).lower() or 'month' in ' '.join(div.get('class', [])).lower() or 'day' in ' '.join(div.get('class', [])).lower()]
    if date_divs:
        print(f"Date-related divs: {[(div.get('class'), div.get_text(strip=True)[:20]) for div in date_divs[:5]]}")

    # Look for field names containing date
    field_divs = [div for div in all_divs if div.get('class') and any('field--name' in cls for cls in div.get('class', []))]
    date_fields = [div for div in field_divs if 'date' in ' '.join(div.get('class', [])).lower() or 'month' in ' '.join(div.get('class', [])).lower()]
    if date_fields:
        print(f"Date fields: {[(div.get('class'), div.get_text(strip=True)[:30]) for div in date_fields[:3]]}")

    # Look at the full structure around dates
    date_wrapper = event_container.find('div', class_='date-wrapper')
    if date_wrapper:
        print(f"Date wrapper content: {date_wrapper.get_text(strip=True)[:100]}")
        print(f"Date wrapper HTML: {str(date_wrapper)[:300]}...")

events = scraper.scrape_events(max_pages=1, fetch_details=False)

print(f'Final result: Found {len(events)} events')
