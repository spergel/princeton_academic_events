#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class ComputerScienceCloudScraper:
	def __init__(self):
		self.scraper = cloudscraper.create_scraper(
			browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
			delay=10
		)
		self.scraper.headers.update({
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.9',
			'Accept-Encoding': 'gzip, deflate, br',
			'DNT': '1',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1'
		})

	def scrape_cs_events(self):
		print("SCRAPING COMPUTER SCIENCE EVENTS")
		print("="*60)
		# Prefer saved HTML to avoid brotli parsing issues
		try:
			with open('computer_science_cloudscraper_content.html', 'r', encoding='utf-8') as f:
				html_content = f.read()
				print(f"✅ Loaded saved HTML file, length: {len(html_content)}")
				return self.parse_cs_events(html_content, "saved_file")
		except FileNotFoundError:
			print("Saved HTML file not found, fetching from URL...")

		url = "https://www.cs.princeton.edu/events"
		try:
			print(f"Fetching: {url}")
			resp = self.scraper.get(url, timeout=30)
			if resp.status_code == 200:
				print(f"✅ Success! HTML length: {len(resp.text)}")
				return self.parse_cs_events(resp.text, url)
			else:
				print(f"❌ Failed to fetch: {resp.status_code}")
				return []
		except Exception as e:
			print(f"❌ Error: {e}")
			return []

	def parse_cs_events(self, html, source_url):
		soup = BeautifulSoup(html, 'html.parser')
		events = []
		print("\nParsing CS events...")
		if not soup.find('body'):
			print("❌ No body tag found")
			return []

		# Common containers on CS site
		selectors = [
			'.content-list-items', '.content-list-item', '.views-row', '.event-list', '.event-item', '.view-content'
		]
		event_items = []
		for sel in selectors:
			items = soup.select(sel)
			if items:
				print(f"Found {len(items)} items with selector: {sel}")
				event_items = items
				break

		# Fallback: links likely containing events
		event_links = soup.find_all('a', href=lambda x: x and any(w in x.lower() for w in ['event', 'seminar', 'colloquium', 'talk', 'lecture']))
		print(f"Found {len(event_links)} event links")

		for item in event_items:
			try:
				event = self.parse_cs_item(item)
				if event and self.is_academic_event(event):
					events.append(event)
			except Exception as e:
				print(f"Error parsing item: {e}")

		for link in event_links:
			try:
				event = self.parse_cs_link(link)
				if event and self.is_academic_event(event):
					events.append(event)
			except Exception as e:
				print(f"Error parsing link: {e}")

		# Dedup by title
		unique = []
		seen = set()
		for e in events:
			key = e['title'].lower().strip()
			if key not in seen:
				seen.add(key)
				unique.append(e)
		print(f"\nExtracted {len(events)} events, {len(unique)} unique")
		return unique

	def parse_cs_item(self, item):
		title_elem = (
			item.find('span', class_='field--name-title') or
			item.find('h3') or item.find('h2') or item.find('h1') or
			item.find('a', href=True)
		)
		if not title_elem:
			return None
		title = title_elem.get_text().strip()
		if not title or len(title) < 5:
			return None

		date_elem = item.find('div', class_=lambda x: x and 'date' in x.lower())
		start_date = self.extract_date_from_text(date_elem.get_text()) if date_elem else self.extract_date_from_text(title)
		loc_elem = item.find('div', class_=lambda x: x and 'location' in x.lower())
		location = loc_elem.get_text().strip() if loc_elem else self.extract_location_from_text(title)
		desc_elem = item.find('div', class_=lambda x: x and 'description' in x.lower())
		description = desc_elem.get_text().strip() if desc_elem else title

		href = ""
		link = item.find('a', href=True)
		if link:
			href = link['href']
			if href.startswith('/'):
				href = f"https://www.cs.princeton.edu{href}"
			elif not href.startswith('http'):
				href = f"https://www.cs.princeton.edu/{href}"

		return {
			'id': f"cs_{start_date}_{title[:20].replace(' ', '_')}",
			'title': title,
			'description': description,
			'start_date': start_date,
			'end_date': None,
			'time': '',
			'location': location,
			'event_type': self.determine_event_type(title),
			'department': 'Computer Science',
			'meta_category': 'science_engineering',
			'source_url': href,
			'source_name': 'Computer Science Department Events',
			'tags': self.extract_tags(title),
			'created_at': datetime.now().isoformat(),
			'updated_at': datetime.now().isoformat()
		}

	def parse_cs_link(self, link):
		title = link.get_text().strip()
		if not title or len(title) < 5:
			return None
		href = link.get('href')
		if href.startswith('/'):
			href = f"https://www.cs.princeton.edu{href}"
		elif not href.startswith('http'):
			href = f"https://www.cs.princeton.edu/{href}"
		start_date = self.extract_date_from_text(title)
		location = self.extract_location_from_text(title)
		return {
			'id': f"cs_{start_date}_{title[:20].replace(' ', '_')}",
			'title': title,
			'description': title,
			'start_date': start_date,
			'end_date': None,
			'time': '',
			'location': location,
			'event_type': self.determine_event_type(title),
			'department': 'Computer Science',
			'meta_category': 'science_engineering',
			'source_url': href,
			'source_name': 'Computer Science Department Events',
			'tags': self.extract_tags(title),
			'created_at': datetime.now().isoformat(),
			'updated_at': datetime.now().isoformat()
		}

	def extract_date_from_text(self, text):
		if not text:
			return datetime.now().strftime('%Y-%m-%d')
		patterns = [
			r'(\w+ \d{1,2},? \d{4})', r'(\d{1,2}/\d{1,2}/\d{4})', r'(\d{4}-\d{2}-\d{2})', r'(\w+ \d{1,2})', r'(\d{1,2} \w+ \d{4})', r'(\w+ \d{1,2}, \d{4})'
		]
		for pat in patterns:
			m = re.search(pat, text, re.I)
			if m:
				date_str = m.group(1)
				for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d', '%B %d', '%d %B %Y', '%b %d, %Y']:
					try:
						dt = datetime.strptime(date_str, fmt)
						if fmt == '%B %d':
							dt = dt.replace(year=datetime.now().year)
						return dt.strftime('%Y-%m-%d')
					except ValueError:
						continue
		return datetime.now().strftime('%Y-%m-%d')

	def extract_location_from_text(self, text):
		if not text:
			return "TBD"
		for pat in [r'at\s+([^,|\-]+)', r'in\s+([^,|\-]+)']:
			m = re.search(pat, text)
			if m:
				return m.group(1).strip()
		return "TBD"

	def determine_event_type(self, title):
		t = title.lower()
		mapping = {
			'seminar': 'Seminar', 'lecture': 'Lecture', 'talk': 'Talk', 'colloquium': 'Colloquium', 'workshop': 'Workshop', 'conference': 'Conference', 'symposium': 'Symposium'
		}
		for k, v in mapping.items():
			if k in t:
				return v
		return 'Academic Event'

	def extract_tags(self, title):
		text = title.lower()
		tags = []
		for tag in [
			'seminar','lecture','talk','colloquium','workshop','conference','symposium',
			'computer','computing','systems','theory','ai','machine learning','ml','vision','graphics','security','networks','databases'
		]:
			if tag in text:
				tags.append(tag)
		return tags

	def is_academic_event(self, event):
		t = event['title'].lower()
		acad = ['seminar','lecture','talk','colloquium','workshop','conference','symposium','presentation']
		non = ['reception','party','festival','music','dance','worship']
		return any(k in t for k in acad) and not any(k in t for k in non)

	def save_events(self, events):
		if not events:
			print("No events to save")
			return
		filename = 'computer_science_cloudscraper_events.json'
		data = {
			'metadata': {
				'total_events': len(events),
				'department': 'Computer Science',
				'date_range': {
					'earliest': min(e.get('start_date', '') for e in events) if events else None,
					'latest': max(e.get('start_date', '') for e in events) if events else None
				},
				'scraped_at': datetime.now().isoformat(),
				'source': 'CS CloudScraper',
				'note': 'Scraped from cs.princeton.edu/events using cloudscraper'
			},
			'events': events
		}
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
		print(f"\nSaved {len(events)} events to {filename}")
		return data

	def print_summary(self, events):
		print("\n=== CS EVENTS SUMMARY ===")
		print(f"Total Events: {len(events)}")
		type_counts = {}
		for e in events:
			et = e.get('event_type', 'Unknown')
			type_counts[et] = type_counts.get(et, 0) + 1
		print("\nEvents by Type:")
		for et, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
			print(f"  {et}: {c}")


def main():
	s = ComputerScienceCloudScraper()
	events = s.scrape_cs_events()
	if events:
		s.save_events(events)
		s.print_summary(events)
		print(f"\n🎓 Successfully scraped {len(events)} CS events!")
	else:
		print("\n💀 No CS events found.")

if __name__ == "__main__":
	main()
