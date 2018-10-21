# -*- coding:utf-8
import define
import math
import numpy as np
import common
import settings

# 计算两个分类型数值的相似度
def get_sim_categorical(attr_name, x, y):
    return (1 - settings.SIM_A) * get_intra_sim_categorical(attr_name, x, y) + settings.SIM_A * get_inter_sim_categorical(attr_name, x, y)

# 计算一个数值型属性的松弛后的区间
def get_relaxed_range_numerical(attr_name, rang):
    attr = common.ATTRS.get(attr_name)
    n = len(attr.flat_values)
    std_dev = np.std(attr.flat_values)
    h = 1.06 * std_dev * pow(n, -0.2)
    sub_threshold = common.SUB_THRESHOLDS.get(attr_name)
    param = math.sqrt( (1- sub_threshold) / (sub_threshold) )
    return [rang[0] - param, rang[1] + param]

# 计算一个分类型查询松弛后的区间
def get_relaxed_range_categorical(attr_name, query):
    final_result = []
    attr = common.ATTRS.get(attr_name)
    if not isinstance(query, list):
        query = [query]
    final_result += query
    for q in query:
        for v in attr.flat_values:
            if get_sim_categorical(attr_name, q, v) > settings.THRESHOLD:
                final_result.append(v)
    return set(final_result)

def get_intra_sim_categorical(attr_name, x, y):
    attr = common.ATTRS.get(attr_name)
    nx = attr.get_occurs(x)
    ny = attr.get_occurs(y)
    return ( nx * ny * 1.0 ) / (nx + ny + nx * ny)

def get_inter_sim_categorical(attr_name, x, y):
    ier = 0
    # aj标识当前需要处理的属性
    aj = common.ATTRS.get(attr_name)
    # 只需处理用户指定的属性
    specified_attrs = {}
    for k in common.WEIGHTS.keys():
        specified_attrs[k] = common.ATTRS.get(k)
        
    for k, ak in specified_attrs.items():
        if attr_name == k:
            continue
        else:
            icr = 0
            wset = get_common_wset(ak, aj, x, y)
            for w in wset:
                icr +=  min(get_icp(ak, w, aj, x), get_icp(ak, w, aj, y))
            ier += common.WEIGHTS[k] * icr
    return ier

# 获取属性aj中值x和值y在属性ak上的共享值
def get_common_wset(ak, aj, x, y):
    vk_x = []
    vk_y = []
    x_ids = []
    y_ids = []
    for k, v in aj.values.items():
        if v == x:
            x_ids.append(k)
        elif v == k:
            y_ids.append(k)
    for k, v in ak.values.items():
        if k in x_ids:
            vk_x.append(v)
        if k in y_ids:
            vk_y.append(v)
    return set(vk_x + vk_y)

# 计算icp
def get_icp(ak, vk, aj, x):
    common = 0
    total = 0
    for k, v in aj.values.items():
        if v == x:
            total += 1
        if ak.values[k] == vk:
            common += 1
    return common * 1.0 / total