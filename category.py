# -*- coding:utf-8

import numpy as np
import math
from define import Attribute, Bucket, NavNode
from settings import AttributeType, BUCKET_NUM, NAV_TREE_MAX_NODE
from collections import Counter

'''
计算分类时使用的权重
d_attrs -> 在整个数据集上计算得出的属性辅助表(map)
r_attrs -> 在结果集上计算得出的属性辅助表(map)
'''
def calc_category_weights(r_attrs, d_attrs):
    weights = {}
    r_buckets_map = {}
    sum_distance = 0
    for k, attr in r_attrs.items():
        d_attr = d_attrs.get(k)
        d_buckets = build_buckets(d_attr.typ, d_attr.flat_values, BUCKET_NUM)
        r_buckets = build_r_buckets(attr.typ, d_buckets, attr.flat_values)
        kl_dis = calc_kl_distance(d_buckets, r_buckets, len(d_attr.flat_values), len(attr.flat_values))
        print kl_dis
        sum_distance += kl_dis
        weights[k] = kl_dis
        # 进一步处理r_buckets
        r_buckets_map[k] = [i for i in r_buckets if i.cnt > 0]
    for k, w in weights.items():
        weights[k] = w / sum_distance
    return weights, r_buckets_map

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
            rb.k_range = db.k_range
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

'''
导航树生成算法
weights -> 计算得出的分类权重集合
attrs -> 以属性辅助表方式储存的结果集
buckets_map -> 以dict方式储存的所有属性的分桶结果 
'''
def generate_nav_tree(weights, attrs, buckets_map):
    level = 0
    # 1. 生成一个空的根节点, 所有的id从attrs的第一个里面取
    for a in attrs.values():
        root = NavNode('root', '', level, a.val_map.keys())
        break
    # 储存level - 1 层所有的分类节点
    level_categories = [root]
    while weights:
        level += 1
        # 暂存本level生成的所有新分类节点
        temp_level_categories = []
        # 2. 选定本层要分类的属性，并将其从map中移除
        category_name = select_category(weights)
        weights.pop(category_name)
        # 3. 枚举该属性的所有桶
        attr = attrs.get(category_name)
        buckets = buckets_map.get(category_name)
        for category in level_categories:
            if len(category.indexes) <= NAV_TREE_MAX_NODE:
                # 子节点数已经满足限制，无需再进一步分类了
                continue
            for bucket in buckets:
                child = build_nav_node(attr.name, bucket, attr.val_map, category.indexes, level)
                temp_level_categories.append(child)
                category.add_child(child)
        level_categories = temp_level_categories
    return root
            

def build_nav_node(attr_name, bucket, values, indexes, level):
    this_indexes = []
    for id in indexes:
        val = values.get(id)
        if bucket.typ == AttributeType.categorical:
            if val == bucket.k:
                this_indexes.append(id)
        elif bucket.typ == AttributeType.numerical:
            if bucket.k_range[0] <= val and val < bucket.k_range[1]:
                this_indexes.append(id)
    return NavNode(attr_name, bucket.k, level, this_indexes)



def select_category(category_weights):
    max_val = max(category_weights.values())
    for k, v in category_weights.items():
        if v == max_val:
            return k

def dfs_print_nav_tree(blank, node):
    if len(node.indexes) < 1:
        return
    if node.label == '':
        print '[{attr}]({label}) -> {cnt}'.format(attr=node.attr, label=node.label, cnt=len(node.indexes))
    else:
        print blank + '[{attr}]({label}) -> {cnt}'.format(attr=node.attr, label=node.label, cnt=len(node.indexes))
    for i in range(len(node.children)):
        dfs_print_nav_tree('   ' + blank,  node.children[i])

'''
入口
'''
def get_nav_tree(r_attrs, d_attrs):
    weights, r_buckets_map = calc_category_weights(r_attrs, d_attrs)
    nav_tree = generate_nav_tree(weights, r_attrs, r_buckets_map)
    return nav_tree

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
    
    weights, r_buckets_map = calc_category_weights(r_attrs, d_attrs)
    print weights
    nav_tree = generate_nav_tree(weights, r_attrs, r_buckets_map)
    dfs_print_nav_tree('', nav_tree)
    import pdb;pdb.set_trace()