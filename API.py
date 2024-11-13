import random
import math
from collections import deque
from tqdm import tqdm
from itertools import combinations
from geopy.distance import geodesic
import folium
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from flask_cors import CORS
import json
import csv
from fourmie import *
#---------------------------------------------------------------Fonctions----------------------------------------------------------------
def load_random_cities_from_csv(file_path, num_cities):
    cities = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            cities.append(row[0]) 
    return random.sample(cities, num_cities)


app = Flask(__name__)
CORS(app)  



@app.route('/api/fourmie', methods=['POST'])
def fourmie_route():
    data = request.json
    # Declare global variables at the module level
    nb_fourmis = 100
    max_iteration = 100
    t_evaporation = 0.1  
    i_phero, i_visi, depot_phero = 1, 2, 100  
    capacite_max = 20
    cache_probabilites = {}

    t0 = tp.time()
    random.seed(48)

    city_names = data
    villes = get_city_coordinates(city_names)
    distances = generate_distance_matrix(villes)
    nom_ville = [city[0] for city in villes]
    ville_d = {nom_ville[0]: 0} 
    ville_d.update({valeur: random.randint(1, 10) for valeur in nom_ville[1:]})

    n = len(nom_ville)
    v_phero = np.ones((n, n), dtype=float) - np.eye(n)  
    visibilités = 1 / (distances + np.eye(n))  

    # Initialisation des solutions
    meilleur_solution, meilleur_distance, meilleur_capacite = None, float('inf'), None
    solution, capacite, distance = resoudre(v_phero, meilleur_distance, meilleur_solution, meilleur_capacite, max_iteration, nb_fourmis,nom_ville, distances, capacite_max, ville_d, v_phero, visibilités, i_phero, i_visi, cache_probabilites,t_evaporation, depot_phero)
    tf = tp.time()
    afficher_carte(solution, nom_ville, distances)
    return jsonify({
        'message': 'Solution trouvée',
        'solution': solution,
        'capacite': capacite,
        'distance': distance,
        'nb_camions': len(solution),
        'temps_execution': tf - t0
    })





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
    

@app.route('/api/random_cities', methods=['GET'])
def get_random_cities():
    num_cities = int(request.args.get('num_cities', 10))  
    file_path = 'cities.csv' 
    random_cities = load_random_cities_from_csv(file_path, num_cities)
    geolocator = Nominatim(user_agent="city_locator")
    cities_info = []
    for city_name in random_cities:
        location = geolocator.geocode(city_name)
        if location:
            cities_info.append(
                {    
                    'Cityname': city_name,
                }
            )
    return jsonify(cities_info)
    
if __name__ == '__main__':
    app.run(debug=True)



