## @file bot_MinMax.py
## Fonctions d'implémentations d'un bot utilisant MinMax

from Plateau import Plateau
import numpy as np
import multiprocessing

def victoire_ou_nul(grille, joueur):
    """
    @brief Vérifie l'état de la partie pour un joueur donné (Victoire ou nul)
    @param grille Plateau du jeu en cours
           joueur Humain ou bot 
    @return (True, 1) si victoire du joueur
            (True, 0) si match nul
            (False, -1) sinon
    """
    if check_victoire_matrice(grille, joueur):
        return (True, 1)
    if est_pleine(grille):
        return (True, 0)
    return (False, -1)

def est_pleine(grille):
    """
    @brief Vérifie si la grille est pleine (match nul)
    @param grille Plateau du jeu en cours
    @return True si la grille est pleine
            False sinon
    """
    return all(grille.fill_matrice[col] >= grille.l for col in range(grille.c))

def check_victoire_matrice(grille, joueur):
    """
    @brief Vérifie si joueur a gagné. Ici, nous n'utilisons pas les bitboards.
    @param grille Plateau du jeu en cours
           joueur Humain ou bot 
    @return True si le joueur a une victoire 
            False sinon
    """
    mat = grille.matrice
    l, c, w = grille.l, grille.c, grille.win

    # Horizontale
    for r in range(l):
        for col in range(c - w + 1):
            window = mat[r, col:col+w]
            if np.all(window == joueur):
                return True
    # Verticale
    for col in range(c):
        for r in range(l - w + 1):
            window = mat[r:r+w, col]
            if np.all(window == joueur):
                return True
    # Diagonale \
    for r in range(l - w + 1):
        for col in range(c - w + 1):
            if all(mat[r+i, col+i] == joueur for i in range(w)):
                return True
    # Diagonale /
    for r in range(w - 1, l):
        for col in range(c - w + 1):
            if all(mat[r-i, col+i] == joueur for i in range(w)):
                return True
    return False


def quel_coup_matrice(grille, joueur):
    """
    @brief Vérifie si il existe un coup gagnant immédiat pour joueur et le renvoit immédiatement si il existe. Ici, nous n'utilisons pas les bitboards.
    @param grille Plateau du jeu en cours
        joueur Humain ou bot 
    @return Renvoit le coup gagnant si il existe
            -1 sinon
    """
    for col in range(grille.c):
        if grille.fill_matrice[col] >= grille.l:
            continue
        grille.play(col, joueur)
        if check_victoire_matrice(grille, joueur):
            grille.undo(col)
            return col
        grille.undo(col)
    return -1

def coup_bloquant(grille, adversaire):
    """
    @brief Vérifie si il existe un coup gagnant immédiat pour adversaire et le renvoit immédiatement si il existe. Ici, nous n'utilisons pas les bitboards.
    @param grille Plateau du jeu en cours
        joueur Humain ou bot 
    @return Renvoit le coup permettant de bloquer l'adversaire si il existe
            -1 sinon
    """
    for col in range(grille.c):
        if grille.fill_matrice[col] >= grille.l:
            continue
        grille.play(col, adversaire)
        if check_victoire_matrice(grille, adversaire):
            grille.undo(col)
            return col
        grille.undo(col)
    return -1



def evaluate_window(window, joueur_max, joueur_min):

    """
    @brief Évalue heuristiquement une fenêtre de 4 cases pour le MinMax.
    @param window Liste/array de 4 entiers (0 = vide, 1 = humain, 2 = IA)
           joueur_max Entier du joueur à maximiser (ex. 2 pour l'IA)
           joueur_min Entier du joueur à minimiser (ex. 1 pour l'humain)
    @return Renvoit le score de la fenêtre (positif si favorable à joueur_max, négatif si favorable à joueur_min)
    """

    score = 0
    window = list(window)
    count_max = window.count(joueur_max)
    count_min = window.count(joueur_min)
    count_empty = window.count(0)

    # Opportunités / menaces
    if count_max == 4:
        score += 100000
    elif count_max == 3 and count_empty == 1:
        score += 120
    elif count_max == 2 and count_empty == 2:
        score += 15

    if count_min == 3 and count_empty == 1:
        score -= 100
    elif count_min == 2 and count_empty == 2:
        score -= 8

    return score

def score_position(grille, joueur_max=2, joueur_min=1):
    """
    @brief Calcule le score heuristique global d'une position pour le MinMax.
    @param grille Plateau du jeu en cours
           joueur_max Joueur à maximiser (ex. 2 pour l'IA)
           joueur_min Joueur à minimiser (ex. 1 pour l'humain)
    @return Renvoit le score global (positif si favorable à joueur_max, négatif si favorable à joueur_min)
    """

    mat = grille.matrice
    l, c, w = grille.l, grille.c, grille.win
    score = 0

    # Bonus centre (favorise colonnes centrales)
    center = c // 2
    center_array = mat[:, center]
    score += 3 * np.count_nonzero(center_array == joueur_max)

    # Horizontal
    for r in range(l):
        for col in range(c - w + 1):
            window = mat[r, col:col+w].tolist()
            score += evaluate_window(window, joueur_max, joueur_min)

    # Vertical
    for col in range(c):
        for r in range(l - w + 1):
            window = mat[r:r+w, col].tolist()
            score += evaluate_window(window, joueur_max, joueur_min)

    # Diagonale \
    for r in range(l - w + 1):
        for col in range(c - w + 1):
            window = [mat[r+i, col+i] for i in range(w)]
            score += evaluate_window(window, joueur_max, joueur_min)

    # Diagonale /
    for r in range(w - 1, l):
        for col in range(c - w + 1):
            window = [mat[r-i, col+i] for i in range(w)]
            score += evaluate_window(window, joueur_max, joueur_min)

    return score

# === MinMax (BASIQUE, SANS alpha-beta) ===

def colonnes_ordonnees(grille):
    """
    @brief Génère la liste des colonnes jouables dans un ordre optimisé (centre → bords).
    @param grille Plateau du jeu en cours
    @return Renvoit la liste des indices de colonnes jouables, triées par priorité (centre en premier)
    """
    c = grille.c
    centre = c // 2
    ordre = []
    for d in range(c):
        left = centre - d
        right = centre + d
        if 0 <= left < c:
            ordre.append(left)
        if 0 <= right < c and right != left:
            ordre.append(right)
    return [col for col in ordre if grille.fill_matrice[col] < grille.l]

def minmax(grille, profondeur, maximising=True):
    """
    @brief Calcule le score d'une position par MinMax sur la matrice.
    @param grille Plateau du jeu en cours
           profondeur Profondeur de recherche restante 
           maximising Booléen : True si c'est le tour du joueur à maximiser (IA=2), False sinon (humain=1)
    @return Renvoit le score évalué de la position (positif si favorable à l'IA, négatif si favorable à l'humain)
    """

    # États terminaux
    if check_victoire_matrice(grille, 2):
        return 1000000
    if check_victoire_matrice(grille, 1):
        return -1000000
    if est_pleine(grille) or profondeur == 0:
        return score_position(grille, joueur_max=2, joueur_min=1)

    cols = colonnes_ordonnees(grille)
    if maximising:
        best = -10**9
        for col in cols:
            grille.play(col, 2)
            val = minmax(grille, profondeur - 1, maximising=False)
            grille.undo(col)
            if val > best:
                best = val
        return best
    else:
        best = 10**9
        for col in cols:
            grille.play(col, 1)
            val = minmax(grille, profondeur - 1, maximising=True)
            grille.undo(col)
            if val < best:
                best = val
        return best

def eval_coup(args):
    """Fonction pour multiprocessing"""
    grille, col, profondeur = args
    grille.play(col, 2)
    score = minmax(grille, profondeur - 1, maximising=False)
    grille.undo(col)
    return col, score

def meilleur_coup(grille, profondeur):
    """
    @brief Sélectionne le meilleur coup pour l'IA en priorisant: coup gagnant, blocage, puis MinMax. Pour l'algorithme Minmax, on utilise le multiprocesing.
    @param grille Plateau du jeu en cours
           profondeur Profondeur de recherche pour MinMax
    @return Renvoit l'index de la colonne choisie pour jouer (0..grille.c-1)
    """
    # 1) Coup gagnant immédiat
    cg = quel_coup_matrice(grille, 2)
    if cg != -1:
        return cg

    # 2) Blocage
    cb = coup_bloquant(grille, 1)
    if cb != -1:
        return cb

    # 3) MinMax
    best_score = -10**9
    best_col = None

    cols = colonnes_ordonnees(grille)
    args_list = [(Plateau(grille.l, grille.c, grille.win), col, profondeur) for col in cols]

    for i, col in enumerate(cols):
            args_list[i][0].matrice = grille.matrice.copy()
            args_list[i][0].fill_matrice = grille.fill_matrice.copy()
            args_list[i][0].bitboards = grille.bitboards.copy()

    with multiprocessing.Pool(processes=min(len(cols), multiprocessing.cpu_count())) as pool :
        results = pool.map(eval_coup, args_list)

    best_col, best_score = max(results, key=lambda x : x[1])
    return best_col


##Il me reste ça refaire et à doxygen
def partie_vs_bot(grille, profondeur=4):
    joueur = 1  # humain commence

    print("\n=== DÉBUT DE LA PARTIE ===\n")

    while True:
        # Affichage console
        for ligne in grille.matrice:
            print(" | ".join(str(x) for x in ligne))
        print("-" * (grille.c * 4))

        # Tour du joueur humain
        if joueur == 1:
            col = input(f"\nÀ toi de jouer ! Choisis une colonne (0-{grille.c - 1}) : ")
            try:
                col = int(col)
            except ValueError:
                print("Entre un nombre valide.")
                continue
            if col < 0 or col >= grille.c:
                print("Colonne hors limites.")
                continue
            if grille.fill_matrice[col] >= grille.l:
                print("Colonne pleine.")
                continue

            grille.play(col, 1)

            term, etat = victoire_ou_nul(grille, 1)
            if term:
                if etat == 1:
                    print("⚠️ Victoire du joueur 1 !")
                elif etat == 0:
                    print("😐 Match nul !")
                break

        # Tour de l'IA
        else:
            print("\n🤖 L'IA réfléchit...")
            col = meilleur_coup(grille, profondeur)
            print(f"L'IA joue en colonne {col}")
            grille.play(col, 2)

            term, etat = victoire_ou_nul(grille, 2)
            if term:
                if etat == 1:
                    print("⚠️ Victoire de l'IA !")
                elif etat == 0:
                    print("😐 Match nul !")
                break

        # Alterner joueur
        joueur = 3 - joueur  # 1 ↔ 2

    print("\n=== FIN DE PARTIE ===")

if __name__ == "__main__":
    g = Plateau(lignes=6, colones=7, win_conditon=4)
    partie_vs_bot(g, profondeur=4)
