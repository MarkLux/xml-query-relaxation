# -*- coding:utf-8
import collections
import importance
import settings

'''
====== INTRO =====
in this file, some basic model is defined
'''

'''
attribute defintion
this class is used as auxiliary table in process.
'''
class Attribute(object):
    def __init__(self, name, typ, depth = 0):
        # the attribute name
        self.name = name
        # the attribute values, this is a collection of Val objects.
        self.values = []
        # attribute values in map format, key: identifier of node
        self.val_map = {}
        # cache array of values
        self.flat_values = []
        # attribute type, see settings.py
        self.typ = typ
        # the depth of attribute (level 0 - n)
        self.depth = depth
        # the cache map of attribute value idf
        self.attr_idf = {}
    
    '''
    add a new value
    '''
    def add_val(self, identifier, val, prob = 1.0):
        # covert the value into float for numerical attribute.
        if (self.typ == settings.AttributeType.numerical):
            val = float(val)
        new_val = Val(identifier, val, prob)
        self.values.append(new_val)
        self.val_map[identifier] = val
        self.flat_values.append(val)

    '''
    calculate idf of a single value.
    val: the single value
    '''
    def get_idf(self, val):
        # 
        if self.attr_idf.has_key(val):
            # try to read from cache first
            return self.attr_idf.get(val)

        if self.typ == settings.AttributeType.categorical:
            counter = collections.Counter(self.flat_values)
            idf =  importance.get_idf_categorical(len(self.flat_values), counter.get(val) or 0)
        elif self.typ == settings.AttributeType.numerical:
            idf =  importance.get_idf_numeric(self.flat_values, val)
        else:
            idf = None

        self.attr_idf[val] = idf
        return idf

    '''
    calculate the idf of a value range(for numerical attribute) or collection(for categorical attribute)
    vals: the range or collection in format of list
          i.e. [1.0, 10.0] for numerical attribute / ['sunny', 'cloudy', 'windy'] for categorical attribute
    '''
    def get_idf_range(self, vals):
        if self.typ == settings.AttributeType.numerical:
            # if the input is a numerical range, convert it into a collection of possible values
            start = vals[0]
            end = vals[1]
            value_set = set(self.flat_values)
            vals = [i for i in value_set if i >= start and i <= end]

        # the output idf is the mininum one of the possible values.
        min_idf = 1
        for v in vals:
            v_idf = self.attr_idf.get(v) or self.get_idf(v)
            if v_idf < min_idf:
                min_idf = v_idf
        return min_idf

    # calculate the sum of probablity for a value
    def get_occurs(self, val):
        occur = 0
        for v in self.values:
            if v.val == val:
                occur += v.prob
        return occur
'''
bucket definition
'''
class Bucket(object):
    def __init__(self, typ, k='', k_range=[], cluster=[], cnt=0):
        self.typ = typ
        # the bucket name (key)
        self.k = ''
        # the bucket range (for numerical attribute)
        self.k_range = []
        # the cluster results (for temporal & spatio attribute)
        self.cluster = []
        # number of values in this bucket
        self.cnt = 0

'''
nav tree node definition
'''
class NavNode(object):
    def __init__(self, attr, label, level, indexes):
        # level
        self.level = level
        # children nodes
        self.children = []
        # attribute name
        self.attr = attr
        # label for user to recognize
        self.label = label
        # indexes to xml tree ndoes.
        self.indexes = indexes

    def add_index(self, id):
        self.indexes.append(id)

    def add_child(self, child):
        self.children.append(child)

'''
the definition of a single value
'''
class Val(object):
    def __init__(self, index, val, prob=1.0):
        # the index of xml node it belongs to
        self.index = index
        # value
        self.val = val
        # fuzzy probablity
        self.prob = prob