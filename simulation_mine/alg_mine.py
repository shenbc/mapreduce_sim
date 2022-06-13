import pulp
from config import *
from simulation_mine.PS import PS
from simulation_mine.worker import Worker
from simulation_mine.spine import Spine
from simulation_mine.leaf import Leaf
from simulation_mine.model import Model
from simulation_mine.link import Link

simplify_flag = True # 是否对alpha beta化简
reduce_flag = False # 是否将0-1规划转换为线性规划


def mine(SPINE_NUM, LEAF_NUM, MAPPER_NUM, REDUCER_NUM, S_CAL_ABILITY, LINK_BANDWIDTH, links_cost):

    spine_set = []
    leaf_set= []

    model_set = []
    link_set = []

    reducer_set = []
    mapper_set = []

    for i in range(0, REDUCER_NUM):
        ps = PS(ID=i, model=reducer_task_type[i])
        reducer_set.append(ps)
    for i in range(0, MAPPER_NUM):
        worker = Worker(ID=i, model=mapper_task_type[i], PS=reducer_task_type.index(mapper_task_type[i]))
        mapper_set.append(worker)
    for i in range(0, SPINE_NUM):
        spine = Spine(ID=i, capacity=S_CAL_ABILITY)
        spine_set.append(spine)
    for i in range(0,LEAF_NUM):
        leaf = Leaf(i)
        leaf_set.append(leaf)
    for i in range(0, len(reducer_task_type)):
        model = Model(ID=i, task_type=reducer_task_type[i], name=tasks_para_name[reducer_task_type[i]], size=tasks_para_size[reducer_task_type[i]],\
                      gradient_trans_rate=tasks_para_size[reducer_task_type[i]], cost=tasks_para_size[reducer_task_type[i]], PS=-1)
        model_set.append(model)

    # for mapper in mapper_set:
    #     print(mapper.name, mapper.model)
    # for reducer in reducer_set:
    #     print(reducer.name)
    # for spine in spine_set:
    #     print(spine.name)
    # for leaf in leaf_set:
    #     print(leaf.name)
    # for model in model_set:
    #     print(model.ID, model.task_type, model.name)

    for i in range(0, SPINE_NUM):
        for j in range(0, LEAF_NUM):
            if j != LEAF_NUM -1:
                link_set.append(Link(ID=-1, begin=spine_set[i].name, end=leaf_set[j].name, capacity=LINK_BANDWIDTH, is_before_spine= True))
            else:
                link_set.append(Link(ID=-1, begin=spine_set[i].name, end=leaf_set[j].name, capacity=LINK_BANDWIDTH, is_before_spine=False))
    for i in range(0, LEAF_NUM - 1):
        for j in range(0, MAPPER_NUM_PER):
            link_set.append(Link(ID=-1, begin=leaf_set[i].name, end=mapper_set[j].name,capacity=LINK_BANDWIDTH, is_before_spine= True))
    for j in range(0, REDUCER_NUM):
        link_set.append(Link(ID=-1, begin=leaf_set[LEAF_NUM - 1].name, end=reducer_set[j].name,capacity=LINK_BANDWIDTH, is_before_spine=False))

    # for link in link_set:
    #     print(link.begin,link.end)


    MINE(mapper_set,reducer_set, spine_set, leaf_set, model_set, link_set, links_cost)


def MINE(worker_set,reducer_set, spine_set,leaf_set, model_set, link_set, links_cost):
    # 创建模型
    prob_mine = pulp.LpProblem("MINE", pulp.LpMinimize)

    # x是0-1变量,y是0-1变量,z是0-1变量, lambda是连续变量
    # w的梯度是否经过s
    variables_X_s_w = []
    # w的梯度是否在s上聚合
    variables_Y_s_w = []
    # s上k类的聚合次数
    variables_alpha_s_k = []
    # s上是否发生k类聚合
    variables_beta_s_k = []

    if reduce_flag == False:
        for s in spine_set:
            for w in worker_set:
                variables_X_s_w.append(pulp.LpVariable(
                    'X_s' + str(s.ID) + '_w' + str(w.ID), cat=pulp.LpBinary))
                variables_Y_s_w.append(pulp.LpVariable(
                    'Y_s' + str(s.ID) + '_w' + str(w.ID), cat=pulp.LpBinary))
            for k in model_set:
                variables_alpha_s_k.append(pulp.LpVariable(
                    'Alpha_s' + str(s.ID) + '_k' + str(k.ID), lowBound=0, cat=pulp.LpInteger))
                variables_beta_s_k.append(pulp.LpVariable(
                    'Beta_s' + str(s.ID) + '_k' + str(k.ID), cat=pulp.LpBinary))
    else:
        for s in spine_set:
            for w in worker_set:
                variables_X_s_w.append(pulp.LpVariable(
                    'X_s' + str(s.ID) + '_w' + str(w.ID), lowBound=0, upBound=1, cat=pulp.LpContinuous))
                variables_Y_s_w.append(pulp.LpVariable(
                    'Y_s' + str(s.ID) + '_w' + str(w.ID), lowBound=0, upBound=1, cat=pulp.LpContinuous))
            for k in model_set:
                variables_alpha_s_k.append(pulp.LpVariable(
                    'Alpha_s' + str(s.ID) + '_k' + str(k.ID), lowBound=0, cat=pulp.LpInteger))
                variables_beta_s_k.append(pulp.LpVariable(
                    'Beta_s' + str(s.ID) + '_k' + str(k.ID), cat=pulp.LpBinary))
    variable_lambda = pulp.LpVariable(
        'lambda', lowBound=0, upBound=1, cat=pulp.LpContinuous)


    # 添加目标函数
    prob_mine += variable_lambda, "min lambda"

    # 不等式1 y与x的关系
    for s in spine_set:
        for w in worker_set:
            prob_mine += variables_Y_s_w[s.ID * len(
                worker_set) + w.ID] <= variables_X_s_w[s.ID * len(worker_set) + w.ID]
            # print(variables_Y_s_w[s.ID * len(
            #     worker_set) + w.ID] <= variables_X_s_w[s.ID * len(worker_set) + w.ID])

    # 是否使用化简后的问题定义
    if simplify_flag:
        # 不等式2 alpha与y的关系
        for s in spine_set:
            for k in model_set:
                sum_Y_s_w = 0
                for w in worker_set:
                    if w.model == k.task_type:
                        sum_Y_s_w += variables_Y_s_w[s.ID *
                                                     len(worker_set) + w.ID]
                prob_mine += variables_alpha_s_k[s.ID *
                                                 len(spine_set) + k.ID] >= sum_Y_s_w - 1
                # print(variables_alpha_s_k[s.ID *
                #                                  len(spine_set) + k.ID] >= sum_Y_s_w - 1, '======\n')

        # 不等式3 beta与y的关系
        for s in spine_set:
            for k in model_set:
                for w in worker_set:
                    if w.model == k.task_type:
                        prob_mine += variables_beta_s_k[s.ID * len(
                            reducer_set) + k.ID] >= variables_Y_s_w[s.ID * len(worker_set) + w.ID]
                        # print(variables_beta_s_k[s.ID * len(
                        #     spine_set) + k.ID] >= variables_Y_s_w[s.ID * len(worker_set) + w.ID], '=========')
    else:
        # 等式2,3 alpha/beta的计算方式
        for s in spine_set:
            for k in model_set:
                sum_Y_s_w = 0
                for w in worker_set:
                    if w.model == k.task_type:
                        sum_Y_s_w += variables_Y_s_w[s.ID *
                                                     len(worker_set) + w.ID]
                if sum_Y_s_w <= 1:
                    prob_mine += variables_beta_s_k == sum_Y_s_w
                else:
                    prob_mine += variables_alpha_s_k == 1
                
                sum_Y_s_w -= 1
                if sum_Y_s_w >= 0:
                    prob_mine += variables_alpha_s_k == sum_Y_s_w
                else:
                    prob_mine += variables_alpha_s_k == 0
                    

    # 不等式4 交换机处理能力约束
    for s in spine_set:
        sum_alpha_s_k = 0
        for k in model_set:
            sum_alpha_s_k += variables_alpha_s_k[s.ID *
                                                 len(reducer_set) + k.ID] * k.cost
        # print(sum_alpha_s_k <= s.capacity, '====\n')
        prob_mine += sum_alpha_s_k <= s.capacity

    # 不等式5 链路带宽约束
    for e in link_set:
        flow = 0
        for s in spine_set:
            for w in worker_set:
                if (e.begin==s.name and e.is_before_spine==True) or (e.end==w.name and e.is_before_spine==True):
                    flow += tasks_para_size[w.model] * variables_X_s_w[s.ID * len(worker_set) + w.ID]
                if (e.begin==s.name and e.is_before_spine==False) or (e.end==reducer_set[reducer_task_type.index(w.model)].name and e.is_before_spine==False):
                    flow += tasks_para_size[w.model] * (variables_X_s_w[s.ID * len(worker_set) + w.ID] - variables_Y_s_w[s.ID * len(worker_set) + w.ID])
            for k in model_set:
                for w in worker_set:
                    '''
                    if w.model == k.task_type:
                        # spine前的流量
                        # if e.begin == w.name or e.end == s.name:
                        if e.is_before_spine == True:
                            flow += k.gradient_trans_rate * \
                                variables_X_s_w[s.ID * len(worker_set) + w.ID]
                        # spine后未聚合的流量
                        # if e.begin == s.name or e.end == 'R'+str(k.PS):
                        if e.is_before_spine == False:
                            flow += k.gradient_trans_rate * \
                                (variables_X_s_w[s.ID * len(worker_set) + w.ID] -
                                 variables_Y_s_w[s.ID * len(worker_set) + w.ID])
                    '''
                # spine聚合的流量
                # if e.begin == s.name or e.end == 'R'+str(k.PS):
                if (e.begin[0]=='S' and e.is_before_spine ==False) or (e.end[0]=='R' and e.is_before_spine ==False):
                    flow += k.gradient_trans_rate * \
                        variables_beta_s_k[s.ID * len(reducer_set) + k.ID]
        # print(flow <= e.capacity * variable_lambda,'=========\n')
        prob_mine += flow <= e.capacity * variable_lambda


    # 等式6 路由约束
    for w in worker_set:
        sum_X_s_w = 0
        for s in spine_set:
            sum_X_s_w += variables_X_s_w[s.ID * len(worker_set) + w.ID]
            # print(s.name,w.name)
            # print(s.ID * len(worker_set) + w.ID)
            # print(variables_X_s_w[s.ID * len(worker_set) + w.ID])
        # print(sum_X_s_w,'\n==============')
        prob_mine += sum_X_s_w == 1

    prob_mine.solve()

    # log status
    # print(variables_X_s_w)
    # print(variables_Y_s_w)
    # print(variables_alpha_s_k)
    # print(variables_beta_s_k)

    # print ans and write
    # for var in variables_X_s_w:
    #     if var.varValue > 0:
    #         print(var.name, var.varValue)
    # for var in variables_Y_s_w:
    #     if var.varValue > 0:
    #         print(var.name, var.varValue)



    filename = 'alg_fsia_' + str(SPINE_NUM) + '_' + str(LEAF_NUM) + '_' + str(MAPPER_NUM) + '_' + str(
        REDUCER_NUM)
    f = open('log/' + filename + '.txt', 'w')
    f.write('spines num : ' + str(SPINE_NUM) + '\n')
    f.write('leafs num : ' + str(LEAF_NUM) + '\n')
    f.write('mappers num : ' + str(MAPPER_NUM) + '\n')
    f.write('reducers num : ' + str(REDUCER_NUM) + '\n')
    f.write('S_CAL_ABILITY: ' + str(S_CAL_ABILITY) + '\n')
    f.write('L_CAL_ABILITY: ' + str(L_CAL_ABILITY) + '\n')
    f.write('LINK_BANDWIDTH: ' + str(LINK_BANDWIDTH) + '\n')
    f.write('mapper_task_type: ' + str(mapper_task_type) + '\n')
    f.write('reducer_task_type: ' + str(reducer_task_type) + '\n\n')
    f.write('solutions:\n')

    answer = []
    for i, v in enumerate(prob_mine.variables()):
        if i < len(spine_set) * len(reducer_set) * 2:
            continue
        print(v.name, "=", v.varValue)
        f.write(str(v.name) + "=" + str(v.varValue) + '\n')
        answer.append([v.name,str(v.varValue)])
    # print(variable_lambda.name, variable_lambda.varValue)
    # f.write('\n\n' + str(variable_lambda.name) + '=' + str(variable_lambda.varValue))
    # for item in answer:
    #     print(item[0])

    # 下面处理线性规划-01规划结果近似
    if reduce_flag == True:
        for i in range(0,len(worker_set)):
            choosed_spine_idx = i
            for j in range(0, len(spine_set)):
                if str(answer[i+len(worker_set)*j][1]) > str(answer[choosed_spine_idx][1]):
                    choosed_spine_idx = i+len(worker_set)*j
            for j in range(0, len(spine_set)):
                if i+len(worker_set)*j != choosed_spine_idx:
                    answer[i+len(worker_set)*j][1] = '0' # x
                    answer[i+len(worker_set)*j + len(spine_set)*len(worker_set)][1] = '0' # y
                else:
                    answer[i + len(worker_set) * j][1] = '1'
                    if float(answer[i+len(worker_set)*j + len(spine_set)*len(worker_set)][1])>=0.5:
                        answer[i + len(worker_set) * j + len(spine_set) * len(worker_set)][1] = '1'
                    else:
                        answer[i + len(worker_set) * j + len(spine_set) * len(worker_set)][1] = '0'
        print('\nsolutions: liner to 0-1 :')
        f.write('\nsolutions: liner to 0-1 :\n')
        for item in answer:
            print(item[0],item[1])
            f.write(str(item[0])+str(item[1])+'\n')
        print('\n')
        f.write('\n')



    # 下面应该计算各个边的流量
    his = [(-1,-1)] # spine_idx, work_type
    for i, v in enumerate(answer):
        print(i, v)
        if i < len(spine_set) * len(worker_set): # 只遍历X_s_w
            if v[1] == '1': #
                spine_idx = int(i / len(worker_set))
                mapper_idx = int(i - spine_idx * len(worker_set))
                leaf_idx = int(mapper_idx / MAPPER_NUM_PER)
                reducer_idx = reducer_task_type.index(mapper_task_type[mapper_idx])
                # mapper 到 spine 路径增加link cost
                links_cost['S'+str(spine_idx)+'-L'+str(leaf_idx)] += tasks_para_size[mapper_task_type[mapper_idx]]
                links_cost['L' + str(leaf_idx) + '-M' + str(mapper_idx)] += tasks_para_size[mapper_task_type[mapper_idx]]
                print('S'+str(spine_idx)+'-L'+str(leaf_idx)+'add',tasks_para_size[mapper_task_type[mapper_idx]])
                print('L' + str(leaf_idx) + '-M' + str(mapper_idx)+'add',tasks_para_size[mapper_task_type[mapper_idx]])
                if answer[i + len(worker_set)*len(spine_set)][1] == '1': # 对应y=1，聚合
                    if(spine_idx, mapper_task_type[mapper_idx]) not in his: # 第一次出现，增加link cost，记录his信息
                        links_cost['S' + str(spine_idx) + '-L' + str(LEAF_NUM-1)] += tasks_para_size[
                            mapper_task_type[mapper_idx]]
                        links_cost['L' + str(LEAF_NUM-1) + '-R' + str(reducer_idx)] += tasks_para_size[
                            mapper_task_type[mapper_idx]]
                        his.append((spine_idx, mapper_task_type[mapper_idx]))
                else: # y=0，不聚合
                    links_cost['S' + str(spine_idx) + '-L' + str(LEAF_NUM - 1)] += tasks_para_size[
                        mapper_task_type[mapper_idx]]
                    links_cost['L' + str(LEAF_NUM - 1) + '-R' + str(reducer_idx)] += tasks_para_size[
                        mapper_task_type[mapper_idx]]


    total_cost = 0
    print('\n' + 'link cost(MB):')
    f.write('\n' + 'link cost(MB):\n')
    for key, value in links_cost.items():
        print(str(key) + '    ' + str(value))
        f.write(str(key) + '    ' + str(value) + '\n')
        total_cost += value

    print('\ntotal link cost:', total_cost)
    f.write('\n\n' + 'total link cost:' + '\n')
    f.write(str(total_cost))

    f.close()



if __name__ == '__main__':
    mine(SPINE_NUM, LEAF_NUM, MAPPER_NUM, REDUCER_NUM, S_CAL_ABILITY, LINK_BANDWIDTH)  # test
