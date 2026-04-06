import random
import time


def change_wall(side1, side2, maze, bit):
    if side1[0] == side2[0]:
        maze[side1[0]][side1[1]][1] = bit
        maze[side2[0]][side2[1]][3] = bit
    else:
        maze[side1[0]][side1[1]][2] = bit
        maze[side2[0]][side2[1]][0] = bit


def check_large_open_areas(width: int, height: int, maze):
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            if (maze[x][y] == [0, 0, 0, 0]
                    and maze[x - 1][y][1] == 0 and maze[x - 1][y][3] == 0
                    and maze[x + 1][y][1] == 0 and maze[x + 1][y][3] == 0
                    and maze[x][y - 1][0] == 0 and maze[x][y - 1][2] == 0
                    and maze[x][y + 1][0] == 0 and maze[x][y + 1][2] == 0):
                return False
    return True


def add_forty_two_pattern(width: int, height: int, scores):
    (x, y) = ((width // 2) - 3, (height // 2) - 2)
    for i in range(3):
        scores[x][y + i] = -1
        scores[x + 2][y + 2 + i] = -1
        scores[x + 6][y + i] = -1
        scores[x + 4][y + 2 + i] = -1
        scores[x + i][y + 2] = -1
        scores[x + 4 + i][y] = -1
        scores[x + 4 + i][y + 2] = -1
        scores[x + 4 + i][y + 4] = -1


def kruskal_generator(width: int, height: int, seed: float, perfect: bool):
    random.seed(seed)
    maze = [[[1, 1, 1, 1] for y in range(height)] for x in range(width)]
    scores = [[1 for y in range(height)] for x in range(width)]
    k = 1
    for x in range(width):
        for y in range(height):
            scores[x][y] = k
            k += 1
    add_forty_two_pattern(width, height, scores)
    vertical_breakable_walls = [[(x, y), (x, y + 1)]
                                for x in range(width)
                                for y in range(height - 1)
                                if
                                scores[x][y] != -1 and scores[x][y + 1] != -1]
    horizontal_breakable_walls = [[(x, y), (x + 1, y)]
                                  for x in range(width - 1)
                                  for y in range(height)
                                  if
                                  scores[x][y] != -1 and scores[x + 1][y] != -1]
    breakable_walls = vertical_breakable_walls + horizontal_breakable_walls
    available_walls = []
    while breakable_walls != []:
        (u, v), (x, y) = random.choice(breakable_walls)
        if scores[u][v] != scores[x][y]:
            change_wall((u, v), (x, y), maze, 0)
            for (i, j) in [(i, j) for i in range(width) for j in range(height)
                           if scores[i][j] == scores[x][y]]:
                scores[i][j] = scores[u][v]
        else:
            available_walls.append([(u, v), (x, y)])
        breakable_walls.remove([(u, v), (x, y)])

    if perfect is False:
        while True:
            (u, v), (x, y) = random.choice(available_walls)
            change_wall((u, v), (x, y), maze, 0)
            if check_large_open_areas(width, height, maze):
                break
            change_wall((u, v), (x, y), maze, 1)
            available_walls.remove([(u, v), (x, y)])
    return maze


def connected_neighbors(cell, maze):
    neighbors = []
    if maze[cell[0]][cell[1]][0] == 0:
        neighbors.append((cell[0] - 1, cell[1]))
    if maze[cell[0]][cell[1]][1] == 0:
        neighbors.append((cell[0], cell[1] + 1))
    if maze[cell[0]][cell[1]][2] == 0:
        neighbors.append((cell[0] + 1, cell[1]))
    if maze[cell[0]][cell[1]][3] == 0:
        neighbors.append((cell[0], cell[1] - 1))
    return neighbors


def bfts_solution(width: int, height: int, maze, entry, exit):
    visited_matrix = [[False for y in range(height)] for x in range(width)]
    solution_path = "\n"
    segments = [[entry, entry]]
    current_cell = entry
    i = 0
    while current_cell != exit:
        visited_matrix[current_cell[0]][current_cell[1]] = True
        for neighbor in connected_neighbors(current_cell, maze):
            if visited_matrix[neighbor[0]][neighbor[1]] is False:
                segments.append([current_cell, neighbor])
        i += 1
        current_cell = segments[i][1]
    while current_cell != entry:
        visited_cells = [segment[1] for segment in segments]
        predecessor = segments[visited_cells.index(current_cell)][0]
        if predecessor[0] == current_cell[0]:
            if predecessor[1] < current_cell[1]:
                solution_path = "S" + solution_path
            else:
                solution_path = "N" + solution_path
        else:
            if predecessor[0] < current_cell[0]:
                solution_path = "E" + solution_path
            else:
                solution_path = "W" + solution_path
        current_cell = predecessor
    return solution_path


if __name__ == "__main__":
    start = time.time()
    width = 10
    height = 10
    maze = kruskal_generator(width, height, 42, True)
    print(bfts_solution(width, height, maze, (0, 0), (9, 9)))
    end = time.time()
    print(f'Elapsed: {end - start:.2f} seconds')
    with open("maze.txt", "a") as f:
        for y in range(height):
            str = ""
            for x in range(width):
                hexa = maze[x][y][0] * 8 + maze[x][y][1] * 4 + maze[x][y][
                    2] * 2 + \
                       maze[x][y][3]
                if hexa < 10:
                    str += f"{hexa}"
                else:
                    str += f'{chr(65 + hexa - 10)}'
            f.write(str + "\n")
