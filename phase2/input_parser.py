# input_parser.py
import sys
from process import Process

def parse_input(filename="input.txt"):
    try:
        with open(filename) as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERROR: File '{filename}' not found")
        sys.exit(1)

    def get_line():
        if not lines:
            raise ValueError("Unexpected end of input file")
        return lines.pop(0)

    try:
        n = int(get_line())
        m = int(get_line())
        total_resources = list(map(int, get_line().split()))
        if len(total_resources) != m:
            raise ValueError(f"Expected {m} resource values, got {len(total_resources)}")

        processes = []

        for pid in range(n):
            ic = int(get_line())
            instructions = []
            for _ in range(ic):
                parts = get_line().split()
                if not parts:
                    raise ValueError("Empty instruction")
                cmd = parts[0]
                if cmd in ['Run', 'Sleep']:
                    if len(parts) != 2 or not parts[1].isdigit():
                        raise ValueError(f"Invalid {cmd} instruction format")
                elif cmd in ['Allocate', 'Free']:
                    if len(parts) != 3 or not all(p.isdigit() for p in parts[1:]):
                        raise ValueError(f"Invalid {cmd} instruction format")
                instructions.append(parts)
            processes.append(Process(pid, instructions))

        return n, m, total_resources, processes

    except ValueError as e:
        print(f"ERROR parsing input: {e}")
        sys.exit(1)
