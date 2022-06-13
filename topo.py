from config import *
class Mapper:
    def __init__(self, idx, task_type):
        self.idx = idx
        self.task_type = task_type
        self.name = 'M'+ str(idx)

class Reducer:
    def __init__(self, idx, task_type):
        self.idx = idx
        self.task_type = task_type
        self.name = 'R' + str(idx)

class Spine:
    def __init__(self, idx, cal_ability, cal_cost, tran_cost=0): # 从0起编号、合并计算能力、计算消耗，转发消耗
        self.idx = idx
        self.cal_ability = cal_ability
        self.cal_cost = cal_cost
        self.name = 'S' + str(idx)
        self.tran_cost = tran_cost # 记录交换机收到的数据流
        self.tran_flow_idxs = [] # flow流来自M1则 idx=1，仅P4COM使用
        self.agg_info = {} # 记录交换机聚合信息，{3:[1,2], 5:[3,4}表示任务类型3的流1、2在此聚合...
        for i in range(0, len(tasks_para_size)):
            self.agg_info[i] = []

class Leaf:
    def __init__(self, idx, cal_ability, cal_cost, tran_cost=0):
        self.idx = idx
        self.cal_ability = cal_ability
        self.cal_cost = cal_cost
        self.name = 'L' + str(idx)
        self.tran_cost = tran_cost
        self.tran_flow_idxs = []  # flow流来自M1则 idx=1，仅P4COM使用
        self.agg_info = {}
        for i in range(0, len(tasks_para_size)):
            self.agg_info[i] = []
