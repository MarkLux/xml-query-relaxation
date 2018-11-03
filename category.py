# -*- coding:utf-8

import numpy as np
from define import Attribute, Bucket
from settings import AttributeType
from collections import Counter

'''
结果分类相关计算
'''

def build_buckets(attr, n_bucket = 0, n_dataset = 0):
    buckets = []
    if attr.typ == AttributeType.categorical:
        counter = Counter(attr.flat_values)
        for v in set(attr.flat_values):
            bucket = Bucket(attr.typ)
            bucket.k = v
            bucket.cnt = counter.get(v) or 0
            buckets.append(bucket)
    elif attr.typ == AttributeType.numerical:
        low = min(attr.flat_values)
        up = min(attr.flat_values)
        max_val = up
        lb = n_dataset / n_bucket
        while low < max_val:
            cnt = query_cnt(low, up, attr.flat_values)
            if cnt <= lb:
                bucket = Bucket(attr.typ)
                bucket.k_range = [low, up]
                buckets.append(bucket)
            else:
                up = low + (up - low) / 2
    return buckets

def query_cnt(low, up, values):
    cnt = 0
    for v in values:
        if low <= v and v < up:
            cnt += 1
    return cnt