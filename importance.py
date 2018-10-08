# -*-coding:utf-8 
'''
和属性重要程度相关的计算函数定义
'''
import numpy as np
import math
import settings

ATTR_WEIGHTS = {}

def get_idf_categorical(total, contains):
    # avoid the exception of divide zero.
    if contains <= 0:
        return 0
    return math.log(total / contains, 10)

def get_idf_numeric(values, v):
    # calc the standard deviation of whole values.
    n = len(values)
    std_dev = np.std(values)
    h = 1.06 * std_dev * pow(n, -0.2)
    denominator = 0
    for j in range(0, n):
        body = (values[j] - v) / h
        denominator += math.exp(-0.5 * pow(body, 2))
    return math.log(n / denominator, 10)

'''
query为用户的查询，用字典表示
e.g.
{
    'view': 'sea',
    'price': [150, 200]
}
attributes为预处理得到的属性辅助表，以name为key
'''
def get_attribute_weights(query, attributes):
    attr_weights = {}
    attr_idf = {}
    for name, limit in query.items():
        if isinstance(limit, list):
            attr_idf[name] = attributes.get(name).get_idf_range(limit)
        else:
            attr_idf[name] = attributes.get(name).get_idf(limit)
    sum_of_weights = sum(attr_idf.values())
    for k in query.keys():
        attr_weights[k] = attr_idf.get(k) / sum_of_weights
    return attr_weights

def get_sub_thresholds(attr_weights):
    # 根据公式，设 sub_threshold(i) = m * w(i)，解出m即可
    sum_of_power = 0
    for w in attr_weights.values():
        sum_of_power += pow(w, 2)
    m = settings.THRESHOLD / sum_of_power
    sub_thresholds = {}
    for attr in attr_weights.keys():
        sub_thresholds[attr] = m * attr_weights[attr]
    return sub_thresholds