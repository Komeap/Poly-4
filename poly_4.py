import tkinter as tk
import numpy as np

class Plateau:
    ## @brief Initialisation du plateau de puissance 4
    ## @param lignes Nombre de lignes du plateau
    ## @param colones Nombre de colones du plateau
    ## @param win conditon du tableau, nbr de jeton qu'il faut alligner
    def __init__(self, lignes, colones, win_conditon):
        self.l = lignes
        self.c = colones
        self.win = win_conditon
        self.matrice = np.zeros((lignes, colones), dtype = int)
        self.fill_matrice = np.zeros((colones), dtype = int)


    ## @brief Permet l'affichage du plateau et de ca matrice de remplissage qui indique le nombre de jeton jouer sur cette colonnes
    def print_tab(self):
        print(self.matrice)
        print(self.fill_matrice)


    ## @brief Joue sur la colone play_colone
    ## @param joueur 1 ou 2 celon le joueur (Peut etre d'autre chiffre celon les bonus, ...)
    ## @return !!!!!! Return 1 si ca peut pas jouer, et 0 si c'est ok et ca joue
    def play(self, play_colone, joueur):
        ## @breif joue en [(hauteur de la matrice)-(le nombre de jeton sur cette colone)][colone ou c'est jouer]
        if (self.fill_matrice[play_colone] < self.l ) :
            self.matrice[(self.l - 1) - self.fill_matrice[play_colone]][play_colone] = joueur
            ## @brief modifie la matrice de remplicage en ajoutant le coup jouer 
            self.fill_matrice[play_colone] += 1
            return 0
        else :
            return 1


    ## @brief Verifie si le joueur a gagner 
    ## @return (booleen win, le joueur qui a gagner) -> (0,-1): pas de gagant // (1, 1): le joueur 1 a gagner // (1, 2): le joueur 2 a gagner
    def check_win(self):
        ## @brief Check la conditon de victoire sur les colones
        for i in range(self.c) :
            nbr_a_la_suite = 0
            nbr_rechercher = -1
            for j in range(self.l) :
                #print("Je check la case ",j," ",i)
                if nbr_rechercher == -1 or nbr_rechercher == 0:
                        nbr_rechercher = self.matrice[j][i]
                if nbr_rechercher == self.matrice[j][i] and self.matrice[j][i] != 0:
                    nbr_a_la_suite += 1
                elif nbr_rechercher != self.matrice[j][i]:
                    nbr_rechercher = self.matrice[j][i]
                    nbr_a_la_suite = 1
                if nbr_a_la_suite == self.win :
                    return (1, nbr_rechercher)
        
        ## @brief Check la conditon de victoire sur les lignes
        for j in range(self.l) :
            nbr_a_la_suite = 0
            nbr_rechercher = -1
            for i in range(self.c) :
                #print("Je check la case ",j," ",i)
                if nbr_rechercher == -1 or nbr_rechercher == 0:
                        nbr_rechercher = self.matrice[j][i]
                if nbr_rechercher == self.matrice[j][i] and self.matrice[j][i] != 0:
                    nbr_a_la_suite += 1
                elif nbr_rechercher != self.matrice[j][i]:
                    nbr_rechercher = self.matrice[j][i]
                    nbr_a_la_suite = 1
                if nbr_a_la_suite == self.win :
                    return (1, nbr_rechercher)
                    
        ## Faire le check en diagonale
        return (0, -1)



game = Plateau(4,4,3)
joueur = 1
while game.check_win()[0] == 0:
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
game.print_tab()

