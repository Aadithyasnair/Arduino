from flask import Flask, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)

# Load Firebase credentials path from environment variable
firebase_cred_path = os.environ.get('FIREBASE_CRED_PATH')
if not firebase_cred_path:
    raise ValueError("Environment variable FIREBASE_CRED_PATH not set")

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ipa-gas-sensor-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def classify_gas_level(ppm):
    """Classify gas level based on PPM value"""
    ppm = float(ppm)
    if ppm <= 300:
        return 'Green'
    elif 300 <= ppm <= 999:
        return 'Yellow'
    elif 1000 <= ppm <= 2999:
        return 'Orange'
    else:
        return 'Red'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gas_data', methods=['GET'])
def get_gas_data():
    try:
        ref = db.reference('house')
        houses = ref.get()

        gas_data = []
        for house_name, house_info in houses.items():
            location = house_info.get('location', {})
            sensor_data = house_info.get('sensorData', {})

            lat = location.get('latitude')
            lon = location.get('longitude')
            ppm = sensor_data.get('ppm')

            if lat is None or lon is None or ppm is None:
                continue  # Skip incomplete data

            ppm_value = float(ppm)
            gas_level = classify_gas_level(ppm_value)

            gas_data.append({
                'id': house_name,
                'coordinates': [lat, lon],
                'gasLevel': gas_level,
                'ppm': ppm_value,
                'address': house_name
            })

        return jsonify(gas_data)

    except Exception as e:
        print(f"Error fetching data from Firebase: {e}")
        return jsonify({'error': 'Error fetching data'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
