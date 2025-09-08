# simulation.py
from collections import deque
from safety_checker import is_safe

def run_simulation(n, m, total_resources, processes):
    time = 0
    event_log = []
    ready_queue = deque(processes)
    available = total_resources.copy()
    max_time = 1000

    # Initialize max demand
    for p in processes:
        p.allocation = [0] * m
        p.max_demand = [0] * m
        for instr in p.instructions:
            if instr[0] == 'Allocate':
                X, Y = int(instr[1]), int(instr[2])
                p.max_demand[Y] += X

    blocked_processes = set()

    while time < max_time and any(p.state != 'FINISHED' for p in processes):
        # Wake sleeping processes
        for p in processes:
            if p.state == 'SLEEP' and time >= p.sleep_until:
                p.state = 'READY'
                ready_queue.append(p)
                blocked_processes.discard(p.pid)

        if not ready_queue:
            sleeping = [p.sleep_until for p in processes if p.state == 'SLEEP']
            if sleeping:
                time = min(sleeping)
                continue
            if all(p.pid in blocked_processes for p in processes if p.state != 'FINISHED'):
                break
            time += 1
            continue

        p = ready_queue.popleft()
        if p.pc >= len(p.instructions):
            p.state = 'FINISHED'
            blocked_processes.discard(p.pid)
            continue

        instr = p.instructions[p.pc]
        cmd = instr[0]
        made_progress = False

        if cmd == 'Run':
            dur = int(instr[1])
            event_log.append(f'EXECUTE {p.pid} {time} {time + dur}')
            time += dur
            p.pc += 1
            made_progress = True

        elif cmd == 'Sleep':
            dur = int(instr[1])
            event_log.append(f'WAIT {p.pid} {time} {time + dur}')
            p.sleep_until = time + dur
            p.state = 'SLEEP'
            p.pc += 1
            made_progress = True

        elif cmd == 'Allocate':
            X, Y = int(instr[1]), int(instr[2])
            request = [0] * m
            request[Y] = X
            if available[Y] >= X and p.allocation[Y] + X <= p.max_demand[Y] and is_safe(processes, available, p.pid, request):
                p.allocation[Y] += X
                available[Y] -= X
                event_log.append(f'TAKE {p.pid} {X} {Y} {time}')
                p.pc += 1
                made_progress = True
            else:
                blocked_processes.add(p.pid)

        elif cmd == 'Free':
            X, Y = int(instr[1]), int(instr[2])
            if p.allocation[Y] >= X:
                p.allocation[Y] -= X
                available[Y] += X
                event_log.append(f'GIVE {p.pid} {X} {Y} {time}')
                p.pc += 1
                made_progress = True
                blocked_processes.clear()
                for proc in processes:
                    if proc.state == 'READY' and proc.pc < len(proc.instructions) and proc not in ready_queue:
                        ready_queue.append(proc)

        if made_progress:
            blocked_processes.discard(p.pid)
            if p.state == 'READY' and p.pc < len(p.instructions):
                ready_queue.append(p)

    if time >= max_time:
        print("WARNING: Simulation stopped after reaching maximum time limit")

    print(len(event_log))
    for e in event_log:
        print(e)
