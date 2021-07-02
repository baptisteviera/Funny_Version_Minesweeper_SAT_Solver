from utils import *


def animal_constraints(width: int, height: int) -> ClausesBase:
    """
    Permet de gérer des clauses qui garantissent la contrainte "1 animal par cellule" et la contrainte entre
    le type d'animal et le type d'environnement
    :param width: largeur de la grille
    :param height: hauteur de la grille
    :return: liste de clauses modélisant les contraintes citées au dessus
    """
    list_clauses = []
    for r in range(height):
        for c in range(width):
            # one_ani_per_cell
            type_T_var = cell_type_ani_to_variable(r, c, width, height, "T")
            type_S_var = cell_type_ani_to_variable(r, c, width, height, "S")
            type_C_var = cell_type_ani_to_variable(r, c, width, height, "C")
            list_clauses += atmost_parametrable([type_T_var, type_S_var, type_C_var], 1)

            # ani_env_constraints
            type_env_var = cell_type_env_to_variable(r, c, width, height)
            list_clauses += [[type_env_var, -type_T_var]]
            list_clauses += [[-type_env_var, -type_S_var]]

    return list_clauses
