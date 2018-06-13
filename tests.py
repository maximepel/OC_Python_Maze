# -*-coding:utf-8 -*
import os
import random
import unittest
from copy import deepcopy

from maze import Maze

class MazeTests(unittest.TestCase):

    def setUp(self):
        """Méthode appelée avant chaque test"""
        self.maze = Maze()

    def test_get_map_list(self):
        """ Teste la fonction qui retourne la liste des cartes """
        liste_maze = self.maze.get_map_list()
        self.maps_directory = "cartes"
        
        liste = []
        for nom_fichier in os.listdir(self.maps_directory):
            if nom_fichier.endswith(".txt"):
                chemin = os.path.join(self.maps_directory, nom_fichier)
                nom_carte = nom_fichier[:-4] ## Retire l'extension
                liste.append([nom_carte, chemin])
        # S'il n'y a pas de carte, on en génère une nouvelle avec un fichier :
        if(len(liste) == 0):
            liste.append(self._generate_base_map())

        self.assertEqual(liste_maze, liste)

    def test_load_map(self):
        """ load_map prend un chemin de fichier en paramètre et crée le labyrinthe en fonction """
        with open("cartes/atest.txt", 'r') as file:
            lignes = file.read().split("\n")
        current_map = []
        i=0
        j=0
        while(i < len(lignes)):
            if(lignes[i] != ""): 
                j = 0
                ligneTmp = []
                while(j < len(lignes[i])):                    
                    if(lignes[i][j] in self.maze.COMPONENT):
                        if(lignes[i][j] in [" ", "X", "x"]):
                            ligneTmp.append(self.maze.COMPONENT[" "]) # Si c'est un robot X/x, on le retire de la carte
                        else:
                            ligneTmp.append(self.maze.COMPONENT[lignes[i][j]])
                    else: 
                        ligneTmp.append(self.maze.COMPONENT[" "])
                    j+=1
                current_map.append(ligneTmp)
            i+=1
        self.maze.load_map("cartes/atest.txt")

        self.assertEqual(self.maze.current_map, current_map)


    def test_set_robot(self):
        """ Teste création robot et nommage """
        self.maze.load_map("cartes/atest.txt") # Pour avoir les places disponibles

        self.maze.set_robot("Paul") # Paul c'est l'identifiant
        self.maze.set_robot_name("Paul", "Jean-Claude")
        self.assertEqual(self.maze.robots["Paul"].name, "Jean-Claude")
        self.assertEqual(("Paul" in self.maze.robots), True)

    def test_place_robot(self):
        """ Teste placement robot """
        self.maze.load_map("cartes/atest.txt") # Pour avoir les places disponibles
        self.maze.set_robot("Paul") # Paul c'est l'identifiant
        positions_possibles = deepcopy(self.maze.positions_depart)
        self.maze.place_robot("Paul")
        paul_pos_x, paul_pos_y = self.maze.robots["Paul"].position

        self.assertIn([paul_pos_x, paul_pos_y], positions_possibles)

    def test_bool_all_robot_named(self):
        """ S'assure que tous les robots ont un nom, c'est une étape importante pour chaque naissance... """
        self.maze.robots = {}        
        self.maze.set_robot("id1") 
        self.maze.set_robot_name("id1", "Jean-Claude")
        
        self.maze.set_robot("id2") # Pas nommé encore
        self.assertEqual(False, self.maze.bool_all_robot_named())

        self.maze.set_robot_name("id2", "Jean-Peuplu_de_ces_tests")
        self.assertEqual(True, self.maze.bool_all_robot_named())



unittest.main()