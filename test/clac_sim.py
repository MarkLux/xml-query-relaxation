import math

def calc_sim(origin, target):
    up = 0
    for i in range(len(origin)):
        up += origin[i] * target[i]
    down = calc_dis(origin) * calc_dis(target)
    return up / down

def calc_dis(tup):
    s = 0
    for i in range(len(tup)):
        s += (tup[i] * tup[i])
    return math.sqrt(s)

if __name__ == "__main__":
    origin = (10, 20, 1)
    t1 = (10, 20, 5)
    t2 = (20, 40, 2)
    t3 = (30, 40, 3)
    print calc_sim(origin, t1)
    print calc_sim(origin, t2)
    print calc_sim(origin, t3)