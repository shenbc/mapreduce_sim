class PS:
    def __init__(self, ID, model, capacity = 0):
        self.ID = ID
        self.role = "ps"
        self.name = 'R' + str(ID)
        self.model = model
        self.worker_list = []
        self.capacity = capacity # 废弃

    def addworker(self, worker):
        if worker not in self.worker_list:
            self.worker_list.append(worker)
