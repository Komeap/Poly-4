
# main.py
from Plateau import Plateau
import numpy as np

# === Victoire / nul (MATRICE uniquement) ===

def victoire_ou_nul(grille, joueur_affichage):
    """
    Renvoie (True, 1) si victoire du joueur affiché,
    (True, 0) si match nul,
    (False, -1) sinon
    """
    if check_win_matrix(grille, joueur_affichage):
        return (True, 1)
    if is_full(grille):
        return (True, 0)
    return (False, -1)

def is_full(grille):
    """True si la grille est pleine (match nul)."""
    return all(grille.fill_matrice[col] >= grille.l for col in range(grille.c))

def check_win_matrix(grille, joueur):
    """Vérifie si 'joueur' (1 ou 2) a une victoire dans la matrice."""
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

# === Détections immédiates ===

def quel_coup(grille, joueur_affichage):
    """
    Renvoie un coup gagnant immédiat pour le joueur j_affichage s'il existe, sinon -1.
    Utilise la matrice uniquement.
    """
    for col in range(grille.c):
        if grille.fill_matrice[col] >= grille.l:
            continue
        grille.play(col, joueur_affichage)
        if check_win_matrix(grille, joueur_affichage):
            grille.undo(col)
            return col
        grille.undo(col)
    return -1

def coup_bloquant(grille, adversaire):
    """
    Renvoie un coup qui bloque une victoire immédiate de l'adversaire, sinon -1.
    """
    for col in range(grille.c):
        if grille.fill_matrice[col] >= grille.l:
            continue
        grille.play(col, adversaire)
        if check_win_matrix(grille, adversaire):
            grille.undo(col)
            return col
        grille.undo(col)
    return -1

# === Heuristique ===

def evaluate_window(window, joueur_max, joueur_min):
    """
    Eval d'une fenêtre de 4 cellules.
    Score positif si bon pour joueur_max (IA = 2), négatif si bon pour joueur_min (humain = 1).
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
    Heuristique globale:
    - Bonus centre
    - Somme des évaluations sur toutes les fenêtres de 4 (horiz/vert/diag)
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
    Ordre des colonnes: centre -> proche du centre -> extérieur, filtrées par jouabilité.
    (Pas obligatoire, mais aide le MinMax basique.)
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
    MinMax basique sur la MATRICE (sans alpha-beta).
    maximising: True pour l'IA (joueur 2), False pour humain (joueur 1).
    Retourne un score.
    """
    # États terminaux
    if check_win_matrix(grille, 2):
        return 1000000
    if check_win_matrix(grille, 1):
        return -1000000
    if is_full(grille) or profondeur == 0:
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

def meilleur_coup(grille, profondeur):
    """
    Politique IA:
    1) Coup gagnant immédiat (IA)
    2) Blocage du coup gagnant adverse
    3) MinMax basique
    """
    # 1) Coup gagnant immédiat
    cg = quel_coup(grille, 2)
    if cg != -1:
        return cg

    # 2) Blocage
    cb = coup_bloquant(grille, 1)
    if cb != -1:
        return cb

    # 3) MinMax (sans alpha-beta)
    best_score = -10**9
    best_col = None
    for col in colonnes_ordonnees(grille):
        grille.play(col, 2)
        score = minmax(grille, profondeur - 1, maximising=False)
        grille.undo(col)
        if score > best_score:
            best_score = score
            best_col = col

    if best_col is None:
        # fallback si aucune colonne (rare)
        valid = [c for c in range(grille.c) if grille.fill_matrice[c] < grille.l]
        best_col = valid[0] if valid else 0
    return best_col

# === Partie CLI ===

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
    # Profondeur 4 ou 5 selon la vitesse désirée (MinMax sans pruning est plus lent qu'alpha-beta)
    partie_vs_bot(g, profondeur=4)
