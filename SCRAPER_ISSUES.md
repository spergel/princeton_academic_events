# Scraper Issues Report

## 🚨 Critical Errors (Need Immediate Fix)

### 1. **Physics JSON Scraper** - Syntax Error
- **File**: `physics_json_scraper.py`
- **Error**: `unexpected indent (physics_json_scraper.py, line 285)`
- **Status**: ❌ BROKEN - Python syntax error
- **Action**: Fix indentation on line 285

### 2. **Domain Resolution Errors** - Multiple Departments
These domains don't exist or are unreachable:

- **French & Italian**: `frit.princeton.edu` - Domain not found
- **Medieval Studies**: `medieval.princeton.edu` - Domain not found  
- **African Studies**: `africanstudies.princeton.edu` - Domain not found
- **East Asian Studies**: `eastasianstudies.princeton.edu` - Domain not found
- **South Asian Studies**: `southasianstudies.princeton.edu` - Domain not found
- **Russian/East European Studies**: `rees.princeton.edu` - Domain not found
- **Astrophysical Sciences**: `astro.princeton.edu` - Domain not found

### 3. **Access Forbidden**
- **Environmental Studies**: `environment.princeton.edu/events` - Returns 403 Forbidden
- **Sociology**: `sociology.princeton.edu/events` - Returns 403 Forbidden (blocks automated requests)
- **Psychology**: `psychology.princeton.edu/events` - Returns 403 Forbidden (blocks automated requests)

## 📊 Scrapers with Zero Events (Need Investigation)

### Working URLs but No Events Found:  
- **Anthropology**: `https://anthropology.princeton.edu/events` - 0 events
- **History**: `https://history.princeton.edu/news-events/events` - 0 events
- **English**: `https://english.princeton.edu/events` - 0 events
- **Classics**: `https://classics.princeton.edu/events` - 0 events
- **Comparative Literature**: `https://complit.princeton.edu/events` - 0 events
- **Music**: `https://music.princeton.edu/events` - 0 events
- **Art & Archaeology**: `https://artandarchaeology.princeton.edu/events` - 0 events
- **Religion**: `https://religion.princeton.edu/events` - 0 events
- **Slavic Languages**: `https://slavic.princeton.edu/events` - 0 events
- **Gender & Sexuality Studies**: `https://gss.princeton.edu/events` - 0 events
- **Humanities Council**: `https://humanities.princeton.edu/events` - 0 events
- **Near Eastern Studies**: `https://nes.princeton.edu/events` - 0 events
- **Latin American Studies**: `https://plas.princeton.edu/events` - 0 events
- **Hellenic Studies**: `https://hellenic.princeton.edu/events` - 0 events
- **Chemical & Biological Engineering**: `https://cbe.princeton.edu/events` - 0 events
- **Operations Research**: `https://orfe.princeton.edu/events` - 0 events
- **Electrical Engineering**: `https://ece.princeton.edu/events` - 0 events
- **Molecular Biology**: `https://molbio.princeton.edu/events` - 0 events
- **Ecology & Evolutionary Biology**: `https://eeb.princeton.edu/events` - 0 events
- **Civil & Environmental Engineering**: `https://cee.princeton.edu/events` - 0 events
- **Mechanical & Aerospace Engineering**: `https://mae.princeton.edu/events` - 0 events
- **Center for Information Technology Policy**: `https://citp.princeton.edu/events` - 0 events

### Special Case - PACM:
- **Program in Applied & Computational Mathematics**: `https://pacm.princeton.edu/events` - Found 7 events but 0 unique events (likely duplicate filtering issue)

## ✅ Working Scrapers (7/41)

1. **Geosciences**: 97 events ✅
2. **Mathematics**: 83 events ✅  
3. **Philosophy**: 32 events ✅
4. **Politics**: 20 events ✅
5. **Computer Science**: 12 events ✅
6. **Economics**: 1 event ✅
7. **SPIA**: 1 event ✅

## 🎯 Priority Actions

### Immediate Fixes Needed:
1. **Fix physics_json_scraper.py** - Line 285 indentation error
2. **Remove broken domains** from scraper list
3. **Investigate zero-event departments** - may need different URLs or scraping methods
4. **Fix PACM scraper** - duplicate filtering issue

### Investigation Needed:
- Check if departments have moved to different URL structures
- Verify if some departments don't publish events online
- Consider alternative event sources for zero-event departments

## 📈 Current Status
- **Total Scrapers**: 41
- **Working**: 7 (17%)
- **Zero Events**: 24 (59%)
- **Broken/Errors**: 10 (24%)
- **Total Events Found**: 246
