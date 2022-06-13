class Worker:
    def __init__(self, ID, model, PS):
        self.ID = ID
        self.role = "worker"
        self.name = 'M' + str(ID)
        # 处理的模型类型
        self.model = model
        self.PS = PS
        # self.PS.addworker(self)