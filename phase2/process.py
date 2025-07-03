# process.py
class Process:
    def __init__(self, pid, instructions):
        self.pid = pid
        self.instructions = instructions
        self.pc = 0
        self.state = 'READY'
        self.sleep_until = 0
        self.allocation = []
        self.max_demand = []

    def __repr__(self):
        return (f"Process(pid={self.pid}, state={self.state}, "
                f"pc={self.pc}, alloc={self.allocation}, max={self.max_demand})")
