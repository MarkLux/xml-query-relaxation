# -*- coding:utf-8
import define
import math
import numpy as np
import settings
import random

# 计算两个分类型数值的相似度
def get_sim_categorical(attrs, weights, attr_name, x, y):
    return (1 - settings.SIM_A) * get_intra_sim_categorical(attrs, attr_name, x, y) + settings.SIM_A * get_inter_sim_categorical(attrs, weights, attr_name, x, y)

# 计算一个数值型属性的松弛后的区间
def get_relaxed_range_numerical(attrs, sub_thresholds, attr_name, rang):
    attr = attrs.get(attr_name)
    n = len(attr.flat_values)
    std_dev = np.std(attr.flat_values)
    h = 1.06 * std_dev * pow(n, -0.2)
    sub_threshold = sub_thresholds.get(attr_name)
    param = math.sqrt((1 - sub_threshold) / (sub_threshold))
    return [rang[0] - param, rang[1] + param]

# 计算一个分类型查询松弛后的区间
def get_relaxed_range_categorical(attrs, weights, attr_name, query):
    final_result = []
    attr = attrs.get(attr_name)
    if not isinstance(query, list):
        query = [query]
    final_result += query
    for q in query:
        for v in set(attr.flat_values):
            # import pdb;pdb.set_trace()
            s = get_sim_categorical(attrs, weights, attr_name, q, v)
            print v, s
            if s > settings.THRESHOLD:
                final_result.append(v)
    return set(final_result)

def get_intra_sim_categorical(attrs, attr_name, x, y):
    attr = attrs.get(attr_name)
    nx = attr.get_occurs(x)
    ny = attr.get_occurs(y)
    return (nx * ny * 1.0) / (nx + ny + nx * ny)

def get_inter_sim_categorical(attrs, weights, attr_name, x, y):
    ier = 0
    # aj标识当前需要处理的属性
    aj = attrs.get(attr_name)
    # 只需处理用户指定的属性
    specified_attrs = {}
    for k in weights.keys():
        specified_attrs[k] = attrs.get(k)
    for k, ak in specified_attrs.items():
        if attr_name == k:
            continue
        else:
            icr = 0
            wset = get_common_wset(ak, aj, x, y)
            for w in wset:
                icr += min(get_icp(ak, w, aj, x), get_icp(ak, w, aj, y))
            ier += weights[k] * icr
    return ier

# 获取属性aj中值x和值y在属性ak上的共享值
def get_common_wset(ak, aj, x, y):
    vk_x = []
    vk_y = []
    x_ids = []
    y_ids = []
    for v in aj.values:
        if v.val == x:
            x_ids.append(v.index)
        elif v.val == y:
            y_ids.append(v.index)
    for v in ak.values:
        if v.index in x_ids:
            vk_x.append(v.val)
        if v.index in y_ids:
            vk_y.append(v.val)
    return set(vk_x + vk_y)

# 计算icp
def get_icp(ak, vk, aj, x):
    common = 0
    total = 0
    for v in aj.values:
        if v.val == x:
            total += 1
        for vv in ak.values:
            if vv.index == v.index and vv.val == vk:
                common += 1
    if total > 0:
        return common * 1.0 / total
    else:
        return 0

# 计算时间属性的相似度, 注意第一个入参必须是用户指定的数据
def get_time_sim(time_x, time_y, prob = 1.0):
    distance = calc_euclidean_distance(time_x, time_y)
    # 先判断重叠的case
    if (time_x[0] >= time_y[0] and time_x[1] <= time_y[1]):
        distance = 0
    elif (time_x[0] <= time_y[0] and time_x[1] >= time_y[1]):
        distance = 0
    return get_pre_prob(prob) * ( 1- distance / settings.TIME_MAX_DIST)

# 计算空间属性的相似度
def get_space_sim(point_a, point_b, prob = 1.0):
    return get_pre_prob(prob) * (1 - calc_euclidean_distance(point_a, point_b) / settings.SPACE_MAX_DIST)

# 获取前置系数
def get_pre_prob(prob):
    return min(prob, settings.SIM_MIN_PROB) * 1.0 / settings.SIM_MIN_PROB

# 计算两个点的欧氏距离
def calc_euclidean_distance(a, b):
    return math.sqrt(math.pow((a[0] - b[0]), 2) + math.pow((a[1] - b[1]), 2))

if __name__ == "__main__":
    time_mock_data = []

    query_p = (12, 14)

    for i in range(100):
        start = int(random.random() * 24)
        end = int(random.random() * 24)
        if end < start:
            t = end
            end = start
            start = t
        mock = {
            'time': (start, end),
            'prob': random.random(),
            'hit': False,
            'distance': calc_euclidean_distance((start, end), query_p)
        }
        if mock['distance'] > settings.TIME_MAX_DIST:
            settings.TIME_MAX_DIST = mock['distance']
        time_mock_data.append(mock)

    threshold = 0.8

    print settings.TIME_MAX_DIST

    print '------'

    cnt = 0

    for mock in time_mock_data:
        # import pdb;pdb.set_trace()
        sim = get_time_sim(mock['time'], query_p, mock['prob'])
        if sim > threshold:
            mock['hit'] = True
            print str(sim) + ' .... ' + str(mock)
            cnt += 1

    for mock in time_mock_data:
        if not mock['hit']:
            print mock

    print cnt

    print '-----'

    cnt = 0

    time_mock_data_no_prob = []

    for mock in time_mock_data:
        sim = get_time_sim(mock['time'], query_p, 1.0)
        if sim > threshold:
            mock['hit'] = True
            print str(sim) + ' .... ' + str(mock)
            cnt += 1
        
    for mock in time_mock_data:
        if not mock['hit']:
            print mock

    print cnt