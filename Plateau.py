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
        ## "0000" --> les 0 "mur" dans la bitboard (5 0)
        ## [0000]
        ## [0000] -> devient 10000 00000 00000 11000 (lecture en colone de gauche a droite)
        ## [1000]
        ## [1001]

        ## hauteur H, +1 pour le décalage de la bitboard
        self.H = self.l + 1

        ## un masque couvrant les bit utilise du plateau
        total_bits = self.c * self.H
        self.mask = (1 << total_bits) - 1
        
    
    ## @brief permet d'ajouter le coup a la bitbord du joueur
    ## @param pos = (colone , ligne, numéro du joueur)
    def add_coup_bitboard(self, pos):
        
        self.bitboards[pos[2]] = self.bitboards[pos[2]] | (1 << (pos[0] + (self.H * pos[1])) )
        ## ajoute a la bitbord du joueur le coup qui vient d'être ajouter
        ## l'operation | 'le ou binaire', ajoute un chiffre bianaire (met les 1 du deuxieme dans le permier si y'a un zero a la place)
        ## 1 << (pos[1] + hauteur*pos[0])  creer le chiffre binaire associé au coup qui vient d'etre jouer '<<' -> met un 1 en position x
        ## pos[1] -> décalage sur ligne , hauteur*pos[0] -> saute pos[0] colone

    ## @brief Joue sur la colone play_colone
    ## @param joueur 1 ou 2 celon le joueur (Peut etre d'autre chiffre celon les bonus, ...)
    ## @return !!!!!! Return 1 si ca peut pas jouer, et return (ligne, colone, num du joueur) si c'est ok et ca joue !!!!!!!
    def play(self, play_colone, joueur):
        ## @breif joue en [(hauteur de la matrice)-(le nombre de jeton sur cette colone)][colone ou c'est jouer]
        if joueur == 2 : j = 0 
        else : j = joueur
        if (play_colone < self.c and play_colone >= 0): ## si le coup est possible
            if (self.fill_matrice[play_colone] < self.l) : ## si la colone est pas pleine
                self.matrice[(self.l - 1) - self.fill_matrice[play_colone]][play_colone] = joueur
                ## @brief modifie la matrice et la matrice de remplicage eavec le coup jouer
                self.fill_matrice[play_colone] += 1
                #print("Le coup est en (", self.fill_matrice[play_colone] - 1,",", play_colone,") du joueur :", joueur)
                ## @brief modifi la bitboard avec une fonction précédente
                self.add_coup_bitboard((self.fill_matrice[play_colone] - 1 , play_colone, j)) ## modifi la bitbord du joeuur en même temps
                return (self.fill_matrice[play_colone] - 1 , play_colone, joueur)
        return 1

    def undo(self, play_colone):
        if (play_colone < self.c and play_colone >= 0): ## si le undo est possible
            if (self.fill_matrice[play_colone] > 0) : ## si la colone est pas vide
                self.matrice[(self.l - 1) - self.fill_matrice[play_colone] + 1][play_colone] = 0
                ## @brief modifie la matrice et la matrice de remplicage avec le coup enlever
                self.fill_matrice[play_colone] -= 1
                """
                ## @brief Exactement la meme chose que add bitboard mais l'opération est ^, ce qui retire le 1 de la bitboard au lieu de l'ajouter
                self.bitboards[1] = self.bitboards[1] ^ (1 << (play_colone + (self.l + 1)*(self.fill_matrice[play_colone])))
                self.bitboards[0] = self.bitboards[0] ^ (1 << (play_colone + (self.l + 1)*(self.fill_matrice[play_colone])))"""
                hauteur = self.l + 1
                ligne_actuelle = self.fill_matrice[play_colone]
                index = ligne_actuelle + (self.H * play_colone)
                
                # On retire le bit avec XOR (^)
                mask = 1 << index
                self.bitboards[1] ^= mask
                self.bitboards[0] ^= mask

        return 1

    def power_bomb(self, colone_cible):
        self.matrice[:, colone_cible] = 0 
        self.fill_matrice[colone_cible] = 0 # modifie la matrice
        
        H = self.l + 1 # modificationde la bitboard
        shift = colone_cible * H
        masque_colonne = ((1 << self.l) - 1) << shift
        
        masque_nettoyage = ~masque_colonne
        
        self.bitboards[0] = self.bitboards[0] & masque_nettoyage
        self.bitboards[1] = self.bitboards[1] & masque_nettoyage
        
        return 1 

    ## @brief Verifie si il y a une victoire
    ## Comment ca marche, Magic bitboard -> explication pour détection en ligne : 
    ## On prend notre bitboard on la décale de 1, et on compare les deux ex : 0110 devient 1100
    ## Pourquoi, si on compare on obtient 0100 signification on avait deux 1 a coté si on a 0 on avait pas de 1 a coté
    ## il suffit de fait cette opération de comparaison et de décalage le nombre de fois qu'on veut de chiffre a coté et si le chiffre est différent de 0 alors c'est good
    ## exemple 3 1 a cote 001110 -> 00110 -> 00010
    ## si on décale de H(hauteur) on obtient on verifie si deux 1 sont l'un sur l'autre
    ## si on decale de H + 1 -> au dessus décaler a droite -> diag /
    ## H - 1 -> diag \
    ## @param joueur le joueur pour le qu'elle on verifie si ca gagne
    def check_win_bitboard(self, joueur, win_cond):
        ## modification de la valeur joueur, car ici ceulement on a besoin de 1 ou 0 et pas 1ou 2
        if joueur == 2 : j = 0 
        else : j = joueur
        ## H taille d'une colone pour la bitboard taille + 1 ajout de la séparation entre colone
        H = self.l +1
        # différentes direction possible, pour verifie en ligne 
        directions = [1, H, H+1, H-1 ]
        for d in directions:
            bb = self.bitboards[j]
            for i in range(win_cond - 1):
                bb = bb & (bb >> d) ## 'et bianire' etape de "comparaison" des deuc bitboard décaler (bb >> d -> on décale de d) 

            if bb != 0:
                return True
        return False

