import operator
import random
import secrets

from client.crocomine_client import *
from constraints_cnf import *

# Connect to server
server = "http://croco.lagrue.ninja:80"
group = "Groupe 51"
members = "Nguyen Bang et Baptiste Viera"
password = "IAZone51"
croco_client = CrocomineClient(server, group, members, password)


def do_chord(r: int, c: int, win: bool, lose: bool, n: int, m: int, grid: Grid, clauses: ClausesBase) -> (bool, bool):
    """
    Permet de faire l'action chord et de récupérer le status de la partie à la suite de cette action

    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param win: status gagné ou pas encore gagné (si win = True alors gagné sinon pas encore gagné)
    :param lose: status perdu ou pas encore perdu (si lose = True alors perdu sinon pas encore perdu)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :param clauses: liste de clauses
    :return: un tuple qui renvoie le status de la partie après avoir fait l'action chord
    """
    status, msg, infos = croco_client.chord(r, c)
    print("\nChord [%d, %d]" % (r, c))
    print(status, msg)
    win, lose = check_status(win, lose, status)
    update_info(n, m, grid, clauses, infos)
    return win, lose


def do_guess(r: int, c: int, ani: str, win: bool, lose: bool, n: int, m: int, grid: Grid, clauses: ClausesBase) \
        -> (bool, bool):
    """
    Permet de faire l'action guess et de récupérer le status de la partie à la suite de cette action

    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param ani: le nom de l'animal ( T ou S ou C)
    :param win: status gagné ou pas encore gagné (si win = True alors gagné sinon pas encore gagné)
    :param lose: status perdu ou pas encore perdu (si lose = True alors perdu sinon pas encore perdu)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :param clauses: liste de clauses
    :return: un tuple qui renvoie le status de la partie après avoir fait l'action guess
    """
    status, msg, infos = croco_client.guess(r, c, ani)
    print("\nGuess [%d, %d, %s]" % (r, c, ani))
    print(status, msg)
    win, lose = check_status(win, lose, status)
    update_info(n, m, grid, clauses, infos)
    return win, lose


def do_discover(r: int, c: int, win: bool, lose: bool, n: int, m: int, grid: Grid, clauses: ClausesBase) -> (
        bool, bool):
    """
    Permet de faire l'action discover et de récupérer le status de la partie à la suite de cette action

    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param win: status gagné ou pas encore gagné (si win = True alors gagné sinon pas encore gagné)
    :param lose: status perdu ou pas encore perdu (si lose = True alors perdu sinon pas encore perdu)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :param clauses: liste de clauses
    :return: un tuple qui renvoie le status de la partie après avoir fait l'action discover
    """
    status, msg, infos = croco_client.discover(r, c)
    print("\nDiscover [%d, %d]" % (r, c))
    print(status, msg)
    win, lose = check_status(win, lose, status)
    update_info(n, m, grid, clauses, infos)
    return win, lose


def get_list_actions_probab(n: int, m: int, grid: Grid) -> List[dict]:
    """
    Cette fonction est obsolete. Nous obtenons d'après nos quelques tests de meilleurs résultats en évaluant le nombre
    d'animaux potentiels.

    Parcours l'ensemble de la grille et pour chaque cellule déjà découverte, nous analysons le voisinage autour afin
    d'être en mesure de faire des calculs de probabilités des quatre actions possibles (guess_T, guess_S, guess_C et discover)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :return: une liste de dictionnaire qui contient l'ensemble des actions avec leur probabilité respective (entre autres) pour chaque cellule analysée.
    """
    list_actions = []
    for r in range(m):
        for c in range(n):
            if grid[r][c]["prox_count"] != [-1, -1, -1]:
                nb_env_type = {"land": 0, "sea": 0}
                env_type_cell = {"land": [], "sea": []}
                neighbors_cells = get_neighbors(r, c, n, m)
                # nombre d'animaux déjà devinés initialisés à 0
                counter = {"T": 0, "S": 0, "C": 0}

                for nei in neighbors_cells:
                    # nombre d'animaux déjà devinés
                    if grid[nei[0]][nei[1]]["ani"] != "?":
                        counter[grid[nei[0]][nei[1]]["ani"]] += 1

                    # cellules de type land
                    if grid[nei[0]][nei[1]]["env"] == "land" and grid[nei[0]][nei[1]]["prox_count"] == [-1, -1, -1] and \
                            grid[nei[0]][nei[1]]["ani"] == "?":
                        nb_env_type["land"] += 1
                        env_type_cell["land"].append([nei[0], nei[1]])

                    # cellules de type sea
                    elif grid[nei[0]][nei[1]]["env"] == "sea" and grid[nei[0]][nei[1]]["prox_count"] == [-1, -1, -1] and \
                            grid[nei[0]][nei[1]]["ani"] == "?":
                        nb_env_type["sea"] += 1
                        env_type_cell["sea"].append([nei[0], nei[1]])

                if nb_env_type["land"] != 0 or nb_env_type["sea"] != 0:
                    # guess T
                    if nb_env_type["land"] != 0:
                        probability = (grid[r][c]["prox_count"][0] - counter["T"]) / nb_env_type["land"]
                        list_actions.append({"type_action": "guess", "cell": [r, c, "T"], "probability": probability,
                                             "env_cells": env_type_cell})

                    # guess S
                    if nb_env_type["sea"] != 0:
                        probability = (grid[r][c]["prox_count"][1] - counter["S"]) / nb_env_type["sea"]
                        list_actions.append({"type_action": "guess", "cell": [r, c, "S"], "probability": probability,
                                             "env_cells": env_type_cell})

                    # guess C
                    probability = (grid[r][c]["prox_count"][2] - counter["C"]) / (
                            nb_env_type["land"] + nb_env_type["sea"])
                    list_actions.append({"type_action": "guess", "cell": [r, c, "C"], "probability": probability,
                                         "env_cells": env_type_cell})

                    # discover
                    nb_ani_discovered = counter["T"] + counter["S"] + counter["C"]
                    nb_ani_rest = grid[r][c]["prox_count"][0] + grid[r][c]["prox_count"][1] + grid[r][c]["prox_count"][
                        2] - nb_ani_discovered
                    probability = 1 - (nb_ani_rest / (nb_env_type["land"] + nb_env_type["sea"]))
                    list_actions.append({"type_action": "discover", "cell": [r, c], "probability": probability,
                                         "env_cells": env_type_cell})
    return list_actions


def random_by_probability(win: bool, lose: bool, n: int, m: int, grid: Grid, clauses: ClausesBase, ani_limit: dict) -> (bool, bool):
    """
    Cette fonction est obsolete. Nous obtenons d'après nos quelques tests de meilleurs résultats en évaluant le nombre
    d'animaux potentiel

    Permet de trier une liste d'action que l'on a récupéré en fonction des probabilités décroissante et de faire l'action
    avec le plus de probabilité de ne pas perdre
    :param win: status gagné ou pas encore gagné (si win = True alors gagné sinon pas encore gagné)
    :param lose: status perdu ou pas encore perdu (si lose = True alors perdu sinon pas encore perdu)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :param clauses: liste de clauses
    :param ani_limit:
    :return: un tuple qui renvoie le status de la partie après avoir fait un des 2 types d'action (guess ou discover)
    """
    list_actions = get_list_actions_probab(n, m, grid)
    if len(list_actions) > 0:
        list_actions.sort(key=operator.itemgetter('probability'), reverse=True)
        print(list_actions)
        # vérifier si proba de discover est égale à la proba d'un guess. Si c'est le cas nous privilégions de faire un
        # discover au lieu d'un guess car celui-ci nous apporte plus d'informations
        id_action = choose_best_action_id(list_actions, "type_action", "discover")
        env_type_cell_tot = list_actions[id_action]["env_cells"]["land"] + list_actions[id_action]["env_cells"]["sea"]
        env_type_cell = list_actions[id_action]["env_cells"]
        random.shuffle(env_type_cell_tot)
        random.shuffle(env_type_cell["land"])
        random.shuffle(env_type_cell["sea"])
        if list_actions[id_action]["type_action"] == "discover":
            print("liste coord", env_type_cell_tot)
            [r, c] = secrets.choice(env_type_cell_tot)
            print("Discover random: ", r, c)
            win, lose = do_discover(r, c, win, lose, n, m, grid, clauses)
        else:
            if list_actions[id_action]["probability"] > 0:
                if list_actions[id_action]["cell"][-1] == "T" and len(env_type_cell["land"]) > 0:
                    [r, c] = secrets.choice(env_type_cell["land"])
                elif list_actions[id_action]["cell"][-1] == "S" and len(env_type_cell["sea"]) > 0:
                    [r, c] = secrets.choice(env_type_cell["sea"])
                else:
                    [r, c] = secrets.choice(env_type_cell_tot)
                ani = list_actions[id_action]["cell"][-1]
                print(list_actions[id_action]["type_action"], r, c, ani)
                win, lose = do_guess(r, c, ani, win, lose, n, m, grid, clauses)
                ani_limit[ani] -= 1
    else:
        return False, True

    return win, lose


def is_opened(r: int, c: int, grid: Grid) -> bool:
    """
    :param r: numéro de la ligne de la cellule sélectionnée
    :param c: numéro de la colonne de la cellule sélectionnée
    :param grid: la carte / la grille
    :return: True si c'est ouvert
    """
    return grid[r][c]["ani"] != "?" or grid[r][c]["prox_count"] != [-1, -1, -1]


def get_list_actions_counting(n: int, m: int, grid: Grid) -> List[dict]:
    """
    Nous calculons pour chaque cellule non ouverte le nombre d'animaux potentiels afin de decider quelle cellule
    à découvrir
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :return: liste des cellules à découvrir avec le nombre d'animaux potentiels associé
    """
    list_actions = []
    for r in range(m):
        for c in range(n):
            if not is_opened(r, c, grid):
                list_actions.append({"type_action": "discover", "cell": [r, c], "ani_potential": m * n})
                ani_potential = -1
                for neighbor in get_neighbors(r, c, n, m):
                    ani_left = {"T": 0, "S": 0, "C": 0}
                    ani_discovered = {"T": 0, "S": 0, "C": 0}
                    if grid[neighbor[0]][neighbor[1]]["prox_count"] != [-1, -1, -1]:
                        for nei in get_neighbors(neighbor[0], neighbor[1], n, m):
                            if grid[nei[0]][nei[1]]["ani"] != "?":
                                ani_discovered[grid[nei[0]][nei[1]]["ani"]] += 1
                        for i in range(len(LIST_ANIMALS) - 1):
                            ani_left[LIST_ANIMALS[i]] = grid[neighbor[0]][neighbor[1]]["prox_count"][i] - \
                                                        ani_discovered[LIST_ANIMALS[i]]
                            if ani_left[LIST_ANIMALS[i]] > 0 and is_compatible(LIST_ANIMALS[i], grid[r][c]["env"]):
                                ani_potential += 1
                                if ani_potential == 0:
                                    ani_potential += 1
                if ani_potential != -1:
                    list_actions.append({"type_action": "discover", "cell": [r, c], "ani_potential": ani_potential})

    return list_actions


def random_by_counting(win: bool, lose: bool, n: int, m: int, grid: Grid, clauses: ClausesBase) -> (bool, bool):
    """
    Permet de choisir la cellule ayant le nombre d'animaux potentiels le plus bas. En cas d'égalité de ce nombre, nous
    choisissons une cellule aléatoire
    :param win: status gagné ou pas encore gagné (si win = True alors gagné sinon pas encore gagné)
    :param lose: status perdu ou pas encore perdu (si lose = True alors perdu sinon pas encore perdu)
    :param n: largeur de la grille
    :param m: longueur de la grille
    :param grid: la carte / la grille
    :param clauses: liste de clauses
    :return: un tuple qui renvoie le status de la partie après avoir fait le discover
    """
    list_actions = get_list_actions_counting(n, m, grid)
    if len(list_actions) == 0:
        return False, True
    list_actions.sort(key=operator.itemgetter("ani_potential"))
    r = 0
    # Trouver toutes les cellules qui portent le même nombre d'animaux potentiels
    while (r + 1 < len(list_actions)) and (list_actions[r + 1]["ani_potential"] == list_actions[0]["ani_potential"]):
        r += 1
    print(list_actions)
    action = secrets.choice(list_actions[0:r + 1])
    [r, c] = action["cell"]
    win, lose = do_discover(r, c, win, lose, n, m, grid, clauses)
    return win, lose


def run_solver():
    """

    :return:
    """
    total_game = win_count = 0
    # Game loop
    while True:
        # input()
        # Ask for new grid
        status, msg, grid_infos = croco_client.new_grid()
        print("[%s] %s" % (status, msg))
        if status == "Err":
            # No more grid
            break

        total_game += 1

        # Gather infos about new grid
        m, n = (grid_infos["m"], grid_infos["n"])
        ani_limit = {"T": grid_infos["tiger_count"], "S": grid_infos["shark_count"], "C": grid_infos["croco_count"]}
        land_limit = {"sea": grid_infos["sea_count"], "land": grid_infos["land_count"]}

        # Init data
        clauses = animal_constraints(n, m)

        grid: Grid = [[0] * n for _ in range(m)]
        for r in range(m):
            for c in range(n):
                grid[r][c] = {"safe": False, "ani": "?", "env": "?", "prox_count": [-1, -1, -1]}

        # Solving loop
        win = False
        lose = False

        start_r, start_c = (grid_infos["start"][0], grid_infos["start"][1])
        win, lose = do_discover(start_r, start_c, win, lose, n, m, grid, clauses)

        while (not win) and (not lose):
            # input()
            # Update safety
            relevant_cells = get_relevant_cells(n, m, grid)
            for [r, c] in relevant_cells:
                if (not grid[r][c]["safe"]) and (grid[r][c]["ani"] == "?"):
                    grid[r][c]["safe"] = is_safe(r, c, n, m, clauses)

            need_random_action = True
            # Vérifier si on peut guess avec certitude
            relevant_cells = get_relevant_cells(n, m, grid)
            for [r, c] in relevant_cells:
                for ani in LIST_ANIMALS[:-1]:
                    if (ani_limit[ani] > 0) and (grid[r][c]["ani"] == "?") and (grid[r][c]["env"] != "?") and (
                            is_compatible(ani, grid[r][c]["env"])) and (sure_has_animal(r, c, n, m, ani, clauses)):
                        win, lose = do_guess(r, c, ani, win, lose, n, m, grid, clauses)
                        need_random_action = False
                        if win or lose:
                            break
                        ani_limit[ani] -= 1
                if win or lose:
                    break
            if win or lose:
                break
            # Vérifier si on peut chord avec certitude
            for r in range(m):
                for c in range(n):
                    if is_satisfied(r, c, n, m, grid):
                        win, lose = do_chord(r, c, win, lose, n, m, grid, clauses)
                        need_random_action = False

                        if win or lose:
                            break
                if win or lose:
                    break
            if win or lose:
                break
            # Vérifier si on peut discover avec certitude
            relevant_cells = get_relevant_cells(n, m, grid)
            for [r, c] in relevant_cells:
                if (grid[r][c]["prox_count"] == [-1, -1, -1]) and (grid[r][c]["safe"]):
                    win, lose = do_discover(r, c, win, lose, n, m, grid, clauses)
                    need_random_action = False
                    if win or lose:
                        break
            if win or lose:
                break

            if not need_random_action:
                continue

            # Random discover
            win, lose = random_by_counting(win, lose, n, m, grid, clauses)
            # deprecated
            # win, lose = random_by_probability(win, lose, n, m, grid, clauses)

        if win:
            win_count += 1

    print("Win %d/%d" % (win_count, total_game))


run_solver()
