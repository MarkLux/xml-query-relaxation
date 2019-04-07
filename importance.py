# -*-coding:utf-8 

import numpy as np
import math
import settings

'''
===== INTRO =====
the calculation related to attribute & value importance defined here
'''

'''
calculate the idf of a categorical value
total: the total value numbers of specified attribute
contains: the occur times of the specified value
'''
def get_idf_categorical(total, contains):
    # avoid the exception of dividing zero.
    if contains <= 0:
        return 0
    return math.log(total * 1.0 / contains, 10)

'''
calculate the idf of a numberical value
values: the value collection of attribute
v: the specified value
'''
def get_idf_numeric(values, v):
    # calc the standard deviation of whole values.
    if not v in values:
        return 0
    n = len(values)
    std_dev = np.std(values)
    h = 1.06 * std_dev * pow(n, -0.2)
    denominator = 0
    for j in range(0, n):
        body = (values[j] - v) / h
        denominator += math.exp(-0.5 * pow(body, 2))
    return math.log(n / denominator, 10)

'''
calculate attribute weights from user query
@return: the attribute weights map
query: the user query in format of map,
i.e.
{
    'view': 'sea',
    'price': [150, 200]
}
attributes: the collection of attributes build from the xml document
'''
def get_attribute_weights(query, attributes):
    attr_weights = {}
    attr_idf = {}
    filter_q = {}
    # filter out the spatio attribute and temporal attribute 
    for k, v in query.items():
        if attributes.get(k).typ == settings.AttributeType.time \
            or attributes.get(k).typ == settings.AttributeType.space:
            continue
        filter_q[k] = v
    for name, limit in filter_q.items():
        if isinstance(limit, list):
            attr_idf[name] = attributes.get(name).get_idf_range(limit)
        else:
            attr_idf[name] = attributes.get(name).get_idf(limit)
    sum_of_weights = sum(attr_idf.values())
    for k in filter_q.keys():
        attr_weights[k] = attr_idf.get(k) / sum_of_weights
    return attr_weights

'''
calculate the sub thresholds
attr_weights: the weights of attributes
'''
def get_sub_thresholds(attr_weights):
    sum_of_power = 0
    for w in attr_weights.values():
        sum_of_power += pow(w, 2)
    if sum_of_power == 0:
        return {}
    m = settings.THRESHOLD / sum_of_power
    sub_thresholds = {}
    for attr in attr_weights.keys():
        sub_thresholds[attr] = m * attr_weights[attr]
    return sub_thresholds