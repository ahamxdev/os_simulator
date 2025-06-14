import sys
from process import Process
from scheduler import fcfs_scheduler

def main():

    input_lines = sys.stdin.read().splitlines()
    idx = 0

    n = int(input_lines[idx])
    idx += 1

    m = int(input_lines[idx])
    idx += 1

    resource_line = input_lines[idx]
    idx += 1

    ps, pc = map(int, input_lines[idx].split())
    idx += 1

    processes = []
    for pid in range(n):
        ic = int(input_lines[idx])
        idx += 1
        proc = Process(pid)
        for _ in range(ic):
            parts = input_lines[idx].split()
            command = parts[0]
            args = list(map(int, parts[1:]))
            proc.add_command(command, *args)
            idx += 1
        processes.append(proc)

    output = fcfs_scheduler(processes)
    print(len(output))
    for line in output:
        print(line)

if __name__ == "__main__":
    main()
