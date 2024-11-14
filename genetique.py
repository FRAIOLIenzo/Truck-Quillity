import random
import math
import json
import numpy as np
from typing import List, Dict
import folium
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time as tp
import colorsys  # Importation du module colorsys pour la génération de couleurs uniques

geolocator = Nominatim(user_agent="city_locator")
# Classe City représentant une ville avec nom, coordonnées GPS, nombre de colis et demande totale
class City:
    def __init__(self, index: int, name: str, lat: float, lon: float, demand: int):
        self.index = index
        self.name = name
        self.lat = lat
        self.lon = lon
        self.demand = demand  # Demande en unités (poids, volume, etc.)

# Fonction pour calculer la distance entre deux villes (formule de Haversine)
def calculate_distance(city1: City, city2: City) -> float:
    R = 6371  # Rayon de la Terre en km
    lat1_rad = math.radians(city1.lat)
    lat2_rad = math.radians(city2.lat)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = math.radians(city2.lon - city1.lon)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Fonction pour lire les villes à partir d'un fichier JSON
def read_cities_from_json(filename: str) -> List[City]:
    cities = []
    try:
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for idx, item in enumerate(data['cities']):
                try:
                    name = item['label']
                    lat_str = item['latitude']
                    lon_str = item['longitude']
                    if lat_str == '' or lon_str == '':
                        continue  # Ignorer cette ville
                    lat = float(lat_str)
                    lon = float(lon_str)
                    demand = 0  # La demande sera définie plus tard
                    cities.append(City(idx + 1, name, lat, lon, demand))
                except ValueError:
                    continue  # Ignorer cette ville
        return cities
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
        return []
    except KeyError as e:
        print(f"Clé manquante dans le fichier JSON : {e}")
        return []
    except json.JSONDecodeError:
        print("Erreur lors du décodage du fichier JSON.")
        return []

# Fonction pour générer des demandes aléatoires pour les villes
def generate_random_demands(cities: List[City], min_demand: int = 1, max_demand: int = 10):
    for city in cities:
        city.demand = random.randint(min_demand, max_demand)

# Fonction pour calculer la matrice des distances
def calculate_distance_matrix(cities: List[City]) -> np.ndarray:
    num_cities = len(cities)
    distance_matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(i, num_cities):
            dist = calculate_distance(cities[i], cities[j])
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist
    return distance_matrix

# Fonction de clustering K-Means capacitaire
def kmeans_capacitated_clustering(cities: List[City], vehicle_capacity: int) -> List[List[City]]:
    # Calcul du nombre minimal de camions nécessaires
    total_demand = sum(city.demand for city in cities)
    num_clusters = math.ceil(total_demand / vehicle_capacity)

    # Initialisation du clustering
    coordinates = np.array([[city.lat, city.lon] for city in cities])
    demands = np.array([city.demand for city in cities])

    # Clustering initial avec K-Means
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(coordinates)
    labels = kmeans.labels_

    # Création des clusters avec les villes et leurs demandes
    clusters = [[] for _ in range(num_clusters)]
    cluster_demands = [0] * num_clusters
    for idx, city in enumerate(cities):
        cluster_idx = labels[idx]
        clusters[cluster_idx].append(city)
        cluster_demands[cluster_idx] += city.demand

    # Ajustement des clusters pour respecter les capacités
    adjusted = True
    while adjusted:
        adjusted = False
        for i in range(num_clusters):
            while cluster_demands[i] > vehicle_capacity:
                # Trouver la ville la plus éloignée du centre du cluster
                center = kmeans.cluster_centers_[i]
                furthest_city = max(clusters[i], key=lambda c: math.hypot(c.lat - center[0], c.lon - center[1]))
                clusters[i].remove(furthest_city)
                cluster_demands[i] -= furthest_city.demand

                # Trouver un nouveau cluster pour cette ville
                # Affecter au cluster le plus proche qui peut l'accueillir
                min_distance = float('inf')
                best_cluster = -1
                for j in range(num_clusters):
                    if i != j and cluster_demands[j] + furthest_city.demand <= vehicle_capacity:
                        center_j = kmeans.cluster_centers_[j]
                        distance = math.hypot(furthest_city.lat - center_j[0], furthest_city.lon - center_j[1])
                        if distance < min_distance:
                            min_distance = distance
                            best_cluster = j
                if best_cluster == -1:
                    # Si aucun cluster ne peut l'accueillir, il faut augmenter le nombre de clusters
                    num_clusters += 1
                    clusters.append([])
                    cluster_demands.append(0)
                    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(coordinates)
                    labels = kmeans.labels_
                    adjusted = True
                    break  # Recommencer l'ajustement avec le nouveau nombre de clusters
                else:
                    clusters[best_cluster].append(furthest_city)
                    cluster_demands[best_cluster] += furthest_city.demand
                    adjusted = True
    return clusters

# Création de la population initiale pour l'algorithme génétique
def create_initial_population(city_indices: List[int], population_size: int) -> List[List[int]]:
    num_cities = len(city_indices)
    population = []
    for _ in range(population_size):
        individual = city_indices[:]
        random.shuffle(individual)
        population.append(individual)
    return population

# Fonction pour évaluer la fitness d'un individu (distance totale du trajet)
def fitness_function(individual: List[int], distance_matrix: np.ndarray) -> float:
    total_distance = 0
    current_city = 0  # Index du dépôt
    for city_idx in individual:
        total_distance += distance_matrix[current_city][city_idx]
        current_city = city_idx
    # Retour au dépôt après la dernière ville
    total_distance += distance_matrix[current_city][0]
    return total_distance

# Sélection par tournoi pour l'algorithme génétique
def selection(population: List[List[int]], fitnesses: List[float], num_selected: int) -> List[List[int]]:
    selected = []
    population_with_fitness = list(zip(population, fitnesses))
    pop_size = len(population_with_fitness)
    tournament_size = min(5, pop_size)
    for _ in range(num_selected):
        participants = random.sample(population_with_fitness, k=tournament_size)
        winner = min(participants, key=lambda x: x[1])
        selected.append(winner[0])
    return selected

# Croisement PMX pour l'algorithme génétique
def crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    size = len(parent1)
    child = [None]*size
    start, end = sorted(random.sample(range(size), 2))
    child[start:end] = parent1[start:end]
    for idx in range(size):
        if child[idx] is None:
            gene = parent2[idx]
            while gene in child:
                gene = parent2[parent1.index(gene)]
            child[idx] = gene
    return child

# Mutation par inversion pour l'algorithme génétique
def mutate(individual: List[int], mutation_rate: float) -> List[int]:
    num_mutations = max(1, int(len(individual) * mutation_rate))
    for _ in range(num_mutations):
        start, end = sorted(random.sample(range(len(individual)), 2))
        individual[start:end] = reversed(individual[start:end])
    return individual

# Algorithme génétique pour résoudre le TSP pour chaque camion
def genetic_algorithm_tsp(cities: List[City], depot: City, generations=1000, population_size=500, mutation_rate=0.4) -> Dict:
    all_cities = [depot] + cities
    num_cities = len(all_cities)
    city_indices = list(range(1, num_cities))  # Exclure le dépôt

    # Ajuster la taille de la population si nécessaire
    max_permutations = math.factorial(len(city_indices))
    if population_size > max_permutations:
        population_size = max_permutations

    population = create_initial_population(city_indices, population_size)
    distance_matrix = calculate_distance_matrix(all_cities)

    best_individual = None
    best_fitness = float('inf')
    no_improvement = 0
    max_no_improvement = 100

    for generation in range(generations):
        fitnesses = [fitness_function(individual, distance_matrix) for individual in population]

        current_best_fitness = min(fitnesses)
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_individual = population[fitnesses.index(best_fitness)].copy()
            no_improvement = 0
            print(f"Génération {generation}: Nouvelle meilleure solution avec distance = {best_fitness:.2f} km")
        else:
            no_improvement += 1

        if no_improvement >= max_no_improvement:
            print("Arrêt précoce : aucune amélioration observée au cours des dernières générations.")
            break

        selected = selection(population, fitnesses, population_size)
        new_population = []
        while len(new_population) < population_size:
            parents = random.sample(selected, min(2, len(selected)))
            child = crossover(parents[0], parents[1]) if len(parents) == 2 else parents[0][:]
            child = mutate(child, mutation_rate)
            new_population.append(child)
        population = new_population

    route = best_individual
    total_distance = best_fitness

    return {
        'route': route,
        'distance': total_distance,
        'distance_matrix': distance_matrix,
        'all_cities': all_cities
    }

# Fonction pour afficher la solution
def print_solution(depot: City, result: Dict, truck_number: int, vehicle_capacity: int):
    route = result['route']
    distance = result['distance']
    distance_matrix = result['distance_matrix']
    all_cities = result['all_cities']

    route_demand = sum(all_cities[city_idx].demand for city_idx in route)

    print(f"\n🚛 Camion {truck_number} :")
    print(f"Charge totale : {route_demand}/{vehicle_capacity} unités")
    print(f"Départ du dépôt ({depot.name})")

    current_city = 0  # Dépôt
    for city_idx in route:
        next_city = all_cities[city_idx]
        distance_segment = distance_matrix[current_city][city_idx]
        print(f" - {next_city.name} (Demande : {next_city.demand} unités, Distance depuis {all_cities[current_city].name} : {distance_segment:.2f} km)")
        current_city = city_idx

    # Retour au dépôt
    distance_to_depot = distance_matrix[current_city][0]
    print(f"Retour au dépôt ({depot.name}) avec une distance de {distance_to_depot:.2f} km")
    print(f"Distance totale pour Camion {truck_number} : {distance:.2f} km")

# Fonction pour créer la carte avec folium
def create_map(depot: City, results: List[Dict]):
    map_center = [depot.lat, depot.lon]
    folium_map = folium.Map(location=map_center, zoom_start=6)

    # Marquer le dépôt
    folium.Marker(
        [depot.lat, depot.lon],
        popup=f"Dépôt ({depot.name})",
        icon=folium.Icon(color='red', icon='home')
    ).add_to(folium_map)

    # Générer des couleurs uniques pour chaque camion
    def generate_unique_colors(n):
        colors = []
        for i in range(n):
            hue = i / n
            lightness = 0.5
            saturation = 0.9
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            colors.append(hex_color)
        return colors

    num_trucks = len(results)
    colors = generate_unique_colors(num_trucks)

    for idx, result in enumerate(results):
        route = result['route']
        all_cities = result['all_cities']
        color = colors[idx]

        route_points = [[depot.lat, depot.lon]]
        for city_idx in route:
            city = all_cities[city_idx]
            folium.Marker(
                [city.lat, city.lon],
                popup=f"{city.name} (Demande : {city.demand} unités)",
                icon=folium.Icon(color='blue', icon_color=color)
            ).add_to(folium_map)
            route_points.append([city.lat, city.lon])
        route_points.append([depot.lat, depot.lon])
        folium.PolyLine(route_points, color=color, weight=2.5, opacity=0.8).add_to(folium_map)

    folium_map.save("map.html")
    print("La carte a été sauvegardée sous le nom 'vrp_solution_map.html'.")

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

def get_cities_from_names(city_names: List[str]) -> List[City]:
    cities = []
    for idx, name in enumerate(city_names, start=1):
        coordinates = get_coordinates(name)
        if coordinates:
            lat, lon = coordinates
            cities.append(City(idx, name, lat, lon, 0))
    return cities
