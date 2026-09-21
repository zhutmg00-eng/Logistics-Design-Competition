# -*- coding: utf-8 -*-
import os
import re

files = [
    'docs/第4章_末端配送网络模型建立.md',
    'docs/第5章_多尺度社区配送需求概率估计与情景模拟模型.md',
    'docs/第7章_无人配送与人工协同运行优化.md',
    'README.md'
]

def analyze():
    for f in files:
        if not os.path.exists(f):
            continue
        print("========================================")
        print("FILE:", f)
        with open(f, 'r', encoding='utf-8') as fp:
            lines = fp.read().splitlines()
        
        for i, l in enumerate(lines):
            if l.strip().startswith('|') and '$' in l:
                print(f"  [TABLE Line {i+1}]: {l[:110]}")
            elif not l.strip().startswith('|') and '$$' not in l:
                m = re.findall(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', l)
                if sum(x.count('_') for x in m) >= 2:
                    print(f"  [MULTI-_ Line {i+1}]: {l[:110]}")

if __name__ == '__main__':
    analyze()
