# -*-coding:utf-8

import string
import random
import time

class TreeNode(object):
    def __init__(self, name, val, prob):
        self.name = name
        self.val = val
        self.prob = prob
        self.children = []


'''
XML Fuzzy属性储存方式，级联查询性能对比
'''

ROW_N = 100000
ATTR_N = 20

def run_xml_fuzzy():
    # table head
    mock_attributes = []
    mock_value = ['a', 'b', 'c', 'd', 'e']
    for i in range(ATTR_N):
        a = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        mock_attributes.append(a)
    # main
    mock_data = []
    for i in range(ROW_N):
        m = {}
        for j in range(ATTR_N):
            m[mock_attributes[j]] = {
                'prob': 1.0,
                'val': random.choice(mock_value)
            }
        mock_data.append(m)
    # 模拟树结构
    mock_tree_nodes = []
    for i in range(ROW_N):
        node = []
        for j in range(ATTR_N):
            node.append({
                'attribute': mock_attributes[j],
                'val': mock_data[i][mock_attributes[j]]['val'],
                'prob': 1.0
            })
        mock_tree_nodes.append(node)
    
    # 模拟二维表结构
    mock_base_table = []
    for i in range(ROW_N):
        for j in range(ATTR_N):
            m = {}
            m['id'] = i
            m['attribute'] = mock_attributes[j]
            m['val'] = mock_data[i][mock_attributes[j]]['val']
            mock_base_table.append(m)
    
    mock_relation_table = []
    for i in range(ATTR_N):
        for j in range(ROW_N):
            mock_relation_table.append({
                'id': j,
                'attribute': mock_attributes[i],
                'prob': 1.0
            })
    # 最终目的：计算出某个属性的某个值面在库中所有出现的概率总和
    k = mock_attributes[int(random.random() * ATTR_N)]
    # 树状结构时间：
    s1 =  int(round(time.time() * 1000))
    s = 0
    for i in range(len(mock_tree_nodes)):
        for n in mock_tree_nodes[i]:
            if n['attribute'] == k and n['val'] == 'a':
                s += n['prob']
        # import pdb;pdb.set_trace()
        # if mock_data[i][k]['val'] == 'a':
        #     # print i
        #     s += mock_data[i][k]['prob']
    print s
    s2 = int(round(time.time() * 1000))
    print s2 - s1

    # 二维表查询时间
    s = 0
    f = []
    for m in mock_base_table:
        if m['val'] == 'a' and m['attribute'] == k:
            f.append(m['id'])
    for v in mock_relation_table:
        if  v['attribute'] == k and v['id'] in f:
            s += mock_relation_table[j]['prob']
    print s
    s3 =  int(round(time.time() * 1000))
    print s3 - s2

if __name__ == "__main__":
    run_xml_fuzzy()
