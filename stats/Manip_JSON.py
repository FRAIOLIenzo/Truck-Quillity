import json as js

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
                data = js.load(file)
            except js.JSONDecodeError:
                data={}
            data["Game_"+str(Num_Jeu)]= test
            file.seek(0)
            js.dump(data,file, indent=4)
            file.truncate()
        else:
            try:
                data = js.load(file)
            except js.JSONDecodeError:
                data={}
            test = {
                    "NombreCamion" : Nombre_Camion,
                    "Distance": km,
                    "Temps" : tps,
                    "ListeTrajet" : Liste_Trajet
                }
            data["Game_"+str(Num_Jeu)][Nom_Algo] = test
            file.seek(0)
            js.dump(data, file, indent=4)
            file.truncate()

    print("Données mises à jour")

def STAT_JSON(Liste_ville,Num_Jeu,tps, Nom_Algo, Nombre_Camion, Liste_Trajet,km, JSON_Path):
    with open(JSON_Path, "r+") as file:
        test = {
            "villes":Liste_ville, 
            Nom_Algo:{
            "NombreCamion":Nombre_Camion,
            "Distance":km,
            "Temps":tps,
            "ListeTrajet":Liste_Trajet
            }
        }
        try :
            data = js.load(file)
        except js.JSONDecodeError:
            data={}
        print("Mise à jour réussie")
        data[str(Num_Jeu)]= test
        file.seek(0)
        js.dump(data,file, indent=4)
        file.truncate()
