from typing import List, Tuple, TypedDict
import subprocess
import itertools

# alias de types
Variable = int
Clause = List[Variable]
Model = List[Variable]
ClausesBase = List[Clause]
Grid = List[List[dict]]
# server data

TStatus = str  # "OK"|"KO"|"Err"|"GG"
TMsg = str


class TInfo(TypedDict):
    pos: Tuple[int, int]  # (i, j) i < M, j < N
    field: str  # "sea"|"land"
    prox_count: Tuple[int, int, int]  # (tiger_count, shark_count, croco_count), optional


TInfos = List[TInfo]
TGridInfos = {
    "m": int,
    "n": int,
    "start": Tuple[int, int],
    "tiger_count": int,
    "shark_count": int,
    "croco_count": int,
    "sea_count": int,
    "land_count": int,
    "3BV": int,
    "infos": TInfos  # Optional
}

# Consts
LIST_ANIMALS = ["T", "S", "C", ""]


def unique_parametrable(variables: List[Variable], nb: int) -> ClausesBase:
    """
    Permet de générer des clauses qui garantissent la contrainte de type unique (uniquement nb parmi vars)
    :param variables: liste de variables
    :param nb:
    :return: liste de clauses
    """
    list_combination = []

    # at_least (au moins 1 élément vrai)
    for t in list(itertools.combinations(variables, len(variables) - nb + 1)):
        list_combination.append([t[i] for i in range(len(variables) - nb + 1)])
    # at_most (au moins 1 élément faux)
    for t in list(itertools.combinations(variables, nb + 1)):
        list_combination.append([-t[i] for i in range(nb + 1)])
    return list_combination


def atmost_parametrable(variables: List[Variable], nb: int) -> List[List[int]]:
    """
    Permet de générer des clauses qui garantissent la contrainte de type "au plus nb parmi vars"
    :param variables: liste de variables
    :param nb:
    :return: liste de clauses
    """
    list_combination = []
    for t in list(itertools.combinations(variables, nb + 1)):
        list_combination.append([-t[i] for i in range(nb + 1)])  # on convertit en liste important
    return list_combination


def clauses_to_dimacs(clauses: ClausesBase, nb_vars: int) -> str:
    """
    Permet de convertir une liste de clauses en chaîne de caractères sous format Dimacs
    :param clauses: liste de clauses
    :param nb_vars: nombre de varibales
    :return: chaine de caractères
    """
    dimacs_format = "p cnf %d %d\n" % (nb_vars, len(clauses))
    for listes in clauses:
        for j in listes:
            dimacs_format += str(j) + " "

        dimacs_format += "0\n"
    return dimacs_format


def write_dimacs_file(dimacs: str, filename: str):
    """
    Permet d'écrire dans une fichier
    :param dimacs: chaine de caractère à écrire
    :param filename: nom du fichier
    :return:
    """
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(filename: str, cmd: str = "./gophersat-1.1.6", encoding: str = "utf8") -> Tuple[bool, List[int]]:
    """
     Permet de lancer le solveur sat.
     Auteur : M. Lagrue
    :param filename:
    :param cmd:
    :param encoding:
    :return:
    """
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


# Nombre total de variables : 4*m*n variables
def cell_type_env_to_variable(row: int, col: int, width: int, height: int) -> Variable:
    """
    Transforme le type d'environnement d'une cellule en variable
    :param row:
    :param col:
    :param width:
    :param height:
    :return:
    1 à width * height -> le type de terrain
    """
    offset = row * width + col
    type_env = 1 + offset

    return type_env


def cell_type_ani_to_variable(row: int, col: int, width: int, height: int, animal: str) -> int:
    """
    Transforme le type d'animal d'une cellule en variable

    :param row: numéro de ligne de la cellule sélectionnée
    :param col: numéro de la colonne de la cellule sélectionnée
    :param width: largeur de la carte/grille
    :param height: hauteur de la carte/grille
    :param animal: type d'animal
    :return: variable correspondant
    1 à width * height -> le type de terrain
    width*height + 1 à 2 * width*height -> tigre
    2 * width*height + 1 à 3 * width*height -> requin
    3 * width*height + 1 à 4 * width*height -> croco
    """
    offset = row * width + col
    type_ani = None
    if animal == "T":
        type_ani = width * height + 1 + offset
    if animal == "S":
        type_ani = 2 * width * height + 1 + offset
    if animal == "C":
        type_ani = 3 * width * height + 1 + offset

    return type_ani


def variable_to_text(var: int, w: int, h: int) -> (int, int, str):
    """
    conversion de la variable numérique en chaine de caractères
    :param var: variable numérique associée à une cellule
    :param w: largeur de la carte/grille
    :param h: hauteur de la carte/grille
    :return: un tuple (triple) avec les cordonnées de la cellule et le type de terrain ou d'animal
    """
    v = var
    if v < 0:
        v = -v
    # Permet de retourner le type d'environnement de la cellule
    if (1 <= v) and (v <= w * h):
        offset = v - 1
        row = offset // w
        col = offset - w * row
        if var > 0:
            return row, col, "not sea"
        else:
            return row, col, "sea"

    # Permet de retourner le type d'animal dans la cellule
    # Présence de tigres ou non
    if (w * h + 1 <= v) and (v <= 2 * w * h):
        offset = v - (w * h + 1)
        row = offset // w
        col = offset - w * row
        if var > 0:
            return row, col, "T"
        else:
            return row, col, "not T"
    # Présence de requins ou non
    if (2 * w * h + 1 <= v) and (v <= 3 * w * h):
        offset = v - (2 * w * h + 1)
        row = offset // w
        col = offset - w * row
        if var > 0:
            return row, col, "S"
        else:
            return row, col, "not S"
    # Présence de crocodile ou non
    if (3 * w * h + 1 <= v) and (v <= 4 * w * h):
        offset = v - (3 * w * h + 1)
        row = offset // w
        col = offset - w * row
        if var > 0:
            return row, col, "C"
        else:
            return row, col, "not C"


def mark_env(r: int, c: int, w: int, h: int, type_env: str) -> Clause:
    """
    Permet de marquer une cellule avec son type d'environnement en faisant appel à la fonction cell_type_env_to_variable
    La valeur obtenue est mise dans une liste afin de faciliter par la suite la transformation de nos clauses en dimacs
    :param r: numéro de ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param type_env: chaine de caractères correspondant au type d'environnement
    :return: une variable numérique associée à la cellule qui est contenue dans une liste à 1 seul élément. Si le type \
    d'environnement n'est pas de la terre, nous ajoutons un "-" pour faire la négation
    """
    type_env_var = cell_type_env_to_variable(r, c, w, h)
    if type_env == "land":
        return [type_env_var]
    else:
        return [-type_env_var]


def mark_animal(r: int, c: int, w: int, h: int, type_ani: str) -> Clause:
    """
        Permet de marquer une cellule avec son type d'animal en faisant appel à la fonction cell_type_ani_to_variable
        La valeur obtenue est mise dans une liste afin de faciliter par la suite la transformation de nos clauses en
        dimacs
        :param r: numéro de ligne de la cellule sélectionnée
        :param c: numéro de la colonne de la cellule sélectionnée
        :param w: largeur de la grille
        :param h: hauteur de la grille
        :param type_ani: chaine de caractères correspondant au type d'animal
        :return: une variable numérique associée à la cellule qui est contenue dans une liste à 1 seul élément. S'il n'y
        a pas d'animaux, retourne une liste vide.
        """
    type_ani_var = cell_type_ani_to_variable(r, c, w, h, type_ani)
    if type_ani_var is not None:
        return [type_ani_var]
    else:
        return []


def mark_nb_animals_neighbors(neighbors: List[List[int]], w: int, h: int, nb_animals: int, animal_type: str) \
        -> ClausesBase:
    """
    Permet d'ajouter des contraintes concernant le nombre d'animaux autour d'une cellule
    :param neighbors: Liste des cordonnées des cellules voisines
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param nb_animals: nombre d'animaux d'un type donné parmi la liste de cellules voisines
    :param animal_type: type de l'animal
    :return:
    """
    neighbors_variables = []
    # on transforme les cordonnées des cellules voisines en variable paramétrée avec un type d'animal spécifique.
    # on place l'ensemble des variables dans une liste neighbors_variables
    for neighbor in neighbors:
        neighbors_variables.append(cell_type_ani_to_variable(neighbor[0], neighbor[1], w, h, animal_type))
    # on applique la fonction unique_parametrable afin d'avoir une liste de clauses respectant la contrainte nb_animals
    # parmi neighbors_variables
    return unique_parametrable(neighbors_variables, nb_animals)


def is_valid(x: int, y: int, w: int, h: int) -> bool:
    """
    Vérifie si les cordonnées (x,y) sont des cordonnées valides
    :param x: numéro de la ligne de la cellule sélectionnée
    :param y: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :return: un booleen : vrai si c'est valide
    """
    return (x >= 0) and (x < h) and (y >= 0) and (y < w)


def get_neighbors(x: int, y: int, w: int, h: int) -> List[List[int]]:
    """
       2 1 8
       3 X 7
       4 5 6
    Permet de parcourir les voisins de la cellule sélectionnée dans l'ordre ci-dessus.
    Ajoute dans une liste les voisins de la cellule s'ils existent (condition vérifiée avec la fonction is_valide)

    :param x: numéro de la ligne de la cellule sélectionnée
    :param y: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :return: une liste qui contient sous forme de liste à deux éléments les cordonnées des voisins de la cellule
    sélectionnée
    """

    # Coordonnées relatives des voisins
    dx = [-1, -1, 0, 1, 1, 1, 0, -1]
    dy = [0, -1, -1, -1, 0, 1, 1, 1]
    neighbors = []
    for k in range(len(dx)):
        # Verifier si la cellule n'est pas en dehors de la carte
        if is_valid(x + dx[k], y + dy[k], w, h):
            # Ajouter dans la liste des résultats
            neighbors += [[x + dx[k], y + dy[k]]]

    return neighbors


def get_relevant_cells(w: int, h: int, grid: Grid) -> List[List[int]]:
    """
    Permet de minimiser le nombre de cellules retenues, à analyser
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param grid: la grille / la carte
    :return: la liste des coordonnées des cellules voisines des cellules découvertes
    """
    res = []
    for r in range(h):
        for c in range(w):
            # si la cellule a ete ouverte
            if grid[r][c]["prox_count"] != [-1, -1, -1]:
                neighbors = get_neighbors(r, c, w, h)
                for n in neighbors:
                    if (grid[n[0]][n[1]]["ani"] == "?") and (grid[n[0]][n[1]]["prox_count"] == [-1, -1, -1]) and (
                            n not in res):
                        res += [n]
    return res


def is_compatible(animal: str, env: str) -> bool:
    """
    Vérifie la compatibilité entre le type d'animal et le type d'environnement

    :param animal:
    :param env:
    :return:
    """
    if animal == "T":
        return env == "land"
    if animal == "S":
        return env == "sea"
    return True


def is_safe(r: int, c: int, w: int, h: int, clauses: ClausesBase) -> bool:
    """
    Vérifie par l'absurde si une cellule est safe

    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param clauses: liste de clauses
    :return: True (safe) si le modèle n'est pas satisfiable (raisonnement par l'absurde) et False sinon
    """
    # On suppose que la cellule n'est pas safe => on ajoute la clause suivante : T ou S ou C
    # Raisonnement par l'absurde
    clauses += [[cell_type_ani_to_variable(r, c, w, h, "T"),
                 cell_type_ani_to_variable(r, c, w, h, "S"),
                 cell_type_ani_to_variable(r, c, w, h, "C")]]

    dimacs = clauses_to_dimacs(clauses, 4 * w * h)
    write_dimacs_file(dimacs, "crocomine.cnf")
    sat, model = exec_gophersat(filename="crocomine.cnf")
    # print("Check safe", r, c, sat)
    clauses.pop()  # on supprime la dernière clause ajoutée (clause pour vérification uniquement)
    return not sat


def sure_has_animal(r: int, c: int, w: int, h: int, animal: str, clauses: ClausesBase) -> bool:
    """
    Vérifie par l'absurde sur une cellule a un animal

    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param animal: caractère désignant un animal : T ou S ou C
    :param clauses: liste de clauses
    :return: True (has animal) si le modèle n'est pas satisfiable (raisonnement par l'absurde) et False sinon
    """
    # On suppose qu'il n'y a pas d'animal
    # Clause de test : pas d'animal
    clauses += [[-cell_type_ani_to_variable(r, c, w, h, animal)]]
    dimacs = clauses_to_dimacs(clauses, 4 * w * h)
    write_dimacs_file(dimacs, "crocomine.cnf")
    sat, model = exec_gophersat(filename="crocomine.cnf")
    # print("Check safe", r, c, sat)
    clauses.pop()  # on supprime la dernière clause ajoutée (clause pour vérification uniquement)
    return not sat


def is_satisfied(r: int, c: int, w: int, h: int, grid: Grid) -> bool:
    """
    On vérifie si le nombre d'animal pour chaque type autour de la cellule(r,c) a bien été trouvé
    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param grid: la carte (tableau 2D de dictionnaire)
    :return: True si le nombre de chaque type d'animal de la cellule (r,c) correspond au prox_count de la cellule et si
    le nombre de cellules ouvertes est strictement supérieur à 0
    """
    neighbors = get_neighbors(r, c, w, h)
    counter = {"T": 0, "S": 0, "C": 0}
    openned_cell = 0
    for n in neighbors:
        if grid[n[0]][n[1]]["ani"] != "?":
            counter[grid[n[0]][n[1]]["ani"]] += 1
        if (grid[n[0]][n[1]]["prox_count"] == [-1, -1, -1]) and (grid[n[0]][n[1]]["ani"] == "?"):
            openned_cell += 1

    return (openned_cell > 0) and \
           (grid[r][c]["prox_count"][0] == counter["T"]) and \
           (grid[r][c]["prox_count"][1] == counter["S"]) and \
           (grid[r][c]["prox_count"][2] == counter["C"])


def update_info(w: int, h: int, grid: Grid, clauses: ClausesBase, infos: List[dict]):
    """
    Permet de mettre à jour notre base de clauses en fonction des différentes "découvertes"
    :param w: largeur de la grille
    :param h: hauteur de la grille
    :param grid: la carte
    :param clauses: liste de clauses
    :param infos: liste d'info
    :return: une nouvelle base de clauses
    """
    for info in infos:
        x = info["pos"][0]
        y = info["pos"][1]

        if "field" in info:
            grid[x][y]["env"] = info["field"]
            clauses += [mark_env(x, y, w, h, info["field"])]
        if "prox_count" in info:
            neighbors = get_neighbors(x, y, w, h)
            grid[x][y]["prox_count"] = info["prox_count"]
            for animal_id in range(len(LIST_ANIMALS) - 1):
                clauses += mark_nb_animals_neighbors(neighbors, w, h, grid[x][y]["prox_count"][animal_id],
                                                     LIST_ANIMALS[animal_id])
        if "animal" in info:
            grid[x][y]["ani"] = info["animal"]
            clauses += [mark_animal(x, y, w, h, grid[x][y]["ani"])]


def choose_best_action_id(list_dict: List[dict], cle: str, value: str) -> int:
    """
    Cette fonction est obsolete. Elle est utilisé pour trouver l'action associée à une cellule qui a le plus de
    probabilité de ne pas conduire à la défaite
    :param list_dict: liste des actions
    :param cle:
    :param value:
    :return:
    """
    best = 0
    for i in range(len(list_dict)):
        if (list_dict[i]["probability"] >= list_dict[best]["probability"]) and (list_dict[i][cle] == value):
            return i

    return 0


def check_status(win: bool, lose: bool, status: str) -> (bool, bool):
    """
    Permet de vérifier le status
    :param win: gagné (variable booléenne)
    :param lose: perdu (variable booléenne)
    :param status: message informatif concernant l'action passée
    :return:
    """
    if status == "GG":
        win = True
    if status == "KO":
        win = False
        lose = True
    if status == "Err":
        win = False
        lose = True
    return win, lose
