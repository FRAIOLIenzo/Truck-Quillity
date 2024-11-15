#   _____      _             _            _         __                           _     
#  / ____|    | |           (_)          | |       / _|                         (_)    
# | |     ___ | | ___  _ __  _  ___    __| | ___  | |_ ___  _   _ _ __ _ __ ___  _ ___ 
# | |    / _ \| |/ _ \| '_ \| |/ _ \  / _` |/ _ \ |  _/ _ \| | | | '__| '_ ` _ \| / __|
# | |___| (_) | | (_) | | | | |  __/ | (_| |  __/ | || (_) | |_| | |  | | | | | | \__ \
# \_____\___/|_|\___/|_| |_|_|\___|  \__,_|\___| |_| \___/ \__,_|_|  |_| |_| |_|_|___/

# Métaheuristique : Colonie de fourmis
# À base de population - Intelligence en essaim

# Importation des bibliothèques
import random
import numpy as np
from data import *
import time as tp
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
import requests
import Manip_JSON as js

# Temps départ
t0 = tp.time()

# Variables globales des fourmis
nb_fourmis = 200
max_iteration = 5000

t_evaporation = 0.1 # Taux d'évaporation
i_phero, i_visi, depot_phero = 1, 2, 100  # Importance des phéromones, visibilité et dépôt

# Variables globales des camions
capacite_max = 50

# Cache pour les probabilités
cache_probabilites = {}

# Fonction pour construire une solution
def construire_solution():
    non_visite = list(ville_d.keys())[1:] # On crée un ensemble de données avec les numéros des villes
    routes = dict() # Liste de toutes les routes de tous les camions
    capacite = dict() # Pour la capacité de chaque camion
    distance_total = 0
    nb_camions = 0
    depot = list(ville_d.keys())[0]  # Convertir les clés en liste et accéder à la première clé

    # Assigner des villes aux camions
    while non_visite:
        ville_actuel = depot # On démarre forcément au dépôt
        routes[f"Camion n{nb_camions + 1}"] = [] # On fait la route pour un seul camion
        routes[f"Camion n{nb_camions + 1}"].append(depot)
        capacite[f"Camion n{nb_camions + 1}"] = 0

        while capacite[f"Camion n{nb_camions + 1}"] < capacite_max and non_visite:
            # Vérifie si au moins une ville peut être ajoutée sans dépasser la capacité maximale
            villes_possibles = [v for v in non_visite if (capacite[f"Camion n{nb_camions + 1}"] + ville_d[v]) <= capacite_max]
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
                        visibilité = visibilites[0][non_visite.index(prochaine_ville) + 1]
                    else:
                        pheromone = v_phero[non_visite.index(ville_actuel) + 1][non_visite.index(prochaine_ville) + 1]
                        visibilité = visibilites[non_visite.index(ville_actuel) + 1][non_visite.index(prochaine_ville) + 1]
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
            routes[f"Camion n{nb_camions + 1}"].append(prochaine_ville)
            non_visite.remove(prochaine_ville)
            distance_total += distances[villes_liste.index(ville_actuel)][villes_liste.index(prochaine_ville)]
            capacite[f"Camion n{nb_camions + 1}"] += ville_d[prochaine_ville]
            ville_actuel = prochaine_ville # Mise à jour de la ville actuelle

        # Retour au dépôt
        distance_total += distances[villes_liste.index(ville_actuel)][0]
        routes[f"Camion n{nb_camions + 1}"].append(depot)
        nb_camions += 1

    return routes, capacite, distance_total

def maj_pheromones(solutions, v_pheromone):
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
                prochaine_ville = villes_liste.index(prochaine_ville_nom) # Index de la prochaine ville
                v_pheromone[ville_actuel][prochaine_ville] += deposit
                ville_actuel = prochaine_ville

            # Retour au dépôt (Nancy)
            v_pheromone[ville_actuel][ville_actuel] += deposit

    return v_pheromone

def resoudre(v_pheromone, meilleur_distance, meilleur_solution, meilleur_capacite):
    for iteration in range(max_iteration):
        # Solutions construites par les fourmis
        solutions = []
        for i in range(nb_fourmis):
            routes, capacite, distance_total = construire_solution()

            # Mise à jour de la meilleure solution
            if distance_total < meilleur_distance:
                meilleur_distance = distance_total
                meilleur_solution = routes
                meilleur_capacite = capacite
            
        # Mise à jour des phéromones
        v_pheromone = maj_pheromones(solutions, v_pheromone)

    return meilleur_solution, meilleur_capacite, meilleur_distance

def main():

    global nom_ville, ville_d, v_phero, visibilites, distances, villes_liste

    # Seed
    random.seed(48)

    # Lecture des données
    result = generate()
    if result:
        villes, distances_t = result

        # Liste des noms de villes
        nom_ville = list(villes)
        taille_groupe = len(villes) // 10  # Nombre de villes par groupe

        for i in range(10):
            # Déterminer les indices de début et de fin pour ce groupe
            debut = i * taille_groupe
            fin = debut + taille_groupe

            ville_d = dict()
            for valeur in nom_ville[debut+1:fin+1]:
                ville_d[valeur[0]] = random.randint(1, 10)
            premiere_cle = list(ville_d.keys())[0]  # On récupère la première clé
            ville_d[premiere_cle] = 0  # On met sa valeur à 0
            
            # Récupère la première clé pour définir le dépôt
            villes_liste = list(ville_d.keys())

            # Extraire la sous-matrice de distances pour ce groupe
            indices = list(range(debut+1, fin+1))
            distances = np.array(distances_t)[np.ix_(indices, indices)].tolist()  # Garder le nom distances

            # Nombre de villes dans le groupe actuel
            n = len(ville_d)
            
            # Initialisation des phéromones et des visibilites
            v_phero = np.ones((n, n), dtype=float) - np.eye(n)  # Initialisation des phéromones
            distance_matrix = np.array(distances)  # Conversion pour manipulation avec numpy
            visibilites = 1 / (distance_matrix + np.eye(n))  # Calcul de la visibilité

            # Initialisation des solutions
            meilleur_solution, meilleur_distance, meilleur_capacite = None, float('inf'), None

            # Résoudre le problème pour ce groupe (appelle ta fonction resoudre)
            t0 = tp.time()  # Temps de départ
            solution, capacite, distance = resoudre(v_phero, meilleur_distance, meilleur_solution, meilleur_capacite)
            tf = tp.time()  # Temps de fin
            tt = tf - t0  # Temps total pour résoudre

            # Nom de la solution pour l'enregistrement
            Nom = "ANT"
            valeur = []
            for _, values in solution.items():
                valeur.append(values)

            # Écriture du résultat dans le fichier JSON (appel de ta fonction Writer_JSON)
            js.Writer_JSON(nom_ville[i * taille_groupe:(i + 1) * taille_groupe], i, tt, Nom, len(capacite), valeur, distance, 
                        'C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result.json')

main()
