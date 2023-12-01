import sys
import re
import optparse

def get_RCM_year(t):
    y = int(t / 100)
    if t % 100 < 9:
        y -= 1

    return y

if __name__ == '__main__':
    pass

