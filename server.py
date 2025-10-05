import os
import math
import datetime
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from astroquery.jplhorizons import Horizons

today = datetime.date.today().strftime("%Y-%m-%d")

app = Flask(__name__)
CORS(app, methods=['POST'])

@app.route("/coordinate", methods=['POST'])
def coordinates():
    data = request.get_json()
    try:
        obj = Horizons(id=f'DES={data['id']}', location='500@399')
        obj.cache_location = "/tmp"
        vectors = obj.vectors()
        x = vectors['x'].value[0]
        y = vectors['y'].value[0]
        z = vectors['z'].value[0]

        R = 6371.0
        dist = (x**2 + y**2 + z**2)**0.5
        x_surf = x * R / dist
        y_surf = y * R / dist
        z_surf = z * R / dist

        lat = math.degrees(math.atan2(z_surf, (x_surf**2 + y_surf**2)**0.5))
        lon = math.degrees(math.atan2(y_surf, x_surf))
        return jsonify({'x': x, 'y': y, 'z': z, 'lat': lat, 'lon': lon}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route("/near_items", methods=['POST'])
def near_items():
    data = request.get_json(silent=True)
    if not data:
        start_date = datetime.date.today().strftime("%Y-%m-%d")
        end_date = datetime.date.today().strftime("%Y-%m-%d")
    else:
        start_date = data.get('start_date', datetime.date.today().strftime("%Y-%m-%d"))
        end_date = data.get('end_date', datetime.date.today().strftime("%Y-%m-%d"))
    response = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={os.environ.get("NEOWS_API")}")
    return jsonify(response.json())

@app.route("/velocity_vectors", methods=['POST'])
def velocity_vectors():
    try:
        data = request.get_json()
        obj = Horizons(id=f'DES={data['id']}', location='500@399')
        obj.cache_location = "/tmp"
        vectors = obj.vectors()
        vx = vectors['vx'].value[0]
        vy = vectors['vy'].value[0]
        vz = vectors['vz'].value[0]
        return jsonify({'vx': vx, 'vy': vy, 'vz': vz}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=8000)
