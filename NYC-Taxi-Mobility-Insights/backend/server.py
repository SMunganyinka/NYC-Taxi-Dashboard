from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import db
import os

# Frontend folder path (relative to backend)
FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), "../frontend")

app = Flask(__name__, static_folder=FRONTEND_FOLDER)
CORS(app)  # allow frontend to fetch data

# -----------------------
# API route
# -----------------------
@app.route("/trips")
def get_trips():
    return jsonify(db.fetchall("SELECT * FROM trips LIMIT 100"))

# -----------------------
# Serve index.html and static files
# -----------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_FOLDER, path)

# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
