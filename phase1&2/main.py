import sys
from process import Process
from scheduler import fcfs_scheduler

def main():
    # Read all input lines
    input_lines = sys.stdin.read().splitlines()
    idx = 0

    # n: number of processes
    n = int(input_lines[idx]); idx += 1

    # m: number of resource types
    m = int(input_lines[idx]); idx += 1

    # available resources vector (len = m)
    available = list(map(int, input_lines[idx].split())) if m > 0 else []
    idx += 1

    # PS, PC (not used in phases 1&2)
    ps, pc = map(int, input_lines[idx].split()); idx += 1

    processes = []
    for pid in range(n):
        ic = int(input_lines[idx]); idx += 1
        proc = Process(pid)
        for _ in range(ic):
            parts = input_lines[idx].split(); idx += 1
            cmd = parts[0]
            args = list(map(int, parts[1:]))
            proc.add_command(cmd, *args)
        processes.append(proc)

    # Phase 1: FCFS CPU scheduling
    # Phase 2: Deadlock Detection & Recovery (NOT Banker's)
    fcfs_scheduler(processes, available_resources=available)

if __name__ == "__main__":
    main()
