import eventsData from '../frontend/data/events.json' assert { type: 'json' };

export async function onRequestGet({ request }) {
  try {
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
