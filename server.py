import os
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
        return jsonify({'x': x, 'y': y, 'z': z}), 200
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

if __name__ == "__main__":
    app.run(port=8000)
