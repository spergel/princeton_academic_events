export async function onRequestGet({ request }) {
  try {
    // Fetch the meta data from the static asset
    const metaData = await fetch(new URL('/data/meta.json', request.url));

    if (!metaData.ok) {
      return new Response(JSON.stringify({
        error: 'Meta data not found',
        message: 'Data will be available after the next weekly scrape'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = await metaData.json();

    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
      }
    });
  } catch (error) {
    console.error('Error serving meta:', error);
    return new Response(JSON.stringify({
      error: 'Internal server error',
      message: 'Unable to fetch meta data'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
