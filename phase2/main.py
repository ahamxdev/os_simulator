import os
from input_reader import read_input
from fcfs_scheduler import fcfs_scheduler

def main():
    file_path = os.path.join("..", "phase1", "input.txt")
    processes = read_input(file_path)

    total_resources = [0, 1, 0]

    fcfs_scheduler(processes, total_resources)

if __name__ == '__main__':
    main()
