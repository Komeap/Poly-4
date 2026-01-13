import Plateau as p
import tkinter as tk
from tkinter import font
import cv2
from PIL import Image, ImageTk
import time
from typing import List, Tuple, Dict, Callable, Optional

##screen size
iWIDTH:int = 1350
iHEIGHT:int  = 800


def AddBackground(oMaster: tk.Canvas, sImage: str) -> None:
    """!
    @brief Met une image en background
    @param sImage lien de l'image
    """
    oImageOriginale = Image.open(sImage)
    oImageRedim = oImageOriginale.resize((iWIDTH, iHEIGHT), Image.Resampling.LANCZOS)
    oPhoto = ImageTk.PhotoImage(oImageRedim)

    iBgId = oMaster.create_image(0, 0, image=oPhoto, anchor="nw")
    oMaster.tag_lower(iBgId)
    oMaster.bg_image_cache = oPhoto

def AddCanvasImg(oCanvas: tk.Canvas, sLink: str, tPos: Tuple[int, int], tSize: Tuple[int, int]) -> int:
    """!
    @brief Permet d'ajouter une image sur le canva
    @param sLink lien de l'image
           tPos Une position x, y 
           tSize la taille de l'image 
    """
    oImgPil = Image.open(sLink)
    oImgRes = oImgPil.resize(tSize, Image.LANCZOS)
    oImg = ImageTk.PhotoImage(oImgRes)

    iImgId = oCanvas.create_image(tPos[0], tPos[1], image=oImg, anchor=tk.CENTER)

    if not hasattr(oCanvas, 'images_list'):
        oCanvas.images_list = []
    
    oCanvas.images_list.append(oImg)
    
    return iImgId

def AddCanvasBouton(oCanvas: tk.Canvas, sLink: str, tSize: Tuple[int, int], tPos: Tuple[int, int], fCmd: Callable[[], None], bHover: bool, iZoom: int) ->int:
    """!
    @brief Permet d'ajouter une image qui est un bouton 
    @param sLink lien de l'image du bouton
           tSize la taille de l'image 
           tPos Une position x, y 
           fCmd La fonction qui s'execute quand on clique sur le bouton
           bHover booléen -> true changement de curseur si on passe au dessus
           iZoom De combien ca zoom quand on passe au dessus (effet de style)
           
    """
    oImgPil = Image.open(sLink)
    oImgRes = oImgPil.resize(tSize, Image.LANCZOS)
    oImgZoom = ImageTk.PhotoImage(oImgPil.resize((tSize[0] + iZoom, tSize[1] + iZoom), Image.LANCZOS))
    oImg = ImageTk.PhotoImage(oImgRes)
    
    iImgId = oCanvas.create_image(tPos[0], tPos[1], image=oImg, anchor=tk.CENTER)
    
    # gestion de l'anim
    def OnEnter(oEvent):
        oCanvas.itemconfig(iImgId, image=oImgZoom)

    def OnLeave(oEvent):
        oCanvas.itemconfig(iImgId, image=oImg)

    oCanvas.tag_bind(iImgId, "<Enter>", OnEnter)
    oCanvas.tag_bind(iImgId, "<Leave>", OnLeave)

    oCanvas.tag_bind(iImgId, "<Button-1>", lambda event: fCmd())
    
    # gestion du cursor
    if bHover :
        oCanvas.tag_bind(iImgId, "<Enter>", lambda event: oCanvas.config(cursor="hand2"), add="+")
        oCanvas.tag_bind(iImgId, "<Leave>", lambda event: oCanvas.config(cursor=""), add="+")

    if not hasattr(oCanvas, 'images'):
        oCanvas.images = []
        
    oCanvas.images.append(oImg)
    oCanvas.images.append(oImgZoom)

    return iImgId

def LancerVideo(oCanvas: tk.Canvas, sCheminVideo: str, iLargeur: int=iWIDTH, iHauteur: int=iHEIGHT +150) ->None:
    """!
    @brief lancement de la vidéo
    @param sCheminVideo Lien de la video
           iLargeur Taille de la vidéo
           iHauteur Taille de la vidéo
    """
    FermerVideo(oCanvas)

    oCap = cv2.VideoCapture(sCheminVideo)

    oCanvas.cap = oCap
    oCanvas.video_en_cours = True

    def Stream():
        """!
         @brief Gére lel déroulement de la vidéo
        """
        if not getattr(oCanvas, 'video_en_cours', False):
            oCap.release()
            oCanvas.delete("tag_video")
            return

        bRet, oFrame = oCap.read()
        if bRet:
            oFrame = cv2.cvtColor(oFrame, cv2.COLOR_BGR2RGB)
            oImgPil = Image.fromarray(oFrame)
            oImgPil = oImgPil.resize((iLargeur, iHauteur)) 
            oImgTk = ImageTk.PhotoImage(image=oImgPil)
            oCanvas.create_image(0, -50, anchor="nw", image=oImgTk, tags="tag_video")
            oCanvas.image_ref = oImgTk 
            oCanvas.after(33, Stream)
        else:
            FermerVideo(oCanvas)
    Stream()

def FermerVideo(oCanvas: tk.Canvas) ->None:
    """!
    @brief Permet de fermer la vidéo
    """
    oCanvas.video_en_cours = False
    if hasattr(oCanvas, 'cap') and oCanvas.cap.isOpened():
        oCanvas.cap.release()
    oCanvas.delete("tag_video")

## @brief Class des cases de paramétre du Menu dDéroulant
class TparamCase:
    def __init__(self, oCanvas: tk.Canvas, iX:int, iY:int, sNom: str, tOptions: Optional[List[str]]=None, tStartSize:Tuple[int, int]=(iHEIGHT//4, iHEIGHT//3), fScale: float=1.0, bAffiche: bool =True, iIndex: int=0, fOnChange: Callable[[int], None]=lambda i: None):
        """!
        @brief init
        @param iX, iY position
            sNom Nom de la case
            tStartSize Taille de départ
            fScale valeur entre 0 et 1 du pourcentage de la taille afficher 0.8 affiche la case a une taille de 80%
            bAffiche gére l'affichage ou non de la case
        """
        self.oPARcanvas: tk.Canvas = oCanvas
        self.sPARnom: str = sNom
        self.tPARids: List[int] = []
        self.fPARonChange: Callable[[int], None] = fOnChange

        # choix options
        self.tPARoptions: List[str] = tOptions if tOptions else []
        self.iPARindex: int = iIndex

        # dimension pour la resizer et l'effet de déroulement du menu
        iWRedim = int(tStartSize[0] * fScale)
        iHRedim = int(tStartSize[1] * fScale)
        tSize: Tuple[int, int] = (iWRedim, iHRedim)

        if bAffiche:
            # Image de fond
            self.iPARimgId = AddCanvasImg(oCanvas, "images/param_case.png", (iX,iY), tSize)
            self.tPARids.append(self.iPARimgId)

            # titre des paramétre
            self.iPARtexteNom = oCanvas.create_text(iX, iY - (tSize[1]//2) + int(35*fScale), text=f"{sNom}", font=("Retro Gaming", int(15*fScale)), anchor='center', fill="black")
            self.tPARids.append(self.iPARtexteNom) 

            # Valeur affichée
            if self.tPARoptions:
                sValeur = self.tPARoptions[self.iPARindex]
            else:
                sValeur = ""
            
            # valeur du paramétre affichage
            self.iPARtexteValeur = oCanvas.create_text(iX,iY + 25*fScale,text=sValeur,font=("Retro Gaming", int(20*fScale)),anchor='center',fill="black")
            self.tPARids.append(self.iPARtexteValeur)

            # Bouton up
            self.iPARbtnUId = AddCanvasBouton(oCanvas, "images/bouton_up.png", (iHEIGHT//25, iHEIGHT//25), (iX , iY - tSize[1]//7), self.PARnextValue, True, 10)
            self.tPARids.append(self.iPARbtnUId)

            # Bouton down
            self.iPARbtnDId = AddCanvasBouton(oCanvas, "images/bouton_down.png", (iHEIGHT//25, iHEIGHT//25), (iX, iY + tSize[1]//2.7), self.PARprevValue, True, 10)
            self.tPARids.append(self.iPARbtnDId)

    # Changer de valeur vers HAUT
    def PARnextValue(self) ->None:
        if not self.tPARoptions: 
            return
        self.iPARindex = (self.iPARindex + 1) % len(self.tPARoptions) 
        self.oPARcanvas.itemconfig(self.iPARtexteValeur, text=self.tPARoptions[self.iPARindex]) 
        self.fPARonChange(self.iPARindex)  

    # Changer de valeur vers BAS
    def PARprevValue(self) ->None:
        if not self.tPARoptions: return
        self.iPARindex = (self.iPARindex - 1) % len(self.tPARoptions)
        self.oPARcanvas.itemconfig(self.iPARtexteValeur, text=self.tPARoptions[self.iPARindex])
        self.fPARonChange(self.iPARindex)

    # détruit la case pour l'animation
    def PARdestroy(self) ->None:
        for iItemId in self.tPARids:
            self.oPARcanvas.delete(iItemId) 

## @brief Class qui gérte le Menu déroulant 
class TmenuDeroulant:
    def __init__(self, oCanvas: tk.Canvas, iX: int, iYStart: int, dConfigData: Dict[str, List[str]]):
        """!
        @brief init
        @param iX Positon x du MEnue déroulant
            iYStart Position y de la premier case
            dConfigData Dictionnaire contenant les Nom des case de parametre du menu (TparamCase)
        """
        self.oMENcanvas: tk.Canvas = oCanvas
        self.iMENx: int = iX
        self.iMENyStart: int = iYStart
        # Gestion des valeur des paramétres
        self.tMENparamsData:List[str] = list(dConfigData.keys())
        self.dMENconfig: Dict[str, List[str]] =  dConfigData
        self.dMENchoices: Dict[str, int] = {key: 0 for key in dConfigData}
        
        #Gestion des index
        self.iMENcurrentIndex: int = 0
        self.iMENmaxVisible: int = 3
        self.iMENecart: int = iHEIGHT // 3 + 20
        
        # Positions cible après mouvement
        self.tMENpositionsYFixes: List[int] = [
            self.iMENyStart,                # Position haut
            self.iMENyStart + self.iMENecart,   # Position millieu
            self.iMENyStart + self.iMENecart*2  # Position bas
        ]
        
        # % de la taille pour l'effet de style
        self.tMENtaillesFixes: List[float] = [0.7, 1.0, 0.7] 

        self.tMENactiveCases: List[TparamCase] = []
        
        self.bMENisAnimating: bool = False
        
        self.MENupdateDisplayInstantane()

    def MENupdateDisplayInstantane(self) -> None:
        """!
        @brief Update le menu déroulant et l'afficahge
        """
        for oCase in self.tMENactiveCases: 
            oCase.PARdestroy()
        self.tMENactiveCases = []
        # affiche les cases visibles
        for j in range(self.iMENmaxVisible):
            iDataIndex = self.iMENcurrentIndex + j

            if iDataIndex >= len(self.tMENparamsData): 
                break

            sNom = self.tMENparamsData[iDataIndex]
            tOptions = self.dMENconfig.get(sNom, [])
            iY = self.tMENpositionsYFixes[j]
            fS = self.tMENtaillesFixes[j]

            if sNom == "":
                oNewCase = TparamCase(self.oMENcanvas, self.iMENx, iY, self.tMENparamsData[iDataIndex], fScale=fS, bAffiche=False)
                self.tMENactiveCases.append(oNewCase)
            else :
                oNewCase = TparamCase(self.oMENcanvas, self.iMENx, iY, sNom, tOptions, fScale=fS ,iIndex=self.dMENchoices[sNom], fOnChange=lambda iIdx, sCle=sNom: self.MENsaveChoice(sCle, iIdx))
                self.tMENactiveCases.append(oNewCase)
    
    def MENsaveChoice(self, sNom: str, iIdx: int) -> None:
        """!
        @brief POur pas perdre la selection quand on change l'affichage
        """
        self.dMENchoices[sNom] = iIdx

    def MENscroll(self, iDirection: int) ->None:
        """!
        @brief Permet de scroll en haut ou en bas celon iDirection
        """
        if self.bMENisAnimating: return
        
        iNewIndex = self.iMENcurrentIndex + iDirection
        if not (0 <= iNewIndex < len(self.tMENparamsData)): return


        self.MENanimateTransition(iDirection)

    def MENanimateTransition(self, iDirection: int) ->None:
        """!
        @brief Exécute la transition/ Déplacement
        Calcul le décalage de postion et de proportion et affiche chaque image une par une
        effet rétro
        """
        self.bMENisAnimating = True
        
        # CONFIGURATION DE L'ANIMATION
        iSteps = 3
        iDelay = 1
        
        def StepProcess(iStep):
            """!
            @brief Calcul la nouvel image de la case et les position et la taille
            """

            for oCase in self.tMENactiveCases:
                oCase.PARdestroy()
            self.tMENactiveCases = []
            
            fProgress = iStep / iSteps 
            
            iRangeStart = -1 if iDirection == -1 else 0
            iRangeEnd = self.iMENmaxVisible if iDirection == -1 else self.iMENmaxVisible + 1

            for j in range(iRangeStart, iRangeEnd):
                iDataIndex = self.iMENcurrentIndex + j
                
                if iDataIndex < 0 or iDataIndex >= len(self.tMENparamsData):
                    continue

                sNom = self.tMENparamsData[iDataIndex]
                tOptions = self.dMENconfig.get(sNom, [])
                
                iStartY = self.iMENyStart + (j * self.iMENecart)
                iTargetY = self.iMENyStart + ((j - iDirection) * self.iMENecart)
                fCurrentY = iStartY + (iTargetY - iStartY) * fProgress

                iCenterY = self.iMENyStart + self.iMENecart
                fDist = abs(fCurrentY - iCenterY)
                fRatio = fDist / self.iMENecart
                if fRatio > 1: fRatio = 1
                fCurrentScale = 1.0 - (fRatio * 0.2)

                iSavedIndex = self.dMENchoices.get(sNom, 0)
                
                if sNom == "":
                    oCase = TparamCase(self.oMENcanvas, self.iMENx, fCurrentY, sNom, fScale=fCurrentScale, bAffiche=False)
                    self.tMENactiveCases.append(oCase)
                else :
                    oCase = TparamCase(self.oMENcanvas, self.iMENx, fCurrentY, sNom, tOptions, fScale=fCurrentScale, iIndex=iSavedIndex, fOnChange=lambda iIdx, sCle=sNom: self.MENsaveChoice(sCle, iIdx))
                    self.tMENactiveCases.append(oCase)

            if iStep < iSteps:
                self.oMENcanvas.after(iDelay, lambda: StepProcess(iStep + 1))
            else:
                self.iMENcurrentIndex += iDirection
                self.bMENisAnimating = False
                self.MENupdateDisplayInstantane()

        StepProcess(1)

    def MENprintAllChoices(self) -> None:
        """!
        @brief Affiche les choix de valeur utilisé pour les test
        """
        print("\n=== PARAMÈTRES ACTUELS ===")
        for sNom in self.tMENparamsData:
            if sNom == "": 
                continue 
            iIndex = self.dMENchoices[sNom]
            sValeur = self.dMENconfig[sNom][iIndex]
            print(f"{sNom}: {sValeur}")
        print("==========================\n")

def InitFleche(oCanvas: tk.Canvas) -> int:
    """!
    @brief Initialise l'image de la fléche pour le jeu
    """
    oImgPil = Image.open("images/fleche_in_game.png")
    
    iTaille = getattr(oCanvas, 'taille_case', 50) 
    
    oImgRes = oImgPil.resize((int(iTaille * 0.7), int(iTaille * 0.7)), Image.LANCZOS)
    oImgTk = ImageTk.PhotoImage(oImgRes)

    oCanvas.fleche_img = oImgTk
    iFlecheId = oCanvas.create_image(-100, -100, image=oImgTk, anchor=tk.CENTER)
    
    return iFlecheId

def BougerFleche(oEvent: tk.Event, oCanvas: tk.Canvas, iFlecheId: int) -> None:
    """!
    @brief Gére le mouvemnt de la fléche de jeu
    """

    dGridData = getattr(oCanvas, 'grid_data', None)
    if not dGridData:
        return

    iStartX = dGridData['start_x']
    iStartY = dGridData['start_y']
    iTaille = dGridData['taille']
    iCols = dGridData['cols']
    iGrilleL = dGridData['largeur_totale']

    iMouseX = oEvent.x
    
    if iStartX <= iMouseX <= iStartX + iGrilleL:
        iColIndex = int((iMouseX - iStartX) // iTaille)
        
        if 0 <= iColIndex < iCols:
            iCenterX = iStartX + (iColIndex * iTaille) + (iTaille // 2)

            iPosY = iStartY - (iTaille // 1.5)
 
            oCanvas.coords(iFlecheId, iCenterX, iPosY)

            oCanvas.itemconfigure(iFlecheId, state='normal')
            return

def AjouterPion(oCanvas: tk.Canvas, iLigne: int, iCol: int, sCouleur: str, fFinish: Optional[Callable[[], None]]=None) -> int:
    """!
    @brief Gére l'animation d'ajout de jeton, chute physique + rebond
    """
    dGrid = getattr(oCanvas, 'grid_data', None)
    if not dGrid: return

    iStartX = dGrid['start_x']
    iStartY = dGrid['start_y']
    iTaille = dGrid['taille']
    iNbLignes = dGrid['rows']

    iXCenter = iStartX + (iCol * iTaille) + (iTaille // 2)

    iLigneVisuelle = (iNbLignes - 1) - iLigne
    iYFinal = iStartY + (iLigneVisuelle * iTaille) + (iTaille // 2)
    iYDepart = iStartY 
    iRayon = (iTaille // 2) - 2 

    # image du pion qui va etre bougé
    iPionId = oCanvas.create_oval(iXCenter - iRayon, iYDepart - iRayon,iXCenter + iRayon, iYDepart + iRayon,fill=sCouleur, outline="black", width=1)

    oCanvas.tag_lower(iPionId, "grille")

    dInfoAnim = {"y_actuel": iYDepart, "vitesse": 0, "gravite": 1.5, "rebond": 0.35}

    def AnimChute():
        """!
        @brief Animation au sens de la gravité et rebond réel
        """
        dInfoAnim["vitesse"] += dInfoAnim["gravite"]
        
        fV = dInfoAnim["vitesse"]
        fY = dInfoAnim["y_actuel"]

        if fY + fV >= iYFinal:
            fDistRestante = iYFinal - fY
            oCanvas.move(iPionId, 0, fDistRestante)
            dInfoAnim["y_actuel"] = iYFinal

            fVRebond = -fV * dInfoAnim["rebond"]
            
            if abs(fVRebond) < 2.0:
                if fFinish :
                    fFinish()
                return 
            
            dInfoAnim["vitesse"] = fVRebond
            oCanvas.after(20, AnimChute)

        else:
            oCanvas.move(iPionId, 0, fV)
            dInfoAnim["y_actuel"] += fV
            oCanvas.after(20, AnimChute)
            
    AnimChute()
    return iPionId

def AfficherPlateau(oCanvas: tk.Canvas, iLargeur: int, iHauteur: int) -> None:
    """!
    @brief Affiche le plateau en fonction du nombre de colone et lignes
    Calcul pour qu'il soit tpoujours bien centré peut uimport la taille
    """
    
    fMLarg = iWIDTH*0.2
    fMHaut = iHEIGHT*0.2

    fSizeDispoLarg = abs(iWIDTH - 2*(fMLarg))
    fSizeDispoHaut = abs(iHEIGHT - 2*(fMHaut))

    iSizeCase1 = (int)(fSizeDispoLarg//iLargeur)
    iSizeCase2 = (int)(fSizeDispoHaut//iHauteur)

    iTailleCase = min(iSizeCase1, iSizeCase2)

    iGrilleL = iTailleCase * iLargeur
    iGrilleH = iTailleCase * iHauteur

    iStartX = fMLarg + (fSizeDispoLarg - iGrilleL)//2
    iStartY = fMHaut + (fSizeDispoHaut - iGrilleH)//2

    oCanvas.taille_case = iTailleCase 
    oCanvas.grid_data = {"start_x": iStartX, "start_y": iStartY, "taille": iTailleCase, "cols": iLargeur, "rows": iHauteur, "largeur_totale": iGrilleL}

    oCanvas.image_cache = []
    
    oPilCase = Image.open("images/One_case.png")
    oCaseRedim = oPilCase.resize((iTailleCase, iTailleCase), Image.LANCZOS)
    oCaseTk = ImageTk.PhotoImage(oCaseRedim)
    oCanvas.image_cache.append(oCaseTk)

    oPilBorder = Image.open("images/border.png")

    iEpaisseurMur = iTailleCase // 4
    iOverlap = 2
    iEpaisseurVisuelle = iEpaisseurMur + iOverlap

    iWVisuelHoriz = iGrilleL + iOverlap
    iHVisuelVerti = iGrilleH + iOverlap

    ## Afficheage des 4 bordures rotation + positon

    oImgR = oPilBorder.resize((iEpaisseurVisuelle, iHVisuelVerti), Image.LANCZOS)
    oTkR = ImageTk.PhotoImage(oImgR)
    oCanvas.image_cache.append(oTkR)

    oImgL = oPilBorder.rotate(180).resize((iEpaisseurVisuelle, iHVisuelVerti), Image.LANCZOS)
    oTkL = ImageTk.PhotoImage(oImgL)
    oCanvas.image_cache.append(oTkL)

    oImgT = oPilBorder.rotate(90, expand=True).resize((iWVisuelHoriz, iEpaisseurVisuelle), Image.LANCZOS)
    oTkT = ImageTk.PhotoImage(oImgT)
    oCanvas.image_cache.append(oTkT)

    oImgB = oPilBorder.rotate(-90, expand=True).resize((iWVisuelHoriz, iEpaisseurVisuelle), Image.LANCZOS)
    oTkB = ImageTk.PhotoImage(oImgB)
    oCanvas.image_cache.append(oTkB)

    # Fin affichage bordure

    iCenterGridX = iStartX + (iGrilleL // 2)
    iCenterGridY = iStartY + (iGrilleH // 2)

    oCanvas.create_image(iCenterGridX, iStartY - (iEpaisseurMur//2), image=oTkT, anchor=tk.CENTER)
    oCanvas.create_image(iCenterGridX, iStartY + iGrilleH + (iEpaisseurMur//2), image=oTkB, anchor=tk.CENTER)
    oCanvas.create_image(iStartX - (iEpaisseurMur//2), iCenterGridY, image=oTkL, anchor=tk.CENTER)
    oCanvas.create_image(iStartX + iGrilleL + (iEpaisseurMur//2), iCenterGridY, image=oTkR, anchor=tk.CENTER)
    
    ## Afdfichage de chaque case de la grille
    for iCol in range(iLargeur):
        for iLig in range(iHauteur):
            iPosX = iStartX + (iCol * iTailleCase) + (iTailleCase // 2)
            iPosY = iStartY + (iLig * iTailleCase) + (iTailleCase // 2)

            oCanvas.create_image(iPosX, iPosY, image=oCaseTk, anchor=tk.CENTER, tags="grille")