import random as rand
from utils import get_neighbors
import sys
import os

if len(sys.argv) < 6:
    print("run with: nb_grids, difficulty, min_size, max_size, output_folder")
    exit(0)

num_grid = 0
nb_grids = int(sys.argv[1])
extension = ".croco"
name_grid = "grille"
difficulty = int(sys.argv[2])
elements = []
min_size = int(sys.argv[3])
max_size = int(sys.argv[4])
output_folder = sys.argv[5]

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

for i in range((100 - difficulty) // 2):
    elements += ["~"]
for i in range((100 - difficulty) // 2):
    elements += ["-"]
for i in range(difficulty // 3):
    elements += ["T"]
for i in range(difficulty // 3):
    elements += ["S"]
for i in range(difficulty // 3 // 2):
    elements += ["C"]
for i in range(difficulty // 3 // 2):
    elements += ["W"]


def generator_full_random(min_size, max_size, nb_grids):
    while nb_grids != 0:
        rand.shuffle(elements)
        nb_grids -= 1
        if 0 < min_size <= max_size and max_size > 0:
            w = rand.randint(min_size, max_size)
            h = rand.randint(min_size, max_size)
        grid = [[0 for c in range(w)] for r in range(h)]
        for r in range(h):
            for c in range(w):
                grid[r][c] = rand.randrange(len(elements))
        # print(grid)
        w_start = rand.randrange(w)
        h_start = rand.randrange(h)
        while elements[grid[h_start][w_start]] in ["T", "S", "C", "W"]:  # not safe
            w_start = rand.randrange(w)
            h_start = rand.randrange(h)
        for neighbor in get_neighbors(h_start, w_start, w, h):
            while elements[grid[neighbor[0]][neighbor[1]]] in ["T", "S", "C", "W"]:
                grid[neighbor[0]][neighbor[1]] = rand.randrange(len(elements))
        # print(h_start)
        # print(w_start)
        write_file(grid, w, h, w_start, h_start)


def write_file(grid, w, h, w_start, h_start):
    global num_grid
    global extension
    global name_grid
    filename = os.path.join(output_folder, name_grid + str(num_grid) + extension)
    num_grid += 1
    grid_str = ""
    grid_str += filename + "\n"
    # print(grid_str)
    grid_str += str(h) + " " + str(w) + "\n"
    # print(grid_str)
    grid_str += str(h_start) + " " + str(w_start) + "\n"
    # print(grid_str)
    for r in range(h):
        for c in range(w):
            grid_str += elements[grid[r][c]]
            if c != w - 1:
                grid_str += " "
            else:
                grid_str += "\n"
    # print(grid_str)
    with open(filename, "w", newline="") as gen:
        gen.write(grid_str)


generator_full_random(min_size, max_size, nb_grids)
