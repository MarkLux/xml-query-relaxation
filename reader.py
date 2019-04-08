# -*- coding: utf-8
import xml.dom.minidom
import settings

'''
===== INTRO =====
file read functions
'''

def read_xml_file(path):
    dom_tree = xml.dom.minidom.parse(path)
    element_collection = dom_tree.documentElement
    return element_collection.getElementsByTagName(settings.NODE_TAG)

'''
only for test
'''
if __name__ == "__main__":
    # only for test
    path = 'test/demo.xml'
    collection = read_xml_file(path)
    for col in collection:
        import pdb;pdb.set_trace()
        print col