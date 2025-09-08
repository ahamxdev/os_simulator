class Process:
    def __init__(self, pid):
        self.pid = pid
        self.commands = []

    def add_command(self, command, *args):
        self.commands.append((command, *args))
