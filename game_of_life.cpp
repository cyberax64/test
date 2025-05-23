// Jeu de la vie en C++
#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <cstdlib>
#include <ctime>

using Grid = std::vector<std::vector<int>>;

int countNeighbors(const Grid& grid, int x, int y) {
    int count = 0;
    int rows = grid.size();
    int cols = grid[0].size();
    for (int i = -1; i <= 1; ++i) {
        for (int j = -1; j <= 1; ++j) {
            if (i == 0 && j == 0) continue;
            int nx = x + i;
            int ny = y + j;
            if (nx >= 0 && nx < rows && ny >= 0 && ny < cols) {
                count += grid[nx][ny];
            }
        }
    }
    return count;
}

void printGrid(const Grid& grid) {
    std::cout << "\033[2J\033[H"; // efface l'écran et remonte le curseur
    for (const auto& row : grid) {
        for (int cell : row) {
            std::cout << (cell ? 'O' : ' ');
        }
        std::cout << '\n';
    }
}

int main() {
    const int rows = 20;
    const int cols = 40;
    Grid grid(rows, std::vector<int>(cols));

    // Initialisation aléatoire
    std::srand(static_cast<unsigned>(std::time(nullptr)));
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            grid[i][j] = std::rand() % 2;
        }
    }

    while (true) {
        printGrid(grid);
        Grid next = grid;
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                int alive = countNeighbors(grid, i, j);
                if (grid[i][j]) {
                    next[i][j] = (alive == 2 || alive == 3) ? 1 : 0;
                } else {
                    next[i][j] = (alive == 3) ? 1 : 0;
                }
            }
        }
        grid.swap(next);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    return 0;
}
