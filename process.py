# -*- coding:utf-8
import importance
import reader
import settings
import common
import xml
import sim
from define import Attribute

'''
核心相关处理函数
'''

# 构建属性表
def build_attrs(nodes):
    attr_map = {}
    for node in nodes:
        dfs_build_attrs(None, node, 0, attr_map)
    return attr_map

def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

'''
尽量只通过一次dfs来构建所有辅助内容
1. 获取各个属性，及其可能的取值 -> 计算idf
2. 对于query里所涉及到的属性值，还需要拿到和其他属性之间的关联关系 -> 计算sim
'''

def dfs_build_attrs(id, node, depth, result_map):
    # 先获取id标识
    if not id:
        id = node.attributes.item(0).value
    # dfs方式遍历一个xml文档元素, 先构建对应的attr，只对ELEMENT_NODE生效
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = result_map.get(attr_name)
        if not attr:
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            result_map[attr_name] = attr
        # 处理属性，视为depth + 1的普通文本节点，原则上可以跳过
        if node.hasAttributes():
            for i in range(node.attributes.length):
                item = node.attributes.item(i)
                sub_name = item.nodeName
                if sub_name == "id":
                    # 过滤辅助属性
                    continue
                sub_attr = result_map.get(sub_name)
                if not sub_attr:
                    sub_attr = Attribute(sub_name, settings.ATTR_TYPES.get(attr_name) , depth + 1)
                    result_map.get[sub_name] = sub_attr 
                sub_attr.add_val(id, item.value)
        for child_node in node.childNodes:
            # 处理字面值
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(id, content)
            # 处理下一层的其他节点
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_build_attrs(id, child_node, depth + 1, result_map)

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
    ids = range(0, len(data))
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
                    sub_id.append(v.index)
        elif attr.typ == settings.AttributeType.numerical:
            # 数值型属性
            for v in attr.values:
                if rang[0] <= v.val and v.val < rang[1]:
                    sub_id.append(v.index)
        elif attr.typ == settings.AttributeType.time:
            # 时间属性
            for v in attr.values:
                if sim.get_time_sim(rang, v.val, v.prob) >= settings.TIME_THRESHOLD:
                    sub_id.append(v.index)
        else:
            # 空间属性
            for v in attr.values:
                if sim.get_space_sim(rang, v.val, v.prob) >= settings.SPACE_THRESHOLD:
                    sub_id.append(v.index)
        # 求交集
        ids = ids.intersection(set(sub_id))
    return ids

# 根据id过滤选出符合条件的xml子树
def filter_xml_by_id(nodes, ids):
    result = []
    for node in nodes:
        id = node.attributes.item(0).value
        if id in ids:
            result.append(id)
    return result

if __name__ == "__main__":
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    attrs = build_attrs(nodes)
    q = {
        'type': u'viewable',
        'price': [100, 200]
    }
    print attrs
    idf = attrs.get('type').get_idf(u'viewable')
    weights = importance.get_attribute_weights(q, attrs)
    sub_thresholds = importance.get_sub_thresholds(weights)
    print sub_thresholds
    print sim.get_sim_categorical(attrs, weights, 'type', u'viewable', u'inviewable')
    print sim.get_relaxed_range_numerical(attrs, sub_thresholds, 'price', [100, 200])
    print query_relax(attrs, sub_thresholds, weights, q)