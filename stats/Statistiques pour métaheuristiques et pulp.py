import json
import matplotlib.pyplot as plt
import numpy as np

# Chargement des données JSON
with open("C:/Users/Utilisateur/Arthur/Cours/A3/Algorithme et optimisation combinatoire/Projet/Théophile/result.json", "r") as file:
    data = json.load(file)

# Initialiser des listes pour stocker les valeurs
jeux = []
algorithmes = ["Pulp", "ANT", "Tabu"]
temps_execution = {algo: [] for algo in algorithmes}
distances = {algo: [] for algo in algorithmes}

# Extraction des données
for jeu, contenu in data.items():
    jeux.append(jeu)  # Ajouter le nom du jeu (Game_0, Game_1, etc.)
    for algo in algorithmes:
        if algo in contenu:  # Vérifier si l'algorithme existe pour ce jeu
            temps_execution[algo].append(contenu[algo]["Temps"])  # Ajouter le temps d'exécution
            distances[algo].append(contenu[algo]["Distance"])  # Ajouter la distance
        else:
            # Valeur None pour les jeux sans un algorithme spécifique
            temps_execution[algo].append(None)
            distances[algo].append(None)

# Création des graphiques

# Paramètres de l'affichage
x = np.arange(len(jeux))  # Création des positions pour les jeux
width = 0.2  # Largeur des barres

# Histogramme pour le temps d'exécution
fig, ax = plt.subplots(figsize=(10, 6))
for i, algo in enumerate(algorithmes):
    ax.bar(x + i * width, temps_execution[algo], width, label=algo)

ax.set_xlabel("Games")
ax.set_ylabel("Execution Time (seconds)")
ax.set_title("Execution Time by Game and Algorithm")
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(jeux)
ax.legend()

plt.show()

# Histogramme pour la distance
fig, ax = plt.subplots(figsize=(10, 6))
for i, algo in enumerate(algorithmes):
    ax.bar(x + i * width, distances[algo], width, label=algo)

ax.set_xlabel("Games")
ax.set_ylabel("Distance (units)")
ax.set_title("Distance by Game and Algorithm")
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(jeux)
ax.legend()

plt.show()
