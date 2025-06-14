# fcfs_scheduler.py

from collections import deque
from copy import deepcopy

def fcfs_scheduler(processes):
    current_time = 0
    ready_queue = deque([{'proc': p, 'arrival': 0, 'index': 0} for p in processes])
    sleep_list = []
    blocked_on_resource = {}
    resource_locks = {}
    output = []
    timeline = {}
    next_pid = max(p.pid for p in processes) + 1

    while ready_queue or sleep_list or any(blocked_on_resource.values()):
        sleep_list.sort(key=lambda x: x[0])  # مرتب‌سازی بر اساس زمان بیدار شدن
        for wake_time, p_obj in sleep_list[:]:
            if wake_time <= current_time:
                ready_queue.append(p_obj)
                sleep_list.remove((wake_time, p_obj))

        # بررسی منابع آزاد شده
        for res, queue in list(blocked_on_resource.items()):
            if res not in resource_locks and queue:
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
            output.append(f"EXECUTE {proc.pid} {current_time} {current_time+dur}")
            timeline[proc.pid] += ['E'] * dur
            current_time += dur
            current['index'] += 1
            ready_queue.append(current)

        elif op == 'Sleep':
            dur = cmd[1]
            output.append(f"WAIT {proc.pid} {current_time} {current_time+dur}")
            timeline[proc.pid] += ['W'] * dur
            sleep_list.append((current_time + dur, current))
            current['index'] += 1
            current_time += 1

        elif op == 'Lock':
            res = cmd[1]
            if res not in resource_locks:
                resource_locks[res] = proc.pid
                output.append(f"LOCK {proc.pid} {res} {current_time}")
                current['index'] += 1
                ready_queue.append(current)
            else:
                if res not in blocked_on_resource:
                    blocked_on_resource[res] = deque()
                blocked_on_resource[res].append(current)

        elif op == 'Unlock':
            res = cmd[1]
            if resource_locks.get(res) == proc.pid:
                del resource_locks[res]
                output.append(f"UNLOCK {proc.pid} {res} {current_time}")
            current['index'] += 1
            ready_queue.append(current)

        elif op == 'Fork':
            child = Process(next_pid)
            child.commands = deepcopy(proc.commands[current['index'] + 1:])
            output.append(f"FORK {proc.pid} {next_pid} {current_time}")
            ready_queue.append({'proc': child, 'arrival': current_time, 'index': 0})
            next_pid += 1
            current['index'] += 1
            ready_queue.append(current)

        elif op == 'Exit':
            output.append(f"EXIT {proc.pid} {current_time}")
            # پردازش حذف می‌شود

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
