from json import *

def Writer_JSON(Liste_ville,Num_Jeu,tps, Nom_Algo, Nombre_Camion, Liste_Trajet,km, JSON_Path):
    
    
    with open(JSON_Path, "r+") as file:
        if Nom_Algo == "Pulp":
            test = {
                "villes":Liste_ville, 
                Nom_Algo:{
                    "NombreCamion":Nombre_Camion,
                    "Distance":km,
                    "Temps":tps,
                    "ListeTrajet":Liste_Trajet
                }
            }
            print("Jeu de donnée généré")
            try :
                data = load(file)
            except JSONDecodeError:
                data={}
            data["Jeu_"+str(Num_Jeu)]= test
            file.seek(0)
            dump(data,file, indent=4)
            file.truncate()
        else:
            try:
                data = load(file)
            except JSONDecodeError:
                data={}
            test = {
                    "NombreCamion" : Nombre_Camion,
                    "Distance": km,
                    "Temps" : tps,
                    "ListeTrajet" : Liste_Trajet
                }
            data["Jeu_"+str(Num_Jeu)][Nom_Algo] = test
            file.seek(0)
            dump(data, file, indent=4)
            file.truncate()
            
    print("Données mises à jour")
        
def Read_JSON(JSON_Path,Num_jeu,Algo):
    with open(JSON_Path,"w", "r") as file:
        data = load(file)
        Villes = data[Num_jeu]["villes"]
        Nbr_Camion = data[Num_jeu][Algo]["NbrCamion"]
        Liste_Trajet = data[Num_jeu][Algo]["ListeTrajet"]
        return Villes, Nbr_Camion, Liste_Trajet