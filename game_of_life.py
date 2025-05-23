#!/usr/bin/env python3
# Jeu de la Vie en Python

import random
import time
import os
import sys

Grid = list[list[int]]

def count_neighbors(grid: Grid, x: int, y: int) -> int:
    rows, cols = len(grid), len(grid[0])
    count = 0
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue
            nx, ny = x + i, y + j
            if 0 <= nx < rows and 0 <= ny < cols:
                count += grid[nx][ny]
    return count


def print_grid(grid: Grid) -> None:
    sys.stdout.write("\033[2J\033[H")  # Efface l'écran et replace le curseur en haut
    for row in grid:
        for cell in row:
            sys.stdout.write('O' if cell else ' ')
        sys.stdout.write('\n')
    sys.stdout.flush()


def main() -> None:
    rows, cols = 20, 40
    # Initialisation aléatoire
    grid: Grid = [[random.randint(0, 1) for _ in range(cols)] for _ in range(rows)]

    try:
        while True:
            print_grid(grid)
            next_grid: Grid = [[0] * cols for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    alive = count_neighbors(grid, i, j)
                    if grid[i][j]:
                        next_grid[i][j] = 1 if alive in (2, 3) else 0
                    else:
                        next_grid[i][j] = 1 if alive == 3 else 0
            grid = next_grid
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nArrêt du programme.")


if __name__ == "__main__":
    main()