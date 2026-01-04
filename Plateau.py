import numpy as np

class Tplateau:
    ## @brief Initialisation du plateau de puissance 4
    ## @param iLignes Nombre de lignes du plateau
    ## @param iColonnes Nombre de colones du plateau
    ## @param iWinCondition du tableau, nbr de jeton qu'il faut alligner
    def __init__(self, iLignes, iColonnes, iWinCondition):
        self.iPLAlignes = iLignes ## nombre de lignes <=> hauteur d'uen colone
        self.iPLAcolonnes = iColonnes
        self.iPLAwin = iWinCondition
        self.tPLAmatrice = np.zeros((iLignes, iColonnes), dtype=int)
        self.tPLAfillMatrice = np.zeros((iColonnes), dtype=int)
        self.tPLAbitboards = [0, 0]## @brief bitboards[0] -> celle de l'ordi, bitboards[1]-> celle du joueur
        ## Une bitboard est un nombre binaire, qui représente le plateau de jeu "applatie", avec 1 un jeton et 0 jetons enemmie, ou rien
        ## "0000" --> les 0 "mur" dans la bitboard (5 0)
        ## [0000]
        ## [0000] -> devient 10000 00000 00000 11000 (lecture en colone de gauche a droite)
        ## [1000]
        ## [1001]

        ## hauteur H, +1 pour le décalage de la bitboard
        self.iPLAh = self.iPLAlignes + 1

        ## un masque couvrant les bit utilise du plateau
        iTotalBits = self.iPLAcolonnes * self.iPLAh
        self.iPLAmask = (1 << iTotalBits) - 1
        
    
    ## @brief permet d'ajouter le coup a la bitbord du joueur
    ## @param tPos = (colone , ligne, numéro du joueur)
    def PLAaddCoupBitboard(self, tPos):
        self.tPLAbitboards[tPos[2]] = self.tPLAbitboards[tPos[2]] | (1 << (tPos[0] + (self.iPLAh * tPos[1])))
        ## ajoute a la bitbord du joueur le coup qui vient d'être ajouter
        ## l'operation | 'le ou binaire', ajoute un chiffre bianaire (met les 1 du deuxieme dans le permier si y'a un zero a la place)
        ## 1 << (pos[1] + hauteur*pos[0])  creer le chiffre binaire associé au coup qui vient d'etre jouer '<<' -> met un 1 en position x
        ## pos[1] -> décalage sur ligne , hauteur*pos[0] -> saute pos[0] colone

    ## @brief Joue sur la colone play_colone
    ## @param iJoueur 1 ou 2 celon le joueur (Peut etre d'autre chiffre celon les bonus, ...)
    ## @return !!!!!! Return 1 si ca peut pas jouer, et return (ligne, colone, num du joueur) si c'est ok et ca joue !!!!!!!
    def PLAplay(self, iPlayColone, iJoueur):
        ## joue en [(hauteur de la matrice)-(le nombre de jeton sur cette colone)][colone ou c'est jouer]
        if iJoueur == 2: iJ = 0 
        else: iJ = iJoueur
        
        if (iPlayColone < self.iPLAcolonnes and iPlayColone >= 0): ## si le coup est possible
            if (self.tPLAfillMatrice[iPlayColone] < self.iPLAlignes): ## si la colone est pas pleine
                self.tPLAmatrice[(self.iPLAlignes - 1) - self.tPLAfillMatrice[iPlayColone]][iPlayColone] = iJoueur
                ## modifie la matrice et la matrice de remplicage eavec le coup jouer

                self.tPLAfillMatrice[iPlayColone] += 1
                #print("Le coup est en (", self.fill_matrice[play_colone] - 1,",", play_colone,") du joueur :", joueur)
                ## @brief modifi la bitboard avec une fonction précédente

                self.PLAaddCoupBitboard((self.tPLAfillMatrice[iPlayColone] - 1 , iPlayColone, iJ))  ## modifi la bitbord du joeuur en même temps
                return (self.tPLAfillMatrice[iPlayColone] - 1 , iPlayColone, iJoueur)
        return 1

    def PLAundo(self, iPlayColone):
        if (iPlayColone < self.iPLAcolonnes and iPlayColone >= 0): ## si le undo est possible
            if (self.tPLAfillMatrice[iPlayColone] > 0): ## si la colone est pas vide 
                self.tPLAmatrice[(self.iPLAlignes - 1) - self.tPLAfillMatrice[iPlayColone] + 1][iPlayColone] = 0
                ## @brief modifie la matrice et la matrice de remplicage avec le coup enlever
                self.tPLAfillMatrice[iPlayColone] -= 1
                """
                ## @brief Exactement la meme chose que add bitboard mais l'opération est ^, ce qui retire le 1 de la bitboard au lieu de l'ajouter
                self.bitboards[1] = self.bitboards[1] ^ (1 << (play_colone + (self.l + 1)*(self.fill_matrice[play_colone])))
                self.bitboards[0] = self.bitboards[0] ^ (1 << (play_colone + (self.l + 1)*(self.fill_matrice[play_colone])))"""
                
                iHauteur = self.iPLAlignes + 1
                iLigneActuelle = self.tPLAfillMatrice[iPlayColone]
                iIndex = iLigneActuelle + (self.iPLAh * iPlayColone)
                
                # On retire le bit avec XOR (^)
                iMask = 1 << iIndex
                self.tPLAbitboards[1] ^= iMask
                self.tPLAbitboards[0] ^= iMask

        return 1

    def PLApowerBomb(self, iColoneCible):
        self.tPLAmatrice[:, iColoneCible] = 0 
        self.tPLAfillMatrice[iColoneCible] = 0 ## modifie la matrice
        
        iH = self.iPLAlignes + 1 # modificationde la bitboard
        iShift = iColoneCible * iH
        iMasqueColonne = ((1 << self.iPLAlignes) - 1) << iShift
        
        iMasqueNettoyage = ~iMasqueColonne
        
        self.tPLAbitboards[0] = self.tPLAbitboards[0] & iMasqueNettoyage
        self.tPLAbitboards[1] = self.tPLAbitboards[1] & iMasqueNettoyage
        
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
    ## @brief Verifie si il y a une victoire
    def PLAcheckWinBitboard(self, iJoueur, iWinCond):
        ## modification de la valeur joueur, car ici ceulement on a besoin de 1 ou 0 et pas 1ou 2   
        if iJoueur == 2: iJ = 0 
        else: iJ = iJoueur
        ## H taille d'une colone pour la bitboard taille + 1 ajout de la séparation entre colone
        iH = self.iPLAlignes + 1
        # différentes direction possible, pour verifie en ligne 
        tDirections = [1, iH, iH+1, iH-1]
        for iD in tDirections:
            iBb = self.tPLAbitboards[iJ]
            for i in range(iWinCond - 1):
                iBb = iBb & (iBb >> iD) ## 'et bianire' etape de "comparaison" des deuc bitboard décaler (bb >> d -> on décale de d) 
            if iBb != 0:
                return True
        return False