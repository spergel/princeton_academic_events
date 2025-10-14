export async function onRequestGet({ request }) {
  try {
    // For Cloudflare Pages Functions, we can fetch static assets from the same origin
    const eventsData = await fetch('/data/events.json');

    if (!eventsData.ok) {
      return new Response(JSON.stringify({
        error: 'Events data not found',
        message: 'Data will be available after the next weekly scrape'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = await eventsData.json();

    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
      }
    });
  } catch (error) {
    console.error('Error serving events:', error);
    return new Response(JSON.stringify({
      error: 'Internal server error',
      message: 'Unable to fetch events data'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
