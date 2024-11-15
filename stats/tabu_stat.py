
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
from itertools import *
from Data_reader import *
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
from Manip_JSON import *

#----------------------------------------------------------------Générateur d'instance----------------------------------------------------------------

random.seed(42)

#----------------------------------------------------------------Fonctions----------------------------------------------------------------

def generate_path(nb_villes):
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


def calculate_path_distance(path, distance_matrix):
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

def calculate_weight(sol):
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
    courantes = deque(()) 
    meilleures_courantes = deque(()) 

    while (nb_iter < iter_max):                                                
        valeur_meilleure = float('inf')    

        # On parcourt tous les voisins de la solution courante                
        for voisin in generate_neighbors(solution_courante).items():
            dico = solution_courante
            dico[voisin[0]] = voisin[1]
            valeur_voisin = calculate_path_distance(dico, matrix)
            poids_voisin = calculate_weight(dico)

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

        courantes.append(calculate_path_distance(solution_courante, matrix)) 
        meilleures_courantes.append(valeur_meilleure_globale) 
                                                                                                              
        # on passe au meilleur voisin non tabou trouvé                         
        solution_courante = meilleure                                          
                                                                               
        # on met à jour la liste tabou                                         
        liste_tabou.append(solution_courante)                                  

    return meilleure_globale, courantes, meilleures_courantes

def multi_start(nb_villes, solution_initiale, distance_matrix, nb_test):
    taille_tabou = 100
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
        poids_courant = calculate_weight(sol_courante)

        solutions.append(val_courante)
        
        if val_courante < val_max:
            val_max = val_courante
            sol_max = sol_courante
            poids_max = poids_courant
        
        best_solutions.append(val_max)
        sac = generate_path(nb_villes)

    return sol_max, val_max, nb_test, solutions, best_solutions, poids_max

#---------------------------------------------------------------Main----------------------------------------------------------------
taille_tabou = 0
iter_max = 0
nb_test = 0

for i in range(10):

    start = tp.time()

    q_list, d_list, _ = data_reader("C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/Data/data_100.csv")

    distances = d_list
    villes = q_list
    
    nom_ville = []
    for city, _ in villes.items():
        nom_ville.append(city)


    ville_d = villes
    premiere_cle = list(ville_d.keys())[0]  # On récupère la première clé
    ville_d[premiere_cle] = 0 # Dépôt - demande à 0
    print("Main \n")

    # Initialisation des paramètres
    nb_villes = len(nom_ville)
    capacite_max = 50
    taille_tabou += 50
    iter_max += 50 
    path = generate_path(nb_villes)
    solution_initiale = path

    # Run multi start
    nb_test += 200
    sol_max, val_max, nb_test, solutions, best_solutions, poids = multi_start(nb_villes, solution_initiale, distances, nb_test)
    stop = tp.process_time()
    Nom = "Tabu : length tabu, " + str(taille_tabou) + " ; maximum iteration, " + str(iter_max) + " ; number of tests, " + str(nb_test)
    
    liste_ville = []
    STAT_JSON(liste_ville,"Test " + str(i), tp.time()-start, Nom, len(sol_max), list(sol_max.values()),val_max,"C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result_tabu.json")
    