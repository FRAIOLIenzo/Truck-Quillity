import folium
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/test', methods=['POST'])
def get_location():
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)
    data = request.json
    geolocator = Nominatim(user_agent="city_locator")
    
    if isinstance(data, list):
        for city in data:
            city_name = city.get('city_name')
            location = geolocator.geocode(city_name)
            if location:
                folium.Marker([location.latitude, location.longitude], popup=city_name).add_to(m)
                if len(data) > 1:
                    points = [(geolocator.geocode(city.get('city_name')).latitude, geolocator.geocode(city.get('city_name')).longitude) for city in data if geolocator.geocode(city.get('city_name'))]
                    folium.PolyLine(points, color="blue", weight=2.5, opacity=1).add_to(m)
        m.save('map.html')
        return jsonify({'message': 'Markers added successfully'})
    else:
        city_name = data.get('city_name')
        location = geolocator.geocode(city_name)
        if location:
            folium.Marker([location.latitude, location.longitude], popup=city_name).add_to(m)
            m.save('map.html')
            return jsonify({'latitude': location.latitude, 'longitude': location.longitude})
        else:
            return jsonify({'error': 'Location not found'}), 404

@app.route('/api/reset', methods=['POST'])
def get_reset():
    data = request.json
    city_name = data.get('city_name')
    if city_name == 'reset':
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)
        m.save('map.html')
        return jsonify({'message': 'Map reset successfully'})
    else:
        return jsonify({'error': 'Location not found'}), 404
    
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)


