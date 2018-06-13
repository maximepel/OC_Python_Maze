## OC_Python_Maze
Ceci est un exercice en python du cours openclassrooms. Il s'agissait de créer un ensemble Server-Client permettant de jouer à faire parcourir un labyrinthe à un robot.
Le jeu est très conceptuel et n'est présenté qu'en mode console pour l'instant car en faire une interface graphique serait un projet trop ambitieux pour le moment.

# Exemple :
![Image du jeu en mode console](https://gyazo.com/3a9689cfbcaa4addee83c674e9cdce88)
- Le X étant votre joueur, les petits x ceux des autres joueurs
- Les O étant les murs
- Le U étant la sortie à atteindre
- Les . étant des portes
- Les commandes sont S N E O (Sur Nord Est, Ouest)

# Modification du visuel :
J'ai changé les caractères par rapport à ce qui était demandé dans l'exercice.
Ainsi les murs sont des "█", les portes des "░", la sortie est un "♥", son propre robot est "☻" et les ennemis sont des "☺".
J'ai fait en sorte que le programme puisse tout de même parser des fichiers texte basiques pour creer ses propres cartes personnalisées en utilisant les caractères d'origine de l'exercice.
