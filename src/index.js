// Princeton Academic Events API
// Cloudflare Worker for serving Princeton academic events

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
      if (path === '/api/events') {
        return await handleEvents(request, env, corsHeaders);
      } else if (path === '/api/departments') {
        return await handleDepartments(request, env, corsHeaders);
      } else if (path === '/api/events/search') {
        return await handleSearch(request, env, corsHeaders);
      } else if (path === '/api/rss') {
        return await handleRSS(request, env, corsHeaders);
      } else if (path === '/api/stats') {
        return await handleStats(request, env, corsHeaders);
      } else if (path === '/api/import') {
        return await handleImport(request, env, corsHeaders);
      } else if (path === '/api/clear') {
        return await handleClear(request, env, corsHeaders);
      } else if (path === '/api/refresh') {
        return await handleRefresh(request, env, corsHeaders);
      } else if (path === '/') {
        return new Response(JSON.stringify({
          name: 'Princeton Academic Events API',
          version: '2.0.0',
          description: 'API for Princeton University academic events with meta-category filtering',
          endpoints: {
            events: '/api/events',
            departments: '/api/departments',
            search: '/api/events/search',
            rss: '/api/rss',
            stats: '/api/stats',
            import: '/api/import',
            clear: '/api/clear',
            categories: {
              humanities: 'Humanities departments',
              socialSciences: 'Social Sciences departments',
              science: 'Science departments',
              engineering: 'Engineering departments',
              technology: 'Technology Policy departments',
              environmental: 'Environmental Studies departments'
            }
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
  }
};

// Meta-categories mapping
const META_CATEGORIES = {
  humanities: ['Philosophy', 'History', 'English', 'Classics', 'Religion', 'Comparative Literature', 'Art and Archaeology', 'Music', 'Near Eastern Studies', 'Latin American Studies', 'Gender and Sexuality Studies', 'Hellenic Studies', 'South Asian Studies', 'East Asian Studies'],
  socialSciences: ['Politics', 'Psychology', 'Sociology', 'Economics', 'Anthropology', 'Public and International Affairs'],
  science: ['Physics', 'Computer Science', 'Molecular Biology', 'Ecology and Evolutionary Biology', 'Geosciences', 'Mathematics'],
  engineering: ['Chemical and Biological Engineering', 'Civil and Environmental Engineering', 'Electrical and Computer Engineering', 'Operations Research and Financial Engineering', 'Program in Applied and Computational Mathematics'],
  technology: ['Center for Information Technology Policy'],
  environmental: ['Program in Environmental Studies']
};

// Handle events endpoint
async function handleEvents(request, env, corsHeaders) {
  const url = new URL(request.url);
  const params = url.searchParams;
  
  // Build query for new data structure
  let query = `
    SELECT e.*, e.department
    FROM events e
    WHERE 1=1
  `;
  const queryParams = [];

  // Filter by department
  if (params.get('department')) {
    query += ' AND e.department = ?';
    queryParams.push(params.get('department'));
  }

  // Filter by meta category
  if (params.get('category') && params.get('category') !== 'all') {
    const category = params.get('category');
    const departments = META_CATEGORIES[category] || [];
    if (departments.length > 0) {
      const placeholders = departments.map(() => '?').join(',');
      query += ` AND e.department IN (${placeholders})`;
      queryParams.push(...departments);
    }
  }

  // Filter by date range
  if (params.get('start_date')) {
    query += ' AND e.date >= ?';
    queryParams.push(params.get('start_date'));
  }

  if (params.get('end_date')) {
    query += ' AND e.date <= ?';
    queryParams.push(params.get('end_date'));
  }

  // Search in title and description
  if (params.get('q')) {
    query += ' AND (e.title LIKE ? OR e.description LIKE ? OR e.department LIKE ?)';
    const searchTerm = `%${params.get('q')}%`;
    queryParams.push(searchTerm, searchTerm, searchTerm);
  }

  // Order by date
  query += ' ORDER BY e.date ASC, e.time ASC';

  // Pagination
  const limit = parseInt(params.get('limit')) || 50;
  const offset = parseInt(params.get('offset')) || 0;
  query += ' LIMIT ? OFFSET ?';
  queryParams.push(limit, offset);

  const events = await env.DB.prepare(query).bind(...queryParams).all();

  return new Response(JSON.stringify({
    events: events.results,
    pagination: {
      limit,
      offset,
      total: events.results.length
    }
  }), { headers: corsHeaders });
}

// Handle departments endpoint
async function handleDepartments(request, env, corsHeaders) {
  const url = new URL(request.url);
  const params = url.searchParams;
  
  let query = 'SELECT DISTINCT department FROM events WHERE department IS NOT NULL';
  const queryParams = [];

  // Filter by meta category
  if (params.get('category') && params.get('category') !== 'all') {
    const category = params.get('category');
    const departments = META_CATEGORIES[category] || [];
    if (departments.length > 0) {
      const placeholders = departments.map(() => '?').join(',');
      query += ` AND department IN (${placeholders})`;
      queryParams.push(...departments);
    }
  }

  query += ' ORDER BY department ASC';

  const departments = await env.DB.prepare(query).bind(...queryParams).all();

  return new Response(JSON.stringify({
    departments: departments.results.map(d => ({ name: d.department, slug: d.department.toLowerCase().replace(/\s+/g, '-') }))
  }), { headers: corsHeaders });
}

// Handle search endpoint
async function handleSearch(request, env, corsHeaders) {
  const url = new URL(request.url);
  const query = url.searchParams.get('q');
  
  if (!query) {
    return new Response(JSON.stringify({ error: 'Query parameter required' }), {
      status: 400,
      headers: corsHeaders
    });
  }

  const searchQuery = `
    SELECT e.*
    FROM events e
    WHERE (e.title LIKE ? OR e.description LIKE ? OR e.department LIKE ?)
    ORDER BY e.date ASC
    LIMIT 50
  `;

  const searchTerm = `%${query}%`;
  const events = await env.DB.prepare(searchQuery).bind(searchTerm, searchTerm, searchTerm).all();

  return new Response(JSON.stringify({
    query,
    events: events.results,
    total: events.results.length
  }), { headers: corsHeaders });
}

// Handle RSS feed
async function handleRSS(request, env, corsHeaders) {
  const url = new URL(request.url);
  const params = url.searchParams;
  
  let query = `
    SELECT e.*
    FROM events e
    WHERE 1=1
  `;
  const queryParams = [];

  // Filter by department
  if (params.get('department')) {
    query += ' AND e.department = ?';
    queryParams.push(params.get('department'));
  }

  // Filter by meta category
  if (params.get('category') && params.get('category') !== 'all') {
    const category = params.get('category');
    const departments = META_CATEGORIES[category] || [];
    if (departments.length > 0) {
      const placeholders = departments.map(() => '?').join(',');
      query += ` AND e.department IN (${placeholders})`;
      queryParams.push(...departments);
    }
  }

  query += ' ORDER BY e.date ASC LIMIT 100';

  const events = await env.DB.prepare(query).bind(...queryParams).all();

  // Generate RSS XML
  const rss = generateRSS(events.results, params);
  
  return new Response(rss, {
    headers: {
      'Content-Type': 'application/rss+xml',
      'Access-Control-Allow-Origin': '*'
    }
  });
}

// Handle stats endpoint
async function handleStats(request, env, corsHeaders) {
  const stats = await env.DB.prepare(`
    SELECT 
      (SELECT COUNT(*) FROM events) as total_events,
      (SELECT COUNT(DISTINCT department) FROM events WHERE department IS NOT NULL) as total_departments,
      (SELECT COUNT(*) FROM events WHERE date IS NOT NULL AND date >= date('now')) as upcoming_events,
      (SELECT COUNT(*) FROM events WHERE date IS NOT NULL AND date < date('now')) as past_events
  `).first();

  // Category stats
  const categoryStats = [];
  for (const [category, departments] of Object.entries(META_CATEGORIES)) {
    const placeholders = departments.map(() => '?').join(',');
    const count = await env.DB.prepare(`
      SELECT COUNT(*) as count FROM events WHERE department IN (${placeholders})
    `).bind(...departments).first();
    
    categoryStats.push({
      category,
      event_count: count.count,
      departments: departments
    });
  }

  return new Response(JSON.stringify({
    stats: stats,
    categories: categoryStats
  }), { headers: corsHeaders });
}

// Generate RSS feed
function generateRSS(events, params) {
  const getCategoryName = (category) => {
    const names = {
      humanities: 'Humanities',
      socialSciences: 'Social Sciences',
      science: 'Science',
      engineering: 'Engineering',
      technology: 'Technology Policy',
      environmental: 'Environmental Studies'
    };
    return names[category] || category;
  };

  const title = params.get('department') 
    ? `Princeton ${params.get('department')} Events`
    : params.get('category')
    ? `Princeton ${getCategoryName(params.get('category'))} Events`
    : 'Princeton Academic Events';

  const description = params.get('department')
    ? `Academic events from Princeton ${params.get('department')} department`
    : params.get('category')
    ? `Academic events from Princeton ${getCategoryName(params.get('category'))} departments`
    : 'Academic events from Princeton University departments';

  let rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${title}</title>
  <link>https://princeton-academic-events.spergel-joshua.workers.dev</link>
  <description>${description}</description>
  <language>en-us</language>
  <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
  <atom:link href="${params.get('category') ? `/api/rss?category=${params.get('category')}` : '/api/rss'}" rel="self" type="application/rss+xml" />`;

  events.forEach(event => {
    const pubDate = new Date(event.created_at).toUTCString();
    const description = event.description || 'No description available';
    const link = event.url || '#';
    
    rss += `
  <item>
    <title><![CDATA[${event.title}]]></title>
    <link>${link}</link>
    <description><![CDATA[${description}]]></description>
    <pubDate>${pubDate}</pubDate>
    <category>${event.department}</category>
    <guid>${event.event_id || event.id}</guid>
  </item>`;
  });

  rss += `
</channel>
</rss>`;

  return rss;
}

// Handle clear endpoint
async function handleClear(request, env, corsHeaders) {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    await env.DB.prepare('DELETE FROM events').run();
    
    return new Response(JSON.stringify({
      message: 'Database cleared successfully'
    }), { headers: corsHeaders });

  } catch (error) {
    console.error('Clear error:', error);
    return new Response(JSON.stringify({ error: 'Clear failed' }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle data import
async function handleImport(request, env, corsHeaders) {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    const data = await request.json();
    
    if (!data.events || !Array.isArray(data.events)) {
      return new Response(JSON.stringify({ error: 'Invalid data format' }), {
        status: 400,
        headers: corsHeaders
      });
    }

    // Insert new events (don't clear existing ones)
    const stmt = env.DB.prepare(`
      INSERT INTO events (event_id, title, description, date, time, location, department, url, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const batch = data.events.map(event => 
      stmt.bind(
        event.event_id || event.id,
        event.title,
        event.description || null,
        event.date || null,
        event.time || null,
        event.location || null,
        event.department,
        event.url || null,
        new Date().toISOString(),
        new Date().toISOString()
      )
    );

    await env.DB.batch(batch);

    return new Response(JSON.stringify({
      message: `Successfully imported ${data.events.length} events`,
      count: data.events.length
    }), { headers: corsHeaders });

  } catch (error) {
    console.error('Import error:', error);
    return new Response(JSON.stringify({ error: 'Import failed' }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

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
    
    // For now, we'll simulate the scraping process
    // In a real implementation, this would call your actual scrapers
    const scrapedEvents = await simulateScraping();
    
    if (scrapedEvents && scrapedEvents.length > 0) {
      // Clear existing events and import new ones
      await env.DB.prepare('DELETE FROM events').run();
      
      const stmt = env.DB.prepare(`
        INSERT INTO events (event_id, title, description, date, time, location, department, url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      
      const batch = scrapedEvents.map(event => {
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
        message: `Successfully refreshed database with ${scrapedEvents.length} events`,
        count: scrapedEvents.length,
        timestamp: new Date().toISOString()
      }), { headers: corsHeaders });
      
    } else {
      return new Response(JSON.stringify({
        success: false,
        message: 'No events found during refresh',
        count: 0
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

// Simulate scraping process (replace with actual scraper calls)
async function simulateScraping() {
  console.log('🔍 Simulating scraping process...');
  
  // This is where you'd call your actual Python scrapers
  // For now, we'll return sample events
  const events = [
    {
      id: `refresh_${Date.now()}_1`,
      title: 'Philosophy Seminar - Ethics in AI',
      description: 'Discussion of ethical considerations in artificial intelligence',
      start_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '3:00 PM',
      location: '1879 Hall',
      department: 'Philosophy',
      source_url: 'https://philosophy.princeton.edu/events'
    },
    {
      id: `refresh_${Date.now()}_2`,
      title: 'History Workshop - Colonial Resistance',
      description: 'Workshop on resistance movements in colonial contexts',
      start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '2:00 PM',
      location: 'Dickinson Hall',
      department: 'History',
      source_url: 'https://history.princeton.edu/events'
    },
    {
      id: `refresh_${Date.now()}_3`,
      title: 'Mathematics Colloquium',
      description: 'Recent advances in algebraic geometry',
      start_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '4:30 PM',
      location: 'Fine Hall',
      department: 'Mathematics',
      source_url: 'https://math.princeton.edu/events'
    }
  ];
  
  console.log(`📊 Simulated scraping found ${events.length} events`);
  return events;
}
