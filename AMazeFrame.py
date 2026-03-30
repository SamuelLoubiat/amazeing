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

    def close(self, keytype, param):
        if keytype == 113:
            self.__mx.mlx_destroy_image(self.__mlx_ptr, self.__img)
            self.__mx.mlx_destroy_window(self.__mlx_ptr, self.__mlx_window)
            self.__mx.mlx_loop_exit(self.__mlx_ptr)
        if keytype == 112:
            self.__paff = not self.__paff

    def close_icon(self, param):
        self.__mx.mlx_destroy_image(self.__mlx_ptr, self.__img)
        self.__mx.mlx_destroy_window(self.__mlx_ptr, self.__mlx_window)
        self.__mx.mlx_loop_exit(self.__mlx_ptr)

    def create_window(self, title: str) -> None:
        self.__mlx_window = self.__mx.mlx_new_window(self.__mlx_ptr,
                                                     self.__width,
                                                     self.__height, title)
        self.__mx.mlx_hook(self.__mlx_window, 2, 1, self.close, self)
        self.__mx.mlx_hook(self.__mlx_window, 33, 0, self.close_icon, None)

    def add_pixel(self, addr, x, y, stride, color):
        addr[y * stride + x] = color

    def __generate_background(self, color):
        addr_raw, bpp, line_size, endian = self.__mx.mlx_get_data_addr(
            self.__img)

        addr = addr_raw.cast('I')
        stride = line_size // (bpp // 8)
        for y in range(self.__height):
            for x in range(self.__width):
                self.add_pixel(addr, x, y, stride, color)

    def generate_background(self, color) -> None:
        self.__mx.mlx_loop_hook(self.__mlx_ptr, self.__generate_background,
                                color)

    def draw_x(self, addr, stride, x_start, x_end, y, color):
        for x in range(x_start, x_end):
            for i in range(4):
                addr[(y + self.offset + i) * stride
                     + (x + self.offset)] = color

    def draw_y(self, addr, stride, y_start, y_end, x, color):
        for y in range(y_start, y_end):
            for i in range(4):
                addr[(y + self.offset) * stride
                     + (x + self.offset + i)] = color

    def draw_cube(self, addr, stride, x_from, x_to, y_from, y_to, color):
        for x in range(x_from, x_to):
            for y in range(y_from, y_to):
                addr[(y + self.offset) * stride + (x + self.offset)] = color

    def __generate_maze(self, maze_dict: dict):
        maze = maze_dict['maze']
        maze_entry = maze_dict['maze_entry']
        maze_exit = maze_dict['maze_exit']
        resolver = maze_dict['maze_resolv']
        img_w = self.__width - 50
        img_h = self.__height - 50
        addr_raw, bpp, line_size, endian = self.__mx.mlx_get_data_addr(
            self.__img)

        addr = addr_raw.cast('I')
        stride = line_size // (bpp // 8)

        maze_size_x = 0
        maze_size_y = 1

        for char in maze:
            if char == '\n':
                break
            maze_size_x += 1

        for char in maze:
            if char == '\n':
                maze_size_y += 1

        cell_x = img_w // maze_size_x
        cell_y = img_h // maze_size_y
        x = 0
        y = 0
        for char in maze:
            if char == '\n':
                x = 0
                # self.__mx.mlx_put_image_to_window(self.__mlx_ptr,
                #                                  self.__mlx_window,
                #                                  self.__img, 0, 0)
                y += 1
                continue

            self.draw_cube(addr, stride, x * cell_x, x * cell_x + cell_x,
                           cell_y * y, cell_y * y + cell_y, 0x1F000000)
            bits = int(char, 16)
            if (x, y) == maze_entry or (x, y) == maze_exit:
                self.draw_cube(addr, stride, x * cell_x, x * cell_x + cell_x,
                               cell_y * y, cell_y * y + cell_y, 0x123456FF)
            if bits == 15:
                self.draw_cube(addr, stride, x * cell_x, x * cell_x + cell_x,
                               cell_y * y, cell_y * y + cell_y, 0xFFFFFFFF)
                x += 1
                continue
            if bits & (1 << 0):  # Mur Nord
                self.draw_x(addr, stride, x * cell_x, x * cell_x + cell_x,
                            cell_y * y, 0xFFFFFFFF)
            if bits & (1 << 2):  # Mur Sud
                self.draw_x(addr, stride, x * cell_x, x * cell_x + cell_x + 4,
                            cell_y * y + cell_y, 0xFFFFFFFF)
            if bits & (1 << 1):  # Mur Est
                self.draw_y(addr, stride, cell_y * y, cell_y * y + cell_y,
                            x * cell_x + cell_x, 0xFFFFFFFF)
            if bits & (1 << 3):  # Mur Ouest
                self.draw_y(addr, stride, cell_y * y, cell_y * y + cell_y,
                            x * cell_x, 0xFFFFFFFF)
            #self.__mx.mlx_put_image_to_window(self.__mlx_ptr,
            #                                  self.__mlx_window,
            #                                  self.__img, 0, 0)

            x += 1

        x, y = maze_entry
        x_end, y_end = maze_exit
        last_char: str | None = None
        if self.__paff:
            for char in resolver:
                if char == 'N':
                    if last_char is None:
                        pass
                    else:
                        for i in range(-4, 3):
                            self.draw_y(addr, stride, cell_y * y,
                                        cell_y * y + (cell_y // 2),
                                        x * cell_x + (cell_x // 2) + i,
                                        0xFFFF0000)
                    y -= 1
                elif char == 'S':
                    if last_char is None:
                        for i in range(-4, 3):
                            self.draw_y(addr, stride,
                                        cell_y * (y + 1) - (cell_y // 2),
                                        cell_y * (y + 1),
                                        x * cell_x + (cell_x // 2) + i,
                                        0xFFFF0000)
                        self.draw_cube(addr, stride, x * cell_x
                                       + (cell_x // 5),
                                       x * cell_x + cell_x - (cell_x // 5),
                                       cell_y * y + (cell_y // 5),
                                       cell_y * y + cell_y - (cell_y // 5),
                                       0xFFFF0000)
                    else:
                        for i in range(-4, 3):
                            self.draw_y(addr, stride,
                                        cell_y * (y + 1) - (cell_y // 2),
                                        cell_y * (y + 1),
                                        x * cell_x + (cell_x // 2) + i,
                                        0xFFFF0000)
                    y += 1
                elif char == 'W':
                    if last_char is None:
                        pass
                    else:
                        for i in range(-4, 3):
                            self.draw_x(addr, stride, cell_x * x,
                                        cell_x * x + (cell_x // 2),
                                        y * cell_y + (cell_y // 2) + i,
                                        0xFFFF0000)
                    x -= 1
                elif char == 'E':
                    if last_char is None:
                        pass
                    else:
                        for i in range(-4, 3):
                            self.draw_x(addr, stride,
                                        cell_x * x + (cell_x // 2),
                                        cell_x * (x + 1),
                                        y * cell_y + (cell_y // 2) + i,
                                        0xFFFF0000)
                    x += 1
                last_char = char
                if x == x_end and y == y_end:
                    self.draw_cube(addr, stride, x * cell_x + (cell_x // 5),
                                   x * cell_x + cell_x - (cell_x // 5),
                                   cell_y * y + (cell_y // 5),
                                   cell_y * y + cell_y - (cell_y // 5),
                                   0xFFFF0000)
        self.__mx.mlx_put_image_to_window(self.__mlx_ptr,
                                          self.__mlx_window,
                                          self.__img, 0, 0)

    def generate_maze(self, maze: str, maze_entry: tuple[int, int],
                      maze_exit: tuple[int, int], maze_resolv: str):
        self.__mx.mlx_loop_hook(self.__mlx_ptr, self.__generate_maze,
                                {'maze': maze, 'maze_entry': maze_entry,
                                 'maze_exit': maze_exit,
                                 'maze_resolv': maze_resolv})

    def start_loop(self):
        self.__mx.mlx_loop(self.__mlx_ptr)
