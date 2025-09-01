# Princeton Academic Events API

A comprehensive REST API for discovering academic events across Princeton University departments, built with Cloudflare Workers and D1 database.

## 🌐 Live API

**Base URL:** `https://princeton-academic-events.spergel-joshua.workers.dev`

## 📊 Current Status

- **Total Events:** 72 events
- **Total Departments:** 42 departments
- **Categories:** Science & Engineering, Social Sciences, Humanities, Interdisciplinary
- **Working Scrapers:** 12 departments with active event collection

## 🚀 API Endpoints

### 1. API Information
```
GET /
```
Returns basic API information and available endpoints.

**Response:**
```json
{
  "name": "Princeton Academic Events API",
  "version": "1.0.0",
  "endpoints": {
    "events": "/api/events",
    "departments": "/api/departments",
    "search": "/api/events/search",
    "rss": "/api/events/rss",
    "stats": "/api/stats"
  }
}
```

### 2. Events
```
GET /api/events
```

**Query Parameters:**
- `department` - Filter by department slug (e.g., `computer-science`)
- `category` - Filter by meta category (`science_engineering`, `social_sciences`, `humanities`, `interdisciplinary`)
- `type` - Filter by event type (e.g., `Lecture`, `Seminar`, `Colloquium`)
- `start_date` - Filter events from this date (YYYY-MM-DD)
- `end_date` - Filter events until this date (YYYY-MM-DD)
- `q` - Search in title and description
- `limit` - Number of events to return (default: 50, max: 100)
- `offset` - Number of events to skip (default: 0)

**Example:**
```
GET /api/events?department=physics&limit=10
```

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "event_id": "physics_1_quantum_mechanics",
      "title": "Quantum Mechanics Seminar",
      "description": "Weekly seminar on quantum mechanics...",
      "start_date": "2025-01-15",
      "end_date": null,
      "time": "3:00 PM",
      "location": "Jadwin Hall A10",
      "event_type": "Seminar",
      "department_name": "Physics",
      "department_slug": "physics",
      "meta_category": "science_engineering",
      "source_url": "https://physics.princeton.edu/events/...",
      "tags": ["quantum", "physics", "seminar"]
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 1
  }
}
```

### 3. Departments
```
GET /api/departments
```

**Query Parameters:**
- `category` - Filter by meta category

**Example:**
```
GET /api/departments?category=science_engineering
```

**Response:**
```json
{
  "departments": [
    {
      "id": 1,
      "name": "Computer Science",
      "slug": "computer-science",
      "meta_category": "science_engineering",
      "events_url": "https://www.cs.princeton.edu/events",
      "is_active": 1
    }
  ]
}
```

### 4. Search
```
GET /api/events/search?q={query}
```

**Example:**
```
GET /api/events/search?q=lecture
```

**Response:**
```json
{
  "query": "lecture",
  "events": [...],
  "total": 15
}
```

### 5. RSS Feed
```
GET /api/events/rss
```

**Query Parameters:**
- `department` - Filter by department slug
- `category` - Filter by meta category

**Example:**
```
GET /api/events/rss?department=mathematics
```

**Response:** RSS 2.0 XML feed

### 6. Statistics
```
GET /api/stats
```

**Response:**
```json
{
  "stats": {
    "total_events": 72,
    "total_departments": 42,
    "upcoming_events": 0,
    "past_events": 28
  },
  "categories": [
    {
      "meta_category": "humanities",
      "event_count": 30
    }
  ],
  "event_types": [
    {
      "event_type": "Lecture",
      "count": 25
    }
  ]
}
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
npm install

# Start local development server
npm run dev

# Import data to local database
npm run import
```

### Deployment
```bash
# Deploy to Cloudflare Workers
npm run deploy

# Deploy to staging
npm run deploy:staging
```

### Database Management
```bash
# Execute SQL on local database
npm run db:local

# Execute SQL on remote database
npm run db:remote
```

## 📁 Project Structure

```
princeton_academic_events/
├── src/
│   └── index.js              # Main API worker
├── scrapers/                 # Python scraping scripts
│   ├── all_princeton_academic_events.json
│   ├── combine_cloudscraper_events.py
│   └── [department]_cloudscraper.py
├── schema.sql               # Database schema
├── wrangler.toml            # Cloudflare configuration
├── package.json             # Node.js configuration
├── import-events.js         # Local data import
├── import-remote.js         # Remote data import
└── API_README.md            # This file
```

## 🗄️ Database Schema

### Departments Table
- `id` - Primary key
- `name` - Department name
- `slug` - URL-friendly identifier
- `meta_category` - Category (science_engineering, social_sciences, humanities, interdisciplinary)
- `events_url` - Department events page URL
- `is_active` - Whether department is active

### Events Table
- `id` - Primary key
- `event_id` - Unique event identifier
- `title` - Event title
- `description` - Event description
- `start_date` - Event start date
- `end_date` - Event end date
- `time` - Event time
- `location` - Event location
- `event_type` - Type of event
- `department_id` - Foreign key to departments
- `source_url` - Original event URL
- `source_name` - Source name
- `tags` - JSON array of tags

## 🌟 Features

- **RESTful API** with comprehensive filtering and search
- **RSS Feeds** for easy subscription
- **CORS Support** for web applications
- **Pagination** for large result sets
- **Real-time Statistics** on events and departments
- **Cloudflare Workers** for global edge deployment
- **D1 Database** for fast, serverless SQL queries

## 🔗 Integration Examples

### JavaScript/Fetch
```javascript
// Get all physics events
const response = await fetch('https://princeton-academic-events.spergel-joshua.workers.dev/api/events?department=physics');
const data = await response.json();
console.log(data.events);

// Search for lectures
const searchResponse = await fetch('https://princeton-academic-events.spergel-joshua.workers.dev/api/events/search?q=lecture');
const searchData = await searchResponse.json();
console.log(searchData.events);
```

### Python/Requests
```python
import requests

# Get upcoming events
response = requests.get('https://princeton-academic-events.spergel-joshua.workers.dev/api/events?start_date=2025-01-01')
events = response.json()['events']

# Get RSS feed
rss_response = requests.get('https://princeton-academic-events.spergel-joshua.workers.dev/api/events/rss?category=science_engineering')
rss_content = rss_response.text
```

## 📈 Future Enhancements

- [ ] Email digest subscriptions
- [ ] Calendar integration (iCal feeds)
- [ ] Advanced search with filters
- [ ] Event recommendations
- [ ] Department-specific APIs
- [ ] Real-time event updates
- [ ] Mobile app support

## 🤝 Contributing

This API is part of the Princeton Academic Events project. For more information about the scraping infrastructure and data collection, see the main project documentation.

## 📄 License

MIT License - see LICENSE file for details.
