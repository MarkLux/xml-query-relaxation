# -*- coding:utf-8

'''
===== INTRO =====
put the result of clustering here
'''

from define import Bucket
from settings import AttributeType

SPACE_CLUSTER_BUCKETS = [
    Bucket(AttributeType.space, k='cluster1', cnt=1 ,cluster=[
        (113.579371,22.263659)
    ]),
    Bucket(AttributeType.space, k='cluster2', cnt=11 ,cluster=[
        (116.403414,39.924091),
        (116.423633,39.953628),
        (116.417246,39.888243),
        (116.415041,39.946139),
        (116.413239,39.946882),
        (116.428039,39.901052),
        (116.397515,39.908859),
        (116.345657,39.913242),
        (116.388740,39.927599),
        (116.388402,39.940585),
        (116.371754,39.923408)
    ]),
    Bucket(AttributeType.space, k='cluster3', cnt=3 ,cluster=[
        (116.278749,40.004869),
        (116.309983,40.012884),
        (116.189141,39.990246)
    ])
]

TIME_CLUSTER_BUCKETS = [
    Bucket(AttributeType.time, k='cluster1', cnt=4 ,cluster=[
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 8),
    ]),
    Bucket(AttributeType.time, k='cluster2', cnt=4 ,cluster=[
        (8, 10),
        (10, 12),
        (12, 14),
        (14, 16),
    ]),
    Bucket(AttributeType.time, k='cluster3', cnt=4 ,cluster=[
        (16, 18),
        (18, 20),
        (20, 22),
        (22, 24)
    ]),
]