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
    'city': AttrMock('city', 'c', ['BeiJing'])
}

position_data_mock = {
    'The Great Wall': {
        'district': 'YanQing',
        'location': (116.016809,40.361911)
    },
    'The Palace Museum': {
        'district': 'DongCheng',
        'location': (116.403414,39.924091)
    },
    'The Summer Palace': {
        'district': 'HaiDian',
        'location': (116.278749,40.004869)
    },
    'Lama Temple': {
        'district': 'DongCheng',
        'location': (116.423633,39.953628)
    },
    'Garden of Gardens': {
        'district': 'HaiDian',
        'location': (116.309983,40.012884)
    },
    'The Temple of Heaven': {
        'district': 'DongCheng',
        'location': (116.417246,39.888243)
    },
    'Temple of Confucius' : {
        'district': 'DongCheng',
        'location': (39.9461390230,116.4150411626)
    },
    'The Imperial College': {
        'district': 'DongCheng',
        'location': (39.9468822007,116.4132395326)
    },
    'Ming Cheng Wall Ruins Park ': {
        'district': 'DongCheng',
        'location': (39.9010525899,116.4280396238)
    },
    'Tian An Men': {
        'district': 'XiCheng',
        'location': (39.9088596409,116.3975157338)
    },
    'Altar of the Moon Park': {
        'district': 'XiCheng',
        'location': (39.9166844333,116.3524948131)
    },
    'Bei Hai Park': {
        'district': 'XiCheng',
        'location': (39.9275995766,116.3887407049)
    },
    'Shi Sha Lake': {
        'district': 'XiCheng',
        'location': (39.9405859540,116.3884021293)
    },
    'Jing Shan Park': {
        'district': 'XiCheng',
        'location': (22.2636597551,113.5793713618)
    },
    'South Luogu Lane': {
        'district': 'ChaoYang',
        'location': (22.2636597551,113.5793713618)
    },
    'Aquaria of Beijing': {
        'district': 'ShunYi',
        'location': (22.2636597551,113.5793713618)
    },
    'Xiang Shan Park': {
        'district': 'HaiDian',
        'location': (22.2636597551,113.5793713618)
    },
    'Geological Museum Of China': {
        'district': 'HaiDian',
        'location': (39.9915586721,116.3452162875)
    }
}

district_mock = {
    'YanQing': ['sunny', 'windy'],
    'HaiDian': ['sunny', 'windy'],
    'DongCheng': ['rain', 'cloudy', 'windy'],
    'ShunYi': ['windy', 'snowy'],
    'XiCheng': ['sunny', 'cloudy'],
    'ChaoYang': ['windy', 'cloudy']
}

def generate_node(doc_root, id, postion='', date='', district='', w='', location=None, time=None):
    random_seed = random.random()
    row_ele = ET.SubElement(doc_root, 'wheather', {'id': str(id), 'prob': str(random_seed)})
    # 创建general节点
    general_ele = ET.SubElement(row_ele, 'general')
    p_e = ET.SubElement(general_ele, 'position')
    p_e.text = postion
    ds_e = ET.SubElement(general_ele, 'district')
    ds_e.text = district
    d_e = ET.SubElement(general_ele, 'date')
    d_e.text = date
    ty_e = ET.SubElement(general_ele, 'type')
    ty_e.text = w 
    # 创建时空节点
    sp_ele = ET.SubElement(row_ele, 'spatioTemporal')
    l_e = ET.SubElement(sp_ele, 'space', {'x': str(location[0]), 'y': str(location[1])})
    t_e = ET.SubElement(sp_ele, 'time', {'x': str(time[0]), 'y': str(time[1])})
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
    positions = [
        'The Great Wall',
        'The Palace Museum',
        'The Summer Palace',
        'Lama Temple',
        'Garden of Gardens',
        'The Temple of Heaven',
        'Temple of Confucius',
        'The Imperial College',
        'Ming Cheng Wall Ruins Park ',
        'Tian An Men',
        'Altar of the Moon Park',
        'Bei Hai Park',
        'Shi Sha Lake',
        'Jing Shan Park',
        'South Luogu Lane',
        'Aquaria of Beijing',
        'Xiang Shan Park',
        'Geological Museum Of China'
    ]
    date = [
        '20181116',
        '20181117',
        '20181118',
        '20181119',
        '20181120',
    ]
    time = [
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 8),
        (8, 10),
        (10, 12),
        (12, 14),
        (14, 16),
        (16, 18),
        (18, 20),
        (20, 22),
        (22, 24)
    ]
    i = 0
    for p in positions:
        # 枚举日期
        for d in date:
            # 枚举时间
            for t in time:
                i += 1
                district = position_data_mock.get(p).get('district')
                generate_node(doc_root, i, postion=p, date=d, time=t, 
                district=district, 
                w=random.choice(district_mock.get(district)),
                location=position_data_mock.get(p).get('location'))

    output_xml(doc_root, 'result.xml')
    