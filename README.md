# The Minesweeper Of Area 51

Projet réalisé dans le cadre d'un cours d'intelligence artificielle intitulé : Logique et résolution de problèmes par la recherche.

L'objectif du projet est de résoudre une version mutée du célèbre jeu Minesweeper à l'aide d'un solveur SAT.

Veuillez trouver ci-joint l'énoncé : https://hackmd.io/@ia02/By_zb5GFd

Veuillez trouver ci-joint notre brouillon de notes : https://hackmd.io/sfXpR_wRQY2rl0s5pdJ00A


## Comment lancer notre programme ?

Il faut lancer le programme ```main.py```
```
python main.py
```



## Quelles sont les spécificités de notre programme ?

### L'ordre des actions

Dans notre programme, on priorise tout d'abord les guess, puis les chord et à la fin les discover. Comme les guess donneront des informations nécessaires pour les chords, il est nécessaire de faire les guess avant de faire les chords pour optimiser le programme.

### Les guess sûrs

Pour faire un guess sur une cellule, nous utilisons le solveur SAT pour un raisonnement par l'absurde.

La fonction ```sure_has_animal``` prend en paramètre les coordonnées d'une cellule et le type d'animal à tester. Nous générons des clauses qui disent qu'il n'y a pas ce type d'animal dans cette cellule. Si les clauses ne sont pas satisfiables, nous savons qu'il y a sûrement un animal dans cette cellule.


### Les chords sûrs

Pour faire un chord, il est nécessaire de trouver une cellule satisfaite, c'est-à-dire une cellule déjà ouverte, sans animal dont le nombre d'animaux découverts autour de lui a été atteint.

La fonction ```is_satisfied``` renverra vrai / faux si la cellule considérée est chord-able.


### Les discovers sûrs

Même principle que les guess sûrs, nous utilisons aussi le raisonnement par l'absurde pour conclure qu'une cellule est sans-danger.

La fonction ```is_safe``` prend en paramètre les coordonnées d'une cellule et elle renvoie vrai si la cellule est sûrement sans-danger. Nous générons des clauses qui disent qu'il y a au moins un animal dans cette cellule. Si les clauses ne sont pas satisfiables, nous savons que la cellule ne peut posséder aucun animal, elle est donc sans-danger.

### Gestion des hasards

Nous avons tenté deux méthodes différentes pour choisir une action par hasard. La première approche était de calculer le pourcentage de ne pas perdre de chaque action, puis prendre l'action avec la probabilité la plus élevée.

Nous nous sommes rendus compte que la première approche ne donnait pas un résultat très convaincant. Nous avons donc implémenté une deuxième approche qui calcule, pour chaque cellule non-ouverte, le nombre d'animaux potentiels, en fonction des informations de ses voisins. Nous prenons ensuite la cellule avec le nombre d'animaux potentiels le plus petit pour faire un discover.

1. Approche de probabilité

Cette approche se déroule comme suivant :

* Il y a 4 actions possibles parmi les voisins d'une cellule considérée
  * guess un tigre.
  * guess un requin.
  * guess un crocodile.
  * discover.
* Pour chaque cellule ouverte, nous calculons la probabilité de ne pas perdre de chaque action.
* Nous sélectionnons les actions qui ont la plus grande probabilité.
* S'il y a plusieurs actions avec la probabilité maximale, nous prendrons une action aléatoire en priorisant le discover sur le guess.

> Cette approche n'a pas été utilisée pendant la bataille d'IA.

2. Approche du nombre d'animaux potentiels

Cette approche parcourt la grille et :

* Pour chaque cellule non-ouverte nous calculons le nombre d'animaux potentiels (ce nombre représente le nombre de fois qu'elle est considérée candidate pour posséder un animal) :
* Nous sélectionnons les cellules qui ont le nombre d'animaux potentiels le plus bas.
* S'il y a plusieurs cellules candidates, nous prendrons une cellule aléatoire pour faire le discover.

Cette approche est basée sur l'idée qu'un discover donnera plus d'informations qu'un guess. En plus, quand nous jouons au démineur, nous ferons rarement des guess aléatoires, mais plutôt des discovers aléatoires.

> Cette approche a été utilisée pendant la bataille d'IA.

