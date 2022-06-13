from os import link


class Link:
    def __init__(self, ID, begin, end, capacity, is_before_spine):
        self.ID = ID
        self.role = "link"
        self.capacity = capacity
        self.begin = begin
        self.end = end
        self.is_before_spine = False
        self.worker_pass_list = []
        self.is_before_spine = is_before_spine
    
    def addworker(self, worker):
        if worker not in self.worker_pass_list:
            self.worker_pass_list.add(worker)
