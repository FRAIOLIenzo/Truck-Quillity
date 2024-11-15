import random
import requests
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Paramètres
DESIRED_CITIES = 100  # Nombre de villes à sélectionner aléatoirement parmi les 15 000
TOTAL_CITIES = 15000  # Nombre total de villes à récupérer
API_URL = "https://geo.api.gouv.fr/communes"
PARIS_NAME = "Paris"

def get_french_cities():
    """Récupère les 15 000 villes les plus peuplées de France avec leurs coordonnées"""
    params = {
        'fields': 'nom,centre,population',  # On veut le nom, les coordonnées et la population
        'limit': TOTAL_CITIES  # Récupérer un grand nombre de villes
    }

    try:
        # Requête API pour récupérer les données des villes
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Vérifie si la requête a réussi
        all_cities = response.json()

        # Filtrer les villes valides (ayant des coordonnées et une population positive)
        valid_cities = [
            city for city in all_cities
            if city.get('centre') and city.get('nom') and city.get('population', 0) > 0
        ]

        # Trier les villes par population décroissante
        valid_cities.sort(key=lambda x: x['population'], reverse=True)

        # Sélectionner les 15 000 villes les plus peuplées
        return valid_cities[:TOTAL_CITIES]

    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return []

def get_paris():
    """Retourne les coordonnées exactes de Paris"""
    # Paris a des coordonnées connues exactes, donc on le force manuellement
    return ("Paris", 48.8566, 2.3522)

def select_random_cities(cities, n=100):
    """Sélectionne n villes aléatoires parmi les villes récupérées sans doublons"""
    random.shuffle(cities)  # Mélange les villes pour avoir une sélection aléatoire
    selected_cities = []
    seen_coordinates = set()  # Pour éviter les doublons de coordonnées

    for city in cities:
        coordinates = (city['centre']['coordinates'][1], city['centre']['coordinates'][0])
        
        # Ajouter la ville si ses coordonnées ne sont pas déjà dans le set
        if coordinates not in seen_coordinates:
            selected_cities.append((city['nom'], *coordinates))
            seen_coordinates.add(coordinates)
        
        if len(selected_cities) >= n:
            break

    return selected_cities

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

def generate():
    """Fonction principale pour exécuter l'ensemble du processus"""
    # Étape 1: Récupérer les villes les plus peuplées
    cities = get_french_cities()

    if not cities:

        return



    # Étape 2: Sélectionner aléatoirement n villes parmi les 15 000

    selected_cities = select_random_cities(cities, n=DESIRED_CITIES)

    # Étape 3: Ajouter Paris en première position
    paris_info = get_paris()
    selected_cities.insert(0, paris_info)  # Insérer Paris en première position
    
    # Étape 3: Générer la matrice de distances

    distances = generate_distance_matrix(selected_cities)
    y = len(distances)


    return selected_cities, distances
