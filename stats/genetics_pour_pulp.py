import random
import math
import numpy as np
import time as tp # Pour mesurer le temps d'exécution
from typing import List, Dict
from sklearn.cluster import KMeans
from Data_reader import *  # Assurez-vous que le chemin est correc
from Manip_JSON import *

# Inclure la fonction Writer_JSON telle que vous l'avez fournie
import json as js

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

# Fonction pour lire les villes à partir du data_reader
def read_cities_from_datareader(filename: str) -> List[City]:
    cities = []
    try:
        Demands, Distance_matrix, coordinates = data_reader(filename)
        for idx, (city_name, demand) in enumerate(Demands.items()):
            lat, lon = coordinates[city_name]
            cities.append(City(idx + 1, city_name, lat, lon, demand))
        return cities
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
        return []
    except KeyError as e:
        print(f"Clé manquante dans les données : {e}")
        return []

# Fonction de clustering K-Means capacitaire
def kmeans_capacitated_clustering(cities: List[City], vehicle_capacity: int) -> List[List[City]]:
    # Calcul du nombre minimal de camions nécessaires
    total_demand = sum(city.demand for city in cities)
    num_clusters = math.ceil(total_demand / vehicle_capacity)

    # Initialisation du clustering
    coordinates = np.array([[city.lat, city.lon] for city in cities])

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
                    # Augmenter le nombre de clusters si nécessaire
                    num_clusters += 1
                    clusters.append([])
                    cluster_demands.append(0)
                    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(coordinates)
                    labels = kmeans.labels_
                    adjusted = True
                    break
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

# Fonction principale
if __name__ == "__main__":
    try:
        # Lecture des villes depuis le fichier CSV en utilisant data_reader
        data_file_path = 'C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/Data/data_100.csv'
        all_cities = read_cities_from_datareader(data_file_path)

        if not all_cities:
            print("Aucune ville n'a été chargée. Vérifiez le fichier de données.")
            exit()

        # Définir le dépôt
        depot = City(0, "Paris", 48.8566, 2.3522, 0)

        # Définir la capacité du véhicule (par défaut 200 unités)
        vehicle_capacity = 50

        # Nombre total de groupes (10 instances de 10 villes)
        num_groups = 10
        group_size = len(all_cities) // num_groups

        for i in range(num_groups):
            # Obtenir les villes pour ce groupe
            start_index = i * group_size
            end_index = (i + 1) * group_size
            group_cities = all_cities[start_index:end_index]

            print(f"\nTraitement du groupe {i + 1} avec {len(group_cities)} villes.")

            # Calcul du nombre minimal de camions nécessaires
            total_demand = sum(city.demand for city in group_cities)
            num_trucks = math.ceil(total_demand / vehicle_capacity)
            print(f"Nombre total de camions nécessaires pour le groupe {i + 1}: {num_trucks}")

            # Avec 10 villes, nous pouvons utiliser un seul camion sans clustering
            clusters = [group_cities]

            # Exécuter l'algorithme génétique pour chaque cluster et enregistrer les résultats
            for j, cluster in enumerate(clusters):
                print(f"\nOptimisation de l'itinéraire pour le Camion {j + 1} du groupe {i + 1}...")
                # Mesurer le temps de résolution
                t0 = tp.time()

                # Appeler l'algorithme génétique
                result = genetic_algorithm_tsp(cluster, depot, generations=500, population_size=100, mutation_rate=0.4)

                # Calculer le temps écoulé
                tf = tp.time()
                tt = tf - t0  # Temps total pour résoudre

                # Préparer les données pour Writer_JSON
                nom_ville_cluster = [city.name for city in cluster]
                Nom_Algo = "Genetics"
                Nombre_Camion = 1  # Un camion pour ce cluster
                # Liste du trajet en noms de villes
                Liste_Trajet = [depot.name] + [result['all_cities'][idx].name for idx in result['route']] + [depot.name]

                # Obtenir la distance totale pour la solution
                total_distance = result['distance']

                # Écrire dans result.json en utilisant Writer_JSON
                JSON_Path = 'C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result.json'  # Chemin vers votre fichier result.json

                # Utiliser la fonction Writer_JSON fournie
                Writer_JSON(
                    Liste_ville=nom_ville_cluster,
                    Num_Jeu=i,
                    tps=tt,
                    Nom_Algo=Nom_Algo,
                    Nombre_Camion=Nombre_Camion,
                    Liste_Trajet=Liste_Trajet,
                    km=total_distance,
                    JSON_Path=JSON_Path
                )

    except ValueError as e:
        print(e)
