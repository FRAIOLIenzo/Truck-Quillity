#   _____      _             _            _         __                           _     
#  / ____|    | |           (_)          | |       / _|                         (_)    
# | |     ___ | | ___  _ __  _  ___    __| | ___  | |_ ___  _   _ _ __ _ __ ___  _ ___ 
# | |    / _ \| |/ _ \| '_ \| |/ _ \  / _` |/ _ \ |  _/ _ \| | | | '__| '_ ` _ \| / __|
# | |___| (_) | | (_) | | | | |  __/ | (_| |  __/ | || (_) | |_| | |  | | | | | | \__ \
# \_____\___/|_|\___/|_| |_|_|\___|  \__,_|\___| |_| \___/ \__,_|_|  |_| |_| |_|_|___/

# Métaheuristique : Colonie de fourmis
# À base de population - Intelligence en essaim

# Importation des bibliothèques
import time as tp
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import random
import requests
import numpy as np
from math import radians, sin, cos, sqrt, atan2

geolocator = Nominatim(user_agent="vrp_geo_locator")
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points GPS en utilisant la formule de Haversine"""
    R = 6371  # Rayon de la Terre en km

    # Convertir les coordonnées en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calcul des différences de coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Formule de Haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c  # Distance en km

    return distance

def generate_distance_matrix(cities):
    """Génère une matrice de distances entre les villes"""
    n = len(cities)
    distances = np.zeros((n, n))  # Crée une matrice de zéros de taille n x n

    for i in range(n):
        for j in range(i+1, n):
            lat1, lon1 = cities[i][1], cities[i][2]
            lat2, lon2 = cities[j][1], cities[j][2]
            
            # Calculer la distance entre les villes i et j
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            
            # Remplir la matrice symétriquement
            distances[i][j] = distances[j][i] = distance

    return distances

def get_city_coordinates(city_names):
    """Récupère les coordonnées GPS pour une liste de noms de villes"""
    geolocator = Nominatim(user_agent="vrp_geo_locator")
    cities = []

    for city_name in city_names:
        try:
            location = geolocator.geocode(city_name + ", France", timeout=10)
            if location:
                tp.sleep(0.1)  # Pause d'une seconde pour éviter le blocage par Nominatim
                cities.append((city_name, location.latitude, location.longitude))
            else:
                print(f"Coordonnées introuvables pour {city_name}")
        except GeocoderTimedOut:
            print(f"Timeout pour {city_name}, nouvel essai après une pause.")
            tp.sleep(1)
            return get_city_coordinates(city_names)  # Réessayer pour toutes les villes

    return cities

def construire_solution(nom_ville, distances, capacite_max, ville_d, v_phero, visibilités, i_phero, i_visi, cache_probabilites):
    non_visite = nom_ville[1:] # On crée un ensemble de données avec les numéros des villes
    routes = dict() # Liste de toutes les routes de tous les camions
    capacite = dict() # Pour la capacité de chaque camion
    distance_total = 0
    nb_camions = 0
    depot = nom_ville[0]

    # Assigner des villes aux camions
    while non_visite:
        ville_actuel = depot # On démarre forcément au dépôt
        routes[f"Camion n°{nb_camions + 1}"] = [] # On fait la route pour un seul camion
        routes[f"Camion n°{nb_camions + 1}"].append(depot)
        capacite[f"Camion n°{nb_camions + 1}"] = 0

        while capacite[f"Camion n°{nb_camions + 1}"] < capacite_max and non_visite:
            # Vérifie si au moins une ville peut être ajoutée sans dépasser la capacité maximale
            villes_possibles = [v for v in non_visite if (capacite[f"Camion n°{nb_camions + 1}"] + ville_d[v]) <= capacite_max]
            if not villes_possibles:
                # Aucune ville ne peut être ajoutée, on quitte la boucle interne
                break
            
            # Calculer les probabilités pour les chemins vers les villes possibles
            probabilites = dict()
            for prochaine_ville in villes_possibles:
                # Vérification du cache pour les probabilités
                if (ville_actuel, prochaine_ville) in cache_probabilites:
                    probabilite = cache_probabilites[(ville_actuel, prochaine_ville)]
                else:
                    if ville_actuel is not non_visite:
                        pheromone = v_phero[0][non_visite.index(prochaine_ville) + 1]
                        visibilité = visibilités[0][non_visite.index(prochaine_ville) + 1]
                    else:
                        pheromone = v_phero[non_visite.index(ville_actuel) + 1][non_visite.index(prochaine_ville) + 1]
                        visibilité = visibilités[non_visite.index(ville_actuel) + 1][non_visite.index(prochaine_ville) + 1]
                    probabilite = (pheromone ** i_phero) * (visibilité ** i_visi)
                    cache_probabilites[(ville_actuel, prochaine_ville)] = probabilite
                
                probabilites[prochaine_ville] = probabilite
            
            # Sélection de la prochaine ville
            total_proba = sum(probabilites.values())
            if total_proba == 0:
                prochaine_ville = random.choice(villes_possibles)
            else:
                probabilites = {v: prob / total_proba for v, prob in probabilites.items()}
                prochaine_ville = random.choices(
                    population=[v for v, _ in probabilites.items()],
                    weights=[prob for _, prob in probabilites.items()]
                )[0]

            # Mettre à jour la route et la capacité du camion si la ville est ajoutée
            routes[f"Camion n°{nb_camions + 1}"].append(prochaine_ville)
            non_visite.remove(prochaine_ville)
            distance_total += distances[nom_ville.index(ville_actuel)][nom_ville.index(prochaine_ville)]
            capacite[f"Camion n°{nb_camions + 1}"] += ville_d[prochaine_ville]
            ville_actuel = prochaine_ville # Mise à jour de la ville actuelle

        # Retour au dépôt
        distance_total += distances[nom_ville.index(ville_actuel)][0]
        routes[f"Camion n°{nb_camions + 1}"].append(depot)
        nb_camions += 1

    return routes, capacite, distance_total

def maj_pheromones(solutions, v_pheromone, t_evaporation, depot_phero, nom_ville):
    # Évaporation des phéromones
    v_pheromone *= (1 - t_evaporation)

    # Dépôt de nouvelles phéromones pour chaque solution
    for solution in solutions:
        # Solution est un tuple (routes, distance_total)
        routes, distance_total = solution

        # Calcul du dépôt de phéromones pour cette solution
        deposit = depot_phero / distance_total

        # Parcours des itinéraires de chaque camion
        for camion, vehicule_route in routes.items():
            ville_actuel = 0 # Index du dépôt (Nancy)
            
            # On ignore la première et la dernière ville (les deux "Nancy")
            for prochaine_ville_nom in vehicule_route[1:-1]:
                prochaine_ville = nom_ville.index(prochaine_ville_nom) # Index de la prochaine ville
                v_pheromone[ville_actuel][prochaine_ville] += deposit
                ville_actuel = prochaine_ville

            # Retour au dépôt (Nancy)
            v_pheromone[ville_actuel][ville_actuel] += deposit

    return v_pheromone

def resoudre(v_pheromone, meilleur_distance, meilleur_solution, meilleur_capacite, max_iteration, nb_fourmis,nom_ville, distances, capacite_max, ville_d, v_phero, visibilités, i_phero, i_visi, cache_probabilites, t_evaporation, depot_phero):
    for iteration in range(max_iteration):
        # Solutions construites par les fourmis
        solutions = []
        for i in range(nb_fourmis):
            routes, capacite, distance_total = construire_solution(nom_ville, distances, capacite_max, ville_d, v_phero, visibilités, i_phero, i_visi, cache_probabilites)

            # Mise à jour de la meilleure solution
            if distance_total < meilleur_distance:
                meilleur_distance = distance_total
                meilleur_solution = routes
                meilleur_capacite = capacite
            
        # Mise à jour des phéromones
        v_pheromone = maj_pheromones(solutions, v_pheromone, t_evaporation, depot_phero, nom_ville)

    return meilleur_solution, meilleur_capacite, meilleur_distance

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

def afficher_carte(solution, nom_ville, distances):

    # Dictionnaire pour stocker les coordonnées des villes
    coords = {}

    # Récupérer les coordonnées pour chaque ville dans les itinéraires
    for camion, itineraire in solution.items():
        for ville in itineraire:
            if ville not in coords:  # Évite les recherches répétées pour la même ville
                coords[ville] = get_coordinates(ville)

    # Centre de la carte autour de la France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Couleurs aléatoires pour chaque itinéraire
    colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in solution]

    # Ajouter chaque itinéraire à la carte
    for (camion, itineraire), color in zip(solution.items(), colors):
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


