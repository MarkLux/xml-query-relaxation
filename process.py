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
核心相关处理函数
'''

# 构建属性表
def build_attrs(nodes):
    attr_map = {}
    for node in nodes:
        dfs_build_attrs(None, None, node, 0, attr_map)
    return attr_map

def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

'''
尽量只通过一次dfs来构建所有辅助内容
1. 获取各个属性，及其可能的取值 -> 计算idf
2. 对于query里所涉及到的属性值，还需要拿到和其他属性之间的关联关系 -> 计算sim
'''

def dfs_build_attrs(id, prob, node, depth, result_map):
    # 先获取id标识和prob
    if not id:
        id = node.attributes.item(0).value
    if not prob:
        prob = float(node.attributes.item(1).value)
    # dfs方式遍历一个xml文档元素, 先构建对应的attr，只对ELEMENT_NODE生效
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = result_map.get(attr_name)
        # 跳过没有标记的tag节点
        if not attr and (settings.ATTR_TYPES.has_key(attr_name)):
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            result_map[attr_name] = attr
        for child_node in node.childNodes:
            # 处理字面值
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(id, content, prob)
            # 处理下一层的其他节点
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_build_attrs(id, prob, child_node, depth + 1, result_map)

'''
查询松弛，输入原始查询，返回松弛过后的查询
times: 第几次松弛
'''   
def query_relax(attrs, sub_thresholds, weights, raw_query, times = 0):
    relaxed_query = {}
    for k, v in raw_query.items():
        attr = attrs.get(k)
        if attr.typ == settings.AttributeType.categorical:
            relaxed_query[k] = sim.get_relaxed_range_categorical(attrs, weights, k, v)
        elif attr.typ == settings.AttributeType.numerical:
            relaxed_query[k] = sim.get_relaxed_range_numerical(attrs, sub_thresholds, k, v)
    return relaxed_query

'''
核心查询入口
q: 用户查询，data: xml数据集， attrs: 第一次遍历时得到的索引
输出：xml树集合
'''
def query(q, data, attrs):
    # 简单起见，id直接从0开始顺序递增即可
    ids = set(range(0, len(data)))
    hit_ids = _query(q, ids, attrs)
    return filter_xml_by_id(data, hit_ids)

def _query(q, ids, attrs):
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
        elif attr.typ == settings.AttributeType.time:
            # 时间属性
            for v in attr.values:
                if sim.get_time_sim(rang, v.val, v.prob) >= settings.TIME_THRESHOLD:
                    sub_id.append(int(v.index))
        else:
            # 空间属性
            for v in attr.values:
                if sim.get_space_sim(rang, v.val, v.prob) >= settings.SPACE_THRESHOLD:
                    sub_id.append(int(v.index))
        # 求交集
        ids = ids.intersection(set(sub_id))
    return ids

# 根据id过滤选出符合条件的xml子树
def filter_xml_by_id(nodes, ids):
    result = []
    for node in nodes:
        id = int(node.attributes.item(0).value)
        if id in ids:
            result.append(node)
    return result

if __name__ == "__main__":
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    attrs = build_attrs(nodes)
    q = {
        'type': u'cloudy',
        'temperature': [11, 14]
    }
    weights = importance.get_attribute_weights(q, attrs)
    sub_thresholds = importance.get_sub_thresholds(weights)
    relaxed_query = query_relax(attrs, sub_thresholds, weights, q)
    print relaxed_query
    result_nodes = query(relaxed_query, nodes, attrs)
    result_attrs = build_attrs(result_nodes)
    nav_tree = category.get_nav_tree(result_attrs, attrs)
    category.dfs_print_nav_tree(nav_tree)