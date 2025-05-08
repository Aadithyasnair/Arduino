from flask import Flask, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('ipa-gas-sensor-firebase-adminsdk-fbsvc-53db67c55c.json')  # Replace with your path
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

            if gas_level != 'Green' or gas_level == 'Green':
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
