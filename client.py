# -*-coding:Utf-8 -*
import socket
import time
from threading import Thread, RLock


class MazeClient(Thread):

    def __init__(self, host='localhost', port=12555):
        Thread.__init__(self)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.command = ""
        self.code_return = ""
        self.thread_input = False
        self.verrou = RLock()
        # Création des threads associés aux deux fonctions en lien avec le serveur
        Thread(target=self.run_output).start()
        Thread(target=self.run_input).start()

    def run_input(self):
        while self.command != "/quit" and self.code_return != "SERVER_SHUTDOWN":
            try:
                if(self.thread_input): # If it's my turn, server let me know with its code for request
                    self.command = input("")
                    self.server.send(self.command.encode())
                    with self.verrou:
                        self.thread_input = False
            except:
                pass
        self.close()

    def run_output(self):
        while self.command != "/quit" and self.code_return != "SERVER_SHUTDOWN":
            try:
                msg_recv = self.server.recv(2048).decode()
                self.code_return = msg_recv.split('|', 1)[0]
                
                message = msg_recv.split('|', 1)[1]
                print(message)

                if(not self.thread_input and self.code_return == "REQUEST_FROM_SERVER"):
                    with self.verrou:
                        self.thread_input = True
            except:
                pass
            time.sleep(0.1)

    def close():
        print("Fermeture de la connexion...")
        self.server.close()



client = MazeClient()




