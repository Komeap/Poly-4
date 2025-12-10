import Plateau as p
import copy

## Ca marche pas dutout, ca joue des coup pas ouf a revoir, MinMax, evaluer

def count_win_possibility(Plateau_de_jeu, joueur, win_cond):
    if joueur == 2: 
        j_ami = 0
        j_adv = 1
    else: 
        j_ami = 1
        j_adv = 0
        
    ## bitboard de tous les jeton adverse et les miens
    occupied = Plateau_de_jeu.bitboards[j_ami] | Plateau_de_jeu.bitboards[j_adv]
    ## l'inverse pour avvoir des 1 la ou il y a pas de jetons
    empty = ~occupied 

    ## qausi même chose que dans check_win_bitboard sauf que ca verifie si le jeton apres ma suite de nombre est bien vide --> possibilité de victoire

    count = 0
    H = Plateau_de_jeu.l + 1
    directions = [1, H, H+1, H-1]

    for d in directions:

        bb = Plateau_de_jeu.bitboards[j_ami]

        for i in range(win_cond - 2):
            bb = bb & (bb >> d) 
        
        threats_before = (bb >> d) & empty 
        threats_after = (bb << ((win_cond -1) * d)) & empty 

        count += bin(threats_before).count('1')
        count += bin(threats_after).count('1')
        
    return count

def MinMax(Plateau_de_jeu, profondeur, tour_IA):

    if Plateau_de_jeu.check_win_bitboard(2, Plateau_de_jeu.win): 
        return 10000000

    if Plateau_de_jeu.check_win_bitboard(1, Plateau_de_jeu.win): 
        return -10000000

    if profondeur == 0 :
        return eval_score(Plateau_de_jeu, 2)

    if tour_IA :
        max_score = -999999

        col_posssible = []
        for i in range(Plateau_de_jeu.c) :
            if Plateau_de_jeu.fill_matrice[i] < Plateau_de_jeu.l :
                col_posssible.append(i)
    

        for col in col_posssible :
            Plateau_de_jeu.play(col, 2)

            score_remonte = MinMax(Plateau_de_jeu, profondeur - 1, False)

            Plateau_de_jeu.undo(col)

            if score_remonte > max_score :
                max_score = score_remonte

        return max_score
    
    else :
        min_score = 999999

        col_posssible = []
        for i in range(Plateau_de_jeu.c) :
            if Plateau_de_jeu.fill_matrice[i] < Plateau_de_jeu.l :
                col_posssible.append(i)

        for col in col_posssible: 
            Plateau_de_jeu.play(col, 1)

            score_remonte = MinMax(Plateau_de_jeu, profondeur -1, True)

            Plateau_de_jeu.undo(col)

            if score_remonte < min_score :
                min_score = score_remonte

        return min_score

def eval_score(Plateau_de_jeu, joueur_ia):
    score = 0
    
    joueur_adv = 1 if joueur_ia == 2 else 2
    
    for k in range(2, Plateau_de_jeu.win):
        poids = 10 ** (k * 2) 

        mes_motifs = count_win_possibility(Plateau_de_jeu, joueur_ia, k)
        score += mes_motifs * poids

        adv_motifs = count_win_possibility(Plateau_de_jeu, joueur_adv, k)
        score -= adv_motifs * (poids * 2) 

    return score

def trouver_meilleur_coup(plateau_reel, profondeur):
    print(f"L'IA réfléchit (Profondeur {profondeur})...")

    # INit des variable
    meilleur_score = -float('inf')
    meilleure_colonne = -1

    # copy du plateau de jeu, pour pas modif je vrai jeu
    plateau_simu = copy.deepcopy(plateau_reel)

    # nombre de colonne ranger dans un tableau
    colonnes_possibles = []
    for c in range(plateau_simu.c):
        if plateau_simu.fill_matrice[c] < plateau_simu.l:
            colonnes_possibles.append(c)
    
    # cas une colonne possible
    if len(colonnes_possibles) == 1:
        return colonnes_possibles[0]

    for col in colonnes_possibles:

        plateau_simu.play(col, 2)

        score = MinMax(plateau_simu, profondeur - 1, False)
        
        plateau_simu.undo(col)
        
        print(f" > Colonne {col} : Score calculé = {score}")

        if score > meilleur_score:
            meilleur_score = score
            meilleure_colonne = col
            
    return meilleure_colonne

if __name__ == "__main__":
    # 1. Création du jeu (6 lignes, 7 colonnes, 4 pour gagner)
    game = p.Plateau(6, 7, 4)
    running = True
    tour_joueur = 1 # 1 = Humain, 2 = IA

    print("--- DÉBUT DE LA PARTIE ---")
    print("Tu es le Joueur 1 (Humain)")
    print("L'IA est le Joueur 2")
    print(game.matrice) # Affiche le plateau vide (renversé selon ta logique numpy)

    while running:
        if tour_joueur == 1:
            # --- TOUR HUMAIN ---
            try:
                col = int(input("\nÀ toi (0-6) : "))
                if 0 <= col < 7 and game.fill_matrice[col] < game.l:
                    game.play(col, 1)
                    # Vérif Victoire Humain
                    if game.check_win_bitboard(1, game.win):
                        print(game.matrice)
                        print("BRAVO ! Tu as gagné !")
                        running = False
                    else:
                        tour_joueur = 2 # Passe la main à l'IA
                else:
                    print("Coup invalide, réessaie.")
            except ValueError:
                print("Entre un chiffre !")

        else:
            # --- TOUR IA ---
            # Appel de notre fonction wrapper
            # Profondeur 4 est bien pour commencer (rapide)
            col_ia = trouver_meilleur_coup(game, 6) 
            
            if col_ia != -1:
                game.play(col_ia, 2)
                print(f"\nL'IA a joué en colonne {col_ia}")
                print(game.matrice)
                
                # Vérif Victoire IA
                if game.check_win_bitboard(2, game.win):
                    print("L'IA A GAGNÉ ! Dommage...")
                    running = False
                else:
                    tour_joueur = 1 # Passe la main à l'humain
            else:
                print("Match Nul (Plus de place) !")
                running = False