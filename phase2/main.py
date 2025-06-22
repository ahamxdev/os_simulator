# main.py

import os
from input_reader import read_input
from fcfs_scheduler import fcfs_scheduler


def main():
    file_path = os.path.join("..", "phase1", "input.txt")

    processes = read_input(file_path)
    fcfs_scheduler(processes)

if __name__ == '__main__':
    main()
