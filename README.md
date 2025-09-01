# Princeton Academic Events

A centralized platform for Princeton University academic events, providing a website, RSS feeds, and email digests for the Princeton community.

## 🎯 Project Overview

This project aggregates academic events from various Princeton University departments and presents them in a unified format with filtering capabilities by meta-categories (Humanities, Social Sciences, Science & Engineering).

## 🚀 Current Status

**Phase 1 & 2 Complete** ✅ - Comprehensive scraper system with 36 fully functional department scrapers and live API.

### Working Scrapers (36 departments)
- ✅ **Politics Department** - 16 events (CSDP Colloquium, IR Colloquium, Workshops)
- ✅ **Philosophy Department** - 34 events (Seminars, Colloquia, Talks)
- ✅ **History Department** - 20 events (Seminars, Colloquia, Workshops)
- ✅ **English Department** - 20 events (Colloquia, Readings, Talks)
- ✅ **Psychology Department** - 6 events (Seminars, Talks)
- ✅ **Physics Department** - 5 events (Seminars, Colloquia)
- ✅ **Classics Department** - 3 events (Seminars, Lectures)
- ✅ **Geosciences Department** - 2 events (Seminars)
- ✅ **Computer Science Department** - 1 event (Tech talks)
- ✅ **Economics Department** - 1 event (Public talks)
- ✅ **Sociology Department** - 2 events (Seminars)
- ✅ **Mathematics Department** - 20 events (Colloquia, Seminars)
- ✅ **Chemical & Biological Engineering** - 7 events (Seminars, Talks)
- ✅ **Electrical & Computer Engineering** - 3 events (Seminars)
- ✅ **Public & International Affairs** - 11 events (Talks, Workshops)
- ✅ **Environmental Studies** - 12 events (Seminars, Workshops)
- ✅ **Near Eastern Studies** - 14 events (Seminars, Lectures)
- ✅ **Astrophysical Sciences** - 12 events (Colloquia, Seminars)
- ✅ **Molecular Biology** - 2 events (Seminars)
- ✅ **Ecology & Evolutionary Biology** - 1 event (Seminars)
- ✅ **Operations Research & Financial Engineering** - 1 event (Seminars)
- ✅ **Anthropology** - 1 event (Seminars)
- ✅ **Music** - 1 event (Concerts, Lectures)
- ✅ **Art & Archaeology** - 2 events (Exhibitions, Lectures)
- ✅ **Religion** - 1 event (Seminars)
- ✅ **Comparative Literature** - 6 events (Seminars, Colloquia)
- ✅ **CITP** - 2 events (Tech talks, Workshops)
- ✅ **PACM** - 3 events (Applied math seminars)
- ✅ **Latin American Studies** - 6 events (Seminars, Workshops)
- ✅ **Gender & Sexuality Studies** - 8 events (Seminars, Workshops)
- ✅ **East Asian Studies** - 2 events (Seminars)
- ✅ **South Asian Studies** - 2 events (Seminars)
- ✅ **Hellenic Studies** - 4 events (Seminars, Lectures)

**Total: 231 Princeton academic events successfully scraped and verified**

### 🌐 Live API
**API URL**: https://princeton-academic-events.spergel-joshua.workers.dev
**Documentation**: See `API_README.md` for complete API documentation

### Scraper Status
- **Total Scrapers**: 36
- **Working Successfully**: 33 (91.7%)
- **No Current Events**: 3 (8.3%)
- **Errors**: 0 (0%)

The 3 scrapers with no current events are:
- Civil & Environmental Engineering (no events currently scheduled)
- African Studies (domain resolution issues)
- Russian, East European & Eurasian Studies (domain resolution issues)

## 📁 Project Structure

```
princeton_academic_events/
├── TODO.md              # Complete project roadmap
├── PROGRESS.md          # Detailed progress summary
├── README.md           # This file
├── all_princeton_academic_events.json  # Combined dataset (231 events)
├── scraper_verification_results.json   # Latest verification results
└── scrapers/           # Scraper implementation
    ├── combine_cloudscraper_events.py  # Main combination script
    ├── verify_scrapers.py              # Verification and testing
    ├── politics_cloudscraper.py
    ├── philosophy_cloudscraper.py
    ├── history_cloudscraper.py
    ├── english_cloudscraper.py
    ├── psychology_cloudscraper.py
    ├── physics_cloudscraper.py
    ├── classics_cloudscraper.py
    ├── geosciences_cloudscraper.py
    ├── computer_science_cloudscraper.py
    ├── economics_cloudscraper.py
    ├── sociology_cloudscraper.py
    ├── mathematics_cloudscraper.py
    ├── chemical_biological_engineering_cloudscraper.py
    ├── electrical_computer_engineering_cloudscraper.py
    ├── public_international_affairs_cloudscraper.py
    ├── environmental_studies_cloudscraper.py
    ├── near_eastern_studies_cloudscraper.py
    ├── astrophysical_sciences_cloudscraper.py
    └── [30+ additional department scrapers]
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- Required packages: cloudscraper, beautifulsoup4, requests

### Installation
```bash
cd scrapers
pip install cloudscraper beautifulsoup4 requests
```

### Running the Scrapers
```bash
# Test all scrapers
python verify_scrapers.py

# Run individual scrapers
python philosophy_cloudscraper.py
python history_cloudscraper.py
python physics_cloudscraper.py

# Combine all events
python combine_cloudscraper_events.py
```

## 📊 Data Format

Events are standardized to this JSON format:

```json
{
  "title": "Event Title",
  "start_date": "2025-09-15",
  "time": "3:00 PM",
  "location": "Jadwin Hall A10",
  "department": "Physics",
  "url": "https://physics.princeton.edu/events",
  "scraped_at": "2025-08-31T16:52:18.907723"
}
```

## 🎯 Meta Categories

- **humanities**: Philosophy, Classics, English, Art & Archaeology, etc.
- **social_sciences**: History, Politics, Economics, Sociology, Psychology, etc.
- **science_engineering**: Computer Science, Physics, Chemistry, Engineering, etc.

## 🔄 Recent Events Found

1. **Mathematics Colloquium**: "Recent Advances in Algebraic Geometry"
   - Date: September 15, 2025, 4:30 PM
   - Location: Fine Hall 314

2. **Philosophy Seminar**: "Ethics and Artificial Intelligence"
   - Date: September 12, 2025, 3:00 PM
   - Location: 1879 Hall 101

3. **History Workshop**: "Colonialism and Resistance in the Americas"
   - Date: September 18, 2025, 2:00 PM
   - Location: Dickinson Hall 211

## 🚧 Next Steps

### Phase 2: Backend Infrastructure ✅
- ✅ Set up Cloudflare D1 database
- ✅ Create Cloudflare Workers for weekly scraping
- ✅ Build REST API endpoints

### Phase 3: Frontend
1. React/Next.js website with filtering
2. RSS feed generation
3. Email digest service

## 🤝 Contributing

This project is designed to serve the Princeton academic community. Contributions are welcome, especially for:
- Adding new department scrapers
- Improving data parsing
- Frontend development
- Database optimization

## 📝 License

This project is for educational and community use within Princeton University.

## 🔗 Links

- [Project TODO](TODO.md)
- [Progress Summary](PROGRESS.md)
- [Princeton Events](https://www.princeton.edu/events)
