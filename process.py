# -*- coding:utf-8
import importance
import reader
import settings
import xml
from define import Attribute

'''
核心流程中的相关处理函数
'''

ATTRS = {}

# 构建属性辅助表
def build_attrs():
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    for node in nodes:
        dfs_process_node(node, 0)

def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

def dfs_process_node(node, depth):
    # dfs方式遍历一个xml文档元素, 先构建对应的attr，只对ELEMENT_NODE生效
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = ATTRS.get(attr_name)
        if not attr:
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            ATTRS[attr_name] = attr
        # 处理属性，视为depth + 1的普通文本节点，原则上可以跳过
        if node.hasAttributes():
            for i in range(node.attributes.length):
                item = node.attributes.item(i)
                sub_name = item.nodeName
                sub_attr = ATTRS.get(sub_name)
                if not sub_attr:
                    sub_attr = Attribute(sub_name, settings.ATTR_TYPES.get(attr_name) , depth + 1)
                    ATTRS[sub_name] = sub_attr 
                sub_attr.add_val(item.value)
        for child_node in node.childNodes:
            # 处理字面值
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(content)
            # 处理下一层的其他节点
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_process_node(child_node, depth + 1)
                    
if __name__ == "__main__":
    build_attrs()
    q = {
        'type': u'viewable',
        'price': [100, 200]
    }
    import pdb;pdb.set_trace()
    idf = ATTRS.get('type').get_idf(u'viewable')
    weights = importance.get_attribute_weights(q, ATTRS)
    sub_thresholds = importance.get_sub_thresholds(weights)
    print sub_thresholds