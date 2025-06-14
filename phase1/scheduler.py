from collections import deque

class ProcessWrapper:
    def __init__(self, process, arrival_time):
        self.process = process
        self.arrival_time = arrival_time

def fcfs_scheduler(processes):

    current_time = 0
    sleep_list = []
    output = []
    indices = {p.pid: 0 for p in processes}
    ready_queue = deque([ProcessWrapper(p, 0) for p in processes])

    while ready_queue or sleep_list:

        sleep_list.sort()
        woken_procs = []
        for t, pid in sleep_list.copy():
            if t <= current_time:
                proc = next(p for p in processes if p.pid == pid)
                woken_procs.append(ProcessWrapper(proc, current_time))
                sleep_list.remove((t, pid))

        for wp in sorted(woken_procs, key=lambda x: x.process.pid):
            ready_queue.append(wp)

        if not ready_queue and sleep_list:
            current_time = min(t for t, _ in sleep_list)
            continue

        if not ready_queue:
            break

        ready_queue = deque(sorted(ready_queue, key=lambda x: (x.arrival_time, x.process.pid)))

        if ready_queue:
            wrapper = ready_queue.popleft()
            proc = wrapper.process
            pid = proc.pid
            cmd_idx = indices[pid]

            if cmd_idx >= len(proc.commands):
                continue

            cmd = proc.commands[cmd_idx]

            if cmd[0] == "Run":
                duration = cmd[1]
                start = current_time
                end = start + duration
                output.append(f"EXECUTE {pid} {start} {end}")
                current_time = end

                if cmd_idx + 1 < len(proc.commands) and proc.commands[cmd_idx + 1][0] == "Sleep":
                    next_cmd = proc.commands[cmd_idx + 1]
                    sleep_duration = next_cmd[1]
                    start = current_time
                    end = start + sleep_duration
                    output.append(f"WAIT {pid} {start} {end}")
                    sleep_list.append((end, pid))
                    indices[pid] += 2
                else:
                    indices[pid] += 1
                    if indices[pid] < len(proc.commands):
                        ready_queue.append(ProcessWrapper(proc, current_time))

            elif cmd[0] == "Sleep":
                duration = cmd[1]
                start = current_time
                end = start + duration
                output.append(f"WAIT {pid} {start} {end}")
                sleep_list.append((end, pid))
                indices[pid] += 1

    max_time = max((int(line.split()[3]) for line in output if line.startswith("EXECUTE") or line.startswith("WAIT")), default=0)
    timeline = {pid: ["-"] * (max_time + 1) for pid in range(len(processes))}

    for line in output:
        parts = line.split()
        pid = int(parts[1])
        start = int(parts[2])
        end = int(parts[3])
        status = "E" if parts[0] == "EXECUTE" else "W"
        for t in range(start, end):
            timeline[pid][t] = status

    print(len(output))
    for line in output:
        print(line)
    print("Timeline:")
    for pid in range(len(processes)):
        print(f"P{pid}: [{''.join(timeline[pid])}]")

    return output
