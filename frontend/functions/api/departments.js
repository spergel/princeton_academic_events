export async function onRequestGet({ request }) {
  try {
    // Fetch the departments data from the static asset
    const deptData = await fetch(new URL('/data/departments.json', request.url));

    if (!deptData.ok) {
      return new Response(JSON.stringify({
        error: 'Departments data not found',
        message: 'Data will be available after the next weekly scrape'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = await deptData.json();

    return new Response(JSON.stringify(data), {
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
