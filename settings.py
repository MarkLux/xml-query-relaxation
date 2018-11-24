# -*- coding: utf-8
from enum import Enum

'''
the top constant settings in the expriment.
'''

# control the general relaxation threshold
THRESHOLD = 0.58

# the top element tag in raw xml file
TOP_TAG = 'wheathers'

# the single element tag
NODE_TAG = 'wheather'

SOURCE_FILE_PATH = 'test/result.xml'

# 用于调整相似度表现的辅助值
SIM_A = 0.5

# 属性分类枚举
class AttributeType(Enum):
    categorical = 0
    numerical = 1
    time = 2
    space = 3

ATTR_TYPES = {
    'position': AttributeType.categorical,
    'temperature': AttributeType.numerical,
    'humidity': AttributeType.numerical,
    'type': AttributeType.categorical,
    'windForce': AttributeType.numerical,
    'windDirection': AttributeType.categorical,
    'date': AttributeType.numerical,
    'city': AttributeType.categorical,
    'district': AttributeType.categorical,
    'time': AttributeType.time,
    'space': AttributeType.space
}

# 数值型属性进行分桶时的默认桶数
BUCKET_NUM = 3

# 导航树叶子节点最大个数
NAV_TREE_MAX_NODE = 2

# 相似度最小接受系数（γ）
SIM_MIN_PROB = 0.5

# 空间距离最大距离, 10公里范围外的点会被舍弃
SPACE_MAX_DIST = 15000

# 时间距离最大距离
TIME_MAX_DIST = 24

TIME_THRESHOLD = 0.8

SPACE_THRESHOLD = 0.7