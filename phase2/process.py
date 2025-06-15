from copy import deepcopy

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.commands = []

    def add_command(self, command, *args):
        self.commands.append((command, *args))

    def fork_child(self, next_pid, start_index=1):
        child = Process(next_pid)
        child.commands = deepcopy(self.commands[start_index:])
        return child
