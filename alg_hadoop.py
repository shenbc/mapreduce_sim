import random
from config import *


def hadoop(spines, leafs, mappers, reducers, links_cost):
    flows = []
    filename = 'alg_hadoop_'+str(len(spines))+'_'+str(len(leafs))+'_'+str(len(mappers))+'_'+str(len(reducers))
    f = open('log/'+filename+'.txt', 'w')
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
        edge1 = 'L'+str(first_leaf)+'-M'+str(source_mapper)
        links_cost[edge1] += tasks_para_size[mapper.task_type]
        leafs[first_leaf].tran_cost += tasks_para_size[mapper.task_type]
        if links_cost[edge1] >= LINK_BANDWIDTH:
            print(edge1 + ' exceed bandwidth!')

        # step3
        second_spine = random.randint(0, len(spines)-1)
        third_leaf = LEAF_NUM - 1
        edge2 = 'S'+str(second_spine)+'-L'+str(first_leaf)
        edge3 = 'S'+str(second_spine)+'-L'+str(third_leaf)
        fail_times = 0
        while links_cost[edge2] + tasks_para_size[mapper.task_type] >= LINK_BANDWIDTH or \
                links_cost[edge3] + tasks_para_size[mapper.task_type] >= LINK_BANDWIDTH :
            second_spine = (second_spine + 1) % SPINE_NUM
            fail_times = fail_times +1
            if fail_times >= SPINE_NUM - 1:
                print('can\'t choose a spine' )
        edge2 = 'S'+str(second_spine)+'-L'+str(first_leaf)
        links_cost[edge2] += tasks_para_size[mapper.task_type]
        links_cost[edge3] += tasks_para_size[mapper.task_type]
        spines[second_spine].tran_cost += tasks_para_size[mapper.task_type]
        leafs[third_leaf].tran_cost += tasks_para_size[mapper.task_type]

        # step4
        target_reducer = -1
        for i, reducer_task in enumerate(reducer_task_type):
            if mapper.task_type == reducer_task:
                target_reducer = i
                break
        edge4 = 'L' + str(third_leaf) +'-R' + str(target_reducer)
        links_cost[edge4] += tasks_para_size[mapper.task_type]
        if links_cost[edge4] >= LINK_BANDWIDTH:
            print(edge4 + ' exceed bandwidth!')

        flows.append([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
                     [edge3, 0, tasks_para_size[mapper.task_type]], [edge4, 0, tasks_para_size[mapper.task_type]]])
        print([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
                     [edge3, 0, tasks_para_size[mapper.task_type]], [edge4, 0, tasks_para_size[mapper.task_type]]])
        f.write(str([[edge1, 0, tasks_para_size[mapper.task_type]], [edge2, 0, tasks_para_size[mapper.task_type]], \
                     [edge3, 0, tasks_para_size[mapper.task_type]], [edge4, 0, tasks_para_size[mapper.task_type]]])+'\n')


    # print(flows)
    total_cost = 0
    print('\n' +'link cost(MB):')
    f.write('\n' + 'link cost(MB):\n' )
    for key, value in links_cost.items():
        print(str(key) + '    ' + str(value))
        f.write(str(key) + '    ' + str(value) + '\n')
        total_cost += value
    f.write('\n')

    print('switch tran_cost(MB): ')
    f.write('switch tran_cost(MB): \n')
    for spine in spines:
        print(spine.name, spine.tran_cost)
        f.write(spine.name + ' ' +str(spine.tran_cost) + '\n')
    for leaf in leafs:
        print(leaf.name, leaf.tran_cost)
        f.write(leaf.name + ' ' + str(leaf.tran_cost) + '\n')

    print('\ntotal link cost:', total_cost)
    f.write('\n\n'+'total link cost:'+'\n')
    f.write(str(total_cost))

    f.close()
    return flows


if __name__ == '__main__':
    hadoop() # test