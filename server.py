# -*-coding:utf-8 -*
import os
import re
import time
import random
import socket
import select
from maze import Maze

class MazeServer:
    """Classe représentant le serveur"""
    MSG_LENGTH = 2048

    def __init__(self, host='localhost', port=12555):
        self.port = port
        self.host = host
        self.maze = Maze()
        self.map_chosed = False
        self.connected_clients = []
        self.start()

    def start(self):
        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind((self.host, self.port))
        self.main_connection.listen(5)
        print("Serveur opérationnel sur {0}:{1}...".format(self.host, self.port))
        self.wait_for_clients()

    def wait_for_clients(self):
        """Attend que tous les clients soient connectés (au moins 2)"""
        map_chosed = False          # Assure que la carte a été choisie
        nicknames_picked = False    # Assure que tous les joueurs on choisi un pseudo (self.maze.robots[all].name != "")
        game_startable = False      # Assure que le jeu peut être lancé (au moins 2 joueurs, personne en attente de connection)
        # Permet de sortir de la boucle de préparation

        # Expressions régulière pour parser les messages clients
        re_number = r"^[1-9][0-9]*$"
        re_nickname = r"^[a-zA-Z0-9\-_éèïöüûîôâê]{3,}$" 
        # Au moins 3 caractères (chiffres/lettres/-_ Ex : "kévin-le-débile", "Killer_du36", "D4RK-D43M0N" ...)

        while(not game_startable):
            connections_requested, wlist, xlist = select.select([self.main_connection], [], [], 0.05)
            for connection in connections_requested:
                client_connection, info = connection.accept()

                id_client = "%s:%s"%(client_connection.getpeername())
                print("SERVEUR : connexion du client <<%s>>"%id_client)
                self.maze.set_robot(id_client)

                self.connected_clients.append(client_connection) # Joueur 1 est self.connected_clients.append[0] etc.
                self.send_display(client_connection, "Bienvenue sur le serveur du labyrinthe !")
                time.sleep(0.5)
                self.send_to_all_other_clients(client_connection, "Connexion du joueur n°%s"%(len(self.connected_clients)))
                
                if(self.connected_clients[0] == client_connection):
                    self.send_request(client_connection, self.select_map())
                else:
                    self.send_request(client_connection, 'Choisissez un nom pour votre robot (3 caractères min):')
                    nicknames_picked = False

            try:
                to_read_clients, wlist, xlist = select.select(self.connected_clients, [], [], 0.05)
            except select.error:
                pass
            else:
                for client in to_read_clients:
                    # Reponse client : soit son nom de robot, soit le nom de carte, soit début du jeu
                    received_message = client.recv(self.MSG_LENGTH).decode() # Taille de 1024
                    id_client = "%s:%s"%(client.getpeername())
                    print("SERVEUR : Requête de <%s> : %s"%(id_client, received_message))

                    # Si la map n'est pas encore choisie et on est avec client1 : on prend sa réponse
                    if(self.connected_clients[0] == client and not map_chosed): # Si carte pas encore choisie
                        if(re.search(re_number, received_message)):
                            liste = self.maze.get_map_list()
                            numero_carte = abs(int(received_message))
                            if(numero_carte <= len(liste)):
                                self.maze.load_map(liste[int(received_message)-1][1])
                                self.send_to_all_clients("Carte chargée par le joueur 1 : (%s)"%(liste[int(received_message)-1][1]))
                                self.send_request(client, "Maintenant, choisissez un nom pour votre robot :")
                                map_chosed = True
                            else:
                                self.send_request(client, ("Erreur : Il n'y a pas de carte à ce numéro :\n"+self.select_map()))
                        else:
                            self.send_request(client, "Erreur : entrez un numéro :")
                    else:
                        if(not nicknames_picked):
                            # Les joueurs 2 et + arrivent ici directement (contrairement au 1 qui choisit la carte)
                            if(self.maze.robots[id_client].name == "" and re.search(re_nickname, received_message)):
                                retour = self.maze.set_robot_name(id_client, received_message)
                                print(retour)
                                if(retour[:3] == "ERR"):
                                    self.send_request(client, retour)
                                else:
                                    self.send_request(client, retour.split('|',1)[1])
                            else: # Autre joueur, en attente
                                self.send_request(client, "Un nom correct pour votre robot (3 caractères min): ")

                            # Si tous les robots ont un nom et il y a au moins deux robots
                            if(self.maze.bool_all_robot_named() and len(self.maze.robots) >= 2):
                                nicknames_picked = True
                                self.send_to_all_clients("Entrez 'c' pour démarrer :", request=True)
                            else:
                                self.send_request(client, "En attente d'autres joueurs...")
                        else:
                            if(nicknames_picked and map_chosed and received_message.upper() == "C"):
                                game_startable = True
                            else:
                                self.send_request(client, "Entrez 'c' pour démarrer :")
        self.run()


    def run(self):
        """Le jeu est lancé"""
        game_running = True
        # Placer les robots : on ne pouvait pas avant car c'est en fonction de la carte chargée
        for client in self.connected_clients:
            id_client = "%s:%s"%(client.getpeername())
            self.maze.place_robot(id_client)
        self.send_maze_to_all()
        self.send_to_all_clients(self.maze.regles)
        time.sleep(0.5) # Obligé sinon le server.recv du client empile les retours et c'est moche

        # Decider qui commence
        self.whose_turn = random.randint(0, len(self.connected_clients)-1)
        id_client = "%s:%s"%(self.connected_clients[self.whose_turn].getpeername())
        
        self.send_to_all_clients("C'est le joueur %s qui commence : %s"%(self.whose_turn+1, self.maze.robots[id_client].name), request=True)
        # Le 1er a request ; les autres display
            
        while(game_running):
            
            # Liste des clients "qui ont quelque chose à dire" en attente d'être lus par le serveur
            to_read_clients = []
            try:
                to_read_clients, wlist, xlist = select.select(self.connected_clients, [], [], 0.05)
            except select.error:
                # En cas de liste vide, va boucler en attendant qu'un client agisse
                pass 
            else:
                for client in to_read_clients:
                    command = client.recv(1024).decode() 
                    id_client = ("%s:%s"%(client.getpeername()))
                    print("Reçu : %s ==> %s"%(id_client, command))
                    
                    if(command == "/quit"):
                        self.send_to_all_clients("Joueur %s %s s'est déconnecté."%(self.connected_clients.index(client)+1, self.maze.robots[id_client].name), request=True)
                        del self.maze.robots[id_client]
                        # Si c'était à son tour de jouer, on donne le tour au suivant
                        if(self.whose_turn == self.connected_clients.index(client)):
                            self.connected_clients.remove(client)
                            self.next(quit=True)
                        try: 
                            client.close()
                        except: 
                            pass                            
                    elif(command == "/rules"):
                        self.send_display(client, self.maze.regles)
                        if(self.whose_turn == self.connected_clients.index(client)):
                            self.send_request(client, "À votre tour de jouer :")
                        else:
                            self.send_request(client, "Ce n'est pas encore à votre tour de jouer.")
                    else:
                        # Si c'est à son tour de jouer
                        if(self.whose_turn == self.connected_clients.index(client)):
                            retour = self.maze.parse_command(command, id_client)
                            if(retour[:7] == "VICTORY"):
                                self.send_to_all_clients("VICTOIRE DE %s !!!"%(self.maze.robots[id_client].name), request=True)
                                game_running = False
                                self.close()
                            elif(retour[:6] != "SUCCES"):
                                self.send_request(client, "Action impossible, recommencez :")
                            else:
                                self.send_maze_to_all()
                                self.send_to_all_other_clients(client, "Robot %s à joué : %s"%(self.maze.robots[id_client].name, command.upper()))
                                self.send_display(client, "Vous avez joué : %s"%(command.upper()))
                                self.next()
                                time.sleep(0.2)
                                self.send_to_all_other_clients(self.connected_clients[self.whose_turn], "Au joueur %s de jouer..."%str(self.whose_turn+1))
                                self.send_request(self.connected_clients[self.whose_turn], "À votre tour %s :"%self.maze.COMPONENT["X"])
                        else:
                            self.send_request(client, "Ce n'est pas à votre tour de jouer.")


    def next(self, quit=False):
        if(self.whose_turn < len(self.connected_clients)-1):
            if(not quit): self.whose_turn += 1
        else:
            self.whose_turn = 0

    def select_map(self):
        """Factorisation code"""
        cartes = self.maze.get_map_list()
        msg_o_client = "Cartes disponibles sur le serveur : \n"
        for i, carte in enumerate(cartes):
            msg_o_client += "{} - {}\n".format(i + 1, carte[0])
        msg_o_client += "Entrez le numéro de la carte : "
        return msg_o_client
    
    def send_maze_to_all(self):
        if(len(self.connected_clients) > 0):
            for client in self.connected_clients:
                id_client = "%s:%s"%(client.getpeername())
                self.send_request(client, self.maze.display(id_client))
        

    def send_to_all_clients(self, message, request=False):
        """ Permet la mise en forme d'un message destiné à l'affichage chez les clients """
        if(len(self.connected_clients) > 0):
            for client in self.connected_clients:
                if(request):
                    self.send_request(client, message)
                else:
                    self.send_display(client, message)


    def send_to_all_other_clients(self, excepted_client, message, request=False):
        """ Permet la mise en forme d'un message destiné à l'affichage chez les clients (sauf un client, celui qui agit sur le serveur à priori) """
        if(len(self.connected_clients) > 0):
            for client in self.connected_clients:
                if(excepted_client != client):
                    if(request):
                        self.send_request(client, message)
                    else:
                        self.send_display(client, message)

    def send_request(self, client, message):
        """ Permet la mise en forme d'un message destiné à une requête chez le client (le client saura qu'il doit répondre) """
        self._send_to_one_client(client, "REQUEST_FROM_SERVER|"+message)

    def send_display(self, client, message):
        """ Permet la mise en forme d'un message destiné à l'affichage chez le client """
        self._send_to_one_client(client, "DISPLAY|"+message)

    # _Private
    def _send_to_one_client(self, client, message):
        """ Seule fonction qui doit répondre au client, toutes les fonctions d'envoi arrivent ici """
        if(len(self.connected_clients) > 0):
            client.send(message.encode())


    def close(self):
        """Ferme le serveur : avertit tous les clients et ferme les connexions, puis ferme le serveur"""
        print("Fermeture des connexions clientes...")
        for client in self.connected_clients:
            try:
                self._send_to_one_client(client, 'SERVER_SHUTDOWN|Fermeture du serveur.\nEntrée pour fermer la console')
                time.sleep(0.5)
                print("Déconnection de : %s:%s..."%(client.getpeername()))
                client.close()
            except:
                pass
        print("Fermeture de la connexion serveur principale.")
        self.main_connection.close()


serveur = MazeServer()