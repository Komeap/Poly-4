from tkinter_fonction import *
from bot2 import VictoireOuNul, MeilleurCoup
from Plateau import Tplateau
import threading
import random
import time
import os

# ------- Différentes page -------- #

## @brief class maitre qui gére les différentes pages
class Tapp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POLIC")
        ## Génération des taille de page
        iScreenWidth = self.winfo_screenwidth()
        iScreenHeight = self.winfo_screenheight()
        iXCordinate = int((iScreenWidth/2) - (iWIDTH/2))
        iYCordinate = int((iScreenHeight/2) - (iHEIGHT/2))
        ## iWIDTH et iHEIGHT valeur global
        self.geometry("{}x{}+{}+{}".format(iWIDTH, iHEIGHT, iXCordinate, iYCordinate))
        self.oAPPpageEnCours = None
        self.resizable(width=False, height=False)

    ## @brief Changement de page, supprime celle en cours
    ## et en met une autre sans oublier de redéfinir le self
    def APPchangerDePage(self, oPage, **dData):
        if self.oAPPpageEnCours:
            self.oAPPpageEnCours.destroy()

        self.oAPPpageEnCours = oPage(oParent=self, **dData)
        self.oAPPpageEnCours.pack(fill="both", expand=True)

## @brief Page d'accueil
class Tacceuil(tk.Frame):
    def __init__(self, oParent):
        super().__init__(oParent, bg="")

        self.oACCcanva = tk.Canvas(self, width=iWIDTH, height=iHEIGHT, highlightthickness=0, bg="grey")
        self.oACCcanva.pack(fill="both", expand=True)
        
        AddBackground(self.oACCcanva, "images/Acceuil.jpg")
        AddCanvasBouton(self.oACCcanva, "images/bouton_play.png", ((iWIDTH//4),iHEIGHT//6), (iWIDTH//2,(iHEIGHT//12)*11), lambda: oApp.APPchangerDePage(TparamJeu), True, 35)
        AddCanvasBouton(self.oACCcanva, "images/bouton_close.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), oApp.destroy, True, 20)

class TparamJeu(tk.Frame):
    def __init__(self, oParent, **dKwargs):
        super().__init__(oParent, bg="")

        # 1. Création du canva et background
        self.oPAJcanva = tk.Canvas(self, width=oParent.winfo_screenwidth(), height=oParent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.oPAJcanva.pack(fill="both", expand=True)
        AddBackground(self.oPAJcanva, "images/parametre_bg.png")

        dCONFIG_DATA = {
            "": [],
            "Win Condition": [i for i in range(3,50)],
            "Largeur": [i for i in range(4,50)], 
            "Hauteur": [i for i in range(4,50)],
            "Difficulté": ["Facile", "Normal", "Hardcore"],
            "Permier coup": ["bot", "joueur", "random"],
            "Bonus": ["nothing","bombe", "undo", "all"],
            "couleur joueur": ["cyan", "red", "orange", "yellow"],
            "couleur bot":["cyan", "red", "orange", "yellow"]
        }

        dDEFAUTS = {
            "Largeur": 7,          
            "Hauteur": 6,          
            "Win Condition": 4,    
            "Difficulté": "Normal",
            "Permier coup": "random",
            "Bonus": "nothing",
            "couleur joueur": "red",
            "couleur bot": "yellow"
        }

        self.oPAJmenu = TmenuDeroulant(self.oPAJcanva, iWIDTH//2, iHEIGHT//7, dCONFIG_DATA)
        self.oPAJmenu.MENscroll(1)

        for sCle, sValeur in dDEFAUTS.items():
            iIndexParDefaut = dCONFIG_DATA[sCle].index(sValeur)
            self.oPAJmenu.dMENchoices[sCle] = iIndexParDefaut


        AddCanvasBouton(self.oPAJcanva, "images/bouton_up.png", (50, 50), (iWIDTH//2 + 250, iHEIGHT//2 - 50), lambda: self.oPAJmenu.MENscroll(-1), True, 5)
        AddCanvasBouton(self.oPAJcanva, "images/bouton_down.png", (50, 50), (iWIDTH//2 + 250, iHEIGHT//2 + 50), lambda: self.oPAJmenu.MENscroll(1), True, 5)

        AddCanvasBouton(self.oPAJcanva, "images/bouton_back.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), lambda: oApp.APPchangerDePage(Tacceuil), True, 20)
        
        AddCanvasBouton(self.oPAJcanva, "images/boutonNext.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT) - iHEIGHT//10), self.PAJlancerPartie,True, 20)

    def PAJlancerPartie(self):
        
        # Récupération des choix
        dChoix = self.oPAJmenu.dMENchoices
        dConfig = self.oPAJmenu.dMENconfig
        
        # Conversion des choix
        iLargeur = dConfig["Largeur"][dChoix["Largeur"]]
        iHauteur = dConfig["Hauteur"][dChoix["Hauteur"]]
        iWinCond = dConfig["Win Condition"][dChoix["Win Condition"]]
        sNomCoulJ = dConfig["couleur joueur"][dChoix["couleur joueur"]]
        sNomCoulB = dConfig["couleur bot"][dChoix["couleur bot"]]
        sPremierC = dConfig["Permier coup"][dChoix["Permier coup"]]
        sBonus = dConfig["Bonus"][dChoix["Bonus"]]
        sNomDiff = dConfig["Difficulté"][dChoix["Difficulté"]]
        

        # Création du colis de données
        dParametres = {
            "largeur": iLargeur,
            "hauteur": iHauteur,
            "win": iWinCond,
            "diff": sNomDiff,
            "couleur_j": sNomCoulJ,
            "couleur_b": sNomCoulB,
            "premier_c" : sPremierC,
            "bonus" : sBonus
        }

        # Changement de page
        oApp.APPchangerDePage(Tjeu, **dParametres)

class Tjeu(tk.Frame):
    """!
    @brief Réprésente la page de jeu 
    """
    def __init__(self, oParent, **dSettings):
        super().__init__(oParent, bg="")

        self.iJEUnbCols = dSettings.get("largeur")
        self.iJEUnbLignes = dSettings.get("hauteur")
        self.iJEUwinCond = dSettings.get("win")
        self.sJEUdiff = dSettings.get("diff")
        self.sJEUcouleurIa = dSettings.get("couleur_b")
        self.sJEUcouleurJ = dSettings.get("couleur_j")
        self.sJEUpremierCoup = dSettings.get("premier_c")
        self.sJEUbonus = dSettings.get("bonus")
        self.iJEUprofondeur = 4

        self.iJEUbuffer = 1
        self.iJEUnbCoupsIa = 0

        # Gestion du premier tour
        if self.sJEUpremierCoup == "bot" : 
            self.iJEUjoueurActuel = 2
        elif self.sJEUpremierCoup == "joueur": 
            self.iJEUjoueurActuel = 1
        else : 
            self.iJEUjoueurActuel = random.randint(1,2)
        
        # Gestion des couleur, eviter deux fois la même
        if self.sJEUcouleurIa == self.sJEUcouleurJ :
            if self.sJEUcouleurJ == "yellow" :
                self.sJEUcouleurIa = "red"
            else :
                self.sJEUcouleurIa = "yellow"

        self.oJEUgrille = Tplateau(iLignes=self.iJEUnbLignes, iColonnes=self.iJEUnbCols, iWinCondition=self.iJEUwinCond)
        self.bJEUjeuActif = False # attendre l'affichage complet avant de lancer sinon ca bug 

        # Configuration UI
        self.oJEUcanvas = tk.Canvas(self, width=oParent.winfo_screenwidth(), height=oParent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.oJEUcanvas.pack(fill="both", expand=True)

        AddBackground(self.oJEUcanvas, "images/bg.jpg")
        
        # Boutons de navigation
        AddCanvasBouton(self.oJEUcanvas, "images/bouton_back.png", (iHEIGHT//10, iHEIGHT//10), ((iHEIGHT//10)//2 + 5, (iHEIGHT//10)//2 + 5), lambda: oApp.APPchangerDePage(TparamJeu), True, 20)
        AddCanvasBouton(self.oJEUcanvas, "images/bouton_close.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), oApp.destroy, True, 20)
        if self.sJEUbonus == "undo" or self.sJEUbonus == "all" :
            self.iJEUundo = AddCanvasBouton(self.oJEUcanvas, "images/undo_bonus.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8, iHEIGHT//2), self.JEUactionUndo, True, 20)
        if self.sJEUbonus == "bombe"  or self.sJEUbonus == "all": 
            self.iJEUbombe = AddCanvasBouton(self.oJEUcanvas, "images/bouton_bombe.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8 - iHEIGHT//8, iHEIGHT//2), self.JEUactiverModeBombe, True, 20)
            self.iJEUbombe_on = AddCanvasBouton(self.oJEUcanvas, "images/bouton_bombe_press.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8 - iHEIGHT//8, iHEIGHT//2), self.JEUactiverModeBombe, True, 20)
            self.oJEUcanvas.itemconfig(self.iJEUbombe_on, state='hidden')

        # Avatars
        AddCanvasImg(self.oJEUcanvas, "images/gentil_idle.png", (150, (int)(iHEIGHT*0.75)), ((int)(iHEIGHT*0.3), (int)(iHEIGHT*0.3)))
        AddCanvasImg(self.oJEUcanvas, "images/mechant_idle.png", ((int)(iWIDTH*0.85), (int)(iHEIGHT*0.75)), ((int)(iHEIGHT*0.35), (int)(iHEIGHT*0.35)))

        AfficherPlateau(self.oJEUcanvas, self.iJEUnbCols, self.iJEUnbLignes)

        self.iJEUflecheId = InitFleche(self.oJEUcanvas)
        self.oJEUcanvas.bind('<Motion>', lambda event: BougerFleche(event, self.oJEUcanvas, self.iJEUflecheId))
        self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)

        self.iJEUoverlayId = self.oJEUcanvas.create_rectangle(0, 0, iWIDTH, iHEIGHT, fill="black", stipple='gray50')
        
        self.tJEUpionsVisuels = [[] for i in range(self.iJEUnbCols)]
        self.tJEUhistoriqueCoups = []
        self.bJEUactiveBombe = False
        self.bJEUanimEnCours = False

        # Play
        self.iJEUbtnStartId = AddCanvasBouton(self.oJEUcanvas, "images/bouton_ready.png",(150, 150), (iWIDTH//6, iHEIGHT//2), self.JEUlancerLaGame,True, 20)

    def JEUlancerLaGame(self):
        """!
        @brief Pour lancer la partie de puissance 4
        """
        self.oJEUcanvas.delete(self.iJEUbtnStartId)
        if hasattr(self, 'iJEUoverlayId'):
            self.oJEUcanvas.delete(self.iJEUoverlayId)
        
        self.bJEUjeuActif = True
        self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)

        if self.iJEUjoueurActuel == 2: # lancer le tours du bot, avec un delay pour pas qu'il joue avant l'affichage
            self.oJEUcanvas.after(500, self.JEUtourBot)
    
    def JEUannulerUnSeulCoup(self):
        """!
        @brief Annule un seul coup, use in JEUactionUndo
        """
        if not self.tJEUhistoriqueCoups:
            return False

        iCol, iPionId = self.tJEUhistoriqueCoups.pop() # Récup l'id du pio a suppr
        self.oJEUcanvas.delete(iPionId)
        self.oJEUgrille.PLAundo(iCol)
        return True

    def JEUactionUndo(self):
        """!
        @brief suppr le bon nombre de jeton celon le cas
            Cas 1 partie encore en cours -> suppr deux jetons tours du joueur
            Cas 2 Fin, vicoire joueur -> suppr uniquement ke coup du joueur et relance le jeu
            Cas3 FIn, victoire du bot -> suppr deux jetons et relance le jeu  
        """
        if self.bJEUanimEnCours: 
            return

        if not self.tJEUhistoriqueCoups:
            return

        if self.bJEUjeuActif :
            self.JEUannulerUnSeulCoup()
            self.JEUannulerUnSeulCoup()
            self.iJEUjoueurActuel = 1

            self.JEUreactiverJeu()    
        else:
            if self.iJEUjoueurActuel == 2 :
                self.JEUannulerUnSeulCoup()
                self.JEUannulerUnSeulCoup()
                self.iJEUjoueurActuel = 1
            else :
                self.JEUannulerUnSeulCoup()
                self.iJEUjoueurActuel = 1
        
        self.JEUreactiverJeu()
        self.oJEUcanvas.delete(self.iJEUundo)
        # print("Retour Ok")

    def JEUreactiverJeu(self):
        """!
        @brief réactivation du jeu -> suppr les affichage de fin, et réactive le clic souris
        """
        self.bJEUjeuActif = True
        self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)
        self.oJEUcanvas.delete("message_fin")

    def JEUactiverModeBombe(self):
        """!
        @brief active le bonus bombe
        """
        if not self.bJEUjeuActif or self.iJEUjoueurActuel != 1:
            return

        self.bJEUactiveBombe = not self.bJEUactiveBombe 
        if self.bJEUactiveBombe :
            self.oJEUcanvas.itemconfig(self.iJEUbombe, state='hidden')
            self.oJEUcanvas.itemconfig(self.iJEUbombe_on, state='normal')
        else : 
            self.oJEUcanvas.itemconfig(self.iJEUbombe_on, state='hidden')
            self.oJEUcanvas.itemconfig(self.iJEUbombe, state='normal')
        
    def JEUlacherBombe(self, iCol):
        """!
        @brief Joue la bombe
        """
        if self.oJEUgrille.tPLAfillMatrice[iCol] == 0:
            self.bJEUmodeBombe = False
            return

        self.oJEUgrille.PLApowerBomb(iCol)

        for iPionId in self.tJEUpionsVisuels[iCol]:
            self.oJEUcanvas.delete(iPionId)
        
        self.tJEUpionsVisuels[iCol] = []

        self.tJEUhistoriqueCoups = [tCoup for tCoup in self.tJEUhistoriqueCoups if tCoup[0] != iCol]

        # Fin du tour
        self.bJEUactiveBombe = False
        self.oJEUcanvas.delete(self.iJEUbombe) ## suppr le bouton
        self.oJEUcanvas.delete(self.iJEUbombe_on)

        self.iJEUjoueurActuel = 3 - self.iJEUjoueurActuel ## Fait jouer le bot 
        if self.iJEUjoueurActuel == 2:
            self.oJEUcanvas.after(500, self.JEUtourBot)

    def JEUobtenirColonneAleatoire(self):
        """!
        @brief Prend une colone aléatoire, pour la gestion du niveau de bot
        """
        tColsValides = [c for c in range(self.oJEUgrille.iPLAcolonnes) if self.oJEUgrille.tPLAfillMatrice[c] < self.oJEUgrille.iPLAlignes]
        if tColsValides:
            return random.choice(tColsValides)
        return 0

    def JEUclicSouris(self, oEvent):
        """!
        @brief gére le clic souris, pour jouer un coup
        """
        if not self.bJEUjeuActif or self.iJEUjoueurActuel != 1:
            return

        dGridData = getattr(self.oJEUcanvas, 'grid_data', None)
        if not dGridData: return

        if dGridData['start_x'] <= oEvent.x <= dGridData['start_x'] + dGridData['largeur_totale']:
            iCol = int((oEvent.x - dGridData['start_x']) // dGridData['taille'])
            # trouve la colone jouer par rapport a la position de la souris
            if 0 <= iCol < self.oJEUgrille.iPLAcolonnes:
                if self.bJEUactiveBombe :
                    self.JEUlacherBombe(iCol) # joue la bombe
                else :
                    self.JEUjouerCoup(iCol) # joue normalement
    
    def JEUjouerCoup(self, iCol):
        """!
        @brief Joue un coup sur le plateau
        """
        if self.bJEUanimEnCours: return

        if self.oJEUgrille.tPLAfillMatrice[iCol] >= self.oJEUgrille.iPLAlignes: # Verifie si le coup est possible
            print("Erreur")
            return

        tRes = self.oJEUgrille.PLAplay(iCol, self.iJEUjoueurActuel) # Verif si colone pleine
        if tRes == 1:
            print("Colonne pleine")
            return

        iLigneJouee = tRes[0]
        sCouleur = self.sJEUcouleurJ if self.iJEUjoueurActuel == 1 else self.sJEUcouleurIa
        
        # On verrouille le jeu pendant l'animation
        self.bJEUanimEnCours = True 
        self.oJEUcanvas.unbind('<Button-1>')

        def JEUfinDuMouvement():
            """
            @brief Gére la fin de l'animation, relance le jeu 
            """
            self.bJEUanimEnCours = False 
 
            if self.bJEUjeuActif:
                 self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris) # réactive la souris

            bFini, iEtat = VictoireOuNul(self.oJEUgrille, self.iJEUjoueurActuel)

            if bFini: # check victoire
                self.bJEUjeuActif = False
                if iEtat == 1:
                    tPionsGagnants = self.JEUtrouverPionsGagnants(self.iJEUjoueurActuel)
                    self.JEUsurlignerVictoire(tPionsGagnants)
                self.JEUfinDePartie(iEtat)
                return

            self.iJEUjoueurActuel = 3 - self.iJEUjoueurActuel # channgement de joueur
            if self.iJEUjoueurActuel == 2:
                self.oJEUcanvas.after(500, self.JEUtourBot)

        iPionId = AjouterPion(self.oJEUcanvas, iLigneJouee, iCol, sCouleur, fFinish=JEUfinDuMouvement) # ajout du piont jouer

        self.tJEUpionsVisuels[iCol].append(iPionId)
        self.tJEUhistoriqueCoups.append((iCol, iPionId))
    
    def JEUtrouverPionsGagnants(self, iJoueur):
        """!
        @brief scanne le plateau pour trouver les pions gagnant
        @return une liste de tuples (ligne, colonne).
        """
        # On récupère la matrice 
        tMatrice = getattr(self.oJEUgrille, 'tPLAmatrice', [])
        
        iRows = self.iJEUnbLignes
        iCols = self.iJEUnbCols
        iN = self.iJEUwinCond

        # Directions: Horizontal, Vertical, Diagonale Descendante (\), Diagonale Montante (/)
        tDirections = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for iR in range(iRows):
            for iC in range(iCols):
                
                try:
                    if tMatrice[iR][iC] != iJoueur: continue 
                except IndexError:
                    continue 

                for iDr, iDc in tDirections:
                    tLigneTest = [(iR, iC)]
                    for k in range(1, iN):
                        iNr, iNc = iR + iDr * k, iC + iDc * k
                        
                        # Vérification des limites du plateau
                        if 0 <= iNr < iRows and 0 <= iNc < iCols:
                            try:
                                if tMatrice[iNr][iNc] == iJoueur:
                                    tLigneTest.append((iNr, iNc))
                                else:
                                    break
                            except IndexError: break
                        else:
                            break
                    
                    if len(tLigneTest) == iN:
                        return tLigneTest
        return []
    
    def JEUsurlignerVictoire(self, tPions):
        """!
        @brief entour les piosn gagnant du jeu
        """
        if not tPions: return
        
        dGridData = getattr(self.oJEUcanvas, 'grid_data', None)
        if not dGridData: return

        # Couleur (Vert fluo)
        sCOULEUR_VICTOIRE = "#00FF00" 
        iEPAISSEUR = 5

        iTaille = dGridData['taille']
        iStartX = dGridData['start_x']
        iStartY = dGridData['start_y']

        # Dessine les cercle celon la positin des joueurs gagnants
        for r, c in tPions:
            
            iX0 = iStartX + c * iTaille + 5 
            iY0 = iStartY + r * iTaille + 5 
            
            iX1 = iX0 + iTaille - 10
            iY1 = iY0 + iTaille - 10

            self.oJEUcanvas.create_oval(iX0, iY0, iX1, iY1, outline=sCOULEUR_VICTOIRE, width=iEPAISSEUR, tags="message_fin")
    
    def JEUtourBot(self):
        """!
        @brief Gestion du jeu bot
        """
        if not self.bJEUjeuActif: return
        self.oJEUcanvas.unbind('<Button-1>')

        iXPoint = int(iWIDTH * 0.85)
        iYPoint = int(iHEIGHT * 0.45) 
        
        self.iJEUpointInterrogationId = AddCanvasImg(self.oJEUcanvas, "images/pts_interro.png", (iXPoint, iYPoint), (100, 100))

        def JEUprocessIa():
            """!
            @brief Gére la dificulté de l'IA celon les paramétre et joue le coup
            Hardcore utilise meilleur coup a chaque fois
            Normal meilleur coup 2 fois sur 3
            Facile meilleur coup 1 fois sur 2 
            """
            iCol = -1
            if self.sJEUdiff == "Hardcore":
                iCol = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur)      
            elif self.sJEUdiff == "Normal":
                if self.iJEUbuffer == 1:
                    iCol = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur)
                    if self.iJEUnbCoupsIa % 3 == 0:
                        self.iJEUbuffer = 0
                else:
                    iCol = self.JEUobtenirColonneAleatoire()
                    self.iJEUbuffer = 1     
            elif self.sJEUdiff == "Facile":
                if self.iJEUbuffer == 1:
                    iCol = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur)
                    if self.iJEUnbCoupsIa % 2 == 0:
                        self.iJEUbuffer = 0
                else:
                    iCol = self.JEUobtenirColonneAleatoire()
                    self.iJEUbuffer = 1

            self.iJEUnbCoupsIa += 1
            self.oJEUcanvas.after(0, lambda: self.JEUactionBotPostCalcul(iCol))

        oThread = threading.Thread(target=JEUprocessIa) # Utilise le thread pour eviter que ca bloque tous 
        oThread.daemon = True 
        oThread.start()

    def JEUactionBotPostCalcul(self, iCol):
        """!
        @brief joue le coup de l'ia et réactivele clic souris
        """

        if hasattr(self, 'iJEUpointInterrogationId'):
            self.oJEUcanvas.delete(self.iJEUpointInterrogationId)
            del self.iJEUpointInterrogationId

        self.JEUjouerCoup(iCol)
        if self.bJEUjeuActif:
            self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)

    def JEUfinDePartie(self, iEtat):
        """!
        @brief GEstion de fin de partie
        """
        sMsg = "MATCH NUL"
        sCouleurTexte = "white"
        
        if iEtat == 1:
            if self.iJEUjoueurActuel == 1:
                sMsg = "VICTOIRE !"
                sCouleurTexte = "#00FF00"
            else:
                sMsg = "DÉFAITE..."
                sCouleurTexte = "#FF0000"

        self.oJEUcanvas.create_rectangle(iWIDTH//2 - 200, 50, iWIDTH//2 + 200, 150, fill="black", outline="white", width=2, tags="message_fin")
        
        self.oJEUcanvas.create_text(iWIDTH//2, 100, text=sMsg, font=("Arial", 40, "bold"), fill=sCouleurTexte, tags="message_fin")

if __name__ == "__main__":
    oApp = Tapp()
    oApp.APPchangerDePage(Tacceuil)
    oApp.mainloop()