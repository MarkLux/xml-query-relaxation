import xml.dom.minidom
import settings

def read_xml_file(path):
    dom_tree = xml.dom.minidom.parse(path)
    element_collection = dom_tree.documentElement
    return element_collection.getElementsByTagName(settings.NODE_TAG)

if __name__ == "__main__":
    # only for test
    path = 'test/raw.xml'
    collection = read_xml_file(path)
    for col in collection:
        print col