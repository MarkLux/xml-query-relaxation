# -*-coding:utf-8 
'''
we define the functions used by importance calculate here
'''
import numpy as np
import math

def get_idf_categorical(total, contains):
    # avoid the exception of divide zero.
    contains += 1
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

def get_idf_numeric_range(values, v_range):
    # TODO refer to QuestionA, how to determine the min v
    min_idf = 1
    for v in v_range:
        idf = get_idf_numeric(values, v)
        if idf < min_idf:
            min_idf = idf
    return min_idf

# main entrance of the importance calc.
def get_attr_weight(doc, queried_attrs, attr):
    pass:   

if __name__ == "__main__":
