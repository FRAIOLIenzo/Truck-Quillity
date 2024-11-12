
# __/\\\\\\\\\\\\\\\_        _____/\\\\\\\\\____        __/\\\\\\\\\\\\\___        __/\\\________/\\\_        
#  _\///////\\\/////__        ___/\\\\\\\\\\\\\__        _\/\\\/////////\\\_        _\/\\\_______\/\\\_       
#   _______\/\\\_______        __/\\\/////////\\\_        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_      
#    _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\\\\\\\\\\\\__        _\/\\\_______\/\\\_     
#     _______\/\\\_______        _\/\\\\\\\\\\\\\\\_        _\/\\\/////////\\\_        _\/\\\_______\/\\\_    
#      _______\/\\\_______        _\/\\\/////////\\\_        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_   
#       _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_        _\//\\\______/\\\__  
#        _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\\\\\\\\\\\/__        __\///\\\\\\\\\/___ 
#         _______\///________        _\///________\///__        _\/////////////____        ____\/////////_____


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


        

#---------------------------------------------------------------Main----------------------------------------------------------------



#---------------------------------------------------------------Fonctions----------------------------------------------------------------
def generate_coordinates(nb_villes, x_max=100, y_max=100, min_distance=5):
    random.seed(9)
    coordinates = {}
    while len(coordinates) < nb_villes:
        x = random.randint(1, x_max)
        y = random.randint(1, y_max)
        if all(math.sqrt((x - cx) ** 2 + (y - cy) ** 2) >= min_distance for cx, cy in coordinates.values()):
            coordinates[len(coordinates)] = (x, y)
    random.seed()
    return coordinates

def calculate_distances(coordinates):
    distances = {}
    for i, (x1, y1) in coordinates.items():
        for j, (x2, y2) in coordinates.items():
            if i != j:
                distance = round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
                distances[(i, j)] = distance
    return distances

def calculate_real_distances(coordinates):
    distances = {}
    for i, (x1, y1) in coordinates.items():
        for j, (x2, y2) in coordinates.items():
            if i != j:
                distance = round(geodesic((x1, y1), (x2, y2)).kilometers)
                distances[(i, j)] = distance
    return distances

def distances_to_matrix(distances, nb_villes):
    matrix = [[0] * nb_villes for _ in range(nb_villes)]
    for (i, j), distance in distances.items():
        matrix[i][j] = distance
    return matrix

def generate_path(nb_villes, start_city):
    path = list(range(nb_villes))
    path.remove(start_city)
    random.shuffle(path)
    path.insert(0, start_city)
    path.append(start_city)  
    return path

def calculate_path_distance(path, distance_matrix):
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += distance_matrix[path[i]][path[i + 1]]
    total_distance += distance_matrix[path[-1]][path[0]] 
    return total_distance

def generate_neighbors(path):
    neighbors = []
    for i, j in combinations(range(1, len(path) - 1), 2):
            path[i], path[j] = path[j], path[i]
            neighbors.append(path[:])
            path[i], path[j] = path[j], path[i]
    return neighbors

def recherche_tabou(solution_initiale, taille_tabou, iter_max, matrix):
    nb_iter = 0                                                                
    liste_tabou = deque((), maxlen = taille_tabou)                             
                                                                               
    # variables solutions pour la recherche du voisin optimal non tabou        
    solution_courante = solution_initiale                                      
    meilleure = solution_initiale                                              
    meilleure_globale = solution_initiale                                       
                                                                               
    # variables valeurs pour la recherche du voisin optimal non tabou          
    valeur_meilleure = calculate_path_distance(solution_initiale, matrix)                       
    valeur_meilleure_globale = valeur_meilleure
    
    courantes = deque(()) #SOLUTION
    meilleures_courantes = deque(()) #SOLUTION
    # print("nb_voisin : ", len(generate_neighbors(solution_courante))) 
    while (nb_iter < iter_max):                                                
        valeur_meilleure = float('inf')                                                 
                                                                               
        # on parcourt tous les voisins de la solution courante                
        for voisin in generate_neighbors(solution_courante):  
                                      
            valeur_voisin = calculate_path_distance(voisin, matrix)                             
                                                                               
            # MaJ meilleure solution non taboue trouvée                        
            if valeur_voisin < valeur_meilleure and voisin not in liste_tabou: 
                valeur_meilleure = valeur_voisin                               
                meilleure = voisin                                             
                                                                               
        # on met à jour la meilleure solution rencontrée depuis le début       
        if valeur_meilleure < valeur_meilleure_globale:                    
            meilleure_globale = meilleure                                      
            valeur_meilleure_globale = valeur_meilleure                        
            nb_iter = 0     
        else:                                                                  
            nb_iter += 1

        courantes.append(calculate_path_distance(solution_courante, matrix)) 
        meilleures_courantes.append(valeur_meilleure_globale) 

                                                             
                                                                               
        # on passe au meilleur voisin non tabou trouvé                         
        solution_courante = meilleure                                          
                                                                               
        # on met à jour la liste tabou                                         
        liste_tabou.append(solution_courante)                                  
        
        # print(f"Iteration {nb_iter}:")
        # print(f"  Current solution: {solution_courante}")
        # print(f"  Current value: {calculate_path_distance(solution_courante, matrix)}")
        # print(f"  Best global solution: {meilleure_globale}")
        # print(f"  Best global value: {valeur_meilleure_globale}")
                                                                               
    return meilleure_globale, courantes, meilleures_courantes     

def multi_start(nb_villes, solution_initiale, distance_matrix, nb_test):
    taille_tabou = 50
    iter_max = 50

    # multi-start de n itérations
    val_max = float('inf')
    sol_max = None

    sac = solution_initiale
    solutions = []
    best_solutions = []

    for _ in tqdm(range(nb_test)):
        sol_courante, _, _ = recherche_tabou(sac, taille_tabou, iter_max, distance_matrix)
        val_courante = calculate_path_distance(sol_courante, distance_matrix)
        
        solutions.append(val_courante)
        
        if val_courante < val_max:
            val_max = val_courante
            sol_max = sol_courante
        
        best_solutions.append(val_max)
        sac = generate_path(nb_villes, 0)

    return sol_max, val_max, nb_test, solutions, best_solutions

def load_coordinates_from_json_string(json_string):
    data = json.loads(json_string)
    coordinates = {idx: (city['Latitude'], city['Longitude']) for idx, city in enumerate(data)}
    return coordinates

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/test', methods=['POST'])
def get_location():
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)
    data = request.json
    geolocator = Nominatim(user_agent="city_locator")
    cities_info = []
    if isinstance(data, list):
        for idx, city in enumerate(data):
            city_name = city.get('city_name')
            location = geolocator.geocode(city_name)
            if location:
                cities_info.append(
                    {
                        'Cityname': city_name,
                        'Latitude': location.latitude,
                        'Longitude': location.longitude
                    }
                )
        test = json.dumps(cities_info)
        coordinates = load_coordinates_from_json_string(test)
        nb_villes = len(coordinates)
        distances = calculate_real_distances(coordinates)
        distance_matrix = distances_to_matrix(distances, nb_villes)

        random.seed(9)
        path = generate_path(nb_villes, 0)
        random.seed()

        solution_initiale = path

        # Tabou
        # taille_tabou = 50
        # iter_max = 50   
        # tabou, _, _ = recherche_tabou(solution_initiale, taille_tabou, iter_max, distance_matrix)
        # tabou_distance = calculate_path_distance(tabou, distance_matrix)
        # path = tabou
        # distance = tabou_distance

        # Multi start
        nb_test = 100
        sol_max, val_max, nb_test, _, _ = multi_start(nb_villes, solution_initiale, distance_matrix, nb_test)
        path_multi_start = sol_max
        distance_multi_start = val_max

        for city in cities_info:
            folium.Marker([city['Latitude'], city['Longitude']], popup=city['Cityname']).add_to(m)
        # Draw polyline for the path_multi_start of tabou
        tabou_coordinates = [(cities_info[city]['Latitude'], cities_info[city]['Longitude']) for city in path_multi_start]
        folium.PolyLine(tabou_coordinates, color="blue", weight=2.5, opacity=1).add_to(m)
        m.save('map.html')
        return jsonify({'message': 'TKT BRO', 'path_multi_start': path_multi_start, 'distance_multi_start': distance_multi_start})
    
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
    

# print("Main")
# nb_villes = 100

# # distance_matrix = distances_to_matrix(distances, nb_villes)

# # random.seed(9)
# # path = generate_path(nb_villes, Paris) # ville de départ = 0
# # random.seed()
# # start = time.process_time()

# Initialisation des paramètres
# # taille_tabou = 50
# # iter_max = 50 
# # solution_initiale = path
# # tabou, courants, meilleurs_courants = recherche_tabou(solution_initiale, taille_tabou, iter_max, distance_matrix)
# # tabou_distance = calculate_path_distance(tabou, distance_matrix)
# # stop = time.process_time()
# # print("calculé en ", stop-start, 's')
# # print("Distance : ", tabou_distance)


# Run multi start
# # nb_test = 100
# # sol_max, val_max, nb_test, solutions, best_solutions = multi_start(nb_villes, solution_initiale, distance_matrix, nb_test)

if __name__ == '__main__':
    app.run(debug=True)