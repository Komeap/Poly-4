from tkinter_fonction import *
from bot2 import victoire_ou_nul, meilleur_coup
from Plateau import Plateau
import threading
import random
import time

# ------- Différentes page -------- #

## @brief class maitre qui gére les différentes pages
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POLIC")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (WIDTH/2))
        y_cordinate = int((screen_height/2) - (HEIGHT/2))
        
        self.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cordinate, y_cordinate))
        self.page_en_cours = None
        self.resizable(width=False, height=False)

        

    ## @brief CHangement de page, supprime celle en cours
    ## et en met une autre sans oublier de redéfinir le self
    def changer_de_page(self, page, **data):
        if self.page_en_cours:
            self.page_en_cours.destroy()

        self.page_en_cours = page(parent=self, **data)
        self.page_en_cours.pack(fill="both", expand=True)
    
## @brief Page d'accueil
class Acceuil(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="")

        self.canva = tk.Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)
        
        add_bakground(self.canva, "images/Acceuil.jpg")
        add_canvas_bouton(self.canva, "images/bouton_play.png", ((WIDTH//4),HEIGHT//6), (WIDTH//2,(HEIGHT//12)*11), lambda: app.changer_de_page(Param_jeu), True, 35)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

class Param_jeu(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="")

        # 1. Création du canva et background
        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)
        add_bakground(self.canva, "images/parametre_bg.png")

        CONFIG_DATA = {
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

        DEFAUTS = {
            "Largeur": 7,          
            "Hauteur": 6,          
            "Win Condition": 4,    
            "Difficulté": "Normal",
            "Permier coup": "random",
            "Bonus": "nothing",
            "couleur joueur": "red",
            "couleur bot": "yellow"
        }

        self.menu = MenuDeroulant(self.canva, WIDTH//2, HEIGHT//7, CONFIG_DATA)
        self.menu.scroll(1)

        for cle, valeur in DEFAUTS.items():
            index_par_defaut = CONFIG_DATA[cle].index(valeur)
            self.menu.choices[cle] = index_par_defaut


        add_canvas_bouton(self.canva, "images/bouton_up.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 - 50), lambda: self.menu.scroll(-1), True, 5)
        add_canvas_bouton(self.canva, "images/bouton_down.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 + 50), lambda: self.menu.scroll(1), True, 5)

        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Acceuil), True, 20)
        
        add_canvas_bouton(self.canva, "images/boutonNext.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT) - HEIGHT//10), self.lancer_partie,True, 20)

    def lancer_partie(self):
        
        # Récupération des choix
        choix = self.menu.choices
        config = self.menu.config
        
        # Conversion des choix
        largeur = config["Largeur"][choix["Largeur"]]
        hauteur = config["Hauteur"][choix["Hauteur"]]
        win_cond = config["Win Condition"][choix["Win Condition"]]
        nom_coul_j = config["couleur joueur"][choix["couleur joueur"]]
        nom_coul_b = config["couleur bot"][choix["couleur bot"]]
        premier_c = config["Permier coup"][choix["Permier coup"]]
        bonus = config["Bonus"][choix["Bonus"]]
        nom_diff = config["Difficulté"][choix["Difficulté"]]
        

        # Création du colis de données
        parametres = {
            "largeur": largeur,
            "hauteur": hauteur,
            "win": win_cond,
            "diff": nom_diff,
            "couleur_j": nom_coul_j,
            "couleur_b": nom_coul_b,
            "premier_c" : premier_c,
            "bonus" : bonus
        }

        # Changement de page
        app.changer_de_page(Jeu, **parametres)

class Jeu(tk.Frame):
    """
    @brief Réprésente la page de jeu 
    """
    def __init__(self, parent, **settings):
        super().__init__(parent, bg="")

        self.NB_COLS = settings.get("largeur")
        self.NB_LIGNES = settings.get("hauteur")
        self.WIN_COND = settings.get("win")
        self.DIFF = settings.get("diff")
        self.COULEUR_IA = settings.get("couleur_b")
        self.COULEUR_J = settings.get("couleur_j")
        self.PREMIER_COUP = settings.get("premier_c")
        self.BONUS = settings.get("bonus")
        self.PROFONDEUR = 4

        self.buffer = 1
        self.nb_coups_ia = 0

        # Gestion du premier tour
        if self.PREMIER_COUP == "bot" : 
            self.joueur_actuel = 2
        elif self.PREMIER_COUP == "joueur": 
            self.joueur_actuel = 1
        else : 
            self.joueur_actuel = random.randint(1,2)
        
        # Gestion des couleur
        if self.COULEUR_IA == self.COULEUR_J :
            if self.COULEUR_J == "yellow" :
                self.COULEUR_IA = "red"
            else :
                self.COULEUR_IA = "yellow"

        self.grille = Plateau(lignes=self.NB_LIGNES, colones=self.NB_COLS, win_conditon=self.WIN_COND)
        self.jeu_actif = False # attendre l'affichage complet avant de lancer sinon ca bug 

        # Configuration UI
        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        add_bakground(self.canva, "images/bg.jpg")
        
        # Boutons de navigation
        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)
        if self.BONUS == "undo" or self.BONUS == "all" :
            self.undo = add_canvas_bouton(self.canva, "images/undo_bonus.png", (HEIGHT//10, HEIGHT//10), (WIDTH//8, HEIGHT//2), self.action_undo, True, 20)
        if self.BONUS == "bombe"  or self.BONUS == "all": 
            self.bombe = add_canvas_bouton(self.canva, "images/bouton_bombe.png", (HEIGHT//10, HEIGHT//10), (WIDTH//8 - HEIGHT//8, HEIGHT//2), self.activer_mode_bombe, True, 20)

        # Avatars
        add_canvas_img(self.canva, "images/gentil_idle.png", (150, (int)(HEIGHT*0.75)), ((int)(HEIGHT*0.3), (int)(HEIGHT*0.3)))
        add_canvas_img(self.canva, "images/mechant_idle.png", ((int)(WIDTH*0.85), (int)(HEIGHT*0.75)), ((int)(HEIGHT*0.35), (int)(HEIGHT*0.35)))

        afficher_plateau(self.canva, self.NB_COLS, self.NB_LIGNES)

        self.fleche_id = init_fleche(self.canva)
        self.canva.bind('<Motion>', lambda event: bouger_fleche(event, self.canva, self.fleche_id))
        self.canva.bind('<Button-1>', self.clic_souris)

        self.overlay_id = self.canva.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple='gray50')
        
        self.pions_visuels = [[] for i in range(self.NB_COLS)]
        self.historique_coups = []
        self.active_bombe = False
        self.anim_en_cours = False

        # Play
        self.btn_start_id = add_canvas_bouton(self.canva, "images/bouton_ready.png",(150, 150), (WIDTH//6, HEIGHT//2), self.lancer_la_game,True, 20)

    def lancer_la_game(self):
        self.canva.delete(self.btn_start_id)
        if hasattr(self, 'overlay_id'):
            self.canva.delete(self.overlay_id)
        
        self.jeu_actif = True
        self.canva.bind('<Button-1>', self.clic_souris)

        if self.joueur_actuel == 2:
            self.canva.after(500, self.tour_bot)
    
    def annuler_un_seul_coup(self):
        if not self.historique_coups:
            return False

        col, pion_id = self.historique_coups.pop()
        self.canva.delete(pion_id)
        self.grille.undo(col)
        return True

    def action_undo(self):
        if self.anim_en_cours: 
            return

        if not self.historique_coups:
            return

        if self.jeu_actif :
            self.annuler_un_seul_coup()
            self.annuler_un_seul_coup()
            self.joueur_actuel = 1

            self.reactiver_jeu()    
        else:
            if self.joueur_actuel == 2 :
                self.annuler_un_seul_coup()
                self.annuler_un_seul_coup()
                self.joueur_actuel = 1
            else :
                self.annuler_un_seul_coup()
                self.joueur_actuel = 1
        
        self.reactiver_jeu()
        self.canva.delete(self.undo)
        # print("Retour Ok")

    def reactiver_jeu(self):
        self.jeu_actif = True
        self.canva.bind('<Button-1>', self.clic_souris)
        self.canva.delete("message_fin")

    def activer_mode_bombe(self):
        if not self.jeu_actif or self.joueur_actuel != 1:
            return

        self.active_bombe = not self.active_bombe 
        
        if self.active_bombe :
            self.canva.config(cursor="crosshair")
        else:
            self.canva.config(cursor="")

    def lacher_bombe(self, col):
        if self.grille.fill_matrice[col] == 0:
            self.mode_bombe = False
            self.canva.config(cursor="")
            return

        self.grille.power_bomb(col)

        for pion_id in self.pions_visuels[col]:
            self.canva.delete(pion_id)
        
        self.pions_visuels[col] = []

        self.historique_coups = [coup for coup in self.historique_coups if coup[0] != col]

        # 5. Fin du tour
        self.active_bombe = False
        self.canva.delete(self.bombe)

        self.joueur_actuel = 3 - self.joueur_actuel
        if self.joueur_actuel == 2:
            self.canva.after(500, self.tour_bot)

    def obtenir_colonne_aleatoire(self):
        
        cols_valides = [c for c in range(self.grille.c) if self.grille.fill_matrice[c] < self.grille.l]
        if cols_valides:
            return random.choice(cols_valides)
        return 0

    def clic_souris(self, event):
        if not self.jeu_actif or self.joueur_actuel != 1:
            return

        grid_data = getattr(self.canva, 'grid_data', None)
        if not grid_data: return

        if grid_data['start_x'] <= event.x <= grid_data['start_x'] + grid_data['largeur_totale']:
            col = int((event.x - grid_data['start_x']) // grid_data['taille'])
            if 0 <= col < self.grille.c:
                if self.active_bombe :
                    self.lacher_bombe(col)
                else :
                    self.jouer_coup(col)
    
    def jouer_coup(self, col):
        if self.anim_en_cours: return

        if self.grille.fill_matrice[col] >= self.grille.l:
            print("Erreur")
            return

        res = self.grille.play(col, self.joueur_actuel)
        if res == 1:
            print("Colonne pleine")
            return

        ligne_jouee = res[0]
        couleur = self.COULEUR_J if self.joueur_actuel == 1 else self.COULEUR_IA
        
        # On verrouille le jeu
        self.anim_en_cours = True 
        self.canva.unbind('<Button-1>')

        def fin_du_mouvement():
            self.anim_en_cours = False 
 
            if self.jeu_actif:
                 self.canva.bind('<Button-1>', self.clic_souris)

            fini, etat = victoire_ou_nul(self.grille, self.joueur_actuel)

            if fini:
                self.jeu_actif = False
                if etat == 1:
                    pions_gagnants = self.trouver_pions_gagnants(self.joueur_actuel)
                    self.surligner_victoire(pions_gagnants)
                self.fin_de_partie(etat)
                return

            self.joueur_actuel = 3 - self.joueur_actuel
            if self.joueur_actuel == 2:
                self.canva.after(500, self.tour_bot)

        pion_id = ajouter_pion(self.canva, ligne_jouee, col, couleur, finish=fin_du_mouvement)

        self.pions_visuels[col].append(pion_id)
        self.historique_coups.append((col, pion_id))
    def trouver_pions_gagnants(self, joueur):
        """
        Scanne le plateau pour trouver les N pions alignés.
        Retourne une liste de tuples (ligne, colonne).
        """
        # On récupère la matrice (attribut 'matrice' dans ton Plateau.py)
        matrice = getattr(self.grille, 'matrice', [])
        
        rows = self.NB_LIGNES
        cols = self.NB_COLS
        N = self.WIN_COND

        # Directions: Horizontal, Vertical, Diagonale Descendante (\), Diagonale Montante (/)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(rows):
            for c in range(cols):
                # CORRECTION ICI : On accède à matrice[r][c] et non [c][r]
                try:
                    if matrice[r][c] != joueur: continue 
                except IndexError:
                    continue 

                for dr, dc in directions:
                    ligne_test = [(r, c)]
                    for k in range(1, N):
                        nr, nc = r + dr * k, c + dc * k
                        
                        # Vérification des limites du plateau
                        if 0 <= nr < rows and 0 <= nc < cols:
                            try:
                                if matrice[nr][nc] == joueur:
                                    ligne_test.append((nr, nc))
                                else:
                                    break
                            except IndexError: break
                        else:
                            break
                    
                    if len(ligne_test) == N:
                        return ligne_test
        return []
    
    def surligner_victoire(self, pions):
        if not pions: return
        
        grid_data = getattr(self.canva, 'grid_data', None)
        if not grid_data: return

        # Couleur de la victoire (Vert fluo)
        COULEUR_VICTOIRE = "#00FF00" 
        EPAISSEUR = 5

        taille = grid_data['taille']
        start_x = grid_data['start_x']
        start_y = grid_data['start_y']

        for r, c in pions:
            
            x0 = start_x + c * taille + 5 
            y0 = start_y + r * taille + 5 
            
            x1 = x0 + taille - 10
            y1 = y0 + taille - 10

            self.canva.create_oval(x0, y0, x1, y1, outline=COULEUR_VICTOIRE, width=EPAISSEUR, tags="message_fin")
    
    def tour_bot(self):
        if not self.jeu_actif: return
        self.canva.unbind('<Button-1>')

        def process_ia():
            col = -1
            if self.DIFF == "Hardcore":
                col = meilleur_coup(self.grille, self.PROFONDEUR)      
            elif self.DIFF == "Normal":
                if self.buffer == 1:
                    col = meilleur_coup(self.grille, self.PROFONDEUR)
                    if self.nb_coups_ia % 3 == 0: self.buffer = 0
                else:
                    col = self.obtenir_colonne_aleatoire()
                    self.buffer = 1     
            elif self.DIFF == "Facile":
                if self.buffer == 1:
                    col = meilleur_coup(self.grille, self.PROFONDEUR)
                    if self.nb_coups_ia % 2 == 0: self.buffer = 0
                else:
                    col = self.obtenir_colonne_aleatoire()
                    self.buffer = 1

            self.nb_coups_ia += 1
            self.canva.after(0, lambda: self.action_bot_post_calcul(col))

        thread = threading.Thread(target=process_ia)
        thread.daemon = True 
        thread.start()

    def action_bot_post_calcul(self, col):
        self.jouer_coup(col)
        if self.jeu_actif:
            self.canva.bind('<Button-1>', self.clic_souris)

    def fin_de_partie(self, etat):
        msg = "MATCH NUL"
        couleur_texte = "white"
        
        if etat == 1:
            if self.joueur_actuel == 1:
                msg = "VICTOIRE !"
                couleur_texte = "#00FF00"
            else:
                msg = "DÉFAITE..."
                couleur_texte = "#FF0000"

        self.canva.create_rectangle(WIDTH//2 - 200, 50, WIDTH//2 + 200, 150, fill="black", outline="white", width=2, tags="message_fin")
        
        self.canva.create_text(WIDTH//2, 100, text=msg, font=("Arial", 40, "bold"), fill=couleur_texte, tags="message_fin")

if __name__ == "__main__":
    app = App()
    app.changer_de_page(Acceuil)
    app.mainloop()