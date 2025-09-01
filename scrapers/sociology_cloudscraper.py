#!/usr/bin/env python3
import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class SociologyCloudScraper:
	def __init__(self):
		self.scraper = cloudscraper.create_scraper(
			browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
			delay=10
		)
		# Use the working approach: gzip-only Accept-Encoding
		self.scraper.headers.update({
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.9',
			'Accept-Encoding': 'gzip, deflate',  # No brotli - this fixes the compression issue
			'DNT': '1',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1'
		})

	def scrape_sociology_events(self):
		print("SCRAPING SOCIOLOGY EVENTS")
		print("="*60)
		try:
			# Try the decompressed file first
			with open('sociology_decompressed_gzip.html', 'r', encoding='utf-8') as f:
				html = f.read()
				print(f"✅ Loaded decompressed HTML file, length: {len(html)}")
				return self.parse_events(html)
		except FileNotFoundError:
			print("Decompressed HTML file not found, fetching from URL...")
		url = 'https://sociology.princeton.edu/events'
		try:
			resp = self.scraper.get(url, timeout=30)
			if resp.status_code == 200:
				return self.parse_events(resp.text)
			print(f"❌ Failed: {resp.status_code}")
			return []
		except Exception as e:
			print(f"❌ Error: {e}")
			return []

	def parse_events(self, html):
		soup = BeautifulSoup(html, 'html.parser')
		if not soup.find('body'):
			print('❌ No body')
			return []
		selectors = ['.content-list-items', '.views-row', '.view-content', '.event-list']
		items = []
		for sel in selectors:
			found = soup.select(sel)
			if found:
				print(f"Found {len(found)} items with selector: {sel}")
				items = found
				break
		links = soup.find_all('a', href=lambda x: x and any(w in x.lower() for w in ['event','seminar','colloquium','talk','lecture','workshop','conference']))
		print(f"Found {len(links)} event links")
		events = []
		for it in items:
			try:
				e = self.parse_item(it)
				if e and self.is_academic_event(e):
					events.append(e)
			except Exception as e:
				print(f"Item err: {e}")
		for a in links:
			try:
				e = self.parse_link(a)
				if e and self.is_academic_event(e):
					events.append(e)
			except Exception as e:
				print(f"Link err: {e}")
		seen = set(); uniq = []
		for e in events:
			k = e['title'].lower().strip()
			if k not in seen:
				seen.add(k); uniq.append(e)
		print(f"Extracted {len(events)} events, {len(uniq)} unique")
		return uniq

	def parse_item(self, it):
		title_elem = it.find('span', class_='field--name-title') or it.find('h3') or it.find('a', href=True)
		if not title_elem: return None
		title = title_elem.get_text().strip()
		if len(title) < 5: return None
		date_elem = it.find('div', class_=lambda x: x and 'date' in x.lower())
		start_date = self.extract_date_from_text(date_elem.get_text()) if date_elem else self.extract_date_from_text(title)
		loc_elem = it.find('div', class_=lambda x: x and 'location' in x.lower())
		location = loc_elem.get_text().strip() if loc_elem else 'TBD'
		link = it.find('a', href=True)
		href = ''
		if link:
			href = link['href']
			if href.startswith('/'):
				href = f"https://sociology.princeton.edu{href}"
			elif not href.startswith('http'):
				href = f"https://sociology.princeton.edu/{href}"
		return {
			'id': f"sociology_{start_date}_{title[:20].replace(' ','_')}",
			'title': title,
			'description': title,
			'start_date': start_date,
			'end_date': None,
			'time': '',
			'location': location,
			'event_type': self.determine_event_type(title),
			'department': 'Sociology',
			'meta_category': 'social_sciences',
			'source_url': href,
			'source_name': 'Sociology Department Events',
			'tags': self.extract_tags(title),
			'created_at': datetime.now().isoformat(),
			'updated_at': datetime.now().isoformat()
		}

	def parse_link(self, a):
		title = a.get_text().strip()
		if len(title) < 5: return None
		href = a.get('href')
		if href.startswith('/'):
			href = f"https://sociology.princeton.edu{href}"
		elif not href.startswith('http'):
			href = f"https://sociology.princeton.edu/{href}"
		start_date = self.extract_date_from_text(title)
		return {
			'id': f"sociology_{start_date}_{title[:20].replace(' ','_')}",
			'title': title,
			'description': title,
			'start_date': start_date,
			'end_date': None,
			'time': '',
			'location': 'TBD',
			'event_type': self.determine_event_type(title),
			'department': 'Sociology',
			'meta_category': 'social_sciences',
			'source_url': href,
			'source_name': 'Sociology Department Events',
			'tags': self.extract_tags(title),
			'created_at': datetime.now().isoformat(),
			'updated_at': datetime.now().isoformat()
		}

	def extract_date_from_text(self, text):
		if not text: return datetime.now().strftime('%Y-%m-%d')
		for pat in [r'(\w+ \d{1,2},? \d{4})', r'(\d{1,2}/\d{1,2}/\d{4})', r'(\d{4}-\d{2}-\d{2})', r'(\w+ \d{1,2})']:
			m = re.search(pat, text, re.I)
			if m:
				for fmt in ['%B %d, %Y','%B %d %Y','%m/%d/%Y','%Y-%m-%d','%B %d']:
					try:
						dt = datetime.strptime(m.group(1), fmt)
						if fmt == '%B %d': dt = dt.replace(year=datetime.now().year)
						return dt.strftime('%Y-%m-%d')
					except: pass
		return datetime.now().strftime('%Y-%m-%d')

	def determine_event_type(self, title):
		t = title.lower()
		mapping = {'seminar':'Seminar','lecture':'Lecture','talk':'Talk','colloquium':'Colloquium','workshop':'Workshop','conference':'Conference','symposium':'Symposium','panel':'Panel'}
		for k,v in mapping.items():
			if k in t: return v
		return 'Academic Event'

	def extract_tags(self, title):
		text = title.lower(); tags=[]
		for tag in ['seminar','lecture','talk','colloquium','workshop','conference','symposium','sociology','social','inequality','race','gender','class','demography','organizations','culture']:
			if tag in text: tags.append(tag)
		return tags

	def is_academic_event(self, e):
		t = e['title'].lower(); acad=['seminar','lecture','talk','colloquium','workshop','conference','symposium']; non=['reception','party','festival']
		return any(k in t for k in acad) and not any(k in t for k in non)

	def save_events(self, events):
		if not events: print('No events to save'); return
		fn='sociology_cloudscraper_events.json'
		with open(fn,'w',encoding='utf-8') as f:
			json.dump({'metadata':{'total_events':len(events),'department':'Sociology','scraped_at':datetime.now().isoformat()},'events':events},f,indent=2,ensure_ascii=False)
		print(f"Saved {len(events)} events to {fn}")


def main():
	s=SociologyCloudScraper()
	e=s.scrape_sociology_events()
	if e:
		s.save_events(e)
		print(f"🎓 Successfully scraped {len(e)} Sociology events!")
	else:
		print('💀 No Sociology events found.')

if __name__=='__main__':
	main()
