# -*- coding: utf-8
from enum import Enum

'''
the top constant settings in the expriment.
'''

# control the general relaxation threshold
THRESHOLD = 0.5

# the top element tag in raw xml file
TOP_TAG = 'nodes'

# the single element tag
NODE_TAG = 'node'

SOURCE_FILE_PATH = 'test/test.xml'

# 用于调整相似度表现的辅助值
SIM_A = 0.5

# 属性分类枚举
class AttributeType(Enum):
    categorical = 0
    numerical = 1
    spatio_temporal = 2

ATTR_TYPES = {
    'name': AttributeType.categorical,
    'price': AttributeType.numerical,
    'score': AttributeType.numerical,
    'type': AttributeType.categorical,
    'latitdue': AttributeType.spatio_temporal,
    'longtitude': AttributeType.spatio_temporal,
    'time': AttributeType.spatio_temporal
}

# 数值型属性进行分桶时的默认桶数
BUCKET_NUM = 3

# 导航树叶子节点最大个数
NAV_TREE_MAX_NODE = 2

# 相似度最小接受系数（γ）
SIM_MIN_PROB = 0.7

# 空间距离最大距离
SPACE_MAX_DIST = 1

# 时间距离最大距离
TIME_MAX_DIST = 1