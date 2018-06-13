## OC_Python_Maze
Script python permettant de générer un graph à partir de données JSON extraites de l'API "Réseau social virtuel" PPLAPI
Purement, il affiche la moyenne du degré d'agréabilité(y) des zones en fonction de la densité de population(x). Techniquement pour évaluer l'idée que : plus il y a d'individus dans une zone, plus il y a une tendance à avoir un degré d'agréabilité moyen (0).

# Fichiers présents :
> - agents-100k.json => Contient un extrait de la base de données de pplapi.com (100.000 objets)
> - Le script download_agents.py permet de parser le JSON
> - model.py contient le "programme" et les classes nécessaires

# Classes :
- Agent : représente les individus recueillis (100.000 instances)
- Position : représente la position d'un individu sur la Terre (latitude et longitude appliquées à l'échelle de la Terre)
- Zone : classe essentiellement statique qui représente la Terre (une zone de petites zones)
- BaseGraph & AgreeabiliteGraph : pour la représentation visuelle 