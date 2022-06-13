from topo import Spine, Leaf, Mapper, Reducer
from config import *
from alg_hadoop import hadoop
from alg_hit import hit
from alg_p4com import p4com
from simulation_mine.alg_mine import mine


solution_M1 = [['M1-L1', 0, 120], ['L1-S1', 1, 120], ['s1-L2', 0, 120], ['L2-R1', 0, 120]]
solution_M2 = [['M1-L1', 0, 120], ['L1-S1', 1, 120], ['s1-L2', 0, 0], ['L2-R1', 0, 0]]
# 链路,这个链路末端进行聚合/不聚合,流量(只要聚合，之后的流的流量都是0)





# 初始化脊、叶节点（class类）
spines = []
leafs = []
mappers = []
reducers = []
for i in range(0, SPINE_NUM):
    spines.append(Spine(i, S_CAL_ABILITY, 0))
for i in range(0, LEAF_NUM):
    leafs.append(Leaf(i, L_CAL_ABILITY, 0))
for i in range(0, MAPPER_NUM):
    mappers.append(Mapper(i, mapper_task_type[i]))
for i in range(0, REDUCER_NUM):
    reducers.append(Reducer(i,reducer_task_type[i]))

# test below
# for mapper in mappers:
#     print(mapper.name,mapper.task_type)
# for reducer in reducers:
#     print(reducer.name, reducer.task_type)
# for spine in spines:
#     print(spine.name, spine.cal_ability, spine.cal_cost)

# 初始化链路负载（字典）
links_cost = {}
for i in range(0, SPINE_NUM):
    for j in range(0, LEAF_NUM):
        links_cost[spines[i].name+'-'+leafs[j].name] = 0
for i in range(0, LEAF_NUM -1):
    for j in range(0, MAPPER_NUM_PER):
        links_cost[leafs[i].name+'-'+mappers[j+i*MAPPER_NUM_PER].name] = 0
for j in range(0, REDUCER_NUM):
    links_cost[leafs[LEAF_NUM-1].name+'-'+reducers[j].name] = 0

# test below
# for key,value in links_cost.items():
#     print(key,value)


# 不聚合不使用流调度，依次分配(hadoop)
# hadoop(spines, leafs, mappers, reducers, links_cost)

# 使用流调度不使用聚合
# hit(spines, leafs, mappers, reducers, links_cost)

# 使用聚合不使用流调度（类似hadoop+随机）
# p4com(spines, leafs, mappers, reducers, links_cost)

# 使用mine算法
mine(SPINE_NUM, LEAF_NUM, MAPPER_NUM, REDUCER_NUM, S_CAL_ABILITY, LINK_BANDWIDTH, links_cost)

