#!/usr/bin/env node
/**
 * Simple SPA server for production builds
 * Handles client-side routing by always serving index.html
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 5174;
const DIST_DIR = path.join(__dirname, 'dist');

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
};

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // Remove query string
  let filePath = req.url.split('?')[0];
  
  // Serve static files
  if (filePath.startsWith('/assets/') || filePath === '/favicon.ico') {
    const fullPath = path.join(DIST_DIR, filePath);
    
    fs.readFile(fullPath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not Found');
        return;
      }
      
      const ext = path.extname(fullPath);
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  } else {
    // For all other routes, serve index.html (SPA routing)
    const indexPath = path.join(DIST_DIR, 'index.html');
    
    fs.readFile(indexPath, 'utf8', (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Internal Server Error');
        return;
      }
      
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  }
});

server.listen(PORT, () => {
  console.log(`\n✅ SPA Server running at http://localhost:${PORT}`);
  console.log(`📁 Serving files from: ${DIST_DIR}`);
  console.log(`🔄 Client-side routing enabled\n`);
});
