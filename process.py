# -*- coding:utf-8
import importance
import reader
import settings
from define import Attribute

'''
核心流程中的相关处理函数
'''

ATTRS = {}

# 构建属性辅助表
def build_attrs():
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    for node in nodes:
        reader.dfs_read_node(node, _build_attr_walker, 0)
    
def _build_attr_walker(node, depth):
    attr_name = node.nodeName
    attr = ATTRS.get(attr_name) or Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
    # 处理文本内容
    if 