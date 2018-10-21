# -*- coding:utf-8
import importance
import reader
import settings
import common
import xml
import sim
from define import Attribute

'''
核心流程中的相关处理函数
'''

# 构建属性辅助表
def build_attrs():
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    for node in nodes:
        dfs_process_node(None, node, 0)

def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

'''
尽量只通过一次dfs来构建所有辅助内容
1. 获取各个属性，及其可能的取值 -> 计算idf
2. 对于query里所涉及到的属性值，还需要拿到和其他属性之间的关联关系 -> 计算sim
'''

def dfs_process_node(id, node, depth):
    # 先获取id标识
    if not id:
        id = node.attributes.item(0).value
    # dfs方式遍历一个xml文档元素, 先构建对应的attr，只对ELEMENT_NODE生效
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = common.ATTRS.get(attr_name)
        if not attr:
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            common.ATTRS[attr_name] = attr
        # 处理属性，视为depth + 1的普通文本节点，原则上可以跳过
        if node.hasAttributes():
            for i in range(node.attributes.length):
                item = node.attributes.item(i)
                sub_name = item.nodeName
                if sub_name == "id":
                    # 过滤辅助属性
                    continue
                sub_attr = common.ATTRS.get(sub_name)
                if not sub_attr:
                    sub_attr = Attribute(sub_name, settings.ATTR_TYPES.get(attr_name) , depth + 1)
                    common.ATTRS[sub_name] = sub_attr 
                sub_attr.add_val(id, item.value)
        for child_node in node.childNodes:
            # 处理字面值
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(id, content)
            # 处理下一层的其他节点
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_process_node(id, child_node, depth + 1)

'''
查询松弛，输入原始查询，返回松弛过后的查询
times: 第几次松弛
'''   
def query_relax(raw_query, times = 0):
    relaxed_query = {}
    for k, v in raw_query.items():
        attr = common.ATTRS.get(k)
        if attr.typ == settings.AttributeType.categorical:
            relaxed_query[k] = sim.get_relaxed_range_categorical(k, v)
        elif attr.typ == settings.AttributeType.numerical:
            relaxed_query[k] = sim.get_relaxed_range_numerical(k, v)
    return relaxed_query

if __name__ == "__main__":
    build_attrs()
    q = {
        'type': u'viewable',
        'price': [100, 200]
    }
    print common.ATTRS
    idf = common.ATTRS.get('type').get_idf(u'viewable')
    common.WEIGHTS = importance.get_attribute_weights(q, common.ATTRS)
    common.SUB_THRESHOLDS = importance.get_sub_thresholds(common.WEIGHTS)
    print common.SUB_THRESHOLDS
    print sim.get_sim_categorical('type', u'viewable', u'inviewable')
    print sim.get_relaxed_range_numerical('price', [100, 200])
    print query_relax(q)