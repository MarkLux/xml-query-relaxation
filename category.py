# -*- coding:utf-8

import numpy as np
import math
from define import Attribute, Bucket
from settings import AttributeType, BUCKET_NUM
from collections import Counter

'''
计算分类时使用的权重
d_attrs -> 在整个数据集上计算得出的属性辅助表(map)
r_attrs -> 在结果集上计算得出的属性辅助表(map)
'''
def calc_category_weights(r_attrs, d_attrs):
    weights = {}
    sum_distance = 0
    for k, attr in r_attrs.items():
        d_attr = d_attrs.get(k)
        d_buckets = build_buckets(d_attr.typ, d_attr.flat_values, BUCKET_NUM)
        r_buckets = build_r_buckets(attr.typ, d_buckets, attr.flat_values)
        kl_dis = calc_kl_distance(d_buckets, r_buckets, len(d_attr.flat_values), len(attr.flat_values))
        print kl_dis
        sum_distance += kl_dis
        weights[k] = kl_dis
    for k, w in weights.items():
        weights[k] = w / sum_distance
    return weights

'''
结果分类相关计算
入参：typ -> 属性类型, values  -> 所有值集合
'''
def build_buckets(typ, values, n_bucket = 0):
    buckets = []
    if typ == AttributeType.categorical:
        counter = Counter(values)
        for v in set(values):
            bucket = Bucket(typ)
            bucket.k = v
            bucket.cnt = counter.get(v) or 0
            buckets.append(bucket)
    elif typ == AttributeType.numerical:
        low = min(values)
        up = max(values)
        # 将最大上界增加一点幅度，这样才能造出完整的左闭右开区间
        max_val = up + 0.01
        lb = len(values) * 1.0 / n_bucket
        while low < max_val:
            prop_vals = query_vals(low, up, values)
            if prop_vals and len(set(prop_vals)) <= lb:
                bucket = Bucket(typ)
                bucket.k_range = [low, up]
                bucket.k = str(low) + "," + str(up)
                bucket.cnt = len(prop_vals)
                buckets.append(bucket)
                low = up
                up = max_val
            else:
                up = low + (up - low) / 2.0
    return buckets

'''
根据在数据集上得到的分桶进一步计算在结果集上的分桶
'''
def build_r_buckets(typ, d_buckets, values):
    r_buckets = []
    for db in d_buckets:
        rb = Bucket(typ)
        rb.k = db.k
        if typ == AttributeType.categorical:
            counter = Counter(values)
            rb.cnt = counter.get(db.k) or 0
        elif typ == AttributeType.numerical:
            rb.cnt = len(query_vals(db.k_range[0], db.k_range[1], values))
        r_buckets.append(rb)
    return r_buckets

'''
计算KL-Distance
d_buckets -> 在数据集上计算得到的分桶
r_buckets -> 在结果集上计算得到的分桶
'''
def calc_kl_distance(d_buckets, r_buckets, n_d, n_r):
    sum = 0
    for d in d_buckets:
        # 遍历寻找r_buckets中对应的桶
        for r in r_buckets:
            if d.k == r.k:
                pd = d.cnt * 1.0 / n_d
                pr = r.cnt * 1.0 / n_r
                if pr == 0:
                    continue
                sum += (pd * math.log10(pd / pr))
                continue
        # 如果没有找到桶，直接置0
    return sum

def query_vals(low, up, values):
    vals = []
    for v in values:
        if low <= v and v < up:
            vals.append(v)
    return vals

if __name__ == "__main__":
    # 模拟验证权重的合理性
    mock_values = {
        'price': [7045, 3125, 9416, 6610, 265, 1870, 2764, 598, 3539, 743],
        'city': ['A', 'B', 'A', 'A', 'C', 'C', 'B', 'C', 'B', 'C'],
        'sqft': [162, 151, 157, 199, 96, 106, 182, 40, 108, 68],
        'bedrooms': [3, 2, 3, 4, 2, 3, 4, 1, 2, 1],
    }

    mock_query = {
        'price': [1000, 6000]
    }

    d_attrs = {}
    r_attrs = {}

    # 构建price(查询条件)
    price_values = mock_values.get('price')
    d_attr_price = Attribute('price', AttributeType.numerical)
    r_attr_price = Attribute('price', AttributeType.numerical)
    target_ids = []
    for i in range(len(price_values)):
        d_attr_price.add_val(i, price_values[i])
        if price_values[i] > 1000 and price_values[i] <= 6000:
            r_attr_price.add_val(i, price_values[i])
            target_ids.append(i)
    d_attrs['price'] = d_attr_price
    r_attrs['price'] = r_attr_price
    # 构建city
    city_values = mock_values.get('city')
    d_attrs['city'] = Attribute('city', AttributeType.categorical)
    r_attrs['city'] = Attribute('city', AttributeType.categorical)
    for i in range(len(city_values)):
        d_attrs['city'].add_val(i, city_values[i])
        if i in target_ids:
            r_attrs['city'].add_val(i, city_values[i])
    # 构建sqft
    sq_values = mock_values.get('sqft')
    d_attrs['sqft'] = Attribute('sqft', AttributeType.numerical)
    r_attrs['sqft'] = Attribute('sqft', AttributeType.numerical)
    for i in range(len(sq_values)):
        d_attrs['sqft'].add_val(i, sq_values[i])
        if i in target_ids:
            r_attrs['sqft'].add_val(i, sq_values[i])
    # 构建bed_rooms
    bd_values = mock_values.get('bedrooms')
    d_attrs['bedrooms'] = Attribute('bedrooms', AttributeType.numerical)
    r_attrs['bedrooms'] = Attribute('bedrooms', AttributeType.numerical)
    for i in range(len(bd_values)):
        d_attrs['bedrooms'].add_val(i, bd_values[i])
        if i in target_ids:
            r_attrs['bedrooms'].add_val(i, bd_values[i])
    
    weights = calc_category_weights(r_attrs, d_attrs)

    print weights