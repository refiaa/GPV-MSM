import sys
import re
import optparse

def get_RCM_year(t):
    y = int(t / 100)
    if t % 100 < 9:
        y -= 1

    return y

if __name__ == '__main__':

    _period_GCM_HPB =		{'start': 195101, 'end': 201112}
    _period_GCM_HPB_NAT =	{'start': 195101, 'end': 201012}
    _period_GCM_HFB_4K =	{'start': 205101, 'end': 211112}
    _period_GCM_HFB_2K =	{'start': 203101, 'end': 209112}
    _period_GCM_HFB_1_5K =	{'start': 207801, 'end': 211012}
    _period_RCM_HPB =		{'start': 195009, 'end': 201108}
    _period_RCM_HFB_4K =	{'start': 205009, 'end': 211108}
    _period_RCM_HFB_2K =	{'start': 203009, 'end': 209108}
    _period_RCM_HFB_1_5K =	{'start': 208009, 'end': 211008}

    _ensemble_GCM_HPB = list(range(1, 101))
    _ensemble_GCM_HFB_4K = list(range(101, 116))
    _ensemble_GCM_HFB_2K = list(range(101, 110))
    _ensemble_GCM_HFB_1_5K = list(range(1, 10))
    _ensemble_RCM_HPB = [int(i / 10) * 20 + i % 10 + 1 for i in range(50)]
    _ensemble_RCM_HFB_4K = list(range(101, 116))
    _ensemble_RCM_HFB_2K = list(range(101, 110))
    _ensemble_RCM_HFB_1_5K = list(range(1, 10))





    usage = 'usage: %prog [options] {GCM|RCM}/experiment/category'
    version = '%prog 21.1112'

