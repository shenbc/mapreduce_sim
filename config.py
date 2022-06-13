tasks_para_size = [1.25, 11.69, 61.10, 138.36] # squeezenet\resnet18\alexnet\vgg16
tasks_para_name = ['squeezenet', 'resnet18', 'alexnet', 'vgg16']
# tasks_para_size = [1.25, 11.69, 61.10*0.1, 138.36*0.1] # squeezenet\resnet18\alexnet\vgg16
# tasks_para_name = ['squeezenet', 'resnet18', 'alexnet', 'vgg16']
# ========== config here =======================
SPINE_NUM = 2
LEAF_NUM = 4
MAPPER_NUM = 6
REDUCER_NUM = 2
S_CAL_ABILITY = 500  # MB , Spine交换机聚合能力
L_CAL_ABILITY = 500  # MB，Leaf不能聚合因此为0
LINK_BANDWIDTH = int(10*1024/8)  # MB，链路带宽10Gbps
mapper_task_type = [0,1,0,1,0,1] # [2,3,2,3,2,3]
reducer_task_type = [0,1]
# ===============================================
assert MAPPER_NUM % (LEAF_NUM-1) == 0
MAPPER_NUM_PER = int(MAPPER_NUM / (LEAF_NUM-1))

assert len(mapper_task_type) == MAPPER_NUM
assert len(reducer_task_type) == REDUCER_NUM
assert set(mapper_task_type) == set(reducer_task_type)
assert len(set(reducer_task_type)) == len(reducer_task_type) # reducer集合任务类型不重复


if __name__ == '__main__':
    print(len(set(reducer_task_type))) # test