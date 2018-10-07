# -*-coding:utf-8 
'''
和属性重要程度相关的计算函数定义
'''
import numpy as np
import math

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