# input_reader.py

from process import Process

def read_input(filename):
    with open(filename) as f:
        input_lines = f.read().splitlines()

    idx = 0
    n = int(input_lines[idx]); idx += 1
    m = int(input_lines[idx]); idx += 1
    _ = input_lines[idx]; idx += 1
    ps, pc = map(int, input_lines[idx].split()); idx += 1  #

    processes = []
    for pid in range(n):
        ic = int(input_lines[idx]); idx += 1
        proc = Process(pid)
        for _ in range(ic):
            parts = input_lines[idx].split()
            command = parts[0]
            args = list(map(int, parts[1:]))
            proc.add_command(command, *args)
            idx += 1
        processes.append(proc)

    return processes
