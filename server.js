const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 8000;

// MIME types for different file extensions
const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    // Handle API endpoints
    if (pathname.startsWith('/api/')) {
        handleApiRequest(req, res, pathname);
        return;
    }

    // Handle static files
    let filePath = path.join(__dirname, 'frontend', pathname);

    // Default to index.html for root path
    if (pathname === '/' || pathname === '') {
        filePath = path.join(__dirname, 'frontend', 'index.html');
    }

    // Check if file exists
    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            // File not found
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 - File Not Found</h1>');
            return;
        }

        // Get file extension and MIME type
        const ext = path.extname(filePath);
        const contentType = MIME_TYPES[ext] || 'text/plain';

        // Read and serve file
        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/html' });
                res.end('<h1>500 - Internal Server Error</h1>');
                return;
            }

            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        });
    });
});

function handleApiRequest(req, res, pathname) {
    let dataFile = '';

    // Map API endpoints to data files
    switch (pathname) {
        case '/api/meta':
            dataFile = 'frontend/data/meta.json';
            break;
        case '/api/events':
            dataFile = 'frontend/data/events.json';
            break;
        case '/api/departments':
            dataFile = 'frontend/data/departments.json';
            break;
        default:
            res.writeHead(404, {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            });
            res.end(JSON.stringify({ error: 'API endpoint not found' }));
            return;
    }

    // Check if data file exists
    fs.access(dataFile, fs.constants.F_OK, (err) => {
        if (err) {
            res.writeHead(404, {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            });
            res.end(JSON.stringify({
                error: 'Data not found',
                message: 'Data will be available after the next weekly scrape'
            }));
            return;
        }

        // Read and serve JSON data
        fs.readFile(dataFile, 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                });
                res.end(JSON.stringify({ error: 'Internal server error' }));
                return;
            }

            res.writeHead(200, {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            });
            res.end(data);
        });
    });
}

server.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    console.log('Open your browser and go to http://localhost:8000');
    console.log('Press Ctrl+C to stop the server');
});
