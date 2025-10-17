import departmentsData from '../data/departments.json' assert { type: 'json' };

export async function onRequestGet({ request }) {
  try {
    return new Response(JSON.stringify(departmentsData), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
      }
    });
  } catch (error) {
    console.error('Error serving departments:', error);
    return new Response(JSON.stringify({
      error: 'Internal server error',
      message: 'Unable to fetch departments data'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
