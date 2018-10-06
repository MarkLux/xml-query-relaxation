import xml.dom.minidom
import constants

def read_xml_file(path):
    dom_tree = xml.dom.minidom.parse(path)
    element_collection = dom_tree.documentElement
    return element_collection.getElementsByTagName(constants.NODE_TAG)

if __name__ == "__main__":
    path = 'test/raw.xml'
    collection = read_xml_file(path)
    for col in collection:
        print col