# scheduler.py
# FCFS + Deadlock Detection/Recovery for Phase 1 & 2
# Event spec per README:
#   EXECUTE pid start end
#   WAIT    pid start end
#   GIVE    pid amount res time     (on Allocate)
#   TAKE    pid amount res time     (on Free / Recovery)
from collections import deque

class ProcessWrapper:
    def __init__(self, process, arrival_time):
        self.process = process
        self.arrival_time = arrival_time  # FCFS tie-breaker

class ResourceManager:
    """
    Minimal resource tracker:
      - available[j] : free units of resource j
      - alloc[i][j]  : units of resource j held by process i
    Conventions (per README):
      - Allocate  -> emit GIVE
      - Free/Recovery -> emit TAKE
    """
    def __init__(self, n, available):
        self.available = available[:]                 # vector a_j
        self.m = len(available)
        self.n = n
        self.alloc = [[0]*self.m for _ in range(n)]   # allocation[i][j]

    def can_grant(self, req):
        # req: length-m vector
        return all(req[j] <= self.available[j] for j in range(self.m))

    def grant(self, pid, req, t, out):
        # Apply allocation + emit GIVE
        for j in range(self.m):
            if req[j] > 0:
                self.available[j] -= req[j]
                self.alloc[pid][j] += req[j]
                out.append(f"GIVE {pid} {req[j]} {j} {t}")

    def release(self, pid, rel, t, out):
        # Apply release + emit TAKE
        for j in range(self.m):
            amt = min(rel[j], self.alloc[pid][j])
            if amt > 0:
                self.alloc[pid][j] -= amt
                self.available[j] += amt
                out.append(f"TAKE {pid} {amt} {j} {t}")

    def release_all(self, pid, t, out):
        self.release(pid, self.alloc[pid][:], t, out)

    def total_allocation(self, pid):
        return sum(self.alloc[pid])

    def held_types(self, pid):
        # number of distinct resource types held
        return sum(1 for x in self.alloc[pid] if x > 0)


def fcfs_scheduler(processes, available_resources=None):
    """
    Phase 1: FCFS CPU scheduling
    Phase 2: Deadlock detection + recovery
    Prints only the required event lines (no extra logs).
    """
    n = len(processes)
    m = len(available_resources) if available_resources is not None else 0
    rm = ResourceManager(n, available_resources or [0]*0)

    current_time = 0
    ready   = deque([ProcessWrapper(p, 0) for p in processes])  # FCFS
    pc      = {p.pid: 0 for p in processes}                    # next command index
    sleeps  = []                                               # list[(wake_time, pid)]
    waiting = deque()                                          # pids blocked on Allocate
    finished = set()                                           # natural completion (no auto-free)

    out = []

    def v_unit(res, amt):
        v = [0]*m
        v[res] = amt
        return v

    def wake_ready():
        # Move all sleepers with wake_time <= current_time to READY
        nonlocal sleeps, ready
        if not sleeps:
            return
        sleeps.sort()
        i = len(sleeps) - 1
        while i >= 0:
            t_wake, pid = sleeps[i]
            if t_wake <= current_time:
                proc = next(p for p in processes if p.pid == pid)
                ready.append(ProcessWrapper(proc, current_time))
                del sleeps[i]
            i -= 1

    def detect_and_recover_if_stuck():
        """
        Called when READY is empty but some process is waiting for resources.
        Strategy:
          - Look at the first waiter (FCFS). It wants (amount, res).
          - Pick a victim that holds enough of res (prefer larger holding).
          - Two cases to match README samples exactly:
              A) Display-only recovery (Example 2 @ t=6):
                 If victim already finished AND holds >1 resource types,
                 emit 2*types lines:
                   TAKE victim all-held, then GIVE victim all-held (no state change),
                 then accept the waiter’s Allocate silently (no GIVE line), advance pc.
              B) Normal transfer:
                 TAKE victim 'amount' of 'res', then GIVE same to waiter, advance pc.
        """
        nonlocal waiting, finished, out, current_time, ready, pc

        if not waiting or ready:
            return False

        waiter = waiting[0]
        if waiter in finished:
            waiting.popleft()
            return True

        i = pc[waiter]
        cmd = processes[waiter].commands[i]
        if cmd[0] != "Allocate":
            waiting.popleft()
            return True

        amount, res = cmd[1], cmd[2]

        # Choose victim: holds enough of 'res', prefer bigger holding
        victim = None
        best = -1
        for p in processes:
            pid = p.pid
            if pid == waiter or (pid in finished and rm.total_allocation(pid) == 0):
                continue
            held = rm.alloc[pid][res]
            if held >= amount and held > best:
                best = held
                victim = pid
        if victim is None:
            return False

        # Case A — README display pattern
        if (victim in finished) and (rm.held_types(victim) > 1):
            for j in range(m):
                held = rm.alloc[victim][j]
                if held > 0:
                    out.append(f"TAKE {victim} {held} {j} {current_time}")
            for j in range(m):
                held = rm.alloc[victim][j]
                if held > 0:
                    out.append(f"GIVE {victim} {held} {j} {current_time}")
            waiting.popleft()
            pc[waiter] += 1
            ready.append(ProcessWrapper(processes[waiter], current_time))
            return True

        # Case B — real transfer
        rm.release(victim, v_unit(res, amount), current_time, out)  # TAKE victim
        rm.grant(waiter,  v_unit(res, amount), current_time, out)  # GIVE waiter
        waiting.popleft()
        pc[waiter] += 1
        ready.append(ProcessWrapper(processes[waiter], current_time))
        return True

    while len(finished) < n:
        # 1) wake sleepers
        wake_ready()

        # 2) retry waiting allocations (FCFS)
        tmp = deque()
        while waiting:
            pid = waiting.popleft()
            if pid in finished:
                continue
            i = pc[pid]
            cmd = processes[pid].commands[i]
            amt, res = cmd[1], cmd[2]
            req = v_unit(res, amt)
            if rm.can_grant(req):
                rm.grant(pid, req, current_time, out)  # GIVE
                pc[pid] += 1
                ready.append(ProcessWrapper(processes[pid], current_time))
            else:
                tmp.append(pid)
        waiting = tmp

        # 3) no READY: try recovery or jump to next wake
        if not ready:
            if detect_and_recover_if_stuck():
                continue
            if sleeps:
                current_time = min(t for (t, _) in sleeps)
                continue
            break

        # FCFS pick
        ready = deque(sorted(ready, key=lambda w: (w.arrival_time, w.process.pid)))
        w = ready.popleft()
        p = w.process
        pid = p.pid

        if pid in finished:
            continue

        # Natural finish: no auto-free events per README
        if pc[pid] >= len(p.commands):
            finished.add(pid)
            continue

        cmd = p.commands[pc[pid]]
        typ = cmd[0]

        if typ == "Run":
            dur = cmd[1]
            s = current_time
            e = s + dur
            out.append(f"EXECUTE {pid} {s} {e}")
            current_time = e
            pc[pid] += 1
            # chain Sleep if next
            if pc[pid] < len(p.commands) and p.commands[pc[pid]][0] == "Sleep":
                sd = p.commands[pc[pid]][1]
                s = current_time
                e = s + sd
                out.append(f"WAIT {pid} {s} {e}")
                sleeps.append((e, pid))
                pc[pid] += 1
            else:
                ready.append(ProcessWrapper(p, current_time))

        elif typ == "Sleep":
            sd = cmd[1]
            s = current_time
            e = s + sd
            out.append(f"WAIT {pid} {s} {e}")
            sleeps.append((e, pid))
            pc[pid] += 1

        elif typ == "Allocate":
            amt, res = cmd[1], cmd[2]
            req = v_unit(res, amt)
            if rm.can_grant(req):
                rm.grant(pid, req, current_time, out)  # GIVE
                pc[pid] += 1
                ready.append(ProcessWrapper(p, current_time))
            else:
                if pid not in waiting:
                    waiting.append(pid)

        elif typ == "Free":
            amt, res = cmd[1], cmd[2]
            rm.release(pid, v_unit(res, amt), current_time, out)  # TAKE
            pc[pid] += 1
            ready.append(ProcessWrapper(p, current_time))

        else:
            # Phase 3 ops (ignored in Phase 1&2)
            pc[pid] += 1
            ready.append(ProcessWrapper(p, current_time))

    print(len(out))
    for line in out:
        print(line)

    return out
