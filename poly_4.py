import tkinter as tk
import numpy as np

class Plateau:
    ## @brief Initialisation du plateau de puissance 4
    ## @param lignes Nombre de lignes du plateau
    ## @param colones Nombre de colones du plateau
    ## @param win conditon du tableau, nbr de jeton qu'il faut alligner
    def __init__(self, lignes, colones, win_conditon):
        self.l = lignes ## nombre de lignes <=> hauteur d'uen colone
        self.c = colones
        self.win = win_conditon
        self.matrice = np.zeros((lignes, colones), dtype = int)
        self.fill_matrice = np.zeros((colones), dtype = int)
        self.bitboards = [0, 0] ## @brief bitboards[0] -> celle de l'ordi, bitboards[1]-> celle du joueur
        ## Une bitboard est un nombre binaire, qui représente le plateau de jeu "applatie", avec 1 un jeton et 0 jetons enemmie, ou rien

    def add_coup_bitboard(self, pos):
        hauteur = self.l + 1 ## ajout d'un zero a la fin de chaque colone en guise de "mur" 
        self.bitboards[pos[2]] = self.bitboards[pos[2]] | (1 << (pos[1] + hauteur*pos[0]) )

    ## @brief Permet l'affichage du plateau et de ca matrice de remplissage qui indique le nombre de jeton jouer sur cette colonnes
    def print_tab(self):
        print(self.matrice)
        print(self.fill_matrice)


    ## @brief Joue sur la colone play_colone
    ## @param joueur 1 ou 2 celon le joueur (Peut etre d'autre chiffre celon les bonus, ...)
    ## @return !!!!!! Return 1 si ca peut pas jouer, et return (ligne, colone, num du joueur) si c'est ok et ca joue !!!!!!!
    def play(self, play_colone, joueur):
        ## @breif joue en [(hauteur de la matrice)-(le nombre de jeton sur cette colone)][colone ou c'est jouer]
        if joueur == 2 : j = 0 
        else : j = joueur
        if (play_colone < self.c and play_colone >= 0):
            if (self.fill_matrice[play_colone] < self.l) :
                self.matrice[(self.l - 1) - self.fill_matrice[play_colone]][play_colone] = joueur
                ## @brief modifie la matrice de remplicage en ajoutant le coup jouer 
                self.fill_matrice[play_colone] += 1
                print("Le coup est en (", self.fill_matrice[play_colone] - 1,",", play_colone,") du joueur :", joueur)
                
                self.add_coup_bitboard((self.fill_matrice[play_colone] - 1 , play_colone, j)) ## modifi la bitbord du joeuur en même temps
                return (self.fill_matrice[play_colone] - 1 , play_colone, joueur)
        return 1


    def check_win_bitboard(self, joueur):
        ## @brief chack vers le bas
        H = self.l +1
        directions = [1, H, H+1, H-1 ]
        for d in directions:
            bb = self.bitboards[joueur]
            for i in range(self.win - 1):
                bb = bb & (bb >> d)

            if bb != 0:
                return True
        return False


            
        
game = Plateau(5,4,4)
joueur = 1
while not(game.check_win_bitboard(1)):
    print(game.matrice)
    next = int(input())
    game.play(next, joueur)
    if joueur == 1:
        joueur = 2
    else : joueur = 1
print(game.matrice)




"""while game.check_win()[0] == 0:
    print(game.matrice)
    next = int(input())
    game.play(next, joueur)
    if joueur == 1:
        joueur = 2
    else : joueur = 1
    

if game.check_win()[0] == 0:
    print("Pas de gagnant")
else : 
    print("Le joueur", game.check_win()[1], "a gagner")
game.print_tab()"""

