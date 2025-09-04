def generer_plateau():
    """
    Construit un tableau représentant le plateau de jeu.

    Renvoie un tableau à deux dimensions de taille 3x3 dont chaque élément vaut " ".
    """
    pass


def afficher_plateau(plateau):
    """
    Affiche le plateau de jeu

    Paramètre :
    plateau -- Tableau deux dimensions représentant le plateau de jeu
    """
    pass


def obtenir_position(joueur):
    """
    Affiche un message demandant au joueur de saisir la position à jouer et attend sa saisie.

    Paramètre :
    joueur -- Vaut "O" ou "X" selon le joueur courant

    Renvoie la position de jeu sous forme d'un tuple (ligne, colonne).
    """
    pass


def placer_pion(plateau, joueur, position):
    """
    Affecte la valeur de joueur à la position indiquée.

    Paramètres :
    plateau  -- Tableau à deux dimensions du plateau de jeu
    joueur   -- Vaut "O" ou "X" selon le joueur courant
    position -- Tuple (ligne, colonne) de la position à jouer
    """
    pass


def verifier_victoire(plateau, joueur):
    """
    Vérifie si un joueur remporte la victoire.

    Paramètres :
    plateau -- Tableau à deux dimensions du plateau de jeu
    joueur  -- Vaut "O" ou "X" selon le joueur courant

    Renvoie True si le joueur a réussi à aligner 3 pions, False sinon.
    """
    pass


def afficher_victoire(joueur):
    """
    Affiche la victoire pour un joueur donné

    Paramètre :
    joueur -- Vaut "O" ou "X" selon le joueur courant
    """
    pass


def jeu():
    """
    Fonction principale du jeu
    """
    pass


if __name__ == "__main__":
    jeu()
