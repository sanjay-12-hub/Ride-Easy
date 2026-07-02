import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", 3000))
DB_FILE = os.path.join(os.path.dirname(__file__), "rideeasy.db")
HTML_FILE = os.path.join(os.path.dirname(__file__), "demo.html")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def default_state():
    return {
        "users": {},
        "vehicles": [
            {
                "id": 1,
                "owner": "demo-owner@rideeasy.com",
                "name": "Honda Activa",
                "type": "Bike",
                "price": 400,
                "status": "available",
                "renter": None,
                "days": 0,
                "ownerName": "Asha Kumar",
                "ownerPhone": "9876543210",
                "pickupAddress": "Near MG Road",
                "image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=900&q=80"
            },
            {
                "id": 2,
                "owner": "demo-owner@rideeasy.com",
                "name": "Royal Enfield Classic",
                "type": "Bike",
                "price": 900,
                "status": "available",
                "renter": None,
                "days": 0,
                "ownerName": "Asha Kumar",
                "ownerPhone": "9876543210",
                "pickupAddress": "Near MG Road",
                "image": "https://images.unsplash.com/photo-1511994298241-608e28f14fde?auto=format&fit=crop&w=900&q=80"
            },
            {
                "id": 3,
                "owner": "demo-owner@rideeasy.com",
                "name": "Maruti Swift",
                "type": "Car",
                "price": 1800,
                "status": "available",
                "renter": None,
                "days": 0,
                "ownerName": "Asha Kumar",
                "ownerPhone": "9876543210",
                "pickupAddress": "Near MG Road",
                "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=900&q=80"
            },
            {
                "id": 4,
                "owner": "demo-owner@rideeasy.com",
                "name": "TVS iQube",
                "type": "Scooter",
                "price": 500,
                "status": "available",
                "renter": None,
                "days": 0,
                "ownerName": "Asha Kumar",
                "ownerPhone": "9876543210",
                "pickupAddress": "Near MG Road",
                "image": "https://images.unsplash.com/photo-1555652736-e92021d28bba?auto=format&fit=crop&w=900&q=80"
            }
        ],
        "bookings": [],
        "currentUser": None,
        "nextVehicleId": 5
    }


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS app_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            payload TEXT NOT NULL
        )
    """)
    conn.commit()

    row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
    if row is None:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
            conn.execute("INSERT INTO app_state(id, payload) VALUES (1, ?)", (json.dumps(existing),))
        else:
            conn.execute("INSERT INTO app_state(id, payload) VALUES (1, ?)", (json.dumps(default_state()),))
        conn.commit()
    conn.close()


def read_state():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return default_state()
    return json.loads(row["payload"])


def write_state(state):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO app_state(id, payload) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
        (json.dumps(state),),
    )
    conn.commit()
    conn.close()


class RideEasyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            self.send_json(200, read_state())
        elif path in ["/", "/demo.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(HTML_FILE, "rb") as fh:
                self.wfile.write(fh.read())
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/state":
            self.send_json(404, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            state = json.loads(body)
            write_state(state)
            self.send_json(200, state)
        except Exception:
            self.send_json(400, {"error": "Invalid JSON body"})

    def send_json(self, status_code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), RideEasyHandler)
    print(f"RideEasy backend running at http://localhost:{PORT}")
    print(f"SQLite database: {DB_FILE}")
    server.serve_forever()
