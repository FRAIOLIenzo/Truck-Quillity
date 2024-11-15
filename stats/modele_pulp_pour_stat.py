import pulp
from matplotlib import pyplot as plt
from itertools import *
from data import *
from json import *
from Manip_JSON import *
from time import time
import random

t0 = time()
#-----------Résolution du problème avec pulp-----------#
def Solver_PuLP(q, d, Q):
    # Chargement des données
    somme_demande = sum(q.values())
    
    # Calcul du nombre de camions nécessaire
    M = 0
    while somme_demande > 0.75 * M * Q:
        M += 1

    # Obtenir la liste des villes
    villes = list(q.keys())
    N = len(villes) - 1  # Nombre de clients, sans compter le dépôt

    alpha = 1
    beta = 1

    # Création du problème
    vrp_problem = pulp.LpProblem("VRP", pulp.LpMinimize)

    # Variables de décision
    x = pulp.LpVariable.dicts("x", ((i, j, k) for i in range(len(d)) for j in range(len(d)) for k in range(M)), cat='Binary')
    u = pulp.LpVariable.dicts("u", (i for i in range(len(d))), lowBound=0, cat='Continuous')

    # Fonction objectif
    vrp_problem += (alpha * pulp.lpSum(d[i][j] * x[i, j, k] for i in range(len(d)) for j in range(len(d)) for k in range(M))
                    + beta * pulp.lpSum(x[0, j, k] for j in range(1, len(villes)) for k in range(M)))

    # Contraintes

    # 1. Chaque client doit être visité une fois
    for i in range(1, len(villes)):
        vrp_problem += pulp.lpSum(x[i, j, k] for j in range(len(villes)) for k in range(M) if i != j) == 1

    # 2. Conservation des flux pour chaque client et chaque camion
    for k in range(M):
        for i in range(1, len(villes)):
            vrp_problem += pulp.lpSum(x[i, j, k] for j in range(len(villes))) == pulp.lpSum(x[j, i, k] for j in range(len(villes)))

    # 3. Capacité des camions
    for k in range(M):
        vrp_problem += pulp.lpSum(q[villes[0]] * x[i, j, k] for i in range(1, len(villes)) for j in range(len(villes))) <= Q

    # 4. Dépôt visité une seule fois par chaque camion
    depot = villes[0]  # Supposons que le premier élément de `villes` est le dépôt
    for k in range(M):
        vrp_problem += pulp.lpSum(x[0, j, k] for j in range(1, len(villes))) == 1
        vrp_problem += pulp.lpSum(x[i, 0, k] for i in range(1, len(villes))) == 1

    # 5. Contrainte de sous-tour pour éviter les sous-tours (MTZ)
    for i in range(len(villes)):
        for j in range(len(villes)):
            if i != j:
                for k in range(M):
                    if i == 0:
                        u[i] = 0
                    elif j == 0:
                        u[j] = 0
                    else:
                        vrp_problem += u[i] - u[j] + N * x[i, j, k] <= N - 1

    # Résoudre le problème
    vrp_problem.solve()
    print("Status:", pulp.LpStatus[vrp_problem.status])

    list_camion = []
    if pulp.LpStatus[vrp_problem.status] == "Optimal":
        solution = {}
        for i in range(len(villes)):
            for j in range(len(villes)):
                for k in range(M):
                    if x[i, j, k].value() is not None and x[i, j, k].value() > 0:
                        solution[(i, j, k)] = x[i, j, k].value()
        
        list_camion = [[] for _ in range(M)]
        for k in range(M):
            ville_actuelle = 0
            list_camion[k].append(ville_actuelle)
            while True:
                ville_prochaine = None
                for (i, j, p), val in solution.items():
                    if i == ville_actuelle and k == p and val > 0:
                        ville_prochaine = j
                        break
                if ville_prochaine is None or ville_prochaine == 0:
                    break
                list_camion[k].append(ville_prochaine)
                ville_actuelle = ville_prochaine
            list_camion[k].append(0)

        # Calcul de la distance totale
        distance = 0
        for k in range(M):
            for i in range(len(list_camion[k]) - 1):
                point_actuel = list_camion[k][i]
                point_futur = list_camion[k][i + 1]
                distance += d[point_actuel][point_futur]
        print(f'Distance totale : {distance} km')
        
        for k in range(M):
            print(f"Trajet du camion {k} : {list_camion[k]}")
    print(q)
    element_q = list(q.items())

    return k, list_camion, villes, M, element_q, distance

def plot_pulp(c,k,M):
    # Tracé des villes
    for ville, coord in c.items():
        plt.plot(coord[0], coord[1], 'o', markersize=10, label=ville if ville == '0' else "")
        plt.text(coord[0] + 0.1, coord[1] + 0.1, ville, fontsize=12)

    # Tracé des trajets par camion
    colors = ['b', 'g', 'r', 'c', 'm']
    for k in range(M):
        route = list_camion[k]
        for i in range(len(route) - 1):
            qepart = villes[route[i]]
            ville_arrivee = villes[route[i + 1]]
            x = [c[qepart][0], c[ville_arrivee][0]]
            y = [c[qepart][1], c[ville_arrivee][1]]
            plt.plot(x, y, colors[k % len(colors)], linewidth=2, label=f"Camion {k}" if i == 0 else "")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Itinéraires des camions entre les villes")
    plt.legend(loc="best")
    plt.grid()
    plt.show()

random.seed(48)
result = generate()
if result:
    villes, distances_t = result

    nom_ville = list(villes)
    taille_groupe = len(villes) // 10  # Nombre de villes par groupe

    for i in range(10):
        # Déterminer les indices de début et de fin pour ce groupe
        debut = i * taille_groupe
        fin = debut + taille_groupe
            
        q = dict()
        for valeur in nom_ville[debut+1:fin+1]:
            q[valeur[0]] = random.randint(1, 10)
        premiere_cle = list(q.keys())[0]  # On récupère la première clé
        q[premiere_cle] = 0  # On met sa valeur à 
        
        indices = list(range(debut+1, fin+1))
        d = np.array(distances_t)[np.ix_(indices, indices)].tolist()  # Garder le nom distances

            
        k, list_camion, villes, M, element_q, Distance_totale = Solver_PuLP(q,d,50)
        list_nom_ville = []
        for p in range(len(list_camion)):
            list_nom_ville.append([])
            for j in range(len(list_camion[p])):
                list_nom_ville[p].append(villes[list_camion[p][j]])
        print(list_nom_ville)
        
        liste_ville = []
        
        
        Nom = "Pulp"
        
        
        for j in range(len(element_q)):
            liste_ville.append([element_q[j][0],element_q[j][1]])
        Writer_JSON(liste_ville,i,time()-t0, Nom, k+1, list_nom_ville,Distance_totale, 'C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result.json')

#plot_pulp(c,k,M)