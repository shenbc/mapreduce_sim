# 先按hadoop随机分配流后，再处理聚合
import random
from config import *

def p4com(spines, leafs, mappers, reducers, links_cost):
    flows = []
    filename = 'alg_p4com_' + str(len(spines)) + '_' + str(len(leafs)) + '_' + str(len(mappers)) + '_' + str(
        len(reducers))
    f = open('log/' + filename + '.txt', 'w')
    f.write('spines num : ' + str(len(spines)) + '\n')
    f.write('leafs num : ' + str(len(leafs)) + '\n')
    f.write('mappers num : ' + str(len(mappers)) + '\n')
    f.write('reducers num : ' + str(len(reducers)) + '\n')
    f.write('S_CAL_ABILITY: ' + str(S_CAL_ABILITY) + '\n')
    f.write('L_CAL_ABILITY: ' + str(L_CAL_ABILITY) + '\n')
    f.write('LINK_BANDWIDTH: ' + str(LINK_BANDWIDTH) + '\n')
    f.write('mapper_task_type: ' + str(mapper_task_type) + '\n')
    f.write('reducer_task_type: ' + str(reducer_task_type) + '\n\n')
    f.write('solutions:\n')
    print('solutions')


    for mapper in mappers:
        # step 1
        source_mapper = mapper.idx

        # step 2
        first_leaf = int(mapper.idx / MAPPER_NUM_PER)
        edge1 = 'L' + str(first_leaf) + '-M' + str(source_mapper)
        links_cost[edge1] += tasks_para_size[mapper.task_type]
        leafs[first_leaf].tran_cost += tasks_para_size[mapper.task_type]
        leafs[first_leaf].tran_flow_idxs.append(mapper.idx)
        if links_cost[edge1] >= LINK_BANDWIDTH:
            print(edge1 + ' exceed bandwidth!')

        # step3
        second_spine = random.randint(0, len(spines) - 1)
        third_leaf = LEAF_NUM - 1
        edge2 = 'S' + str(second_spine) + '-L' + str(first_leaf)
        edge3 = 'S' + str(second_spine) + '-L' + str(third_leaf)
        fail_times = 0
        while links_cost[edge2] + tasks_para_size[mapper.task_type] >= LINK_BANDWIDTH or \
                links_cost[edge3] + tasks_para_size[mapper.task_type] >= LINK_BANDWIDTH:
            second_spine = (second_spine + 1) % SPINE_NUM
            fail_times = fail_times + 1
            if fail_times >= SPINE_NUM - 1:
                print('can\'t choose a spine')
        edge2 = 'S' + str(second_spine) + '-L' + str(first_leaf)
        links_cost[edge2] += tasks_para_size[mapper.task_type]
        links_cost[edge3] += tasks_para_size[mapper.task_type]
        spines[second_spine].tran_cost += tasks_para_size[mapper.task_type]
        leafs[third_leaf].tran_cost += tasks_para_size[mapper.task_type]
        spines[second_spine].tran_flow_idxs.append(mapper.idx)
        leafs[third_leaf].tran_flow_idxs.append(mapper.idx)

        # step4
        target_reducer = -1
        for i, reducer_task in enumerate(reducer_task_type):
            if mapper.task_type == reducer_task:
                target_reducer = i
                break
        edge4 = 'L' + str(third_leaf) + '-R' + str(target_reducer)
        links_cost[edge4] += tasks_para_size[mapper.task_type]
        if links_cost[edge4] >= LINK_BANDWIDTH:
            print(edge4 + ' exceed bandwidth!')

        flows.append([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
                      [edge3, 0, tasks_para_size[mapper.task_type]], [edge4, 0, tasks_para_size[mapper.task_type]]])
        # print([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
        #        [edge3, 0, tasks_para_size[mapper.task_type]], [edge4, 0, tasks_para_size[mapper.task_type]]])
        # f.write(str([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
        #              [edge3, 0, tasks_para_size[mapper.task_type]],
        #              [edge4, 0, tasks_para_size[mapper.task_type]]]) + '\n')


    # deal with aggregration : first switch !
    for leaf in leafs:
        if leaf.idx == LEAF_NUM - 1:
            break # 只考虑接入mapper的leaf交换机
        appear_task_types = [] # 记录第一次出现的任务类型
        appear_task_types_flow_idx = [] # 记录第一次出现的任务类型 的流编号（从哪个mapper发出的）

        for flow_idx in leaf.tran_flow_idxs: # 读流经leaf交换机的全部流
            if mapper_task_type[flow_idx] in appear_task_types: # 如果该流的任务类型曾出现过
                if leaf.cal_ability >= leaf.cal_cost + tasks_para_size[mapper_task_type[flow_idx]]: # 如果交换机有能力聚合
                    # 找到appear_task_types中出现这个任务类型的下标，即发出当前流的mapper在当前叶交换机下的序号，而不是mapper序号，也不能用来索引flows
                    appear_task_types_pos = 0
                    for i,types in enumerate(appear_task_types):
                        if types == mapper_task_type[flow_idx]:
                            appear_task_types_pos = i
                            break
                    # 处理聚合：交换机信息
                    leaf.cal_cost += tasks_para_size[mapper_task_type[flow_idx]]
                    templist = leaf.agg_info[mapper_task_type[flow_idx]]
                    templist.append(appear_task_types_flow_idx[appear_task_types_pos])
                    templist.append(flow_idx)
                    leaf.agg_info[mapper_task_type[flow_idx]] = templist
                    # 处理聚合：当前流flow_idx和前一条流appear_task_types_pos信息（solutions）
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0: # 当前流的第一条边,标记聚合
                            edge[1] = 1
                        else: # 后续边，将流量减少为0
                            edge[2] = 0
                    for i, edge in enumerate(flows[appear_task_types_flow_idx[appear_task_types_pos]]): # flows[appear_task_types_pos + MAPPER_NUM_PER * leaf.idx]不对
                        if i == 0: # 当前流的第一条边,标记聚合
                            edge[1] = 1
                    # 处理聚合：link_cost信息,通过遍历flow_idx所经过的边，将对应link_cost扣除相应参数大小
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0:
                            continue
                        else:
                            links_cost[edge[0]] = links_cost[edge[0]] - tasks_para_size[mapper_task_type[flow_idx]]

            else: # 如果该流的任务类型 未 曾出现过
                appear_task_types.append(mapper_task_type[flow_idx])
                appear_task_types_flow_idx.append(flow_idx)

        for key,value in leaf.agg_info.items():
            leaf.agg_info[key] = list(set(leaf.agg_info[key])) # 去重
            # print(key,value)

    # deal with aggregration : second switch !
    for spine in spines:
        appear_task_types = [] # 记录第一次出现的任务类型
        appear_task_types_flow_idx = [] # 记录第一次出现的任务类型 的流编号（从哪个mapper发出的）

        for flow_idx in spine.tran_flow_idxs: # 读流经leaf交换机的全部流
            if flows[flow_idx][1][2] == 0: # 该流之前已经被聚合，数据为0了
                continue
            if mapper_task_type[flow_idx] in appear_task_types : # 如果该流的任务类型曾出现过 
                if spine.cal_ability >= spine.cal_cost + tasks_para_size[mapper_task_type[flow_idx]] : # 如果交换机有能力聚合
                    # 找到appear_task_types中出现这个任务类型的下标，即发出当前流的mapper在当前叶交换机下的序号，而不是mapper序号，也不能用来索引flows
                    appear_task_types_pos = 0
                    for i,types in enumerate(appear_task_types):
                        if types == mapper_task_type[flow_idx]:
                            appear_task_types_pos = i
                            break
                    # 处理聚合：交换机信息
                    spine.cal_cost += tasks_para_size[mapper_task_type[flow_idx]]
                    templist = spine.agg_info[mapper_task_type[flow_idx]]
                    templist.append(appear_task_types_flow_idx[appear_task_types_pos])
                    templist.append(flow_idx)
                    spine.agg_info[mapper_task_type[flow_idx]] = templist
                    # 处理聚合：当前流flow_idx和前一条流appear_task_types_pos信息（solutions）
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0: # 当前流的第一条边,不处理
                            continue
                        elif i == 1:
                            edge[1] = 1
                        else: # 后续边，将流量减少为0
                            edge[2] = 0
                    for i, edge in enumerate(flows[appear_task_types_flow_idx[appear_task_types_pos]]):
                        if i == 1: # 当前流的第二条边,标记聚合
                            edge[1] = 1
                    # 处理聚合：link_cost信息,通过遍历flow_idx所经过的边，将对应link_cost扣除相应参数大小
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0 or i == 1:
                            continue
                        else:
                            links_cost[edge[0]] = links_cost[edge[0]] - tasks_para_size[mapper_task_type[flow_idx]]

            else: # 如果该流的任务类型 未 曾出现过
                appear_task_types.append(mapper_task_type[flow_idx])
                appear_task_types_flow_idx.append(flow_idx)

        for key,value in spine.agg_info.items():
            spine.agg_info[key] = list(set(spine.agg_info[key])) # 去重
            # print(key,value)

    # deal with aggregration : third switch !
    for leaf in leafs:
        if leaf.idx != LEAF_NUM - 1:
            continue # 只考虑接入reducer的leaf交换机
        appear_task_types = [] # 记录第一次出现的任务类型
        appear_task_types_flow_idx = [] # 记录第一次出现的任务类型 的流编号（从哪个mapper发出的）

        for flow_idx in leaf.tran_flow_idxs: # 读流经leaf交换机的全部流
            if flows[flow_idx][2][2] == 0: # 该流之前已经被聚合，数据为0了
                continue
            if mapper_task_type[flow_idx] in appear_task_types: # 如果该流的任务类型曾出现过
                if leaf.cal_ability >= leaf.cal_cost + tasks_para_size[mapper_task_type[flow_idx]]: # 如果交换机有能力聚合
                    # 找到appear_task_types中出现这个任务类型的下标，即发出当前流的mapper在当前叶交换机下的序号，而不是mapper序号，也不能用来索引flows
                    appear_task_types_pos = 0
                    for i,types in enumerate(appear_task_types):
                        if types == mapper_task_type[flow_idx]:
                            appear_task_types_pos = i
                            break
                    # 处理聚合：交换机信息
                    leaf.cal_cost += tasks_para_size[mapper_task_type[flow_idx]]
                    templist = leaf.agg_info[mapper_task_type[flow_idx]]
                    templist.append(appear_task_types_flow_idx[appear_task_types_pos])
                    templist.append(flow_idx)
                    leaf.agg_info[mapper_task_type[flow_idx]] = templist
                    # 处理聚合：当前流flow_idx和前一条流appear_task_types_pos信息（solutions）
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0 or i == 1:
                            continue
                        elif i == 2: # 当前流的第一条边,标记聚合
                            edge[1] = 1
                        else: # 后续边，将流量减少为0
                            edge[2] = 0
                    for i, edge in enumerate(flows[appear_task_types_flow_idx[appear_task_types_pos]]): # flows[appear_task_types_pos + MAPPER_NUM_PER * leaf.idx]不对
                        if i == 2: # 当前流的第一条边,标记聚合
                            edge[1] = 1
                    # 处理聚合：link_cost信息,通过遍历flow_idx所经过的边，将对应link_cost扣除相应参数大小
                    for i, edge in enumerate(flows[flow_idx]):
                        if i == 0 or i == 1 or i == 2:
                            continue
                        else:
                            links_cost[edge[0]] = links_cost[edge[0]] - tasks_para_size[mapper_task_type[flow_idx]]

            else: # 如果该流的任务类型 未 曾出现过
                appear_task_types.append(mapper_task_type[flow_idx])
                appear_task_types_flow_idx.append(flow_idx)

        for key,value in leaf.agg_info.items():
            leaf.agg_info[key] = list(set(leaf.agg_info[key])) # 去重
            # print(key,value)

    for k, v in links_cost.items():
        v = 0
        print(k,v)
    # for solution in flows:
    #     for edge_info in solution:
    #         links_cost[edge_info[0]] +=edge_info[2]

    # 最终结果
    for solution in flows:
        print(solution)
        f.write(str(solution) + '\n')

    total_cost = 0
    print('\n' + 'link cost(MB):')
    f.write('\n' + 'link cost(MB):\n')
    for key,value in links_cost.items():
        print(str(key) +'    '+ str(value))
        f.write(str(key) +'    '+ str(value) + '\n')
        total_cost += value

    print('\nswitch tran_cost(MB): ')
    f.write('\nswitch tran_cost(MB): \n')
    for spine in spines:
        print(spine.name, spine.tran_cost)
        f.write(spine.name + ' ' + str(spine.tran_cost) + '\n')
    for leaf in leafs:
        print(leaf.name, leaf.tran_cost)
        f.write(leaf.name + ' ' + str(leaf.tran_cost) + '\n')


    print('\nswitch cal_cost(MB): ')
    f.write('\nswitch cal_cost(MB): \n')
    for spine in spines:
        print(spine.name, spine.cal_cost)
        f.write(spine.name + ' ' + str(spine.cal_cost) + '\n')
    for leaf in leafs:
        print(leaf.name, leaf.cal_cost)
        f.write(leaf.name + ' ' + str(leaf.cal_cost) + '\n')

    print('\nswitch agg_info: ')
    f.write('\nswitch agg_info: \n')
    for spine in spines:
        print(spine.name, spine.agg_info)
        f.write(spine.name + ' ' + str(spine.agg_info) + '\n')
    for leaf in leafs:
        print(leaf.name, leaf.agg_info)
        f.write(leaf.name + ' ' + str(leaf.agg_info) + '\n')

    print('\ntotal link cost:', total_cost)
    f.write('\n\n' + 'total link cost:' + '\n')
    f.write(str(total_cost))

    f.close()
    return flows


if __name__ == '__main__':
    p4com()  # test