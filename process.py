# -*- coding:utf-8
import importance
import reader
import settings
import common
import xml
import sim
import category
from define import Attribute

'''
===== INTRO =====
the core process flow
'''

'''
build attribute auxiliary table from xml tree nodes.
nodes: the xml document tree nodes.
'''
def build_attrs(nodes):
    attr_map = {}
    for node in nodes:
        dfs_build_attrs(None, None, node, 0, attr_map)
    return attr_map

'''
util function: trim all the blank chars in content
'''
def filter_blank(content):
    return content.replace('\n', '').replace('\t', '').replace(' ','')

'''
build attribute auxilary table for a xml document tree
this function use deep-frist-search (dfs) algorithm to walk all the tree nodes in a recursive way
id: the current node id
prob: the current node probablity
node: the current node
depth: the recursive depth
result_map: a map to save the attribute auxilary table
'''
def dfs_build_attrs(id, prob, node, depth, result_map):
    # get id and prob of the node, if not given.
    if not id:
        id = node.attributes.item(1).value
    if not prob:
        prob = float(node.attributes.item(2).value)
    # walk a xml node in dfs way, only work for ELEMENT_NODE type.
    if node.nodeType ==  xml.dom.Node.ELEMENT_NODE:
        attr_name = node.nodeName
        attr = result_map.get(attr_name)
        # skip all the tag without marks
        if not attr and (settings.ATTR_TYPES.has_key(attr_name)):
            attr = Attribute(attr_name, settings.ATTR_TYPES.get(attr_name) , depth)
            result_map[attr_name] = attr
        if attr:
            if attr.typ == settings.AttributeType.time or attr.typ == settings.AttributeType.space:
                x = float(node.attributes.item(0).value)
                y = float(node.attributes.item(1).value)
                attr.add_val(id, (x,y), prob)
        for child_node in node.childNodes:
            # handle text nodes.
            if child_node.nodeType == xml.dom.Node.TEXT_NODE:
                content = filter_blank(child_node.nodeValue)
                if content:
                    attr.add_val(id, content, prob)
            # handle the children nodes.
            if child_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                dfs_build_attrs(id, prob, child_node, depth + 1, result_map)

'''
relax a query to a new one according to attribute weights & sub thresholds
attrs: attribute auxilary table
sub_thresholds: sub threshold for each attribute
weights: attribute weights
raw_query: the original query in format of map
times: the relaxed times
'''   
def query_relax(attrs, sub_thresholds, weights, raw_query, times = 0):
    relaxed_query = {}
    for k, v in raw_query.items():
        attr = attrs.get(k)
        if attr.typ == settings.AttributeType.categorical:
            relaxed_query[k] = sim.get_relaxed_range_categorical(attrs, weights, k, v)
        elif attr.typ == settings.AttributeType.numerical:
            relaxed_query[k] = sim.get_relaxed_range_numerical(attrs, sub_thresholds, k, v)
        else:
            relaxed_query[k] = v
    return relaxed_query

'''
main entry of the query
q: original user query
data: xml data set
attrs: auxiliary table
real: a control parameter for test, ignore it.
'''
def query(q, data, attrs, real=False):
    # the id begin with 0
    ids = set(range(0, len(data)))
    hit_ids = _query(q, ids, attrs, real)
    return filter_xml_by_id(data, hit_ids)

'''
inner query method
'''
def _query(q, ids, attrs, real=False):
    for k, rang in q.items():
        attr = attrs.get(k)
        sub_id = []
        if attr.typ == settings.AttributeType.categorical:
            for v in attr.values:
                if v.val in rang:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.numerical:
            for v in attr.values:
                if rang[0] <= v.val and v.val < rang[1]:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.time and not real:
            for v in attr.values:
                sim_t = sim.get_time_sim(rang, v.val, v.prob)
                if sim_t >= settings.TIME_THRESHOLD:
                    print v.index, sim_t
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.space and not real:
            for v in attr.values:
                sim_s = sim.get_space_sim(rang, v.val, v.prob)
                if  sim_s >= settings.SPACE_THRESHOLD:
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.time:
            for v in attr.values:
                if (v.val[0] >= rang[0] and v.val[1] <= rang[1]):
                    sub_id.append(int(v.index))
                elif (v.val[0] <= rang[0] and v.val[1] >= rang[1]):
                    sub_id.append(int(v.index))
        elif attr.typ == settings.AttributeType.space:
            for v in attr.values:
                if v in rang:
                    sub_id.append(int(v.index))
        ids = ids.intersection(set(sub_id))
        print ids
    return ids

'''
filter out nodes with specified ids from a xml tree.
'''
def filter_xml_by_id(nodes, ids):
    result = []
    for node in nodes:
        id = int(node.attributes.item(1).value)
        if id in ids:
            result.append(node)
    return result

if __name__ == "__main__":
    # 1. read forecast data from xml file
    nodes = reader.read_xml_file(settings.SOURCE_FILE_PATH)
    # 2. build attribute auxiliary table
    attrs = build_attrs(nodes)
    # 3. input the user query
    q = {
        'district': 'DongCheng'
    }
    # 4. calculate attribute weights & sub thresholds.
    weights = importance.get_attribute_weights(q, attrs)
    sub_thresholds = importance.get_sub_thresholds(weights)
    # 5. relax the query
    relaxed_query = query_relax(attrs, sub_thresholds, weights, q)
    # debug: print the relaxed query
    print relaxed_query
    # 6. execute the relaxed query and get the result set
    result_nodes = query(relaxed_query, nodes, attrs)
    result_attrs = build_attrs(result_nodes)
    ids = []
    pos = []
    for node in result_nodes:
        ids.append(int(node.attributes.item(1).value))
    # record result set size
    print 'return: ' + str(len(result_nodes))
    ids = set(ids)
    # 7. build navigation tree
    nav_tree = category.get_nav_tree(result_attrs, attrs)
    # 8. print navigation tree
    category.dfs_print_nav_tree(nav_tree)