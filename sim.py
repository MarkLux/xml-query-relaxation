# -*- coding:utf-8
import define
import math
import numpy as np
import settings
import random

from math import radians, cos, sin, asin, sqrt

'''
===== INTRO =====
similarity & proximity calculation
'''

'''
calculate proxmity for two categorical values
@return: the proximity for two categorical values x and y
attrs: auxiliary table for attributes
weights: the attribute weighted calcuated from specified user query
attr_name: the attribute name
x & y: two categorical values
'''
def get_sim_categorical(attrs, weights, attr_name, x, y):
    # intra similiarity
    intra = get_intra_sim_categorical(attrs, attr_name, x, y)
    # inter similiarity
    inter = get_inter_sim_categorical(attrs, weights, attr_name, x, y)

    return (1 - settings.SIM_A) * intra + settings.SIM_A * inter

'''
relax a numerical range
@return: a relaxed numberical range in format of [up, low]
attrs: auxiliary table for attributes
sub_thresholds: sub thresholds calculated from attribute weigths
attr_name: the attribute name
rang: original numberical range, i.e. [1.0, 10.0]
'''
def get_relaxed_range_numerical(attrs, sub_thresholds, attr_name, rang):
    attr = attrs.get(attr_name)
    n = len(attr.flat_values)
    std_dev = np.std(attr.flat_values)
    h = 1.06 * std_dev * pow(n, -0.2)
    sub_threshold = sub_thresholds.get(attr_name)
    param = math.sqrt((1 - sub_threshold) / (sub_threshold))
    return [rang[0] - param, rang[1] + param]

'''
relax a categorical query 
i.e. [windy] -> [windy, cloudy, sunny]
@return: the relaxed categorical query in format of set
calculate proxmity for two categorical values
attrs: auxiliary table for attributes
attr_name: the attribute name
query: the user query
'''
def get_relaxed_range_categorical(attrs, weights, attr_name, query):
    final_result = []
    attr = attrs.get(attr_name)
    if not isinstance(query, list):
        # wrap single value query
        query = [query]
    final_result += query
    for q in query:
        for v in set(attr.flat_values):
            s = get_sim_categorical(attrs, weights, attr_name, q, v)
            print v, s
            if s > settings.THRESHOLD:
                final_result.append(v)
    return set(final_result)

'''
calculate intra similarity of two categorical values
@return: intra similarity
attrs: auxiliary tabel of attributes
attr_name: the attribute name
x & y: two specified values
'''
def get_intra_sim_categorical(attrs, attr_name, x, y):
    attr = attrs.get(attr_name)
    nx = attr.get_occurs(x)
    ny = attr.get_occurs(y)
    return (nx * ny * 1.0) / (nx + ny + nx * ny)

'''
calculate inter similarity of two categorical values
@return: intra similarity
attrs: auxiliary tabel of attributes
attr_name: the attribute name
x & y: two specified values
'''
def get_inter_sim_categorical(attrs, weights, attr_name, x, y):
    ier = 0
    aj = attrs.get(attr_name)
    # only handle the attribute specified by user
    specified_attrs = {}
    for k in weights.keys():
        specified_attrs[k] = attrs.get(k)
    for k, ak in specified_attrs.items():
        if attr_name == k:
            continue
        else:
            icr = 0
            # the wset is the intersection set (U)
            wset = get_common_wset(ak, aj, x, y)
            for w in wset:
                icp1 = get_icp(ak, w, aj, x)
                icp2 = get_icp(ak, w, aj, y)
                icr += min(icp1, icp2)
            ier += weights[k] * icr
    return ier

'''
get the intersection set on attribute ak & aj for x and y
'''
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
    return set(vk_x).intersection(set(vk_y))

'''
calculate information conditional probability ICP(vk|x)
'''
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

'''
calculate proximity of two temporal values
time_x & time_y: temporal value in format of [begin, end]
prob: the probablity of the value
'''
def get_time_sim(time_x, time_y, prob = 1.0):
    distance = calc_euclidean_distance(time_x, time_y)
    # specially, if one of the time range full covered another one, set the distance to zero.
    if (time_x[0] >= time_y[0] and time_x[1] <= time_y[1]):
        distance = 0
    elif (time_x[0] <= time_y[0] and time_x[1] >= time_y[1]):
        distance = 0
    return get_pre_prob(prob) * ( 1- distance / settings.TIME_MAX_DIST)

'''
calcluate proximity of two spatio positions
@returns: the geographical distance of two specified points (in meter)
point_a & point_b: spatio positions in format of (longtitue, latitude)
'''
def get_space_sim(point_a, point_b, prob = 1.0):
    ed = haversine(point_a, point_b)
    dist = (1 -  ed / settings.SPACE_MAX_DIST)
    if dist < 0:
        dist = 0
    return get_pre_prob(prob) * dist 

'''
caculate fuzzy coincidence (FC)
'''
def get_pre_prob(prob):
    return min(prob, settings.SIM_MIN_PROB) * 1.0 / settings.SIM_MIN_PROB

'''
calclate euclidean distance
'''
def calc_euclidean_distance(a, b):
    return math.sqrt(math.pow((a[0] - b[0]), 2) + math.pow((a[1] - b[1]), 2))


'''
calculate the great-circle-distance of two geographical points
'''
def haversine(a, b):
    lon1 = a[0]
    lat1 = a[1] 
    lon2 = b[0] 
    lat2 = b[1]
    
    # transfer decimal numbers into radian
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # the average radius of earth (km)
    r = 6371
    return c * r * 1000

'''
only for test
'''
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