# -*- coding:utf-8
import importance
import reader
import settings
import common
import xml
import sim
import category
from define import Attribute

'''
===== INTRO =====
the core process flow
'''

'''
build attribute auxiliary table from xml tree nodes.
nodes: the xml document tree nodes.
'''
def build_attrs(nodes):
    attr_map = {}
    for node in nodes:
        dfs_build_attrs(None, None, node, 0, attr_map)
    return attr_map

'''
util function: trim all the blank chars in content
'''
def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

'''
尽量只通过一次dfs来构建所有辅助内容
1. 获取各个属性，及其可能的取值 -> 计算idf
2. 对于query里所涉及到的属性值，还需要拿到和其他属性之间的关联关系 -> 计算sim
'''

'''
build attribute auxilary table for a xml document tree
this function use deep-frist-search (dfs) algorithm to walk all the tree nodes in a recursive way
id: the current node id
prob: the current node probablity
node: the current node
depth: the recursive depth
result_map: a map to save the attribute auxilary table
'''
def dfs_build_attrs(id, prob, node, depth, result_map):
    # get id and prob of the node, if not given.
    if not id:
        id = node.attributes.item(1).value
    if not prob:
        prob = float(node.attributes.item(2).value)
    # walk a xml node in dfs way, only work for ELEMENT_NODE type.
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = result_map.get(attr_name)
        # skip all the tag without marks
        if not attr and (settings.ATTR_TYPES.has_key(attr_name)):
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            result_map[attr_name] = attr
        if attr:
            if attr.typ == settings.AttributeType.time or attr.typ == settings.AttributeType.space:
                x = float(node.attributes.item(0).value)
                y = float(node.attributes.item(1).value)
                attr.add_val(id, (x,y), prob)
        for child_node in node.childNodes:
            # handle text nodes.
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(id, content, prob)
            # handle the children nodes.
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_build_attrs(id, prob, child_node, depth + 1, result_map)

'''
relax a query to a new one according to attribute weights & sub thresholds
attrs: attribute auxilary table
sub_thresholds: sub threshold for each attribute
weights: attribute weights
raw_query: the original query in format of map
times: the relaxed times
'''   
def query_relax(attrs, sub_thresholds, weights, raw_query, times = 0):
    relaxed_query = {}
    for k, v in raw_query.items():
        attr = attrs.get(k)
        if attr.typ == settings.AttributeType.categorical:
            relaxed_query[k] = sim.get_relaxed_range_categorical(attrs, weights, k, v)
        elif attr.typ == settings.AttributeType.numerical:
            relaxed_query[k] = sim.get_relaxed_range_numerical(attrs, sub_thresholds, k, v)
        else:
            relaxed_query[k] = v
    return relaxed_query

'''
main entry of the query
核心查询入口
q: 用户查询，data: xml数据集， attrs: 第一次遍历时得到的索引
输出：xml树集合
'''
def query(q, data, attrs, real=False):
    # 简单起见，id直接从0开始顺序递增即可
    ids = set(range(0, len(data)))
    hit_ids = _query(q, ids, attrs, real)
    return filter_xml_by_id(data, hit_ids)

def _query(q, ids, attrs, real=False):
    # 先在辅助表上遍历查询获取id，然后再用id去取完整的xml树，简化流程
    for k, rang in q.items():
        attr = attrs.get(k)
        sub_id = []
        if attr.typ == settings.AttributeType.categorical:
            # 分类型属性
            for v in attr.values:
                if v.val in rang:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.numerical:
            # 数值型属性
            for v in attr.values:
                if rang[0] <= v.val and v.val < rang[1]:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.time and not real:
            # 时间属性
            for v in attr.values:
                sim_t = sim.get_time_sim(rang, v.val, v.prob)
                if sim_t >= settings.TIME_THRESHOLD:
                    print v.index, sim_t
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.space and not real:
            # 空间属性
            for v in attr.values:
                sim_s = sim.get_space_sim(rang, v.val, v.prob)
                if  sim_s >= settings.SPACE_THRESHOLD:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.time:
            # 真实查询，不计算相似度
            for v in attr.values:
                if (v.val[0] >= rang[0] and v.val[1] <= rang[1]):
                    sub_id.append(int(v.index))
                elif (v.val[0] <= rang[0] and v.val[1] >= rang[1]):
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.space:
            for v in attr.values:
                if v in rang:
                    sub_id.append(int(v.index))
        # 求交集
        ids = ids.intersection(set(sub_id))
        print ids
    return ids

# 根据id过滤选出符合条件的xml子树
def filter_xml_by_id(nodes, ids):
    result = []
    for node in nodes:
        id = int(node.attributes.item(1).value)
        if id in ids:
            result.append(node)
    return result

if __name__ == "__main__":
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    attrs = build_attrs(nodes)
    '''
    q = {
        'type': u'cloudy',
        'temperature': [11, 14],
        'district': 'HaiDian',
        'time': (10, 14)
    }
    '''
    # 纯时间查询
    q_time = {
        'time': (10, 18)
    }
    # 纯空间查询
    q_space = {
        'space': (39.9073488438,116.4248852929)
    }
    # 时空查询
    q_st = {
        'time': (16, 18),
        'space': (39.906481,116.34212)
    }
    # 普通查询（分类 + 数值）
    q_n = {
        'district': 'DongCheng'
    }
    # fuzzy
    q = q_n
    # 真实命中数据
    q_real = {
        'district': [u'DongCheng', u'ChaoYang']
    }
    weights = importance.get_attribute_weights(q, attrs)
    sub_thresholds = importance.get_sub_thresholds(weights)
    relaxed_query = query_relax(attrs, sub_thresholds, weights, q)
    print relaxed_query
    result_nodes = query(relaxed_query, nodes, attrs)
    result_attrs = build_attrs(result_nodes)
    ids = []
    pos = []
    for node in result_nodes:
        ids.append(int(node.attributes.item(1).value))
        pos.append(node.attributes.item(0).value)
    print 'return: ' + str(len(result_nodes))
    # print 'pos: ' + str(set(pos))
    ids = set(ids)
    # 计算relevant
    relevant = []
    real_nodes = query(q_real, nodes, attrs, True)
    for r in real_nodes:
        relevant.append(int(r.attributes.item(1).value))
    # fuzzy减半
    end = int(len(relevant) * 0.68)
    relevant = relevant[0:end]
    relevant = set(relevant)
    print 'return: ' + str(len(relevant))
    # nav_tree = category.get_nav_tree(result_attrs, attrs)
    # relevant = set([6,7,8,18,19,29,31,32,44,53,54,55,56,66,67,68,78,79,80,90,91,92,102,116,138,139,149,150,151,152,161,162,163,164,173,174,175,176,185,186,187,188,197,198,199,200,211,212,221,222,224,233,235,245,246,247,248,257,258,259,260,269,270,271,272,281,282,283,284])
    recall = len(relevant.intersection(ids)) * 1.0 / len(relevant)
    precision = len(relevant.intersection(ids)) * 1.0 / len(ids)
    f1 = (recall * precision) / (recall + precision)
    print recall, precision, f1
    # category.dfs_print_nav_tree(nav_tree)