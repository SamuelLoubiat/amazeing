from random import random
from typing import Any

from mlx import Mlx

from Config import Config
from maze_gen import kruskal_generator, bfts_solution


class AMazeFrame:
    def __init__(self) -> None:
        self.__maze_dict: dict[Any, Any] = {}
        self.__settings: Config
        self.__mlx_window = None
        self.__mx = Mlx()
        self.__mlx_ptr = self.__mx.mlx_init()
        v, self.__width, self.__height = self.__mx.mlx_get_screen_size(
            self.__mlx_ptr)
        self.__width = int(self.__width * 0.9)
        self.__height = int(self.__height * 0.9)
        self.__img = self.__mx.mlx_new_image(self.__mlx_ptr, self.__width,
                                             self.__height)
        addr_raw, bpp, line_size, endian = self.__mx.mlx_get_data_addr(
            self.__img)

        self.__addr = addr_raw.cast('I')
        self.__stride = line_size // (bpp // 8)
        self.offset = 25
        self.__paff = False
        self.__update = True
        self.colors = [
            {'wall': 0xFFFFFFFF, 'paff': 0xFF123456, 'background': 0xFF000000},
            {'wall': 0xFF2C3E50, 'background': 0xFF1A1A1A, 'paff': 0xFFE74C3C},
            {'wall': 0xFF0F380F, 'background': 0xFF8BAC0F, 'paff': 0xFF9BBC0F},
            {'wall': 0xFF4B0082, 'background': 0xFF212121, 'paff': 0xFF9B59B6}]
        self.colors_index = 0

    def close(self, *param: Any) -> None:
        if param[0] == 113:
            self.__mx.mlx_destroy_image(self.__mlx_ptr, self.__img)
            self.__mx.mlx_destroy_window(self.__mlx_ptr, self.__mlx_window)
            self.__mx.mlx_loop_exit(self.__mlx_ptr)
        if param[0] == 112:
            self.__paff = not self.__paff
            self.__update = True
        if param[0] == 99:
            self.colors_index += 1
            if self.colors_index == len(self.colors):
                self.colors_index = 0
            self.__maze_dict['wall_color'] = self.colors[self.colors_index][
                'wall']
            self.__maze_dict['paff_color'] = self.colors[self.colors_index][
                'paff']
            self.__maze_dict['background_color'] = \
                self.colors[self.colors_index]['background']
            self.__update = True
        if param[0] == 114:
            maze = kruskal_generator(self.__settings.width,
                                     self.__settings.height, random(),
                                     self.__settings.perfect)
            self.__maze_dict['maze_resolv'] = bfts_solution(
                self.__settings.width,
                self.__settings.height, maze,
                self.__settings.entry,
                self.__settings.exit)

            self.__maze_dict['maze'] = maze
            self.__update = True

    def close_icon(self, _: Any) -> None:
        self.__mx.mlx_destroy_image(self.__mlx_ptr, self.__img)
        self.__mx.mlx_destroy_window(self.__mlx_ptr, self.__mlx_window)
        self.__mx.mlx_loop_exit(self.__mlx_ptr)

    def create_window(self, title: str) -> None:
        self.__mlx_window = self.__mx.mlx_new_window(self.__mlx_ptr,
                                                     self.__width,
                                                     self.__height, title)
        self.__mx.mlx_hook(self.__mlx_window, 2, 1, self.close, self)
        self.__mx.mlx_hook(self.__mlx_window, 33, 0, self.close_icon, self)

    def draw(self, x_from: int, x_to: int, y_from: int, y_to: int,
             color: Any) -> None:
        for x in range(x_from, x_to + 1):
            for y in range(y_from, y_to + 1):
                try:
                    self.__addr[y * self.__stride + x] = color
                except IndexError:
                    raise Exception(x, y)

    def draw_help(self) -> None:
        self.__mx.mlx_string_put(self.__mlx_ptr, self.__mlx_window, 25,
                                 self.__height - 110, 0xFFFFFFFF,
                                 "A-Maze-Ing keyboard Help")
        self.__mx.mlx_string_put(self.__mlx_ptr, self.__mlx_window, 25,
                                 self.__height - 20, 0xFFFFFFFF,
                                 "P: Show/Hide THE BIG PAFF")
        self.__mx.mlx_string_put(self.__mlx_ptr, self.__mlx_window, 25,
                                 self.__height - 40, 0xFFFFFFFF,
                                 "Q: Quit the program")
        self.__mx.mlx_string_put(self.__mlx_ptr, self.__mlx_window, 25,
                                 self.__height - 60, 0xFFFFFFFF,
                                 "C: change color")
        self.__mx.mlx_string_put(self.__mlx_ptr, self.__mlx_window, 25,
                                 self.__height - 80, 0xFFFFFFFF,
                                 "R: Regen the Maze")

    def draw_connection(self, last_char: str, cell: tuple[int, int],
                        color: Any) -> None:
        x, y = cell
        if last_char == 'N':
            self.draw(x * self.cell_x + (self.cell_x // 4),
                      (x + 1) * self.cell_x - (self.cell_x // 4),
                      y * self.cell_y + (self.cell_y // 2),
                      (y + 2) * self.cell_y - (self.cell_y // 2),
                      color)
        if last_char == 'S':
            self.draw(x * self.cell_x + (self.cell_x // 4),
                      (x + 1) * self.cell_x - (self.cell_x // 4),
                      (y - 1) * self.cell_y + (self.cell_y // 2),
                      (y + 1) * self.cell_y - (self.cell_y // 2),
                      color)
        if last_char == 'W':
            self.draw(x * self.cell_x + (self.cell_x // 2),
                      (x + 2) * self.cell_x - (self.cell_x // 2),
                      y * self.cell_y + (self.cell_y // 4),
                      (y + 1) * self.cell_y - (self.cell_y // 4),
                      color)
        if last_char == 'E':
            self.draw((x - 1) * self.cell_x + (self.cell_x // 2),
                      (x + 1) * self.cell_x - (self.cell_x // 2),
                      y * self.cell_y + (self.cell_y // 4),
                      (y + 1) * self.cell_y - (self.cell_y // 4),
                      color)

    def __generate_maze(self, *param: Any) -> None:
        if not self.__update:
            return
        maze = self.__maze_dict['maze']
        maze_entry = self.__maze_dict['maze_entry']
        maze_exit = self.__maze_dict['maze_exit']
        wall_color = self.__maze_dict['wall_color']
        for y in range(self.__settings.height):
            for x in range(self.__settings.width):
                real_x = x * self.cell_x
                real_y = y * self.cell_y
                self.draw(real_x, real_x + self.cell_x,
                          real_y, real_y + self.cell_y,
                          self.__maze_dict['background_color'])
                if (x, y) == maze_entry or (x, y) == maze_exit:
                    self.draw(real_x, real_x + self.cell_x,
                              real_y, real_y + self.cell_y, 0xFF3456FF)
                if maze[x][y][0] and maze[x][y][1] and maze[x][y][2] and \
                        maze[x][y][3]:
                    self.draw(real_x, real_x + self.cell_x, real_y,
                              real_y + self.cell_y, wall_color)
                    continue
                if maze[x][y][3]:  # Mur Nord
                    self.draw(real_x, real_x + self.cell_x, real_y,
                              real_y, wall_color)
                if maze[x][y][1]:  # Mur Sud
                    self.draw(real_x, real_x + self.cell_x,
                              real_y + self.cell_y, real_y + self.cell_y,
                              wall_color)
                if maze[x][y][2]:  # Mur Est
                    self.draw(real_x + self.cell_x, real_x + self.cell_x,
                              real_y, real_y + self.cell_y, wall_color)
                if maze[x][y][0]:  # Mur Ouest
                    self.draw(real_x, real_x, real_y, real_y + self.cell_y,
                              wall_color)

        if self.__paff:
            paff_color = self.__maze_dict['paff_color']
            x, y = maze_entry
            last_char: str = ''
            for char in self.__maze_dict['maze_resolv']:
                if last_char != '':
                    self.draw_connection(last_char, (x, y), paff_color)
                if char == 'N':
                    y -= 1
                elif char == 'S':
                    y += 1
                elif char == 'W':
                    x -= 1
                elif char == 'E':
                    x += 1
                last_char = char
            self.draw_connection(last_char, (x, y), paff_color)

        self.draw_help()
        self.__mx.mlx_put_image_to_window(self.__mlx_ptr,
                                          self.__mlx_window, self.__img,
                                          (self.__width - self.cell_x *
                                           self.__settings.width) // 2,
                                          ((self.__height - 100) - self.cell_y
                                           * self.__settings.height) // 2)
        self.__update = False

    def generate_maze(self, maze: Any, settings: Config,
                      maze_resolv: str) -> None:
        self.__settings = settings
        self.__maze_dict = {'maze': maze, 'maze_entry': settings.entry,
                            'maze_exit': settings.exit,
                            'maze_resolv': maze_resolv,
                            'wall_color': 0xFFFFFFFF,
                            'paff_color': 0xFF123456,
                            'background_color': 0xFF000000}
        img_w = self.__width - 50
        img_h = self.__height - 150
        size = 0
        if img_w == img_h:
            size = img_w
        elif img_w < img_h:
            size = img_w
        elif img_w > img_h:
            size = img_h

        self.cell_x = size // self.__settings.width
        self.cell_y = size // self.__settings.height
        self.__mx.mlx_loop_hook(self.__mlx_ptr, self.__generate_maze, None)

    def start_loop(self) -> None:
        self.__mx.mlx_loop(self.__mlx_ptr)
