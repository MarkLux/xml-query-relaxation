# -*- coding:utf-8
import collections
import importance
import settings

'''
属性的基本定义整合到此类
'''
class Attribute(object):
    def __init__(self, name, typ, depth = 0):
        self.name = name
        # 严格规定，values的类型只有数字和字符两种可能性，不存在其他的复杂类型
        self.values = []
        self.typ = typ
        self.depth = depth
        # idf辅助表，缓存已经计算出的idf，减少重复计算
        self.attr_idf = {}
    
    def add_val(self, val):
        # 如果是numerical的属性，这里要把文本值转换成小数
        if (self.typ == settings.AttributeType.numerical):
            val = float(val)
        self.values.append(val)

    def get_idf(self, val):
        # 如果用户输入的限制条件是单个值, 如: view = sea, 区分数值型和分类型属性
        # NOTICE: 后面计算idf时，有可能会用到深度属性来增强
        if self.attr_idf.has_key(val):
            # 先从缓存的辅助表中读
            return self.attr_idf.get(val)

        if self.typ == settings.AttributeType.categorical:
            counter = collections.Counter(self.values)
            idf =  importance.get_idf_categorical(len(self.values), counter.get(val) or 0)
        elif self.typ == settings.AttributeType.numerical:
            idf =  importance.get_idf_numeric(self.values, val)
        else:
            idf = None

        self.attr_idf[val] = idf
        return idf

    def get_idf_range(self, vals):
        # 如果用户输入的限制条件是一个范围，对于分类型属性是一个集合，如 wheather in [cloudy, rainy, sunny]
        # 对于数值型属性是一个区间, 如price in [150, 200]
        # 统一用vals这个list表示
        if self.typ == settings.AttributeType.numerical:
            # 如果是数值型变量，要将区间先扩展成所有可能的取值集合，认为所有的区间都是开区间
            start = vals[0]
            end = vals[1]
            value_set = set(self.values)
            vals = [i for i in value_set if i >= start and i <= end]

        # 最终输出所有可能取值里，idf最小的那个
        min_idf = 1 # idf不可能大于1
        for v in vals:
            v_idf = self.attr_idf.get(v) or self.get_idf(v)
            if v_idf < min_idf:
                min_idf = v_idf
        return min_idf
