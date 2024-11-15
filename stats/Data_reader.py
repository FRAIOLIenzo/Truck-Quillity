import csv
from math import *
from time import *
from functools import lru_cache

EARTH_RADIUS = 6371

@lru_cache(maxsize=None)
def data_reader(data_batch):
    Demands = {}
    coordinates = {}
    with open(data_batch) as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')         # on lit le fichier csv
        next(reader)                                        # on supprime les titres 
        rows = [row[0].split(',') for row in reader]
        for row in rows: 
            row[1] = float(row[1])
            row[2] = float(row[2])
            row[3] = int(row[3])
        Distance_matrix = [ [0 for _ in range(len(rows))] for _ in range(len(rows))]
        count = 0
        for each in rows:                                   # boucle de lecture pour chaque élément  
            Demands[each[0]] = each[3]                      # on ajoute au dictionnaire des demandes chaque demande
            coordinates[each[0]] = [each[1], each[2]]       
            count2 = 0
            for each_other in rows :
                if each == each_other:
                    Distance_matrix[count][count2]=0
                else:
                    Distance_matrix[count][count2] = calcul_distance(float(each[1]),float(each[2]),float(each_other[1]),float(each_other[2]))
                count2 += 1
            count += 1
        return Demands, Distance_matrix, coordinates

@lru_cache(maxsize=None)
def calcul_distance(latitude1, longitude1, latitude2, longitude2):
    """
    Optimized single distance calculation for when vectorized operation isn't needed.
    Cached for repeated calculations.
    """
    lat1, lon1, lat2, lon2 = map(radians, [latitude1, longitude1, latitude2, longitude2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Precompute trigonometric functions
    sin_dlat_2 = sin(dlat/2)
    sin_dlon_2 = sin(dlon/2)
    cos_lat1 = cos(lat1)
    cos_lat2 = cos(lat2)
    
    a = sin_dlat_2**2 + cos_lat1 * cos_lat2 * sin_dlon_2**2
    
    # Avoid numerical instabilities
    a = min(a, 1.0)
    
    
    c = 2 * EARTH_RADIUS * atan2(sqrt(a), sqrt(1-a))
    return c
