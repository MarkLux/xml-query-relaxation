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