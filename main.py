from tkinter_fonction import *
from bot2 import victoire_ou_nul, meilleur_coup

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

        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        add_bakground(self.canva, "images/bg.jpg")
        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), ((HEIGHT//10)//2 + 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Param_jeu), True, 20)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

        afficher_plateau(self.canva, 12,7)


if __name__ == "__main__":
    app = App()
    app.changer_de_page(Acceuil)
    app.mainloop()