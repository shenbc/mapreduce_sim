class Spine:
    def __init__(self, ID, capacity):
        self.ID = ID
        self.role = "spine"
        self.name = 'S' + str(ID)
        # 聚合能力
        self.capacity = capacity
        # 其上聚合的模型列表
        self.model_agg_list = []

    def addaggmodel(self, model):
        if model in self.model_agg_list: 
            self.model_agg_list.add(model)
       