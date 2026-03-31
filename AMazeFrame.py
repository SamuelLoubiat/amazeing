from typing import Any

from mlx import Mlx


class AMazeFrame:

    def __init__(self, width: int, height: int) -> None:
        self.__mlx_window = None
        self.__width = width
        self.__height = height
        self.__mx = Mlx()
        self.__mlx_ptr = self.__mx.mlx_init()
        self.__img = self.__mx.mlx_new_image(self.__mlx_ptr, width, height)
        self.current_idx = 0
        self.offset = 25
        self.__paff = False
        self.colors = [{'wall': 0xFFFFFFFF,
                                 'paff': 0xFF123456,
                                 'background': 0x5F000000}, {'wall': 0xFF2C3E50, 'background': 0xFF1A1A1A, 'paff': 0xFFE74C3C}, {'wall': 0xFF0F380F, 'background': 0xFF8BAC0F, 'paff': 0xFF9BBC0F}, {'wall': 0xFF4B0082, 'background': 0xFF212121, 'paff': 0xFF9B59B6}]
        self.colors_index = 0

    def close(self, *param: Any) -> None:
        if param[0] == 113:
            self.__mx.mlx_destroy_image(self.__mlx_ptr, self.__img)
            self.__mx.mlx_destroy_window(self.__mlx_ptr, self.__mlx_window)
            self.__mx.mlx_loop_exit(self.__mlx_ptr)
        if param[0] == 112:
            self.__paff = not self.__paff
        if param[0] == 99:
            self.colors_index += 1
            if self.colors_index == len(self.colors):
                self.colors_index = 0
            self.__maze_dict['wall_color'] = self.colors[self.colors_index]['wall']
            self.__maze_dict['paff_color'] = self.colors[self.colors_index]['paff']
            self.__maze_dict['background_color'] = self.colors[self.colors_index]['background']


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

    def add_pixel(self, x: int, y: int, color: int) -> None:
        self.__addr[y * self.__stride + x] = color

    def __generate_background(self, color: Any) -> None:
        for y in range(self.__height):
            for x in range(self.__width):
                self.add_pixel(x, y, color)

    def generate_background(self, color: Any) -> None:
        self.__mx.mlx_loop_hook(self.__mlx_ptr, self.__generate_background,
                                color)

    def draw_x(self, x_start: int, x_end: int, y: int, color: Any) -> None:
        for x in range(x_start, x_end):
            for i in range(1):
                self.__addr[(y + self.offset + i) * self.__stride
                            + (x + self.offset)] = color

    def draw_y(self, y_start: int, y_end: int, x: int, color: Any) -> None:
        for y in range(y_start, y_end):
            for i in range(1):
                self.__addr[(y + self.offset) * self.__stride
                            + (x + self.offset + i)] = color

    def draw_cube(self, x_from: int, x_to: int, y_from: int, y_to: int,
                  color: Any) -> None:
        for x in range(x_from, x_to):
            for y in range(y_from, y_to):
                self.__addr[(y + self.offset) * self.__stride + (
                        x + self.offset)] = color

    def draw_connection(self, last_char: str, cell: tuple[int, int],
                        color: Any) -> None:
        x, y = cell
        if last_char == 'N':
            self.draw_cube(x * self.cell_x + (self.cell_x // 4),
                           (x + 1) * self.cell_x - (self.cell_x // 4),
                           y * self.cell_y + (self.cell_y // 2),
                           (y + 2) * self.cell_y - (self.cell_y // 2),
                           color)
        if last_char == 'S':
            self.draw_cube(x * self.cell_x + (self.cell_x // 4),
                           (x + 1) * self.cell_x - (self.cell_x // 4),
                           (y - 1) * self.cell_y + (self.cell_y // 2),
                           (y + 1) * self.cell_y - (self.cell_y // 2),
                           color)
        if last_char == 'W':
            self.draw_cube(x * self.cell_x + (self.cell_x // 2),
                           (x + 2) * self.cell_x - (self.cell_x // 2),
                           y * self.cell_y + (self.cell_y // 4),
                           (y + 1) * self.cell_y - (self.cell_y // 4),
                           color)
        if last_char == 'E':
            self.draw_cube((x - 1) * self.cell_x + (self.cell_x // 2),
                           (x + 1) * self.cell_x - (self.cell_x // 2),
                           y * self.cell_y + (self.cell_y // 4),
                           (y + 1) * self.cell_y - (self.cell_y // 4),
                           color)

    def __generate_maze(self, maze_dict: dict[Any, Any]) -> None:
        maze = maze_dict['maze']
        maze_entry = maze_dict['maze_entry']
        maze_exit = maze_dict['maze_exit']
        resolver = maze_dict['maze_resolv']
        wall_color = maze_dict['wall_color']
        paff_color = maze_dict['paff_color']
        background_color = maze_dict['background_color']
        img_w = self.__width - 50
        img_h = self.__height - 50
        addr_raw, bpp, line_size, endian = self.__mx.mlx_get_data_addr(
            self.__img)

        self.__addr = addr_raw.cast('I')
        self.__stride = line_size // (bpp // 8)

        maze_size_x = 0
        maze_size_y = 1

        for char in maze:
            if char == '\n':
                break
            maze_size_x += 1

        for char in maze:
            if char == '\n':
                maze_size_y += 1

        self.cell_x = img_w // maze_size_x
        self.cell_y = img_h // maze_size_y
        x = 0
        y = 0
        for char in maze:
            if char == '\n':
                x = 0
                y += 1
                continue

            self.draw_cube(x * self.cell_x,
                           x * self.cell_x + self.cell_x,
                           self.cell_y * y, self.cell_y * y + self.cell_y,
                           background_color)
            bits = int(char, 16)
            if (x, y) == maze_entry or (x, y) == maze_exit:
                self.draw_cube(x * self.cell_x, x * self.cell_x + self.cell_x,
                               self.cell_y * y, self.cell_y * y + self.cell_y,
                               0x5F3456FF)
            if bits == 15:
                self.draw_cube(x * self.cell_x, x * self.cell_x + self.cell_x,
                               self.cell_y * y, self.cell_y * y + self.cell_y,
                               wall_color)
                x += 1
                continue
            if bits & (1 << 0):  # Mur Nord
                self.draw_x(x * self.cell_x, (x * self.cell_x + self.cell_x),
                            self.cell_y * y, wall_color)
            if bits & (1 << 2):  # Mur Sud
                self.draw_x(x * self.cell_x, x * self.cell_x + self.cell_x,
                            self.cell_y * y + self.cell_y, wall_color)
            if bits & (1 << 1):  # Mur Est
                self.draw_y(self.cell_y * y, self.cell_y * y + self.cell_y,
                            x * self.cell_x + self.cell_x, wall_color)
            if bits & (1 << 3):  # Mur Ouest
                self.draw_y(self.cell_y * y, self.cell_y * y + self.cell_y,
                            x * self.cell_x, wall_color)
            x += 1

        x, y = maze_entry
        last_char: str = ''
        if self.__paff:
            for char in resolver:
                if last_char is not '':
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
        self.__mx.mlx_put_image_to_window(self.__mlx_ptr,
                                          self.__mlx_window,
                                          self.__img, 0, 0)

    def generate_maze(self, maze: str, maze_entry: tuple[int, int],
                      maze_exit: tuple[int, int], maze_resolv: str) -> None:
        self.__maze_dict = {'maze': maze, 'maze_entry': maze_entry,
                                 'maze_exit': maze_exit,
                                 'maze_resolv': maze_resolv,
                                 'wall_color': 0xFFFFFFFF,
                                 'paff_color': 0xFF123456,
                                 'background_color': 0x5F000000}
        self.__mx.mlx_loop_hook(self.__mlx_ptr, self.__generate_maze,
                                self.__maze_dict)

    def start_loop(self) -> None:
        self.__mx.mlx_loop(self.__mlx_ptr)
