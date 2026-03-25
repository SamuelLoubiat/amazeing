from AMazeFrame import AMazeFrame

def main():
    am = AMazeFrame(1020, 1020)
    am.create_window('A-Maze-Ing')
    #am.generate_background(0xFFFFFFFF)
    am.generate_maze('FFFF\nFFFF\nFFFF\nFFFF')
    am.start_loop()


main()