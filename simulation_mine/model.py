from unicodedata import name


class Model:
    def __init__(self, ID, task_type, name, size, gradient_trans_rate, cost, PS):
        # 序列编号
        self.ID = ID
        # 任务类型
        self.task_type = task_type
        # 模型名称
        self.name = name
        # 模型大小
        self.size = size
        # 梯度传送速率 h_k
        self.gradient_trans_rate = gradient_trans_rate
        # 聚合代价
        self.cost = cost
        # 该模型的PS节点
        self.PS = PS
       