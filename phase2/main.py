# main.py
import sys
from input_parser import parse_input
from simulation import run_simulation

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"

    try:
        n, m, total_resources, ps, pc, processes = parse_input(input_file)
        run_simulation(n, m, total_resources, processes)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
