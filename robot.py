# -*-coding:Utf-8 -*


class Robot:    
    """Classe représentant un robot. Ici c'est un peu l'équivalent d'un utilisateur"""
    def __init__(self, name="", x=0, y=0):
        self.name = name
        self.pos_x = x
        self.pos_y = y
        self.previous_component = " "

    @property
    def position(self):
        return self.pos_x, self.pos_y
    

