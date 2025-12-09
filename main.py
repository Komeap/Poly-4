import Plateau as p
import tkinter as tk
from tkinter import font
import cv2
from PIL import Image, ImageTk
import time


##screen size
WIDTH, HEIGHT = 1350, 800

## @brief Ajout d'un image en bakground
## @param master Page dans la qu'elle on veut mettre
def add_bakground(master, image):
    image_originale = Image.open(image)
    image_redim = image_originale.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redim)

    bg_id = master.create_image(0, 0, image=photo, anchor="nw")
    master.tag_lower(bg_id)
    master.bg_image_cache = photo

def add_canvas_img(canvas, link, pos, size):
    img_pil = Image.open(link)
    img_res = img_pil.resize(size, Image.LANCZOS)
    img = ImageTk.PhotoImage(img_res)

    img_id = canvas.create_image(pos[0], pos[1], image=img ,anchor=tk.CENTER)

    if not hasattr(canvas, 'images_list'):
        canvas.images_list = []
    
    canvas.images_list.append(img)
    
    return img_id

def add_canvas_bouton(canvas, link, size, pos, cmd, hover, zoom):
    img_pil = Image.open(link)
    img_res = img_pil.resize(size, Image.LANCZOS)
    img_zoom = ImageTk.PhotoImage(img_pil.resize((size[0] + zoom, size[1] + zoom), Image.LANCZOS))
    img = ImageTk.PhotoImage(img_res)
    
    img_id = canvas.create_image(pos[0], pos[1], image=img ,anchor=tk.CENTER)
    

    def on_enter(event):
        canvas.itemconfig(img_id, image=img_zoom)

    def on_leave(event):
        canvas.itemconfig(img_id, image=img)

    canvas.tag_bind(img_id, "<Enter>", on_enter)
    canvas.tag_bind(img_id, "<Leave>", on_leave)

    canvas.tag_bind(img_id, "<Button-1>", lambda event: cmd())
    
    if hover :
        canvas.tag_bind(img_id, "<Enter>", lambda event: canvas.config(cursor="hand2"), add="+")
        canvas.tag_bind(img_id, "<Leave>", lambda event: canvas.config(cursor=""), add="+")

    if not hasattr(canvas, 'images'):
        canvas.images = []
        
    canvas.images.append(img)
    canvas.images.append(img_zoom)

    return img_id

def lancer_video(canvas, chemin_video, largeur=WIDTH, hauteur=HEIGHT +150):
    fermer_video(canvas)

    cap = cv2.VideoCapture(chemin_video)

    canvas.cap = cap
    canvas.video_en_cours = True

    def stream():
        if not getattr(canvas, 'video_en_cours', False):
            cap.release()
            canvas.delete("tag_video")
            return

        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame)
            img_pil = img_pil.resize((largeur, hauteur)) 
            img_tk = ImageTk.PhotoImage(image=img_pil)
            canvas.create_image(0, -50, anchor="nw", image=img_tk, tags="tag_video")
            canvas.image_ref = img_tk 
            canvas.after(33, stream)
        else:
            fermer_video(canvas)
    stream()

def fermer_video(canvas):
    canvas.video_en_cours = False
    if hasattr(canvas, 'cap') and canvas.cap.isOpened():
        canvas.cap.release()
    canvas.delete("tag_video")

class Param_case:
    def __init__(self, canvas, x, y, nom, size=(HEIGHT//4, HEIGHT//3)):
        self.canvas = canvas
        self.nom = nom
        self.size = size
        self.ids = []


        ## a remplcer par l'image 
        ##self.rect = canvas.create_rectangle(x, y, x + 200, y + 60, fill="gray")
        self.img_id = add_canvas_img(canvas, "images/param_case.png", (x,y), size)
        self.ids.append(self.img_id)

        self.texte_id = canvas.create_text(x, y-(size[1]//2) + 35, text=f"{nom}",font=("Retro Gaming", 15) , anchor='center', fill="black")
        self.ids.append(self.texte_id)

        self.btn_u_id = add_canvas_bouton(canvas, "images/bouton_up.png", (HEIGHT//25, HEIGHT//25), (x, y - size[1]//7 ), lambda: "", True, 10 )
        self.ids.append(self.btn_u_id)

        self.btn_d_id = add_canvas_bouton(canvas, "images/bouton_down.png", (HEIGHT//25, HEIGHT//25), (x, y + size[1]//2.7 ), lambda: "", True, 10 )
        self.ids.append(self.btn_d_id)

    def destroy(self):
        for item_id in self.ids:
            self.canvas.delete(item_id)

class MenuDeroulant:
    def __init__(self, canvas, x, y_start, liste_params):
        self.canvas = canvas
        self.x = x
        self.y_start = y_start
        self.params_data = liste_params
        
        self.current_index = 0 
        self.max_visible = 2
        self.ecart = HEIGHT//3 + 20
        
        self.active_cases = []
        
        self.update_display()

    def update_display(self):

        for case in self.active_cases:
            case.destroy()
        self.active_cases = []

        end_index = min(self.current_index + self.max_visible, len(self.params_data))
        
        for i in range(self.current_index, end_index):
            display_pos = i - self.current_index 
            
            y_pos = self.y_start + (display_pos * self.ecart)
            nom_param = self.params_data[i]

            new_case = Param_case(self.canvas, self.x, y_pos, nom_param)
            self.active_cases.append(new_case)

    def scroll(self, direction):
        new_index = self.current_index + direction
        
        if 0 <= new_index <= len(self.params_data) - self.max_visible:
            self.current_index = new_index
            self.update_display()
        elif 0 <= new_index < len(self.params_data):
             self.current_index = new_index
             self.update_display()

# ------- Différentes page -------- #

## @brief class maitre qui gére les différentes pages
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POLIC")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        ## page en cours -> page qui est entrain d'être utiliser
        self.page_en_cours = None

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

        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)
        
        add_bakground(self.canva, "images/Acceuil.jpg")
        add_canvas_bouton(self.canva, "images/bouton_play.png", ((WIDTH//4),HEIGHT//6), (WIDTH//2,(HEIGHT//12)*11), lambda: app.changer_de_page(Param_jeu), True, 35)
        add_canvas_bouton(self.canva, "images/bouton_close.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), app.destroy, True, 20)

class Param_jeu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="")
        
        self.canva = tk.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight(), highlightthickness=0, bg="grey")
        self.canva.pack(fill="both", expand=True)

        add_canvas_bouton(self.canva, "images/bouton_back.png", (HEIGHT//10, HEIGHT//10), (WIDTH - (HEIGHT//10)//2 - 5, (HEIGHT//10)//2 + 5), lambda: app.changer_de_page(Acceuil), True, 20)
        add_bakground(self.canva, "images/parametre_bg.png")

        ##video transition
        ##lancer_video(self.canva, "images/run2.mp4")

        mes_parametres = ["Win Condition", "Largeur", "Hauteur", "Difficulté", "Volume", "Luminosité"]

        self.menu = MenuDeroulant(self.canva, WIDTH//2, HEIGHT//3, mes_parametres)

        # --- BOUTONS DE SCROLL (Fixes sur le côté) ---
        # Bouton Monter (Scroll HAUT -> index diminue -> -1)
        add_canvas_bouton(self.canva, "images/bouton_up.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 - 50), lambda: self.menu.scroll(-1), True, 5)
        
        # Bouton Descendre (Scroll BAS -> index augmente -> 1)
        add_canvas_bouton(self.canva, "images/bouton_down.png", (50, 50), (WIDTH//2 + 250, HEIGHT//2 + 50), lambda: self.menu.scroll(1), True, 5)

        """
        x_depart = WIDTH//2
        y_depart = HEIGHT//2
        ecart = HEIGHT//3 +80 

        for i, nom in enumerate(mes_parametres):
            position_y = y_depart + (i * ecart)
            Param_case(self.canva, x_depart, position_y, nom)
        """




if __name__ == "__main__":
    app = App()
    app.changer_de_page(Acceuil)
    app.mainloop()