const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data.json');
const HTML_FILE = path.join(__dirname, 'demo.html');

function defaultState() {
  return {
    users: {},
    vehicles: [
      { id: 1, owner: 'demo-owner@rideeasy.com', name: 'Honda Activa', type: 'Bike', price: 400, status: 'available', renter: null, days: 0, ownerName: 'Asha Kumar', ownerPhone: '9876543210', pickupAddress: 'Near MG Road', image: 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=900&q=80' },
      { id: 2, owner: 'demo-owner@rideeasy.com', name: 'Royal Enfield Classic', type: 'Bike', price: 900, status: 'available', renter: null, days: 0, ownerName: 'Asha Kumar', ownerPhone: '9876543210', pickupAddress: 'Near MG Road', image: 'https://images.unsplash.com/photo-1511994298241-608e28f14fde?auto=format&fit=crop&w=900&q=80' },
      { id: 3, owner: 'demo-owner@rideeasy.com', name: 'Maruti Swift', type: 'Car', price: 1800, status: 'available', renter: null, days: 0, ownerName: 'Asha Kumar', ownerPhone: '9876543210', pickupAddress: 'Near MG Road', image: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=900&q=80' },
      { id: 4, owner: 'demo-owner@rideeasy.com', name: 'TVS iQube', type: 'Scooter', price: 500, status: 'available', renter: null, days: 0, ownerName: 'Asha Kumar', ownerPhone: '9876543210', pickupAddress: 'Near MG Road', image: 'https://images.unsplash.com/photo-1555652736-e92021d28bba?auto=format&fit=crop&w=900&q=80' }
    ],
    bookings: [],
    currentUser: null,
    nextVehicleId: 5
  };
}

function readState() {
  try {
    if (!fs.existsSync(DATA_FILE)) {
      fs.writeFileSync(DATA_FILE, JSON.stringify(defaultState(), null, 2));
    }
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return defaultState();
  }
}

function writeState(state) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(state, null, 2));
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(payload));
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  if (req.url === '/api/state' && req.method === 'GET') {
    sendJson(res, 200, readState());
    return;
  }

  if (req.url === '/api/state' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const state = JSON.parse(body);
        writeState(state);
        sendJson(res, 200, state);
      } catch (error) {
        sendJson(res, 400, { error: 'Invalid JSON body' });
      }
    });
    return;
  }

  if (req.url === '/' || req.url === '/demo.html') {
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Access-Control-Allow-Origin': '*'
    });
    res.end(fs.readFileSync(HTML_FILE));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`RideEasy backend running at http://localhost:${PORT}`);
});
