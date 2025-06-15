# main.py

from input_reader import read_input
from fcfs_scheduler import fcfs_scheduler

def main():
    processes = read_input(r"C:\Users\Gcc\Desktop\os_simulator\phase1\input.txt")
    fcfs_scheduler(processes)

if __name__ == '__main__':
    main()
