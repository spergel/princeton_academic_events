export async function onRequestGet({ request }) {
  try {
    // Fetch the events data from the static asset
    const eventsResponse = await fetch(new URL('/data/events.json', request.url));

    if (!eventsResponse.ok) {
      return new Response(JSON.stringify({
        error: 'Events data not found',
        message: 'Data will be available after the next weekly scrape'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const eventsData = await eventsResponse.json();

    return new Response(JSON.stringify(eventsData), {
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
