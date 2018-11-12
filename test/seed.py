# -*- coding:utf-8

import random
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

import sys

reload(sys)
sys.setdefaultencoding('utf8')

class AttrMock(object):
    def __init__(self, name, typ, rang):
        self.name = name
        self.typ = typ
        self.rang = rang

general_attr_def = {
    'position': AttrMock('position', 'c', [
        'The Great Wall',
        'The Palace Museum',
        'The Summer Palace',
        'Lama Temple',
        'Garden of Gardens',
        'The Forbidden City',
        'The Temple of Heaven'
    ]),
    'type': AttrMock('type', 'c', [
        'rain',
        'sunny',
        'cloudy',
        'snowy',
        'windy'
    ]),
    'temperature': AttrMock('temperature', 'n', [10.0, 20.0]),
    'humidity': AttrMock('humidity', 'n', [0.4, 0.7]),
    'windForce': AttrMock('windForce', 'n', [3.0, 6.0]),
    'windDirection': AttrMock('windDirection', 'c', [
        'E',
        'W',
        'N',
        'S',
        'ES',
        'EN',
        'WS',
        'WN'
    ]),
    'date': AttrMock('date', 'c', [
        '20181112',
        '20181113'
        '20181114',
        '20181115',
        '20181116',
        '20181117',
        '20181118',
        '20181119'
    ]),
    'city': AttrMock('city', 'c', ['BeiJing']),
    'district': AttrMock('district', 'c', [
        'HaiDian',
        'FengTai',
        'ChaoYang',
        'ShunYi',
        'ChangPing'
    ])
}

def generate_node(doc_root, id):
    random_seed = random.random()
    row_ele = ET.SubElement(doc_root, 'wheather', {'id': str(id), 'prob': str(random_seed)})
    # 创建general节点
    general_ele = ET.SubElement(row_ele, 'general')
    for k,v in general_attr_def.items():
        if v.typ == 'c':
            mock_v = v.rang[int(random_seed * len(v.rang))]
        elif v.typ == 'n':
            gap = v.rang[1] - v.rang[0]
            mock_v = v.rang[0] + random_seed * gap
        e = ET.SubElement(general_ele, k)
        e.text = str(mock_v)
    return row_ele

def output_xml(element, output_file):
    raw_str = ET.tostring(element, 'utf-8')
    with open(output_file, 'w+') as f:
        f.write(raw_str)
    return

if __name__ == "__main__":
    doc_root = ET.Element('wheathers')
    i = 0 
    for i in range(100):
        generate_node(doc_root, i+1)

    output_xml(doc_root, 'result.xml')
    