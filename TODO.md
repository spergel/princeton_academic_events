# Princeton Academic Events - TODO

## Project Overview
Create a centralized website for Princeton University academic events with filtering, RSS feeds, and email listserv functionality.

## Current Status
- ✅ **Backend API**: Live at https://princeton-academic-events.spergel-joshua.workers.dev
- ✅ **Frontend**: Live at https://44aebbc2.princeton-academic-events-frontend.pages.dev
- ✅ **Data Collection**: 200+ events from 40+ departments
- ✅ **Core Functionality**: Search, filtering, responsive design

## Priority 1: Critical Fixes

### 1.1 Scraper Issues
- [ ] **Fix Philosophy scraper** - Investigate and resolve any date parsing or data extraction issues
- [ ] **Fix Math scraper** - Investigate and resolve any date parsing or data extraction issues
- [ ] **Fix duplicate events** - Implement better deduplication logic across all scrapers
- [ ] **Math event routing** - Route to specific event pages instead of general events page

### 1.2 Data Quality
- [ ] **HTML rendering safety** - Safely render HTML content from event pages (prevent XSS)
- [ ] **Data validation** - Add comprehensive validation for all scraped data
- [ ] **Error handling** - Improve error handling and logging for failed scrapes

## Priority 2: UI/UX Improvements

### 2.1 Visual Design
- [ ] **Fix category colors** - Update and standardize category color scheme
- [ ] **Background design** - Add subtle background patterns or gradients
- [ ] **Mobile optimization** - Ensure excellent mobile experience across all devices
- [ ] **Typography** - Improve font choices and text hierarchy

### 2.2 User Experience
- [ ] **Calendar view** - Implement calendar view for events
- [ ] **Calendar integration** - Add "Add to Calendar" functionality (Google, Outlook, Apple)
- [ ] **Event details** - Improve event detail pages with better layout
- [ ] **Loading states** - Add proper loading indicators and skeleton screens

## Priority 3: New Features

### 3.1 Content & Information
- [ ] **About page** - Create comprehensive about page explaining the project
- [ ] **Help/FAQ** - Add help section and frequently asked questions
- [ ] **Contact page** - Add contact information and feedback form
- [ ] **Privacy policy** - Create privacy policy and terms of service

### 3.2 Advanced Functionality
- [ ] **Event notifications** - Allow users to subscribe to event notifications
- [ ] **Personal calendar** - Let users create personal event collections
- [ ] **Event sharing** - Add social sharing functionality
- [ ] **Advanced search** - Implement advanced search with filters

## Priority 4: Technical Improvements

### 4.1 Performance
- [ ] **Caching** - Implement better caching strategies
- [ ] **Image optimization** - Optimize and lazy load images
- [ ] **Bundle optimization** - Reduce JavaScript bundle size
- [ ] **API optimization** - Optimize API response times

### 4.2 Monitoring & Analytics
- [ ] **Error tracking** - Implement error tracking (Sentry, etc.)
- [ ] **Analytics** - Add usage analytics (privacy-friendly)
- [ ] **Performance monitoring** - Monitor Core Web Vitals
- [ ] **Uptime monitoring** - Set up uptime monitoring for API

## Priority 5: Content & Data

### 5.1 Data Expansion
- [ ] **More departments** - Add remaining Princeton departments
- [ ] **Event categories** - Refine and expand event categorization
- [ ] **Speaker information** - Better speaker data extraction and display
- [ ] **Location mapping** - Add location mapping and directions

### 5.2 Content Management
- [ ] **Admin interface** - Create admin interface for data management
- [ ] **Content moderation** - Add content moderation capabilities
- [ ] **Data export** - Allow data export in various formats
- [ ] **Backup system** - Implement data backup and recovery

## Priority 6: Future Enhancements

### 6.1 Advanced Features
- [ ] **Machine learning** - Use ML for event recommendations
- [ ] **Natural language search** - Implement semantic search
- [ ] **Event prediction** - Predict likely events based on patterns
- [ ] **Integration APIs** - Create APIs for third-party integrations

### 6.2 Community Features
- [ ] **User accounts** - Allow user registration and profiles
- [ ] **Event reviews** - Let users rate and review events
- [ ] **Discussion forums** - Add discussion capabilities for events
- [ ] **User-generated content** - Allow users to submit events

## Technical Debt & Maintenance

### Code Quality
- [ ] **Code review** - Implement code review process
- [ ] **Testing** - Add comprehensive test suite
- [ ] **Documentation** - Improve code documentation
- [ ] **Refactoring** - Refactor legacy code for better maintainability

### Infrastructure
- [ ] **CI/CD pipeline** - Set up automated deployment
- [ ] **Environment management** - Better environment configuration
- [ ] **Security audit** - Conduct security audit
- [ ] **Dependency updates** - Keep dependencies up to date

## Data Format Standards

### Event Object Structure
```json
{
  "id": "unique_event_id",
  "title": "Event Title",
  "description": "Event description",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "time": "HH:MM AM/PM",
  "location": "Event location",
  "event_type": "Seminar/Lecture/Talk/etc",
  "department": "Department name",
  "meta_category": "science_engineering|social_sciences|humanities",
  "source_url": "Original event URL",
  "source_name": "Source name",
  "speaker": "Speaker name",
  "speaker_affiliation": "Speaker affiliation",
  "tags": ["tag1", "tag2"],
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

### Meta Categories
- **Science & Engineering**: Computer Science, Mathematics, Physics, Chemistry, Biology, Engineering
- **Social Sciences**: History, Politics, Economics, Sociology, Psychology, Anthropology
- **Humanities**: Philosophy, English, Classics, Religion, Art & Archaeology, Music

## Current Architecture

### Backend (Cloudflare Workers)
- `src/index.js` - Main API worker with all endpoints
- `schema.sql` - Database schema for D1
- `wrangler.toml` - Cloudflare configuration
- `package.json` - Node.js project configuration

### Frontend (React/Next.js)
- `frontend/app/page.tsx` - Main page component
- `frontend/components/` - React components
- `frontend/types/events.ts` - TypeScript type definitions
- `frontend/tailwind.config.js` - Tailwind CSS configuration

### Scrapers (Python)
- Individual department scrapers
- Universal Drupal scraper
- JSON/ICS feed scrapers
- Master combination script

## Success Metrics
- [ ] **Performance**: < 2s page load time
- [ ] **Accessibility**: WCAG 2.1 AA compliance
- [ ] **Mobile**: 95+ Lighthouse mobile score
- [ ] **Data Quality**: < 1% duplicate events
- [ ] **Uptime**: 99.9% API availability
- [ ] **User Engagement**: Track user interactions and feedback

## Notes
- Focus on user experience and data quality
- Maintain Princeton branding and accessibility standards
- Ensure mobile-first responsive design
- Prioritize performance and reliability
- Keep security and privacy as top concerns