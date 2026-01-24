# Projet POLIC - Puissance 4 Modulable

Bienvenue dans la documentation technique du projet **POLIC**. 
Ce projet est une implémentation avancée du jeu Puissance 4 en Python, intégrant une interface graphique `tkinter`, une IA ultra performante et des variantes (taille de grille variable, bonus).

---

## Fonctionnalités Principales

* **Paramétrage complet :** Choix des dimensions de la grille (Lignes x Colonnes) , couleur des pions, premier joueur, bonus, ainsi que la condition de victoire (alignement de N pions).
* **Intelligence Artificielle :**
    * Algorithme **MinMax**.
    * Optimisation par **Multiprocessing**.
    * Niveaux de difficulté : Facile (Aléatoire/Mixte) - 
                              Normal(30% de chance d'un coup 'ok', 70% d'un coup bien sauf dans cas de danger imminent ) - 
                              Hardcore (100 % de meilleur coup)
* **Mécaniques de jeu :**
    * Bonus : **Bombe** (détruit une colonne), **Undo** (annuler un coup), **Help** (recommandation de l'IA). TOus utilisable 1 foispar vous **et** L'IA

---

## Installation et Lancement

Le projet est fourni avec un script d'automatisation pour Windows (Fonctionne sur Linux et WSL normalement, mais peut être assez long a lancé. Si c'est le cas je vous recommande largement les lignes de commande via terminal si dessous).

1.  Assurez-vous d'avoir **Python** installé.
2.  Lancez le fichier `run.bat` à la racine du projet.
    * *Ce script crée automatiquement l'environnement virtuel, installe les dépendances (Numpy, Pillow, OpenCV) et lance le jeu.*

Sinon, via le terminal : 
pip install numpy Pillow opencv-python puis python main.py