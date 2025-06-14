from collections import deque

class ProcessWrapper:
    def __init__(self, process, arrival_time):
        self.process = process
        self.arrival_time = arrival_time  # زمان ورود به ready_queue

def fcfs_scheduler(processes):
    current_time = 0
    sleep_list = []
    output = []
    indices = {p.pid: 0 for p in processes}
    waiting_processes = set()
    ready_queue = deque([ProcessWrapper(p, 0) for p in processes])  # زمان ورود اولیه = 0

    while any(indices[p.process.pid] < len(p.process.commands) for p in ready_queue) or sleep_list:
        # بیدار کردن پروسه‌ها
        woken_procs = []
        for t, pid in sleep_list.copy():
            if t <= current_time:
                proc = next(p for p in processes if p.pid == pid)
                woken_procs.append(ProcessWrapper(proc, current_time))
                sleep_list.remove((t, pid))
                waiting_processes.discard(pid)

        # اضافه کردن به صف آماده
        for wp in woken_procs:
            ready_queue.append(wp)

        # اگر صف خالیه، زمان ببر جلو
        if not ready_queue:
            if sleep_list:
                current_time = min(t for t, _ in sleep_list)
                continue
            break

        # ترتیب FCFS واقعی = طبق زمان ورود به ready_queue
        ready_queue = deque(sorted(ready_queue, key=lambda x: x.arrival_time))

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
            indices[pid] += 1

            # اگر دستور بعدی وجود داره، دوباره به صف اضافه کن با زمان ورود جدید
            if indices[pid] < len(proc.commands):
                ready_queue.append(ProcessWrapper(proc, current_time))

        elif cmd[0] == "Sleep":
            duration = cmd[1]
            start = current_time
            end = start + duration
            output.append(f"WAIT {pid} {start} {end}")
            indices[pid] += 1
            sleep_list.append((end, pid))
            waiting_processes.add(pid)

    return output
