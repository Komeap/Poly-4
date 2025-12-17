from tkinter_fonction import *
from bot2 import victoire_ou_nul, meilleur_coup
from Plateau import Plateau

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
        
        # On applique la taille ET la position
        self.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cordinate, y_cordinate))
        ## page en cours -> page qui est entrain d'être utiliser
        self.page_en_cours = None
        self.resizable(width=False, height=False)

        

    ## @brief CHangement de page, supprime celle en cours
    ## et en met une autre sans oublier de redéfinir le self
    def changer_de_page(self, page):
        if self.page_en_cours:
            self.page_en_cours.destroy()

        self.page_en_cours = page(parent=self)
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
    def __init__(self, parent):
        super().__init__(parent, bg="")


        # Création du canva de la page
        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        # bouton back next de la page
        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Acceuil), True, 20)
        add_canvas_bouton(self.canva, "images/boutonNext.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT) - HEIGHT//10), lambda: (self.menu.print_all_choices(),app.changer_de_page(Jeu)), True, 20)
        add_bakground(self.canva, "images/parametre_bg.png") # ajout background

        ##video transition
        ##lancer_video(self.canva, "images/run2.mp4")

        # Dictionnaire des paramétres et des valeurs
        CONFIG_DATA = {
            "": [],
            "Win Condition": [i for i in range(3,50)],
            "Largeur": [i for i in range(1,50)],
            "Hauteur": [i for i in range(1,50)],
            "Difficulté": ["Facile", "Normal", "Hardcore"],
            "Bonus": ["nothing","bombe", "help", "undo"],
            "couleur": ["bleu", "rouge", "orange", "jaune"]
        }

        # ajoute le Menu Déroulant des paramétre (cf.tkinter_fonction.py)
        self.menu = MenuDeroulant(self.canva, WIDTH//2, HEIGHT//7, CONFIG_DATA)

        # ajout des bouton de scroll du Menu déroulant
        add_canvas_bouton(self.canva, "images/bouton_up.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 - 50), lambda: self.menu.scroll(-1), True, 5)
        add_canvas_bouton(self.canva, "images/bouton_down.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 + 50), lambda: self.menu.scroll(1), True, 5)

class Jeu(tk.Frame):
    """
    @brief Réprésente la page de jeu 
    """
    def __init__(self, parent):
        super().__init__(parent, bg="")

        NB_LIGNES = 6
        NB_COLS = 7
        WIN_COND = 4
        
        self.grille = Plateau(lignes=NB_LIGNES, colones=NB_COLS, win_conditon=WIN_COND)
        self.joueur_actuel = 1
        self.jeu_actif = True

        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        add_bakground(self.canva, "images/bg.jpg")
        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

        afficher_plateau(self.canva, NB_COLS, NB_LIGNES)

        self.fleche_id = init_fleche(self.canva)
        self.canva.bind('<Motion>', lambda event: bouger_fleche(event, self.canva, self.fleche_id))

        self.canva.bind('<Button-1>', self.clic_souris)
    
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

        couleur = "red" if self.joueur_actuel == 1 else "yellow"
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
        """ Logique du bot """
        if not self.jeu_actif: return

        print("L'IA réfléchit...")
        # Appel à bot2.py pour trouver le meilleur coup
        col_bot = meilleur_coup(self.grille, profondeur=4)
        
        print(f"L'IA joue en {col_bot}")
        self.jouer_coup(col_bot)

    def fin_de_partie(self, etat):
        """ Affiche le résultat """
        msg = ""
        if etat == 1:
            msg = "VICTOIRE JOUEUR !" if self.joueur_actuel == 1 else "VICTOIRE BOT !"
            color = "green" if self.joueur_actuel == 1 else "red"
        else:
            msg = "MATCH NUL !"
            color = "white"

        # Affichage basique du texte de victoire au milieu
        self.canva.create_text(
            WIDTH//2, HEIGHT//2, 
            text=msg, 
            font=("Retro Gaming", 50, "bold"), 
            fill=color,
            stroke="black", strokewidth=2 # Contour noir si supporté par ta version tk
        )
        print(msg)


if __name__ == "__main__":
    app = App()
    app.changer_de_page(Acceuil)
    app.mainloop()