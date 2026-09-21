# -*- coding: utf-8 -*-
import sys
import re

def check_file(filepath):
    print(f"Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    issues = []
    # 1. Punctuation touching $
    touching_patterns = [
        (r'([：，。、（；])\$', r'Chinese punctuation before $'),
        (r'\$([：，。、（；）])', r'Chinese punctuation after $'),
        (r'(\()\$(?!\$)', r'Ascii ( before $'),
        (r'(?<!\$)\$(\))', r'Ascii ) after $'),
        (r'(\w)\$', r'Word char directly before $'),
        (r'\$(\w)', r'Word char directly after closing $')
    ]

    for idx, line in enumerate(lines):
        line_num = idx + 1
        # skip lines that are purely display math $$
        stripped = line.strip()
        if stripped == '$$':
            continue

        # Check inline math
        for pat, desc in touching_patterns:
            matches = re.finditer(pat, line)
            for m in matches:
                issues.append((line_num, desc, line.strip()))

        # Check for unclosed $ on line (ignoring escaped \$)
        # Note: display math blocks start and end with $$ on own lines
        if '$$' not in line:
            # count single $
            single_dollars = re.findall(r'(?<!\\)(?<!\$)\$(?!\$)', line)
            if len(single_dollars) % 2 != 0:
                issues.append((line_num, "Odd number of single $ (unbalanced inline math)", line.strip()))

    print(f"Total issues found: {len(issues)}")
    for line_num, desc, content in issues[:20]:
        print(f"  Line {line_num} [{desc}]: {content}")
    return len(issues)

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'docs/第4章_末端配送网络模型建立.md'
    check_file(filepath)
