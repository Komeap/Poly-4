## @file bot_MinMax.py
## Fonctions d'implémentations d'un bot utilisant MinMax

from Plateau import Tplateau
import numpy as np
import multiprocessing
from random import *

def VictoireOuNul(oGrille, iJoueur):
    """
    @brief Vérifie l'état de la partie pour un joueur donné (Victoire ou nul)
    @param oGrille Plateau du jeu en cours
           iJoueur Humain ou bot 
    @return (True, 1) si victoire du joueur
            (True, 0) si match nul
            (False, -1) sinon
    """
    if CheckVictoireMatrice(oGrille, iJoueur):
        return (True, 1)
    if EstPleine(oGrille):
        return (True, 0)
    return (False, -1)

def EstPleine(oGrille):
    """
    @brief Vérifie si la grille est pleine (match nul)
    @param oGrille Plateau du jeu en cours
    @return True si la grille est pleine
            False sinon
    """
    return all(oGrille.tPLAfillMatrice[iCol] >= oGrille.iPLAlignes for iCol in range(oGrille.iPLAcolonnes))

def CheckVictoireMatrice(oGrille, iJoueur):
    """
    @brief Vérifie si joueur a gagné. Ici, nous n'utilisons pas les bitboards.
    @param oGrille Plateau du jeu en cours
           iJoueur Humain ou bot 
    @return True si le joueur a une victoire 
            False sinon
    """

    tMat = oGrille.tPLAmatrice
    iL, iC, iW = oGrille.iPLAlignes, oGrille.iPLAcolonnes, oGrille.iPLAwin

    # Horizontale
    for iR in range(iL):
        for iCol in range(iC - iW + 1):
            tWindow = tMat[iR, iCol:iCol+iW]
            if np.all(tWindow == iJoueur):
                return True
    # Verticale
    for iCol in range(iC):
        for iR in range(iL - iW + 1):
            tWindow = tMat[iR:iR+iW, iCol]
            if np.all(tWindow == iJoueur):
                return True
    # Diagonale \
    for iR in range(iL - iW + 1):
        for iCol in range(iC - iW + 1):
            if all(tMat[iR+i, iCol+i] == iJoueur for i in range(iW)):
                return True
    # Diagonale /
    for iR in range(iW - 1, iL):
        for iCol in range(iC - iW + 1):
            if all(tMat[iR-i, iCol+i] == iJoueur for i in range(iW)):
                return True
    return False


def QuelCoupMatrice(oGrille, iJoueur):
    """
    @brief Vérifie si il existe un coup gagnant immédiat pour joueur et le renvoit immédiatement si il existe. Ici, nous n'utilisons pas les bitboards.
    @param oGrille Plateau du jeu en cours
        iJoueur Humain ou bot 
    @return Renvoit le coup gagnant si il existe
            -1 sinon
    """
    for iCol in range(oGrille.iPLAcolonnes):
        if oGrille.tPLAfillMatrice[iCol] >= oGrille.iPLAlignes:
            continue
        oGrille.PLAplay(iCol, iJoueur)
        if CheckVictoireMatrice(oGrille, iJoueur):
            oGrille.PLAundo(iCol)
            return iCol
        oGrille.PLAundo(iCol)
    return -1

def CoupBloquant(oGrille, iAdversaire):
    """
    @brief Vérifie si il existe un coup gagnant immédiat pour adversaire et le renvoit immédiatement si il existe. Ici, nous n'utilisons pas les bitboards.
    @param oGrille Plateau du jeu en cours
        iJoueur Humain ou bot 
    @return Renvoit le coup permettant de bloquer l'adversaire si il existe
            -1 sinon
    """
    for iCol in range(oGrille.iPLAcolonnes):
        if oGrille.tPLAfillMatrice[iCol] >= oGrille.iPLAlignes:
            continue
        oGrille.PLAplay(iCol, iAdversaire)
        if CheckVictoireMatrice(oGrille, iAdversaire):
            oGrille.PLAundo(iCol)
            return iCol
        oGrille.PLAundo(iCol)
    return -1



def EvaluateWindow(tWindow, iJoueurMax, iJoueurMin):

    """
    @brief Évalue heuristiquement une fenêtre de 4 cases pour le MinMax.
    @param tWindow Liste/array de 4 entiers (0 = vide, 1 = humain, 2 = IA)
           iJoueur_max Entier du joueur à maximiser (ex. 2 pour l'IA)
           iJoueur_min Entier du joueur à minimiser (ex. 1 pour l'humain)
    @return Renvoit le score de la fenêtre (positif si favorable à joueur_max, négatif si favorable à joueur_min)
    """

    iScore = 0
    tWindow = list(tWindow)
    iCountMax = tWindow.count(iJoueurMax)
    iCountMin = tWindow.count(iJoueurMin)
    iCountEmpty = tWindow.count(0)

    # Opportunités / menaces
    if iCountMax == 4:
        iScore += 100000
    elif iCountMax == 3 and iCountEmpty == 1:
        iScore += 120
    elif iCountMax == 2 and iCountEmpty == 2:
        iScore += 15

    if iCountMin == 3 and iCountEmpty == 1:
        iScore -= 100
    elif iCountMin == 2 and iCountEmpty == 2:
        iScore -= 8

    return iScore

def ScorePosition(oGrille, iJoueurMax=2, iJoueurMin=1):
    """
    @brief Calcule le score heuristique global d'une position pour le MinMax.
    @param oGrille Plateau du jeu en cours
           iJoueurMax Joueur à maximiser (ex. 2 pour l'IA)
           iJoueurMin Joueur à minimiser (ex. 1 pour l'humain)
    @return Renvoit le score global (positif si favorable à joueur_max, négatif si favorable à joueur_min)
    """

    tMat = oGrille.tPLAmatrice
    iL, iC, iW = oGrille.iPLAlignes, oGrille.iPLAcolonnes, oGrille.iPLAwin
    iScore = 0

    # Bonus centre (favorise colonnes centrales)
    iCenter = iC // 2
    tCenterArray = tMat[:, iCenter]
    iScore += 3 * np.count_nonzero(tCenterArray == iJoueurMax)

    # Horizontal
    for iR in range(iL):
        for iCol in range(iC - iW + 1):
            tWindow = tMat[iR, iCol:iCol+iW].tolist()
            iScore += EvaluateWindow(tWindow, iJoueurMax, iJoueurMin)

    # Vertical
    for iCol in range(iC):
        for iR in range(iL - iW + 1):
            tWindow = tMat[iR:iR+iW, iCol].tolist()
            iScore += EvaluateWindow(tWindow, iJoueurMax, iJoueurMin)

    # Diagonale \
    for iR in range(iL - iW + 1):
        for iCol in range(iC - iW + 1):
            tWindow = [tMat[iR+i, iCol+i] for i in range(iW)]
            iScore += EvaluateWindow(tWindow, iJoueurMax, iJoueurMin)

    # Diagonale /
    for iR in range(iW - 1, iL):
        for iCol in range(iC - iW + 1):
            tWindow = [tMat[iR-i, iCol+i] for i in range(iW)]
            iScore += EvaluateWindow(tWindow, iJoueurMax, iJoueurMin)

    return iScore

# === MinMax (BASIQUE, SANS alpha-beta) ===

def ColonnesOrdonnees(oGrille):
    """
    @brief Génère la liste des colonnes jouables dans un ordre optimisé (centre → bords).
    @param oGrille Plateau du jeu en cours
    @return Renvoit la liste des indices de colonnes jouables, triées par priorité (centre en premier)
    """
    iC = oGrille.iPLAcolonnes
    iCentre = iC // 2
    tOrdre = []
    for iD in range(iC):
        iLeft = iCentre - iD
        iRight = iCentre + iD
        if 0 <= iLeft < iC:
            tOrdre.append(iLeft)
        if 0 <= iRight < iC and iRight != iLeft:
            tOrdre.append(iRight)
    return [iCol for iCol in tOrdre if oGrille.tPLAfillMatrice[iCol] < oGrille.iPLAlignes]

def Minmax(oGrille, iProfondeur, bMaximising=True):
    """
    @brief Calcule le score d'une position par MinMax sur la matrice.
    @param oGrille Plateau du jeu en cours
           iProfondeur Profondeur de recherche restante 
           bMaximising Booléen : True si c'est le tour du joueur à maximiser (IA=2), False sinon (humain=1)
    @return Renvoit le score évalué de la position (positif si favorable à l'IA, négatif si favorable à l'humain)
    """

    # États terminaux
    if CheckVictoireMatrice(oGrille, 2):
        return 1000000
    if CheckVictoireMatrice(oGrille, 1):
        return -1000000
    if EstPleine(oGrille) or iProfondeur == 0:
        return ScorePosition(oGrille, iJoueurMax=2, iJoueurMin=1)

    tCols = ColonnesOrdonnees(oGrille)
    if bMaximising:
        iBest = -10**9
        for iCol in tCols:
            oGrille.PLAplay(iCol, 2)
            iVal = Minmax(oGrille, iProfondeur - 1, bMaximising=False)
            oGrille.PLAundo(iCol)
            if iVal > iBest:
                iBest = iVal
        return iBest
    else:
        iBest = 10**9
        for iCol in tCols:
            oGrille.PLAplay(iCol, 1)
            iVal = Minmax(oGrille, iProfondeur - 1, bMaximising=True)
            oGrille.PLAundo(iCol)
            if iVal < iBest:
                iBest = iVal
        return iBest

def EvalCoup(tArgs):
    """Fonction pour multiprocessing"""
    oGrille, iCol, iProfondeur = tArgs
    oGrille.PLAplay(iCol, 2)
    iScore = Minmax(oGrille, iProfondeur - 1, bMaximising=False)
    oGrille.PLAundo(iCol)
    return iCol, iScore

def MeilleurCoup(oGrille, iProfondeur):
    """
    @brief Sélectionne le meilleur coup pour l'IA en priorisant: coup gagnant, blocage, puis MinMax. Pour l'algorithme Minmax, on utilise le multiprocesing.
    @param oGrille Plateau du jeu en cours
           iProfondeur Profondeur de recherche pour MinMax
    @return Renvoit l'index de la colonne choisie pour jouer (0..grille.c-1)
    """
    # 1) Coup gagnant immédiat
    iCg = QuelCoupMatrice(oGrille, 2)
    if iCg != -1:
        return iCg

    # 2) Blocage
    iCb = CoupBloquant(oGrille, 1)
    if iCb != -1:
        return iCb

    # 3) MinMax
    iBestScore = -10**9
    iBestCol = None

    tCols = ColonnesOrdonnees(oGrille)
    tArgsList = [(Tplateau(oGrille.iPLAlignes, oGrille.iPLAcolonnes, oGrille.iPLAwin), iCol, iProfondeur) for iCol in tCols]

    for i, iCol in enumerate(tCols):
            tArgsList[i][0].tPLAmatrice = oGrille.tPLAmatrice.copy()
            tArgsList[i][0].tPLAfillMatrice = oGrille.tPLAfillMatrice.copy()
            tArgsList[i][0].tPLAbitboards = oGrille.tPLAbitboards.copy()

    with multiprocessing.Pool(processes=min(len(tCols), multiprocessing.cpu_count())) as oPool :
        tResults = oPool.map(EvalCoup, tArgsList)

    iBestCol, iBestScore = max(tResults, key=lambda x : x[1])
    return iBestCol


##Il me reste ça refaire et à doxygen
def PartieVsBot(oGrille, iColones, sMode, iProfondeur=4):
    iJoueur = 1  # humain commence
    iBuffer = 0
    iNbCoups = 0
    #print("\n=== DÉBUT DE LA PARTIE ===\n")

    while True:
        # Affichage console
        for tLigne in oGrille.tPLAmatrice:
            print(" | ".join(str(x) for x in tLigne))
        print("-" * (oGrille.iPLAcolonnes * 4))

        # Tour du joueur humain
        if iJoueur == 1:
            iCol = input(f"\nÀ toi de jouer ! Choisis une colonne (0-{oGrille.iPLAcolonnes - 1}) : ")
            try:
                iCol = int(iCol)
            except ValueError:
                print("Entre un nombre valide.")
                continue
            if iCol < 0 or iCol >= oGrille.iPLAcolonnes:
                print("Colonne hors limites.")
                continue
            if oGrille.tPLAfillMatrice[iCol] >= oGrille.iPLAlignes:
                print("Colonne pleine.")
                continue

            oGrille.PLAplay(iCol, 1)

            bTerm, iEtat = VictoireOuNul(oGrille, 1)
            if bTerm:
                if iEtat == 1:
                    print("Victoire du joueur 1")
                elif iEtat == 0:
                    print("Match nul")
                break

        # Tour de l'IA
        else:
            print("\n IA réfléchit...")
            if sMode=="Normal" and iBuffer==1 :
                iCol = MeilleurCoup(oGrille, iProfondeur)
                if iNbCoups%3 == 0 :
                    iBuffer = 0
            elif sMode=="Normal" and iBuffer == 0 :
                iCol = randint(0, iColones)
                iBuffer = 1
            elif sMode=="Facile" and iBuffer==1 :
                iCol = MeilleurCoup(oGrille, iProfondeur)
                if iNbCoups%2 == 0 :
                    iBuffer = 0
            elif sMode=="Facile" and iBuffer == 0 :
                iCol = randint(0, iColones)
                iBuffer = 1
                
            else :
                iCol = MeilleurCoup(oGrille, iProfondeur)
            print(f"L'IA joue en colonne {iCol}")
            oGrille.PLAplay(iCol, 2)
            iNbCoups += 1
            bTerm, iEtat = VictoireOuNul(oGrille, 2)
            if bTerm:
                if iEtat == 1:
                    print("Victoire de l'IA")
                elif iEtat == 0:
                    print("Match nul")
                break
            
        # Alterner joueur
        iJoueur = 3 - iJoueur  # 1 ↔ 2

    #print("\n=== FIN DE PARTIE ===")

if __name__ == "__main__":
    oG = Tplateau(iLignes=6, iColonnes=7, iWinCondition=4)
    PartieVsBot(oG, iColones=6, sMode="Facile", iProfondeur=4)