# -*- coding: utf-8
'''
与数据读取有关的处理逻辑
'''
import xml.dom.minidom
import settings

def read_xml_file(path):
    dom_tree = xml.dom.minidom.parse(path)
    element_collection = dom_tree.documentElement
    return element_collection.getElementsByTagName(settings.NODE_TAG)

def dfs_read_node(node, walker_func, depth):
    # dfs方式遍历一个xml文档元素，并对其中的每个tag都应用walker_func函数
    # 处理本层数据
    walker_func(node, depth)
    for child_node in node.childNodes:
        dfs_read_node(child_node, walker_func, depth +1)

if __name__ == "__main__":
    # only for test
    path = 'test/demo.xml'
    collection = read_xml_file(path)
    import pdb;pdb.set_trace()
    for col in collection:
        print col