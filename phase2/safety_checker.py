# safety_checker.py
def is_safe(processes, available, requesting_pid=None, request=None):
    work = available.copy()
    n = len(processes)
    m = len(work)

    finish = [False] * n
    allocation = [p.allocation.copy() for p in processes]
    max_demand = [p.max_demand.copy() for p in processes]
    need = [[max_demand[i][j] - allocation[i][j] for j in range(m)]
            for i in range(n)]

    if requesting_pid is not None and request is not None:
        for j in range(m):
            allocation[requesting_pid][j] += request[j]
            work[j] -= request[j]
            need[requesting_pid][j] -= request[j]

    while True:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += allocation[i][j]
                finish[i] = True
                found = True
                break
        if not found:
            break

    return all(finish)
