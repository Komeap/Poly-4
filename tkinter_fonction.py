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
    def __init__(self, canvas, x, y, nom, options=None, start_size=(HEIGHT//4, HEIGHT//3), scale=1.0, affiche=True, index=0, on_change=lambda i: None):
        self.canvas = canvas
        self.nom = nom
        self.ids = []
        self.on_change = on_change

        # choix options
        self.options = options if options else []
        self.index = index

        # dimension pour la resizer et l'effet de déroulement du menu
        w_redim = int(start_size[0] * scale)
        h_redim = int(start_size[1] * scale)
        size = (w_redim, h_redim)

        # si on affiche la case, on veut pas afficher certain case pour pouvoir d&rouler jusqu'au bout sans avoir de case vide
        if affiche:
            # Image de fond
            self.img_id = add_canvas_img(canvas, "images/param_case.png", (x,y), size)
            self.ids.append(self.img_id)

            # titre des paramétre
            self.texte_nom = canvas.create_text(
                x,
                y - (size[1]//2) + int(35*scale),
                text=f"{nom}",
                font=("Retro Gaming", int(15*scale)),
                anchor='center',
                fill="black"
            )
            self.ids.append(self.texte_nom) # ajout au id pour pas le perdre

            # Valeur affichée
            if self.options:
                valeur = self.options[self.index]
            else:
                valeur = ""
            
            # valeur du paramétre affichage
            self.texte_valeur = canvas.create_text(
                x,
                y + 25*scale,
                text=valeur,
                font=("Retro Gaming", int(20*scale)),
                anchor='center',
                fill="black"
            )
            self.ids.append(self.texte_valeur)

            # Bouton up
            self.btn_u_id = add_canvas_bouton(
                canvas,
                "images/bouton_up.png",
                (HEIGHT//25, HEIGHT//25),
                (x , y - size[1]//7),
                self.next_value,
                True,
                10
            )
            self.ids.append(self.btn_u_id)

            # Bouton down
            self.btn_d_id = add_canvas_bouton(
                canvas,
                "images/bouton_down.png",
                (HEIGHT//25, HEIGHT//25),
                (x, y + size[1]//2.7),
                self.prev_value,
                True,
                10
            )
            self.ids.append(self.btn_d_id)

    # Changer de valeur vers HAUT
    def next_value(self):
        if not self.options: 
            return
        self.index = (self.index + 1) % len(self.options) # modification de l'index ( si on fait +1 a l'index max ca remet au debut (modulo %))
        self.canvas.itemconfig(self.texte_valeur, text=self.options[self.index]) # Changelent des valeurs
        self.on_change(self.index)  # Fait le changement

    # Changer de valeur vers BAS (Pareil que haut mais avec - 1)
    def prev_value(self):
        if not self.options: return
        self.index = (self.index - 1) % len(self.options)
        self.canvas.itemconfig(self.texte_valeur, text=self.options[self.index])
        self.on_change(self.index)

    # détruit la case pour l'animation
    def destroy(self):
        for item_id in self.ids:
            self.canvas.delete(item_id) # Détruire tous puisque tous bouge 

class MenuDeroulant:
    def __init__(self, canvas, x, y_start, CONFIG_DATA):
        self.canvas = canvas
        self.x = x
        self.y_start = y_start
        # Gestion des valeur des paramétres
        self.params_data = list(CONFIG_DATA.keys())
        self.config =  CONFIG_DATA
        self.choices = {key: 0 for key in CONFIG_DATA}
        
        #Gestion des index
        self.current_index = 0
        self.max_visible = 3
        self.ecart = HEIGHT // 3 + 20
        
        # Positions cible après mouvement
        self.positions_y_fixes = [
            self.y_start,                # Position haut
            self.y_start + self.ecart,   # Position millieu
            self.y_start + self.ecart*2  # Position bas
        ]
        
        # % de la taille pour l'effet de style
        self.tailles_fixes = [0.7, 1.0, 0.7] 

        self.active_cases = []
        
        # Variable pour empêcher de spammer le bouton pendant l'animation
        self.is_animating = False
        
        self.update_display_instantane()

    def update_display_instantane(self):
        for case in self.active_cases: 
            case.destroy()
        self.active_cases = []

        for j in range(self.max_visible):
            data_index = self.current_index + j

            if data_index >= len(self.params_data): 
                break

            nom = self.params_data[data_index]
            options = self.config.get(nom, [])
            y = self.positions_y_fixes[j]
            s = self.tailles_fixes[j]

            saved_index = self.choices.get(nom, 0)

            if nom == "":
                new_case = Param_case(self.canvas, self.x, y, self.params_data[data_index], scale=s, affiche=False)
                self.active_cases.append(new_case)
            else :
                new_case = Param_case(self.canvas, self.x, y,nom, options, scale=s ,index=self.choices[nom], on_change=lambda idx, cle=nom: self.save_choice(cle, idx))
                self.active_cases.append(new_case)
    
    def save_choice(self, nom, idx):
        self.choices[nom] = idx

    def scroll(self, direction):
        if self.is_animating: return
        
        new_index = self.current_index + direction
        if not (0 <= new_index < len(self.params_data)): return


        self.animate_transition(direction)

    def animate_transition(self, direction):
        self.is_animating = True
        
        # CONFIGURATION DE L'ANIMATION
        steps = 3
        delay = 1
        
        def step_process(step):
            for case in self.active_cases:
                case.destroy()
            self.active_cases = []
            
            progress = step / steps 
            
            range_start = -1 if direction == -1 else 0
            range_end = self.max_visible if direction == -1 else self.max_visible + 1

            for j in range(range_start, range_end):
                data_index = self.current_index + j
                
                if data_index < 0 or data_index >= len(self.params_data):
                    continue

                nom = self.params_data[data_index]
                options = self.config.get(nom, [])
                
                start_y = self.y_start + (j * self.ecart)
                target_y = self.y_start + ((j - direction) * self.ecart)
                current_y = start_y + (target_y - start_y) * progress

                center_y = self.y_start + self.ecart
                dist = abs(current_y - center_y)
                ratio = dist / self.ecart
                if ratio > 1: ratio = 1
                current_scale = 1.0 - (ratio * 0.2)

                saved_index = self.choices.get(nom, 0)
                

                if nom == "":
                    case = Param_case(self.canvas, self.x, current_y, nom, scale=current_scale, affiche=False)
                    self.active_cases.append(case)
                else :
                    case = Param_case(self.canvas, self.x, current_y, nom, options, scale=current_scale, index=saved_index, on_change=lambda idx, cle=nom: self.save_choice(cle, idx))
                    self.active_cases.append(case)

            if step < steps:
                self.canvas.after(delay, lambda: step_process(step + 1))
            else:
                self.current_index += direction
                self.is_animating = False
                self.update_display_instantane()

        step_process(1)

    def print_all_choices(self):
        print("\n=== PARAMÈTRES ACTUELS ===")
        for nom in self.params_data:
            if nom == "": 
                continue  # lignes vides
            index = self.choices[nom]
            valeur = self.config[nom][index]
            print(f"{nom}: {valeur}")
        print("==========================\n")

def init_fleche(canva):

    img_pil = Image.open("images/fleche_in_game.png")
    
    taille = getattr(canva, 'taille_case', 50) 
    
    img_res = img_pil.resize((int(taille * 0.7), int(taille * 0.7)), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_res)

    canva.fleche_img = img_tk
    fleche_id = canva.create_image(-100, -100, image=img_tk, anchor=tk.CENTER)
    
    return fleche_id

def bouger_fleche(event, canva, fleche_id):
    grid_data = getattr(canva, 'grid_data', None)
    if not grid_data:
        return

    start_x = grid_data['start_x']
    start_y = grid_data['start_y']
    taille = grid_data['taille']
    cols = grid_data['cols']
    grille_l = grid_data['largeur_totale']

    mouse_x = event.x
    
    if start_x <= mouse_x <= start_x + grille_l:
        col_index = int((mouse_x - start_x) // taille)
        
        if 0 <= col_index < cols:
            center_x = start_x + (col_index * taille) + (taille // 2)

            pos_y = start_y - (taille // 1.5)
 
            canva.coords(fleche_id, center_x, pos_y)

            canva.itemconfigure(fleche_id, state='normal')
            return

def ajouter_pion(canva, ligne, col, couleur):
    """
    @brief Dessine un pion sur la grille
    @param ligne : Index de la ligne (0 en haut)
    @param col : Index de la colonne
    @param couleur : 'red' (Joueur 1) ou 'yellow' (Joueur 2 / Bot)
    """
    grid = getattr(canva, 'grid_data', None)
    if not grid: return

    start_x = grid['start_x']
    start_y = grid['start_y']
    taille = grid['taille']

    # Calcul du centre de la case
    x_center = start_x + (col * taille) + (taille // 2)
    y_center = start_y + (ligne * taille) + (taille // 2)

    # Rayon du pion (légèrement plus petit que la case)
    rayon = (taille // 2) - 5

    # Dessin du cercle (pion)
    pion_id = canva.create_oval(
        x_center - rayon, y_center - rayon,
        x_center + rayon, y_center + rayon,
        fill=couleur, outline="black", width=2
    )
    
    return pion_id

def afficher_plateau(canva, largeur, hauteur):
    
    m_larg = WIDTH*0.2
    m_haut = HEIGHT*0.2

    size_dispo_larg = abs(WIDTH - 2*(m_larg))
    size_dispo_haut = abs(HEIGHT - 2*(m_haut))

    size_case_1 = (int)(size_dispo_larg//largeur)
    size_case_2 = (int)(size_dispo_haut//hauteur)

    taille_case = min(size_case_1, size_case_2)

    grille_l = taille_case * largeur
    grille_h = taille_case * hauteur

    start_x = m_larg + (size_dispo_larg - grille_l)//2
    start_y = m_haut + (size_dispo_haut - grille_h)//2

    canva.taille_case = taille_case 
    canva.grid_data = {
        "start_x": start_x,
        "start_y": start_y,
        "taille": taille_case,
        "cols": largeur,
        "largeur_totale": grille_l
    }

    canva.image_cache = []
    
    pil_case = Image.open("images/One_case.png")
    case_redim = pil_case.resize((taille_case, taille_case), Image.LANCZOS)
    case_tk = ImageTk.PhotoImage(case_redim)
    canva.image_cache.append(case_tk)

    pil_border = Image.open("images/border.png")

    epaisseur_mur = taille_case // 4
    overlap = 2
    epaisseur_visuelle = epaisseur_mur + overlap

    w_visuel_horiz = grille_l + overlap
    h_visuel_verti = grille_h + overlap

    img_r = pil_border.resize((epaisseur_visuelle, h_visuel_verti), Image.LANCZOS)
    tk_r = ImageTk.PhotoImage(img_r)
    canva.image_cache.append(tk_r)

    img_l = pil_border.rotate(180).resize((epaisseur_visuelle, h_visuel_verti), Image.LANCZOS)
    tk_l = ImageTk.PhotoImage(img_l)
    canva.image_cache.append(tk_l)

    img_t = pil_border.rotate(90, expand=True).resize((w_visuel_horiz, epaisseur_visuelle), Image.LANCZOS)
    tk_t = ImageTk.PhotoImage(img_t)
    canva.image_cache.append(tk_t)

    img_b = pil_border.rotate(-90, expand=True).resize((w_visuel_horiz, epaisseur_visuelle), Image.LANCZOS)
    tk_b = ImageTk.PhotoImage(img_b)
    canva.image_cache.append(tk_b)

    center_grid_x = start_x + (grille_l // 2)
    center_grid_y = start_y + (grille_h // 2)

    canva.create_image(center_grid_x, start_y - (epaisseur_mur//2), image=tk_t, anchor=tk.CENTER)
    canva.create_image(center_grid_x, start_y + grille_h + (epaisseur_mur//2), image=tk_b, anchor=tk.CENTER)
    canva.create_image(start_x - (epaisseur_mur//2), center_grid_y, image=tk_l, anchor=tk.CENTER)
    canva.create_image(start_x + grille_l + (epaisseur_mur//2), center_grid_y, image=tk_r, anchor=tk.CENTER)
    

    for col in range(largeur):
        for lig in range(hauteur):
            pos_x = start_x + (col * taille_case) + (taille_case // 2)
            pos_y = start_y + (lig * taille_case) + (taille_case // 2)

            canva.create_image(pos_x, pos_y, image=case_tk, anchor=tk.CENTER)