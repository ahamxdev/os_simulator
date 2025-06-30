from collections import deque
from copy import deepcopy
from process import Process

def is_safe_state(available, allocation, need):
    n = len(allocation)
    m = len(available)
    work = available[:]
    finish = [False] * n

    while True:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += allocation[i][j]
                finish[i] = True
                found = True
        if not found:
            break

    return all(finish)

def fcfs_scheduler(processes, total_resources):
    current_time = 0
    n = len(processes)
    m = len(total_resources)

    available_resources = total_resources[:]
    allocation = [[0]*m for _ in range(n)]
    need = [[0]*m for _ in range(n)]

    ready_queue = deque([{'proc': p, 'index': 0} for p in processes])
    sleep_list = []
    blocked_on_resource = {}
    output = []
    timeline = {}

    max_runtime = 100000
    iteration = 0

    while (ready_queue or sleep_list or any(blocked_on_resource.values())) and iteration < max_runtime:
        iteration += 1

        sleep_list.sort(key=lambda x: x[0])
        for wake_time, p_obj in sleep_list[:]:
            if wake_time <= current_time:
                ready_queue.append(p_obj)
                sleep_list.remove((wake_time, p_obj))

        for res, queue in list(blocked_on_resource.items()):
            if available_resources[res] > 0 and queue:
                ready_queue.append(queue.popleft())
                if not queue:
                    del blocked_on_resource[res]

        if not ready_queue:
            current_time += 1
            continue

        current = ready_queue.popleft()
        proc, idx = current['proc'], current['index']

        if proc.pid not in timeline:
            timeline[proc.pid] = []

        if idx >= len(proc.commands):
            continue

        cmd = proc.commands[idx]
        op = cmd[0]

        if op == 'Run':
            dur = cmd[1]
            output.append(f"EXECUTE {proc.pid} {current_time} {current_time + dur}")
            timeline[proc.pid] += ['E'] * dur
            current_time += dur
            current['index'] += 1
            ready_queue.append(current)

        elif op == 'Sleep':
            dur = cmd[1]
            output.append(f"WAIT {proc.pid} {current_time} {current_time + dur}")
            timeline[proc.pid] += ['W'] * dur
            sleep_list.append((current_time + dur, current))
            current['index'] += 1
            current_time += dur

        elif op == 'Allocate':
            res = cmd[1]
            qty = cmd[2]
            pid = proc.pid
            if qty == 0:
                current['index'] += 1
                ready_queue.append(current)
                continue

            if qty <= available_resources[res]:
                # بگیر
                available_resources[res] -= qty
                allocation[pid][res] += qty
                output.append(f"TAKE {pid} {res} {qty} {current_time}")
                current['index'] += 1
                ready_queue.append(current)
            else:
                output.append(f"WAIT {pid} {current_time} {current_time + 1}")
                timeline[pid] += ['W']
                if res not in blocked_on_resource:
                    blocked_on_resource[res] = deque()
                blocked_on_resource[res].append(current)
                current_time += 1

        elif op == 'Free':
            res = cmd[1]
            qty = cmd[2]
            pid = proc.pid
            freed_qty = min(qty, allocation[pid][res])
            allocation[pid][res] -= freed_qty
            available_resources[res] += freed_qty
            output.append(f"GIVE {pid} {res} {freed_qty} {current_time}")
            current['index'] += 1
            ready_queue.append(current)

        elif op == 'Exit':
            output.append(f"EXIT {proc.pid} {current_time}")

    if iteration >= max_runtime:
        print("Warning: Max runtime exceeded, breaking loop to avoid infinite loop.")

    max_time = max((int(line.split()[-1]) for line in output if line.startswith(('EXECUTE', 'WAIT'))), default=0)
    for pid in timeline:
        tl = timeline[pid]
        if len(tl) < max_time:
            tl += ['-'] * (max_time - len(tl))

    print(len(output))
    for line in output:
        print(line)
    print("Timeline:")
    for pid in sorted(timeline):
        print(f"P{pid}: [" + ''.join(timeline[pid]) + "]")
