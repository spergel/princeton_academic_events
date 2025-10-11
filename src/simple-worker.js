// Simple Princeton Academic Events API with Refresh Endpoint
import { ScraperService } from './scraper-service.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Content-Type': 'application/json',
    };

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // API Routes
      if (path === '/api/refresh') {
        return await handleRefresh(request, env, corsHeaders);
      } else if (path === '/api/import') {
        return await handleImport(request, env, corsHeaders);
      } else if (path === '/api/events') {
        return await handleEvents(request, env, corsHeaders);
      } else if (path === '/api/departments') {
        return await handleDepartments(request, env, corsHeaders);
      } else if (path === '/api/rss') {
        return await handleRSS(request, env, corsHeaders);
      } else if (path === '/') {
        return new Response(JSON.stringify({
          name: 'Princeton Academic Events API',
          version: '2.0.0',
          description: 'API for Princeton University academic events with automated refresh',
          endpoints: {
            events: '/api/events',
            refresh: '/api/refresh (POST to trigger scraping)',
            import: '/api/import (POST to import external data)'
          }
        }), { headers: corsHeaders });
      } else {
        return new Response(JSON.stringify({ error: 'Not Found' }), {
          status: 404,
          headers: corsHeaders
        });
      }
    } catch (error) {
      console.error('API Error:', error);
      return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
        status: 500,
        headers: corsHeaders
      });
    }
  },

  // Scheduled trigger - runs every Sunday at 2 AM UTC
  async scheduled(event, env, ctx) {
    console.log('⏰ Scheduled scraping triggered at:', new Date().toISOString());
    
    try {
      // Run the refresh process automatically
      const scraperService = new ScraperService();
      const scrapingResults = await scraperService.runAllScrapers();
      const allEvents = await scraperService.combineAllEvents(scrapingResults);
      const filteredEvents = await scraperService.filterHighQualityEvents(allEvents);
      
      if (filteredEvents && filteredEvents.length > 0) {
        // Clear existing events and import new ones
        await env.DB.prepare('DELETE FROM events').run();
        
        const stmt = env.DB.prepare(`
          INSERT INTO events (event_id, title, description, date, time, location, department, url, created_at, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        
        const batch = filteredEvents.map(event => {
          const eventId = event.id || event.event_id || `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const title = event.title || 'Untitled Event';
          const description = event.description || null;
          const eventDate = event.start_date || event.date || null;
          const time = event.time || null;
          const location = event.location || null;
          const department = event.department || 'Unknown Department';
          const url = event.source_url || event.url || null;
          const now = new Date().toISOString();
          
          return stmt.bind(eventId, title, description, eventDate, time, location, department, url, now, now);
        });
        
        await env.DB.batch(batch);
        
        console.log(`✅ Scheduled scraping completed successfully! Imported ${filteredEvents.length} events`);
      } else {
        console.log('⚠️ Scheduled scraping completed but no high-quality events found');
      }
      
    } catch (error) {
      console.error('❌ Scheduled scraping failed:', error);
    }
  }
};

// Handle refresh endpoint - automatically scrape and update
async function handleRefresh(request, env, corsHeaders) {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    console.log('🔄 Refresh endpoint triggered - starting automated scraping...');
    
    // Initialize the scraper service
    const scraperService = new ScraperService();
    
    // Run all scrapers
    console.log('🚀 Starting comprehensive scraping...');
    const scrapingResults = await scraperService.runAllScrapers();
    
    // Combine all events
    const allEvents = await scraperService.combineAllEvents(scrapingResults);
    
    // Filter for high-quality events
    const filteredEvents = await scraperService.filterHighQualityEvents(allEvents);
    
    if (filteredEvents && filteredEvents.length > 0) {
      console.log(`📊 Importing ${filteredEvents.length} high-quality events to database...`);
      
      // Clear existing events and import new ones
      await env.DB.prepare('DELETE FROM events').run();
      
      const stmt = env.DB.prepare(`
        INSERT INTO events (event_id, title, description, date, time, location, department, url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      
      const batch = filteredEvents.map(event => {
        const eventId = event.id || event.event_id || `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const title = event.title || 'Untitled Event';
        const description = event.description || null;
        const eventDate = event.start_date || event.date || null;
        const time = event.time || null;
        const location = event.location || null;
        const department = event.department || 'Unknown Department';
        const url = event.source_url || event.url || null;
        const now = new Date().toISOString();
        
        return stmt.bind(eventId, title, description, eventDate, time, location, department, url, now, now);
      });
      
      await env.DB.batch(batch);
      
      return new Response(JSON.stringify({
        success: true,
        message: `Successfully refreshed database with ${filteredEvents.length} high-quality events`,
        count: filteredEvents.length,
        timestamp: new Date().toISOString(),
        summary: {
          totalScraped: allEvents.length,
          totalImported: filteredEvents.length,
          departmentsScraped: Object.keys(scrapingResults.departments).length,
          departmentsWithEvents: Object.keys(scrapingResults.departments).filter(d => scrapingResults.departments[d].count > 0).length,
          errors: scrapingResults.errors.length,
          processingTime: `${scrapingResults.startTime} to ${scrapingResults.endTime}`
        }
      }), { headers: corsHeaders });
      
    } else {
      return new Response(JSON.stringify({
        success: false,
        message: 'No high-quality events found during refresh',
        count: 0,
        summary: {
          totalScraped: allEvents.length,
          totalImported: 0,
          departmentsScraped: Object.keys(scrapingResults.departments).length,
          errors: scrapingResults.errors.length
        }
      }), { headers: corsHeaders });
    }
    
  } catch (error) {
    console.error('Refresh error:', error);
    return new Response(JSON.stringify({ 
      error: 'Refresh failed', 
      details: error.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle import endpoint - import external event data
async function handleImport(request, env, corsHeaders) {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    console.log('📥 Import endpoint triggered - importing external event data...');
    
    const requestData = await request.json();
    const events = requestData.events || [];
    
    if (!events || events.length === 0) {
      return new Response(JSON.stringify({ 
        error: 'No events provided',
        message: 'Please provide events array in request body'
      }), {
        status: 400,
        headers: corsHeaders
      });
    }
    
    console.log(`📊 Importing ${events.length} events to database...`);
    
    // Clear existing events and import new ones
    await env.DB.prepare('DELETE FROM events').run();
    
    const stmt = env.DB.prepare(`
      INSERT INTO events (event_id, title, description, date, time, location, department, url, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    const batch = events.map((event, index) => {
      // Generate truly unique event ID with timestamp and index
      const timestamp = Date.now();
      const uniqueId = `event_${timestamp}_${index}_${Math.random().toString(36).substr(2, 9)}`;
      
      const title = event.title || 'Untitled Event';
      const description = event.description || null;
      const eventDate = event.start_date || event.date || null;
      const time = event.time || null;
      const location = event.location || null;
      const department = event.department || 'Unknown Department';
      const url = event.source_url || event.url || null;
      const now = new Date().toISOString();
      
      return stmt.bind(uniqueId, title, description, eventDate, time, location, department, url, now, now);
    });
    
    await env.DB.batch(batch);
    
    // Department breakdown
    const dept_counts = {};
    for (const event of events) {
      const dept = event.department || 'Unknown';
      dept_counts[dept] = (dept_counts[dept] || 0) + 1;
    }
    
    return new Response(JSON.stringify({
      success: true,
      message: `Successfully imported ${events.length} events`,
      count: events.length,
      timestamp: new Date().toISOString(),
      summary: {
        totalImported: events.length,
        departments: Object.keys(dept_counts).length,
        departmentBreakdown: dept_counts
      }
    }), { headers: corsHeaders });
    
  } catch (error) {
    console.error('Import error:', error);
    return new Response(JSON.stringify({ 
      error: 'Import failed', 
      details: error.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle events endpoint
async function handleEvents(request, env, corsHeaders) {
  try {
    const events = await env.DB.prepare('SELECT * FROM events ORDER BY date ASC, time ASC').all();
    
    return new Response(JSON.stringify({
      events: events.results,
      count: events.results.length
    }), { headers: corsHeaders });
    
  } catch (error) {
    console.error('Events error:', error);
    return new Response(JSON.stringify({ error: 'Failed to fetch events' }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle departments endpoint
async function handleDepartments(request, env, corsHeaders) {
  try {
    const result = await env.DB.prepare(`
      SELECT DISTINCT department, COUNT(*) as event_count 
      FROM events 
      WHERE department IS NOT NULL AND department != 'Unknown Department'
      GROUP BY department 
      ORDER BY event_count DESC
    `).all();
    
    const departments = result.results.map(row => ({
      name: row.department,
      event_count: row.event_count
    }));
    
    return new Response(JSON.stringify({
      departments: departments,
      count: departments.length,
      total_events: departments.reduce((sum, dept) => sum + dept.event_count, 0)
    }), { headers: corsHeaders });
    
  } catch (error) {
    console.error('Departments error:', error);
    return new Response(JSON.stringify({ error: 'Failed to fetch departments' }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle RSS feed endpoint
async function handleRSS(request, env, corsHeaders) {
  try {
    const events = await env.DB.prepare(`
      SELECT title, description, date, time, location, department, url, created_at 
      FROM events 
      ORDER BY date ASC, time ASC 
      LIMIT 50
    `).all();
    
    // Generate RSS XML
    const rssXml = generateRSSXML(events.results);
    
    return new Response(rssXml, {
      headers: {
        'Content-Type': 'application/xml; charset=utf-8',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    console.error('RSS error:', error);
    return new Response(JSON.stringify({ error: 'Failed to generate RSS feed' }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Generate RSS XML
function generateRSSXML(events) {
  const now = new Date().toISOString();
  
  let rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Princeton Academic Events</title>
    <link>https://princeton-academic-events.spergel-joshua.workers.dev</link>
    <description>Latest academic events from Princeton University departments</description>
    <language>en-us</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="https://princeton-academic-events.spergel-joshua.workers.dev/api/rss" rel="self" type="application/rss+xml"/>
    <generator>Princeton Academic Events API</generator>`;
  
  events.forEach(event => {
    const title = event.title || 'Untitled Event';
    const description = event.description || 'No description available';
    const date = event.date || event.created_at;
    const location = event.location || 'Location TBA';
    const department = event.department || 'Unknown Department';
    const url = event.url || 'https://princeton-academic-events.spergel-joshua.workers.dev';
    
    // Format date for RSS
    const pubDate = date ? new Date(date).toUTCString() : new Date().toUTCString();
    
    rss += `
    <item>
      <title><![CDATA[${title}]]></title>
      <description><![CDATA[${description}]]></description>
      <link>${url}</link>
      <guid>${url}</guid>
      <pubDate>${pubDate}</pubDate>
      <category>${department}</category>
      <location>${location}</location>
    </item>`;
  });
  
  rss += `
  </channel>
</rss>`;
  
  return rss;
}
