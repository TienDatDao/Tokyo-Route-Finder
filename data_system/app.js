const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Serve static files
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/test-incidents', (req, res) => {
  const { startStation, endStation, incidentsJson } = req.body;

  // Spawn Python process với arguments
  const pythonProcess = spawn('python', [
    path.join(__dirname, 'data_system', 'tests', 'test_route.py'),
    startStation || "JR-East.Joetsu.Minakami",
    endStation || "JR-East.Ryomo.Maebashi",
    incidentsJson || '[]'
  ]);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on('close', (code) => {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    if (code === 0) {
      res.send(`<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: monospace; margin: 20px; background: #f5f5f5; }
    pre { background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h2>Test Results</h2>
  <pre>${escapeHtml(output)}</pre>
  <a href="/public">Back to Admin Panel</a>
</body>
</html>`);
    } else {
      res.send(`<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: monospace; margin: 20px; background: #f5f5f5; }
    pre { background: #ffebee; padding: 20px; border-radius: 8px; border-left: 4px solid #c62828; color: #c62828; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h2>Error</h2>
  <pre>${escapeHtml(errorOutput || output)}</pre>
  <a href="/public">Back to Admin Panel</a>
</body>
</html>`);
    }
  });
});

// Helper function to escape HTML
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

app.listen(PORT, () => {
  console.log(`Admin panel running at http://localhost:${PORT}`);
});
