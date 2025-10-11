# Princeton Academic Events - Project Structure

## 📁 Clean Project Organization

```
princeton_academic_events/
├── 📄 README.md                    # Main project overview
├── 📄 TODO.md                      # Project roadmap and progress
├── 📄 PROGRESS.md                  # Detailed progress tracking
├── 📄 API_README.md                # Complete API documentation
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
│
├── 🗄️ Backend/                     # Cloudflare Workers & Database
│   ├── src/
│   │   └── index.js               # Main API worker
│   ├── schema.sql                 # Database schema
│   ├── wrangler.toml              # Cloudflare configuration
│   ├── package.json               # Node.js configuration
│   ├── import-events.js           # Local data import
│   └── import-remote.js           # Remote data import
│
├── 🕷️ Scrapers/                    # Python scraping infrastructure
│   ├── all_princeton_academic_events.json    # Combined events dataset
│   ├── combine_cloudscraper_events.py        # Master combiner script
│   ├── test_all_princeton_departments.py     # Department tester
│   ├── princeton_department_test_results.json # Test results
│   │
│   ├── Working Scrapers/          # 12 functional department scrapers
│   │   ├── math_cloudscraper.py              # Mathematics (28 events)
│   │   ├── politics_cloudscraper.py          # Politics (16 events)
│   │   ├── philosophy_cloudscraper.py        # Philosophy (14 events)
│   │   ├── history_cloudscraper.py           # History (13 events)
│   │   ├── english_cloudscraper.py           # English (13 events)
│   │   ├── psychology_cloudscraper.py        # Psychology (6 events)
│   │   ├── physics_cloudscraper.py           # Physics (4 events)
│   │   ├── classics_cloudscraper.py          # Classics (3 events)
│   │   ├── geosciences_cloudscraper.py       # Geosciences (2 events)
│   │   ├── computer_science_cloudscraper.py  # Computer Science (1 event)
│   │   ├── economics_cloudscraper.py         # Economics (1 event)
│   │   └── sociology_cloudscraper.py         # Sociology (1 event)
│   │
│   └── Archived/                  # Non-working scrapers (for reference)
│       └── (future blocked department scrapers)
│
└── 🚀 Deployment/                  # Production deployment files
    ├── .wrangler/                 # Cloudflare local state
    └── node_modules/              # Node.js dependencies
```

## 🎯 Current Status

### ✅ **Phase 1: Data Collection** - COMPLETED
- **12 Working Scrapers** collecting from Princeton departments
- **102 Total Events** successfully scraped
- **41 Accessible Departments** identified for future expansion
- **Cloudscraper Implementation** bypassing anti-bot protection

### ✅ **Phase 2: Backend Infrastructure** - COMPLETED
- **Live API**: https://princeton-academic-events.spergel-joshua.workers.dev
- **Cloudflare D1 Database** with 72 events from 42 departments
- **REST API** with filtering, search, and RSS feeds
- **Complete Documentation** and integration examples

### 🔄 **Phase 3: Frontend Development** - NEXT
- React/Next.js website
- Princeton-branded UI
- Event filtering and search
- Calendar and list views

## 📊 Data Summary

### Working Departments (12)
1. **Mathematics** - 28 events (Seminars, Colloquia, Lectures)
2. **Politics** - 16 events (CSDP Colloquium, IR Colloquium, Workshops)
3. **Philosophy** - 14 events (Seminars, Colloquia, Talks)
4. **History** - 13 events (Seminars, Colloquia, Workshops)
5. **English** - 13 events (Colloquia, Readings, Talks)
6. **Psychology** - 6 events (Seminars, Talks)
7. **Physics** - 4 events (Seminars, Colloquia)
8. **Classics** - 3 events (Seminars, Lectures)
9. **Geosciences** - 2 events (Seminars)
10. **Computer Science** - 1 event (Tech talks)
11. **Economics** - 1 event (Public talks)
12. **Sociology** - 1 event (Seminars)

### Meta Categories
- **Science & Engineering**: 6 departments
- **Social Sciences**: 4 departments  
- **Humanities**: 2 departments

## 🛠️ Key Files

### Essential Backend Files
- `src/index.js` - Main API worker with all endpoints
- `schema.sql` - Database schema for D1
- `wrangler.toml` - Cloudflare configuration
- `package.json` - Node.js project configuration

### Essential Scraper Files
- `all_princeton_academic_events.json` - Combined events dataset
- `combine_cloudscraper_events.py` - Master combiner script
- `test_all_princeton_departments.py` - Department tester
- Individual department scrapers (12 working ones)

### Documentation Files
- `README.md` - Main project overview
- `API_README.md` - Complete API documentation
- `TODO.md` - Project roadmap and progress
- `PROGRESS.md` - Detailed progress tracking

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
npm install

# Start local development server
npm run dev

# Import data to local database
npm run import
```

### Production Deployment
```bash
# Deploy to Cloudflare Workers
npm run deploy

# Import data to remote database
node import-remote.js
```

### Scraper Management
```bash
# Run all scrapers
cd scrapers
python combine_cloudscraper_events.py

# Test department accessibility
python test_all_princeton_departments.py
```

## 🎯 Next Steps

1. **Phase 3**: Build React frontend with Princeton branding
2. **Phase 4**: Deploy to Cloudflare Pages with custom domain
3. **Future**: Add email digests, calendar integration, mobile app

## 📝 Notes

- All temporary HTML files and individual JSON outputs have been cleaned up
- Only essential files are kept for a clean, maintainable codebase
- The project is production-ready with a live API and comprehensive documentation
- Ready for frontend development and further expansion
