from tkinter_fonction import *
from bot2 import VictoireOuNul, MeilleurCoup, QuelCoupMatrice, CoupBloquant
from Plateau import Tplateau
import threading
import random
import time
import os
from typing import List, Tuple, Dict, Callable, Optional, Any, Type

# ------- Différentes page -------- #

## @brief class maitre qui gére les différentes pages
class Tapp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("POLIC")
        ## Génération des taille de page
        iScreenWidth: int = self.winfo_screenwidth()
        iScreenHeight: int = self.winfo_screenheight()
        iXCordinate: int = int((iScreenWidth/2) - (iWIDTH/2))
        iYCordinate: int = int((iScreenHeight/2) - (iHEIGHT/2))
        ## iWIDTH et iHEIGHT valeur global
        self.geometry("{}x{}+{}+{}".format(iWIDTH, iHEIGHT, iXCordinate, iYCordinate))
        self.oAPPpageEnCours: Optional[tk.Frame] = None

        self.dSauvegardeParametres: Optional[Dict[str, Any]] = None
        self.resizable(width=False, height=False)

    ## @brief Changement de page, supprime celle en cours
    ## et en met une autre sans oublier de redéfinir le self
    def APPchangerDePage(self, oPage: Type[tk.Frame], **dData: Any) -> None:
        if self.oAPPpageEnCours:
            self.oAPPpageEnCours.destroy()

        self.oAPPpageEnCours = oPage(oParent=self, **dData)
        self.oAPPpageEnCours.pack(fill="both", expand=True)

## @brief Page d'accueil
class Tacceuil(tk.Frame):
    def __init__(self, oParent: Tapp) ->None:
        super().__init__(oParent, bg="")

        self.oACCcanva = tk.Canvas(self, width=iWIDTH, height=iHEIGHT, highlightthickness=0, bg="grey")
        self.oACCcanva.pack(fill="both", expand=True)
        
        AddBackground(self.oACCcanva, "images/Acceuil.jpg")
        AddCanvasBouton(self.oACCcanva, "images/bouton_play.png", ((iWIDTH//4),iHEIGHT//6), (iWIDTH//2,(iHEIGHT//12)*11), lambda: oApp.APPchangerDePage(TparamJeu), True, 35)
        AddCanvasBouton(self.oACCcanva, "images/bouton_close.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), oApp.destroy, True, 20)

class TparamJeu(tk.Frame):
    def __init__(self, oParent: Tapp, **dKwargs: Any) -> None:
        super().__init__(oParent, bg="")

        # 1. Création du canva et background
        self.oPAJcanva = tk.Canvas(self, width=oParent.winfo_screenwidth(), height=oParent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.oPAJcanva.pack(fill="both", expand=True)
        AddBackground(self.oPAJcanva, "images/parametre_bg.png")

        dCONFIG_DATA: Dict[str, List[Any]] = {
            "": [],
            "Win Condition": [i for i in range(3,50)],
            "Largeur": [i for i in range(4,50)], 
            "Hauteur": [i for i in range(4,50)],
            "Difficulté": ["Facile", "Normal", "Hardcore"],
            "Permier coup": ["bot", "joueur", "random"],
            "Bonus": ["nothing","bombe", "undo", "aide", "all"],
            "couleur joueur": ["cyan", "red", "orange", "yellow"],
            "couleur bot":["cyan", "red", "orange", "yellow"]
        }

        dDEFAUTS: Dict[str, Any] = {
            "Largeur": 7,          
            "Hauteur": 6,          
            "Win Condition": 4,    
            "Difficulté": "Normal",
            "Permier coup": "random",
            "Bonus": "nothing",
            "couleur joueur": "red",
            "couleur bot": "yellow"
        }

        if self.master.dSauvegardeParametres is not None:
            dDEFAUTS = self.master.dSauvegardeParametres

        self.oPAJmenu = TmenuDeroulant(self.oPAJcanva, iWIDTH//2, iHEIGHT//7, dCONFIG_DATA)
        self.oPAJmenu.MENscroll(1)

        for sCle, sValeur in dDEFAUTS.items():
            iIndexParDefaut = dCONFIG_DATA[sCle].index(sValeur)
            self.oPAJmenu.dMENchoices[sCle] = iIndexParDefaut


        AddCanvasBouton(self.oPAJcanva, "images/bouton_up.png", (50, 50), (iWIDTH//2 + 250, iHEIGHT//2 - 50), lambda: self.oPAJmenu.MENscroll(-1), True, 5)
        AddCanvasBouton(self.oPAJcanva, "images/bouton_down.png", (50, 50), (iWIDTH//2 + 250, iHEIGHT//2 + 50), lambda: self.oPAJmenu.MENscroll(1), True, 5)

        AddCanvasBouton(self.oPAJcanva, "images/bouton_back.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), lambda: oApp.APPchangerDePage(Tacceuil), True, 20)
        
        AddCanvasBouton(self.oPAJcanva, "images/boutonNext.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT) - iHEIGHT//10), self.PAJlancerPartie,True, 20)

    def PAJlancerPartie(self) -> None:
        
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
        
        dSauvegarde: Dict[str, Any] = {
            "Largeur": iLargeur,          
            "Hauteur": iHauteur,          
            "Win Condition": iWinCond,    
            "Difficulté": sNomDiff,
            "Permier coup": sPremierC,
            "Bonus": sBonus,
            "couleur joueur": sNomCoulJ,
            "couleur bot": sNomCoulB
        }
        self.master.dSauvegardeParametres = dSauvegarde

        # Création du dic de données
        dParametres: Dict[str, Any] = {
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
    def __init__(self, oParent: Tapp, **dSettings: Any) -> None:
        super().__init__(oParent, bg="")

        self.iJEUnbCols: int = dSettings.get("largeur")
        self.iJEUnbLignes: int = dSettings.get("hauteur")
        self.iJEUwinCond:int = dSettings.get("win")
        self.sJEUdiff: str = dSettings.get("diff")
        self.sJEUcouleurIa: str = dSettings.get("couleur_b")
        self.sJEUcouleurJ: str = dSettings.get("couleur_j")
        self.sJEUpremierCoup: str = dSettings.get("premier_c")
        self.sJEUbonus: str = dSettings.get("bonus")
        self.iJEUprofondeur: int = 4

        self.iJEUbuffer: int = 1
        self.iJEUnbCoupsIa: int = 0
        
        self.bJEUbotHasBomb: bool = False
        self.bJEUbotHasUndo: bool = False

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
        self.bJEUjeuActif: bool = False # attendre l'affichage complet avant de lancer sinon ca bug 

        # Configuration UI
        self.oJEUcanvas = tk.Canvas(self, width=oParent.winfo_screenwidth(), height=oParent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.oJEUcanvas.pack(fill="both", expand=True)

        AddBackground(self.oJEUcanvas, "images/bg.jpg")
        
        # Boutons de navigation
        AddCanvasBouton(self.oJEUcanvas, "images/bouton_back.png", (iHEIGHT//10, iHEIGHT//10), ((iHEIGHT//10)//2 + 5, (iHEIGHT//10)//2 + 5), lambda: oApp.APPchangerDePage(TparamJeu), True, 20)
        AddCanvasBouton(self.oJEUcanvas, "images/bouton_close.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH - (iHEIGHT//10)//2 - 5, (iHEIGHT//10)//2 + 5), oApp.destroy, True, 20)
        if self.sJEUbonus == "undo" or self.sJEUbonus == "all" :
            self.bJEUbotHasUndo = True
            self.iJEUundo = AddCanvasBouton(self.oJEUcanvas, "images/undo_bonus.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8, iHEIGHT//2), self.JEUactionUndo, True, 20)
        if self.sJEUbonus == "bombe"  or self.sJEUbonus == "all": 
            self.bJEUbotHasBomb = True
            self.iJEUbombe = AddCanvasBouton(self.oJEUcanvas, "images/bouton_bombe.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8 - iHEIGHT//8, iHEIGHT//2), self.JEUactiverModeBombe, True, 20)
            self.iJEUbombe_on = AddCanvasBouton(self.oJEUcanvas, "images/bouton_bombe_press.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8 - iHEIGHT//8, iHEIGHT//2), self.JEUactiverModeBombe, True, 20)
            self.oJEUcanvas.itemconfig(self.iJEUbombe_on, state='hidden')
        if self.sJEUbonus == "aide" or self.sJEUbonus == "all":
            self.iJEUaide = AddCanvasBouton(self.oJEUcanvas, "images/bouton_help.png", (iHEIGHT//10, iHEIGHT//10), (iWIDTH//8 + iHEIGHT//8, iHEIGHT//2), self.JEUdemanderAide, True, 20)

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
        self.bJEUactiveBombe: bool = False
        self.bJEUanimEnCours: bool = False

        # Play
        self.iJEUbtnStartId = AddCanvasBouton(self.oJEUcanvas, "images/bouton_ready.png",(150, 150), (iWIDTH//6, iHEIGHT//2), self.JEUlancerLaGame,True, 20)

    def JEUlancerLaGame(self) -> None:
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
    
    def JEUannulerUnSeulCoup(self) -> bool:
        """!
        @brief Annule un seul coup, use in JEUactionUndo
        """
        if not self.tJEUhistoriqueCoups:
            return False

        iCol, iPionId = self.tJEUhistoriqueCoups.pop() # Récup l'id du pio a suppr
        self.oJEUcanvas.delete(iPionId)
        self.oJEUgrille.PLAundo(iCol)
        return True

    def JEUactionUndo(self)-> None:
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

    def JEUdemanderAide(self) -> None:
        """!
        @brief Lance le calcul de l'IA pour aider le joueur 1
        """
        if not self.bJEUjeuActif or self.iJEUjoueurActuel != 1 or self.bJEUanimEnCours:
            return

        self.oJEUcanvas.unbind('<Button-1>')


        def ThreadCalculAide():
            import copy
            import numpy as np
            
            # 1. Créa clone plateau
            oClone = copy.deepcopy(self.oJEUgrille)
            
            # 2. INVERSION DES JOUEURS (sur le clone)
            # Le bot est codé pour jouer les 2, n change donc les 1 en 2 dans le clone
            oClone.tPLAmatrice = np.where(oClone.tPLAmatrice == 1, 3, oClone.tPLAmatrice)
            oClone.tPLAmatrice = np.where(oClone.tPLAmatrice == 2, 1, oClone.tPLAmatrice)
            oClone.tPLAmatrice = np.where(oClone.tPLAmatrice == 3, 2, oClone.tPLAmatrice)

            oClone.tPLAbitboards[0], oClone.tPLAbitboards[1] = oClone.tPLAbitboards[1], oClone.tPLAbitboards[0]

            tAction = MeilleurCoup(oClone, self.iJEUprofondeur, bHasBomb=False, bHasUndo=False)
            
            iMeilleurCol = tAction[1]
            
            self.oJEUcanvas.after(0, lambda: self.JEUafficherIndice(iMeilleurCol))

        oThread = threading.Thread(target=ThreadCalculAide)
        oThread.daemon = True
        oThread.start()

    def JEUafficherIndice(self, iCol: int) -> None:
        """!
        @brief Affiche visuellement où jouer
        """
        # Réactiver le jeu
        if self.bJEUjeuActif:
            self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)
        
        dGridData = getattr(self.oJEUcanvas, 'grid_data', None)
        if not dGridData: return
        
        iTaille = dGridData['taille']
        iStartX = dGridData['start_x']
        iStartY = dGridData['start_y']
        
        iX = iStartX + (iCol * iTaille) + (iTaille // 2)
        iY = iStartY - (iTaille // 2)

        iIndiceId = self.oJEUcanvas.create_text(iX, iY, text="⬇", font=("Arial", 40, "bold"), fill="#00FF00")
        
        # Animation cligno
        def Clignoter(iCount):
            if iCount > 6:
                self.oJEUcanvas.delete(iIndiceId)
                return
            
            sState = self.oJEUcanvas.itemcget(iIndiceId, 'state')
            sNewState = 'hidden' if sState == 'normal' else 'normal'
            self.oJEUcanvas.itemconfig(iIndiceId, state=sNewState)
            
            self.oJEUcanvas.after(300, lambda: Clignoter(iCount + 1))
            
        Clignoter(0)

        self.oJEUcanvas.delete(self.iJEUaide)

    def JEUreactiverJeu(self)-> None:
        """!
        @brief réactivation du jeu -> suppr les affichage de fin, et réactive le clic souris
        """
        self.bJEUjeuActif = True
        self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)
        self.oJEUcanvas.delete("message_fin")

    def JEUactiverModeBombe(self)-> None:
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
        
    def JEUlacherBombe(self, iCol: int) -> None:
        """!
        @brief Joue la bombe (Compatible IA et Joueur)
        """
        if self.oJEUgrille.tPLAfillMatrice[iCol] == 0:
            if self.iJEUjoueurActuel == 1: 
                self.bJEUactiveBombe = False
                # Reset boutons visuels joueur
                self.oJEUcanvas.itemconfig(self.iJEUbombe_on, state='hidden')
                self.oJEUcanvas.itemconfig(self.iJEUbombe, state='normal')
            return

        self.oJEUgrille.PLApowerBomb(iCol)

        for iPionId in self.tJEUpionsVisuels[iCol]:
            self.oJEUcanvas.delete(iPionId)
        self.tJEUpionsVisuels[iCol] = []
        
        self.tJEUhistoriqueCoups = [tCoup for tCoup in self.tJEUhistoriqueCoups if tCoup[0] != iCol]

        if self.iJEUjoueurActuel == 1:
            self.bJEUactiveBombe = False
            if hasattr(self, 'iJEUbombe'): self.oJEUcanvas.delete(self.iJEUbombe)
            if hasattr(self, 'iJEUbombe_on'): self.oJEUcanvas.delete(self.iJEUbombe_on)
        
        # Changement de tour
        self.iJEUjoueurActuel = 3 - self.iJEUjoueurActuel 
        
        if self.iJEUjoueurActuel == 2:
            self.oJEUcanvas.after(500, self.JEUtourBot)
        else:
            # Si c'est au joueur, on réactive la souris
            if self.bJEUjeuActif:
                self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)

    def JEUobtenirColonneAleatoire(self) -> int:
        """!
        @brief Prend une colone aléatoire, pour la gestion du niveau de bot
        """
        tColsValides = [c for c in range(self.oJEUgrille.iPLAcolonnes) if self.oJEUgrille.tPLAfillMatrice[c] < self.oJEUgrille.iPLAlignes]
        if tColsValides:
            return random.choice(tColsValides)
        return 0

    def JEUclicSouris(self, oEvent: tk.Event) -> None:
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
    
    def JEUjouerCoup(self, iCol: int) -> None:
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
    
    def JEUtrouverPionsGagnants(self, iJoueur: int) -> List[Tuple[int, int]]:
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
    
    def JEUsurlignerVictoire(self, tPions: List[Tuple[int, int]]) -> None:
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
    
    def JEUtourBot(self) -> None:
        """!
        @brief Gestion du jeu bot avec intelligence adaptative
        """
        if not self.bJEUjeuActif: return
        self.oJEUcanvas.unbind('<Button-1>')

        iXPoint = int(iWIDTH * 0.85)
        iYPoint = int(iHEIGHT * 0.45) 
        
        self.iJEUpointInterrogationId = AddCanvasImg(self.oJEUcanvas, "images/pts_interro.png", (iXPoint, iYPoint), (100, 100))

        def JEUprocessIa():
            """!
            @brief Thread IA
            """
            tAction = (0, 0) # (Type, Col)
            
            iCoupGagnant = -1
            iCoupBloquant = -1
            
            if self.sJEUdiff != "Facile":
                iCoupGagnant = QuelCoupMatrice(self.oJEUgrille, 2)
                iCoupBloquant = CoupBloquant(self.oJEUgrille, 1)


            # MODE HARDCORE toujours meilleur coup
            if self.sJEUdiff == "Hardcore":
                tAction = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur, self.bJEUbotHasBomb, self.bJEUbotHasUndo)      
            
            # MODE NORMAL : Intelligent mais pas trop
            elif self.sJEUdiff == "Normal":
                # Priorité 1 : Gagner si possible
                if iCoupGagnant != -1:
                    tAction = (0, iCoupGagnant)
                # Priorité 2 : Bloquer si nécessaire
                elif iCoupBloquant != -1:
                    tAction = (0, iCoupBloquant)
                else:
                    # Pas de coup spécial
                    # 70% de chance de jouer le MeilleurCoup
                    # 30% de chance de jouer un coup moyen
                    if random.random() < 0.7:
                         tAction = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur, self.bJEUbotHasBomb, self.bJEUbotHasUndo)
                    else:
                         tAction = (0, self.JEUobtenirCoupAleatoireSemiIntelligent())

            # MODE FACILE : Joue de temps en temps bien 
            elif self.sJEUdiff == "Facile":
                # 30% de chance de jouer le meilleur coup
                if random.random() < 0.3:
                    tAction = MeilleurCoup(self.oJEUgrille, self.iJEUprofondeur, self.bJEUbotHasBomb, self.bJEUbotHasUndo)
                else:
                    # 70% random
                    tAction = (0, self.JEUobtenirColonneAleatoire())

            self.iJEUnbCoupsIa += 1
            self.oJEUcanvas.after(0, lambda: self.JEUactionBotPostCalcul(tAction))

        oThread = threading.Thread(target=JEUprocessIa)
        oThread.daemon = True 
        oThread.start()

    def JEUactionBotPostCalcul(self, tAction: Tuple[int, int]) -> None:
        """!
        @brief Joue l'action choisie par l'IA
        @param tAction Tuple (TypeAction, Colonne)
        """
        iType, iCol = tAction

        if hasattr(self, 'iJEUpointInterrogationId'):
            self.oJEUcanvas.delete(self.iJEUpointInterrogationId)
            del self.iJEUpointInterrogationId

        if iType == 2: # UNDO
            # print("Bot joue Undo")
            self.bJEUbotHasUndo = False
            self.JEUactionUndo()
            return

        elif iType == 1: # BOMBE
            print(f"Bot joue Bombe en {iCol}")
            self.bJEUbotHasBomb = False # Consomme le bonus
            self.JEUlacherBombe(iCol)
            return

        else: # COUP NORMAL
            self.JEUjouerCoup(iCol)
            if self.bJEUjeuActif:
                self.oJEUcanvas.bind('<Button-1>', self.JEUclicSouris)

    def JEUobtenirCoupAleatoireSemiIntelligent(self)-> int:
        """!
        @brief Trouve une colonne aléatoire, mais évite de donner une victoire immédiate à l'adversaire.
        """
        tColsValides = [c for c in range(self.oJEUgrille.iPLAcolonnes) if self.oJEUgrille.tPLAfillMatrice[c] < self.oJEUgrille.iPLAlignes]
        
        if not tColsValides: return 0
        
        random.shuffle(tColsValides)
        
        # On cherche une colonne qui n'est pas "suicidaire"
        for iCol in tColsValides:
            self.oJEUgrille.PLAplay(iCol, 2)
            bSuicide = False

            if QuelCoupMatrice(self.oJEUgrille, 1) != -1:
                bSuicide = True
            
            self.oJEUgrille.PLAundo(iCol)
            
            if not bSuicide:
                return iCol

        return tColsValides[0]

    def JEUfinDePartie(self, iEtat: int) -> None:
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
    oApp: Tapp = Tapp()
    oApp.APPchangerDePage(Tacceuil)
    oApp.mainloop()