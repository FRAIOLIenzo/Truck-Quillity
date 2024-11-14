
'''
 __/\\\\\\\\\\\\\\\_        _____/\\\\\\\\\____        __/\\\\\\\\\\\\\___        __/\\\________/\\\_        
  _\///////\\\/////__        ___/\\\\\\\\\\\\\__        _\/\\\/////////\\\_        _\/\\\_______\/\\\_       
   _______\/\\\_______        __/\\\/////////\\\_        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_      
    _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\\\\\\\\\\\\__        _\/\\\_______\/\\\_     
     _______\/\\\_______        _\/\\\\\\\\\\\\\\\_        _\/\\\/////////\\\_        _\/\\\_______\/\\\_    
      _______\/\\\_______        _\/\\\/////////\\\_        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_   
       _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\_______\/\\\_        _\//\\\______/\\\__  
        _______\/\\\_______        _\/\\\_______\/\\\_        _\/\\\\\\\\\\\\\/__        __\///\\\\\\\\\/___ 
         _______\///________        _\///________\///__        _\/////////////____        ____\/////////_____
'''

#----------------------------------------------------------------Importation des bibliothèques----------------------------------------------------------------

import random
from collections import deque
import time as tp
from tqdm import tqdm
from itertools import combinations
import data
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests

geolocator = Nominatim(user_agent="vrp_geo_locator")

def generate_path(nb_villes, capacite_max, ville_d, nom_ville):
    start_city = nom_ville[0]
    nb_camions = 0
    capacite = dict()
    route = dict()
    non_visite = nom_ville[1:]
    random.shuffle(non_visite)
    while non_visite:
        capacite[f"Camion n°{nb_camions + 1}"] = 0
        route[f"Camion n°{nb_camions + 1}"] = []
        route[f"Camion n°{nb_camions + 1}"].append(start_city)
        while capacite[f"Camion n°{nb_camions + 1}"] < capacite_max and non_visite:
            villes_possibles = []
            for i in non_visite:
                if capacite[f"Camion n°{nb_camions + 1}"] + ville_d[i] <= capacite_max:
                    villes_possibles.append(i)
            if not villes_possibles:
            # Aucune ville ne peut être ajoutée, on quitte la boucle interne
                break
            prochaine_ville = random.choice(villes_possibles)
            route[f"Camion n°{nb_camions + 1}"].append(prochaine_ville)
            non_visite.remove(prochaine_ville)
            capacite[f"Camion n°{nb_camions + 1}"] += ville_d[prochaine_ville]
        route[f"Camion n°{nb_camions + 1}"].append(start_city)
        nb_camions += 1
    return route

def calculate_path_distance(path, distance_matrix, nom_ville):
    total_distance = 0
    # Parcourir chaque camion dans le dictionnaire
    for camion_key in path.keys():
        route = path[camion_key]
        # Calculer la distance pour ce camion
        for i in range(len(route)-1):
            ville_depart = route[i]
            ville_arrivee = route[i + 1]
            # Convertir les noms de villes en indices pour la matrice de distance
            index_depart = nom_ville.index(ville_depart)
            index_arrivee = nom_ville.index(ville_arrivee)
            total_distance += distance_matrix[index_depart][index_arrivee]
    
    return total_distance

def calculate_weight(sol, ville_d):
    poids = dict()
    for i in sol.keys():
        poids[i] = 0
        for j in sol[i]:
            poids[i] += ville_d[j]

    return poids

def generate_neighbors(path):
    neighbors = dict()
    # Pour chaque camion dans le chemin
    for k in range(len(path)):
        camion_key = f"Camion n°{k+1}"
        route = path[camion_key]
        # On ne considère que les villes intermédiaires (pas le dépôt)
        for i, j in combinations(range(1, len(route) - 1), 2):
            # On crée une copie du chemin initial
            neighbor = route[:]
            # On permute les villes
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            # On remplace la solution par les voisins
            path[camion_key] = neighbor
    
    return neighbors

def recherche_tabou(solution_initiale, taille_tabou, iter_max, matrix, nom_ville, ville_d):
    nb_iter = 0                                                                
    liste_tabou = deque((), maxlen = taille_tabou)                             
                                                                               
    # variables solutions pour la recherche du voisin optimal non tabou        
    solution_courante = solution_initiale                                      
    meilleure = solution_initiale                                              
    meilleure_globale = solution_initiale                                       
                                                                               
    # variables valeurs pour la recherche du voisin optimal non tabou          
    valeur_meilleure = calculate_path_distance(solution_initiale, matrix, nom_ville)                       
    valeur_meilleure_globale = valeur_meilleure
    courantes = deque(()) 
    meilleures_courantes = deque(()) 

    while (nb_iter < iter_max):                                                
        valeur_meilleure = float('inf')    

        # On parcourt tous les voisins de la solution courante                
        for voisin in generate_neighbors(solution_courante).items():
            dico = solution_courante
            dico[voisin[0]] = voisin[1]
            valeur_voisin = calculate_path_distance(dico, matrix, nom_ville)
            poids_voisin = calculate_weight(dico, ville_d)

            # On met à jour la meilleure solution non taboue trouvée                        
            if valeur_voisin < valeur_meilleure and voisin not in liste_tabou: 
                valeur_meilleure = valeur_voisin
                meilleure = voisin 
                                                             
                                                                               
        # On met à jour la meilleure solution rencontrée depuis le début       
        if valeur_meilleure < valeur_meilleure_globale:                    
            meilleure_globale = meilleure                                      
            valeur_meilleure_globale = valeur_meilleure  
            poids_meilleure_globale = 0
            nb_iter = 0     
        else:                                                                  
            nb_iter += 1

        courantes.append(calculate_path_distance(solution_courante, matrix, nom_ville)) 
        meilleures_courantes.append(valeur_meilleure_globale) 
                                                                                                              
        # on passe au meilleur voisin non tabou trouvé                         
        solution_courante = meilleure                                          
                                                                               
        # on met à jour la liste tabou                                         
        liste_tabou.append(solution_courante)                                  

    return meilleure_globale, courantes, meilleures_courantes

def multi_start(nb_villes, solution_initiale, distance_matrix, nb_test, nom_ville, ville_d, capacite_max):
    taille_tabou = 100
    iter_max = 50

    # multi-start de n itérations
    val_max = float('inf')
    sol_max = None
    sac = solution_initiale
    solutions = []
    best_solutions = []

    for _ in tqdm(range(nb_test)):
        sol_courante, _, _ = recherche_tabou(solution_initiale, taille_tabou, iter_max, distance_matrix, nom_ville, ville_d)
        val_courante = calculate_path_distance(sol_courante, distance_matrix, nom_ville)
        poids_courant = calculate_weight(sol_courante, ville_d)

        solutions.append(val_courante)
        
        if val_courante < val_max:
            val_max = val_courante
            sol_max = sol_courante
            poids_max = poids_courant
        
        best_solutions.append(val_max)
        sac = generate_path(nb_villes, capacite_max, ville_d, nom_ville)

    return sol_max, val_max, nb_test, solutions, best_solutions, poids_max

def get_coordinates(city_name):
    try:
        location = geolocator.geocode(city_name + ", France", timeout=10)
        if location:
            tp.sleep(1)  # Pause d'une seconde pour éviter le blocage par Nominatim
            return (location.latitude, location.longitude)
        else:
            print(f"Coordonnées introuvables pour {city_name}")
            return None
    except GeocoderTimedOut:
        print(f"Timeout pour {city_name}, nouvel essai après une pause.")
        tp.sleep(1)
        return get_coordinates(city_name)

def create_map_with_routes(sol_max):
    coords = {}

    # Récupérer les coordonnées pour chaque ville dans les itinéraires
    for camion, itineraire in sol_max.items():
        for ville in itineraire:
            if ville not in coords:  # Évite les recherches répétées pour la même ville
                coords[ville] = get_coordinates(ville)

    # Centre de la carte autour de la France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Couleurs aléatoires pour chaque itinéraire
    colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in sol_max]

    # Ajouter chaque itinéraire à la carte
    for (camion, itineraire), color in zip(sol_max.items(), colors):
        # Extraire les coordonnées
        latitudes = [coords[ville][0] for ville in itineraire]
        longitudes = [coords[ville][1] for ville in itineraire]
        locations = list(zip(latitudes, longitudes))
        
        # Ajouter le chemin avec une couleur spécifique
        folium.PolyLine(locations, color=color, weight=5, opacity=0.7).add_to(m)
        
        # Ajouter des marqueurs pour chaque ville
        for lat, lon, ville in zip(latitudes, longitudes, itineraire):
            folium.Marker([lat, lon], popup=f"{ville} - {camion}", tooltip=ville).add_to(m)

    # Sauvegarder la carte
    m.save("map.html")

def plot_real_routes_tabu(sol_max, coords):
    # Créer une nouvelle carte
    m_real = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Tracer les vraies routes entre les villes
    for (camion, itineraire), color in zip(sol_max.items(), [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in sol_max]):
        route_coords = []
        for i in range(len(itineraire) - 1):
            ville1 = itineraire[i]
            ville2 = itineraire[i + 1]
            origin = coords[ville1]
            destination = coords[ville2]
            route = get_route(origin, destination, "5b3ce3597851110001cf6248cf662aab956e43739386391547c544bc")
            route_coords.extend(route)
        folium.PolyLine(route_coords, color=color, weight=5, opacity=0.7).add_to(m_real)

        # Ajouter des marqueurs pour chaque ville
        for lat, lon, ville in zip([coords[city][0] for city in itineraire], [coords[city][1] for city in itineraire], itineraire):
            folium.Marker([lat, lon], popup=f"{ville} - {camion}", tooltip=ville).add_to(m_real)

    # Enregistrer la carte avec les vraies routes
    m_real.save("map_tabu.html")

def get_route(origin, destination, api_key):
    # Utiliser un service d'itinéraire pour obtenir les coordonnées de la route
    url = f"https://api.openrouteservice.org/v2/directions/driving-car?start={origin[1]},{origin[0]}&end={destination[1]},{destination[0]}"
    headers = {"Authorization": api_key}
    response = requests.get(url, headers=headers)
    route_data = response.json()

    route_coords = []
    for coordinate in route_data["features"][0]["geometry"]["coordinates"]:
        route_coords.append((coordinate[1], coordinate[0]))

    return route_coords


