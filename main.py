from tkinter_fonction import *
from bot2 import victoire_ou_nul, meilleur_coup
from Plateau import Plateau
import threading
import random

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
            "Bonus": ["nothing","bombe", "help", "undo"],
            "couleur joueur": ["cyan", "red", "orange", "yellow"],
            "couleur bot":["cyan", "red", "orange", "yellow"]
        }

        DEFAUTS = {
            "Largeur": 7,          
            "Hauteur": 6,          
            "Win Condition": 4,    
            "Difficulté": "Normal",
            "Permier coup": "random",
            "couleur joueur": "red",
            "couleur bot": "yellow"
        }

        self.menu = MenuDeroulant(self.canva, WIDTH//2, HEIGHT//7, CONFIG_DATA)

        for cle, valeur in DEFAUTS.items():
            index_par_defaut = CONFIG_DATA[cle].index(valeur)
            self.menu.choices[cle] = index_par_defaut


        add_canvas_bouton(self.canva, "images/bouton_up.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 - 50), lambda: self.menu.scroll(-1), True, 5)
        add_canvas_bouton(self.canva, "images/bouton_down.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 + 50), lambda: self.menu.scroll(1), True, 5)

        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Acceuil), True, 20)
        
        add_canvas_bouton(
            self.canva, 
            "images/boutonNext.png", 
            (HEIGHT//10, HEIGHT//10), 
            (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT) - HEIGHT//10), 
            self.lancer_partie,
            True, 
            20
        )

    def lancer_partie(self):
        """ Cette fonction ne s'exécute que quand on CLIQUE sur le bouton Next """
        
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
        nom_diff = config["Difficulté"][choix["Difficulté"]]
        

        # Création du colis de données
        parametres = {
            "largeur": largeur,
            "hauteur": hauteur,
            "win": win_cond,
            "diff": nom_diff,
            "couleur_j": nom_coul_j,
            "couleur_b": nom_coul_b,
            "premier_c" : premier_c
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
        self.PROFONDEUR = 4

        self.buffer = 1
        self.nb_coups_ia = 0

        if self.PREMIER_COUP == "bot" : 
            self.joueur_actuel = 2
        elif self.PREMIER_COUP == "joueur": self.joueur_actuel = 1
        else : self.joueur_actuel = random.randint(1,2)
        print(self.joueur_actuel)

        if self.COULEUR_IA == self.COULEUR_J :
            if self.COULEUR_J == "yellow" :
                self.COULEUR_IA = "red"
            else :
                self.COULEUR_IA = "yellow"

        
        self.grille = Plateau(lignes=self.NB_LIGNES, colones=self.NB_COLS, win_conditon=self.WIN_COND)
        self.jeu_actif = True

        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        add_bakground(self.canva, "images/bg.jpg")
        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

        add_canvas_img(self.canva, "images/gentil_idle.png", (150, (int)(HEIGHT*0.75)), ((int)(HEIGHT*0.3), (int)(HEIGHT*0.3)))
        add_canvas_img(self.canva, "images/mechant_idle.png", ((int)(WIDTH*0.85), (int)(HEIGHT*0.75)), ((int)(HEIGHT*0.35), (int)(HEIGHT*0.35)))

        afficher_plateau(self.canva, self.NB_COLS, self.NB_LIGNES)

        self.fleche_id = init_fleche(self.canva)
        self.canva.bind('<Motion>', lambda event: bouger_fleche(event, self.canva, self.fleche_id))

        self.canva.bind('<Button-1>', self.clic_souris)

        # Important sinon l'ia joue avant que le jeu soit afficher
        if self.joueur_actuel == 2:
            self.canva.after(1000, self.tour_bot)
    
    def obtenir_colonne_aleatoire(self):
        """Sélectionne une colonne non pleine au hasard"""
        # On regarde quelles colonnes ne sont pas encore remplies
        cols_valides = [c for c in range(self.grille.c) if self.grille.fill_matrice[c] < self.grille.l]
        if cols_valides:
            return random.choice(cols_valides)
        return 0 # Sécurité si tout est plein

    def clic_souris(self, event):
        """ Gère le clic du joueur humain """
        if not self.jeu_actif or self.joueur_actuel != 1:
            return

        grid_data = getattr(self.canva, 'grid_data', None)
        if not grid_data: return

        if grid_data['start_x'] <= event.x <= grid_data['start_x'] + grid_data['largeur_totale']:
            col = int((event.x - grid_data['start_x']) // grid_data['taille'])

            if 0 <= col < self.grille.c:
                self.jouer_coup(col)
    
    def jouer_coup(self, col):
        """ Exécute un coup (Humain ou Bot) """
        
        res = self.grille.play(col, self.joueur_actuel)

        if res == 1:
            print("Colonne pleine ou erreur")
            return

        ligne_jouee = res[0]

        couleur = self.COULEUR_J if self.joueur_actuel == 1 else self.COULEUR_IA
        ajouter_pion(self.canva, ligne_jouee, col, couleur)

        fini, etat = victoire_ou_nul(self.grille, self.joueur_actuel)

        if fini:
            self.jeu_actif = False
            self.fin_de_partie(etat)
            return

        self.joueur_actuel = 3 - self.joueur_actuel
        if self.joueur_actuel == 2:
            self.canva.after(500, self.tour_bot)
    
    def tour_bot(self):
        """ Lance la réflexion de l'IA dans un thread parallèle """
        if not self.jeu_actif: return

        self.canva.unbind('<Button-1>')

        def process_ia():
            col = -1
            
            if self.DIFF == "Hardcore":
                col = meilleur_coup(self.grille, self.PROFONDEUR)      
            elif self.DIFF == "Normal":
                if self.buffer == 1:
                    col = meilleur_coup(self.grille, self.PROFONDEUR)
                    if self.nb_coups_ia % 3 == 0:
                        self.buffer = 0
                else:
                    col = self.obtenir_colonne_aleatoire()
                    self.buffer = 1
                    
            elif self.DIFF == "Facile":
                if self.buffer == 1:
                    col = meilleur_coup(self.grille, self.PROFONDEUR)
                    if self.nb_coups_ia % 2 == 0:
                        self.buffer = 0
                else:
                    col = self.obtenir_colonne_aleatoire()
                    self.buffer = 1

            self.nb_coups_ia += 1
            self.canva.after(0, lambda: self.action_bot_post_calcul(col))

        thread = threading.Thread(target=process_ia)
        thread.daemon = True 
        thread.start()

    def action_bot_post_calcul(self, col):
        """ Cette fonction est appelée par le main thread quand l'IA a fini """
        print(f"L'IA joue en {col}")
        
        self.jouer_coup(col)
        if self.jeu_actif:
            self.canva.bind('<Button-1>', self.clic_souris)

    def fin_de_partie(self, etat):
        """ Affiche le résultat """
        msg = ""
        if etat == 1:
            if self.joueur_actuel == 1 :
                time.sleep(500)
                add_canvas_img(self.canva, "images/Win.png", (WIDTH//2,HEIGHT//2), (WIDTH, HEIGHT))
                add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
                add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

            elif self.joueur_actuel == 2:
                time.sleep(500)
                add_canvas_img(self.canva, "images/lose.png", (WIDTH//2,HEIGHT//2), (WIDTH, HEIGHT))
                add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
                add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

        else:
            msg = "MATCH NUL !"
            color = "white"


if __name__ == "__main__":
    app = App()
    app.changer_de_page(Acceuil)
    app.mainloop()