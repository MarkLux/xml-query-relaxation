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

# the pre factor for inter & intra probablity
SIM_A = 0.5

# enumeration of attribute type
class AttributeType(Enum):
    categorical = 0
    numerical = 1
    time = 2
    space = 3

# type suggestion for each attribute
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

# the default bucket num of bucket construcation
BUCKET_NUM = 3

# tha max tree node number of leaf category attribute
NAV_TREE_MAX_NODE = 2

# fuzzy coincidence factor（γ）
SIM_MIN_PROB = 0.5

# the max space distance threshold (meter)
SPACE_MAX_DIST = 15000

# the max time range distance threshold (hour)
TIME_MAX_DIST = 24

# sub threshold for temporal attribute
TIME_THRESHOLD = 0.8

# sub threshold for spatio attribute
SPACE_THRESHOLD = 0.7