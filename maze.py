# -*-coding:Utf-8 -*
import random
import os
from robot import Robot
from copy import deepcopy

class Maze:    
    """Classe représentant un labyrinthe."""
    MAPS_DIRECTORY = "cartes"
    COMPONENT = {"O" : "█", 
                 "." : "░", 
                 " " : " ", 
                 "U" : "♥", 
                 "X" : "☻", 
                 "x" : "☺"}
    RESPONSE = {"ERROR_ROBOT_NAME" : "ERROR_ROBOT_NAME|ERREUR_NOM_ROBOT: Ce nom de robot est déjà utilisé.|",
                "ERROR_ROBOT" : "ERROR_ROBOT|ERREUR_ROBOT: Il n'y a pas de robot avec vos identifiants de connexion.|",
                "SUCCESS_ROBOT" : "SUCCESS_ROBOT|SUCCES_ROBOT: Votre robot est prêt.|",
                "ERROR_COMMAND" : "ERROR_COMMAND|ERREUR_COMMANDE: Cette commande n'existe pas.|",
                "SUCCESS_MOVE" : "SUCCESS_MOVE|SUCCES_DEPLACEMENT: Mouvement effectué avec succès.|",
                "SUCCESS_CREATE_DOOR" : "SUCCES_CREATE_DOOR|SUCCES_CREER_PORTE: porte créée avec succès.|",
                "SUCCESS_CREATE_WALL" : "SUCCES_CREATE_WALL|SUCCES_CREER_MUR: mur créé avec succès.|",
                "ACTION_IMPOSSIBLE" : "ACTION_IMPOSSIBLE|ACTION_IMPOSSIBLE: Cette action est impossible.|",
                "STOP_WALL" : "STOP_WALL|STOP_MUR: vous ne pouvez pas avancer davantage à cause d'un mur.|",
                "STOP_ENEMI" : "STOP_ENEMI|STOP_ENNEMI: vous ne pouvez pas avancer sur un ennemi.|",
                "ERROR_ACTION" : "ERROR_ACTION|ERREUR_ACTION: cette action est impossible.|",
                "VICTORY" : "VICTORY|VICTOIRE: Vous avez gagné, et pas les autres, vous êtes le plus beau robot.|",
                "END_SERVER" : "END_SERVER|Fermeture du serveur.|"}

    def __init__(self):
        self.current_map = []
        self.robots = {}
        self.file_name = ""  
        self.positions_depart = []
        self.victory = False      

    @property
    def regles(self):
        content = "REGLES : Vous êtes le robot %s "%self.COMPONENT["X"]
        content+= "et vous devez arriver à la sortie %s "%self.COMPONENT["U"] 
        content+= "avant les robots ennemis %s.\n"%self.COMPONENT["x"]
        content+= "ACTIONS : \n"
        content+= "\t>S : se deplacer vers le sud (bas)\n"
        content+= "\t>N : se deplacer vers le sud (haut)\n"
        content+= "\t>O : se deplacer vers l'ouest (gauche)\n"
        content+= "\t>E : se deplacer vers l'est (droite)\n"
        content+= "\t----------------------------------------majuscules ou minuscules--\n"
        content+= "\t>M : Murer une porte\n"
        content+= "\t>P : Percer un mur pour faire une porte\n"
        content+= "\t=>M et P s'utilisent avec une direction : ME, PN, MS...\n"
        return content
    

    def get_map_list(self):
        """ Parcourt le dossier repertoire des cartes et retourne une liste de fichiers"""
        liste = []
        for nom_fichier in os.listdir(self.MAPS_DIRECTORY):
            if nom_fichier.endswith(".txt"):
                chemin = os.path.join(self.MAPS_DIRECTORY, nom_fichier)
                nom_carte = nom_fichier[:-4] ## Retire l'extension
                liste.append([nom_carte, chemin])
        # S'il n'y a pas de carte, on en génère une nouvelle avec un fichier :
        if(len(liste) == 0):
            liste.append(self._generate_base_map())
        
        return liste

    # _Private :
    def _generate_base_map(self):
        """ Cas : pas de fichier carte => en génère une facile"""
        contenu = "OOOOOOOOOO\nO O X  O O\nO .XOOXX O\nO O O XX O\nO OOOO O.O\nOXO O X  U\nO OOOOOO.O\nO O  XX  O\nO O OOOOOO\nO . O  X O\nOOOOOOOOOO"
        chemin = self.MAPS_DIRECTORY+"/auto_gen.txt"
        with open(chemin, 'w') as out_f:
            out_f.write(contenu)
        return ["Carte autogénérée", chemin]


    def load_map(self, map_name):
        """Cherche le nom de carte dans la liste, crée l'objet Labyrinthe"""
        self.file_name = map_name
        with open(self.file_name, 'r') as file:
            lignes = file.read().split("\n")
        
        self.current_map = []
        self.positions_depart = []
        i = 0
        # On a alors un tableau de lignes ["OOOOOOOO", "O  O  XO", "O      O", "OOOOOOOO"]
        while(i < len(lignes)):
            if(lignes[i] != ""): #Ignore les lignes vides, en général la dernière, ça peut être la première 
                j = 0
                ligneTmp = []
                while(j < len(lignes[i])):                    
                    if(lignes[i][j] in self.COMPONENT):
                        if(lignes[i][j] in [" ", "X", "x"]):
                            ligneTmp.append(self.COMPONENT[" "]) # Si c'est un robot X/x, on le retire de la carte
                            self.positions_depart.append([i,j])
                        else:
                            # Si c'est un O ou . (J'ai décidé qu'on ne commençait pas dans une porte)
                            ligneTmp.append(self.COMPONENT[lignes[i][j]])
                    else: 
                        # Sinon c'est un caractère inconnu on met un espace
                        ligneTmp.append(self.COMPONENT[" "])
                        self.positions_depart.append([i,j])
                    j+=1
                # On ajoute la ligne
                self.current_map.append(ligneTmp)
            i+=1
        print("Carte chargée : %s"%map_name)
        
    def save_map(self):
        """ Sauvegarde le labyrinthe dans un fichier """
        # NOTE : on échange les caractères pour mettre les caractères conventionnels X U O .
        contenu = ""
        # j'inverse le dictionnaire MATERIEL pour remettre les caractères par défaut dans le fichier .txt
        inversion_dictionnaire = dict([[v,k] for k,v in self.COMPONENT.items()])
        for i,ligne in enumerate(self.current_map):
            for j,element in enumerate(ligne):
                
                if(str(element) in self.COMPONENT.values()):
                    contenu += inversion_dictionnaire[element]
                else:
                    contenu += inversion_dictionnaire[" "]

            if(j < len(ligne)): contenu += "\n"

        with open(self.file_name, 'w') as out_f:
            out_f.write(contenu)


    def set_robot(self, robot_id):
        """Crée un robot, l'identifiant du robot est son ip:port"""
        robot = Robot()
        print("Log : création robot pour %s"%robot_id)
        self.robots[robot_id] = robot

    def place_robot(self, robot_id):
        """Place un robot aléatoirement, l'identifiant du robot est son ip:port"""
        random.shuffle(self.positions_depart) # Mélange
        position = self.positions_depart.pop() # Prend le dernier membre : [a, b]
        print("Position d'un robot "+str(position))
        self.robots[robot_id].pos_x = position[0]
        self.robots[robot_id].pos_y = position[1]

    def set_robot_name(self, robot_id, name):
        """Donner un nom à son robot"""
        names = []
        print("Log : tentative nommage %s robot pour %s"%(name,robot_id))
        for robot in self.robots.values():
            names.append(robot.name)

        if(name not in names):
            if(robot_id in self.robots):
                self.robots[robot_id].name = name
                print("Log : nommage réussi %s robot pour %s"%(name,robot_id))
                return self.RESPONSE["SUCCESS_ROBOT"]
            else:
                print("Log-Err : identifiant robot invalide."%(name,robot_id))
                return self.RESPONSE["ERROR_ROBOT"]
        else:
            print("Log-Err : nommage %s déjà existant pour un robot (Client-Erreur :%s)."%(name,robot_id))
            return self.RESPONSE["ERROR_ROBOT_NAME"]

    def bool_all_robot_named(self):
        """Retourne true si tous les robots ont un nom"""
        if(len(self.robots) > 1):
            for robot in self.robots.values():
                if(robot.name == ""): return False
        return True

    def parse_command(self, commande, robot_id):
        """
        >Méthode qui analyse une commande et effectue l'action
        >Retourne un code ERREUR/SUCCES
        """
        # Partie 1 de la commande E74 (par exemple) : E
        retour = self.RESPONSE["ERROR_ACTION"]

        action = commande[0].upper()
        if(action not in ["M", "P", "O", "N", "E", "S"]): 
            return self.RESPONSE["ERROR_ACTION"]
        
        # Partie 2 du déplacement E74 par exemple : 74
        if(action == "M"):
            direction = commande[1].upper()
            pos_x, pos_y = self.robots[robot_id].position
            if(direction == "O"):
                retour = self._make_wall(pos_x, pos_y-1)
            elif(direction == "E"):
                retour = self._make_wall(pos_x, pos_y+1)
            elif(direction == "N"):
                retour = self._make_wall(pos_x-1, pos_y)
            elif(direction == "S"):
                retour = self._make_wall(pos_x+1, pos_y)
            else:
                return self.RESPONSE["ERROR_ACTION"]
        elif(action == "P"):
            direction = commande[1].upper()
            pos_x, pos_y = self.robots[robot_id].position
            if(direction == "O"):
                retour = self._make_door(pos_x, pos_y-1)
            elif(direction == "E"):
                retour = self._make_door(pos_x, pos_y+1)
            elif(direction == "N"):
                retour = self._make_door(pos_x-1, pos_y)
            elif(direction == "S"):
                retour = self._make_door(pos_x+1, pos_y)
            else:
                return self.RESPONSE["ERROR_ACTION"]
        else: # O E N S
            retour = self.RESPONSE["ERROR_ACTION"]
            pos_x, pos_y = self.robots[robot_id].position
            if(action == "O"): 
                retour = self._move_robot(robot_id, pos_x, pos_y-1)
            elif(action == "E"): 
                retour = self._move_robot(robot_id, pos_x, pos_y+1)
            elif(action == "N"): 
                retour = self._move_robot(robot_id, pos_x-1, pos_y)
            elif(action == "S"): 
                retour = self._move_robot(robot_id, pos_x+1, pos_y)

        self.save_map()
        return retour


    # _Private :
    def _move_robot(self, robot_id, pos_x, pos_y):
        
        try:
            test = self.current_map[pos_x][pos_y]
        except ValueError:
            print("Le robot essaie de sortir de la carte.")
            return self.RESPONSE["ERROR_ACTION"]

        if(self.current_map[pos_x][pos_y] == self.COMPONENT["O"]):
            return self.RESPONSE["STOP_WALL"]
        elif(self.current_map[pos_x][pos_y] == self.COMPONENT["U"]):
            self.victory = True
            print("Victoire!!!")
            return self.RESPONSE["VICTORY"]
        else: # "x" ou "." ou " "
            self.robots[robot_id].pos_x = pos_x
            self.robots[robot_id].pos_y = pos_y
            return self.RESPONSE["SUCCESS_MOVE"]


    def _make_wall(self, pos_x, pos_y):
        if(self.current_map[pos_x][pos_y] == self.COMPONENT["."]):
            self.current_map[pos_x][pos_y] = self.COMPONENT["O"]
            return self.RESPONSE["SUCCESS_CREATE_WALL"]
        else:
            return self.RESPONSE["ERROR_ACTION"]

    def _make_door(self, pos_x, pos_y):
        if(self.current_map[pos_x][pos_y] == self.COMPONENT["O"]):
            self.current_map[pos_x][pos_y] = self.COMPONENT["."]
            return self.RESPONSE["SUCCESS_CREATE_DOOR"]
        else:
            return self.RESPONSE["ERROR_ACTION"]

    def display(self, robot_id):
        """ Retourne une chaine de caractères du labyrinthe, 
        s'adapte en fonction de quel robot demande l'affichage """

        content = ""
        tmp_list = deepcopy(self.current_map) 
        # Une deepcopy parce que sinon les deux objets ont la même référence
        # J'ai même essayé tmp_list = list(self.current_map) et self.current_map[:]

        # Affiche les robots en fonction de leurs positions
        for id_robot in self.robots:
            pos_x, pos_y = self.robots[id_robot].position
            if(robot_id == id_robot):
                tmp_list[pos_x][pos_y] = self.COMPONENT["X"]
            else:
                # On évite d'afficher les ennemis qui sont sur la même case que nous, on préfère afficher notre robot à nous
                if(tmp_list[pos_x][pos_y] != self.COMPONENT["X"]): 
                    tmp_list[pos_x][pos_y] = self.COMPONENT["x"]
        
        # Affiche les caractères
        i = 0
        j = 0
        while(i < len(tmp_list)):
            while(j < len(tmp_list[i])):
                content += tmp_list[i][j]
                j += 1
            content += "\n"
            j = 0
            i += 1
        return content
