# -*- coding: utf-8
from enum import Enum

'''
the top constant settings in the expriment.
'''

# control the general relaxation threshold
THRESHOLD = 0.7

# the top element tag in raw xml file
TOP_TAG = 'hotels'

# the single element tag
NODE_TAG = 'hotel'

SOURCE_FILE_PATH = 'test/demo.xml'

# 属性分类枚举
class AttributeType(Enum):
    categorical = 0
    numerical = 1
    spatio_temporal = 2

ATTR_TYPES = {
    'title': AttributeType.categorical,
    'score': AttributeType.numerical
}