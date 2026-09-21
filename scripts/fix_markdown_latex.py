# -*- coding: utf-8 -*-
import sys
import re

def fix_file(filepath):
    print(f"Fixing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to process inline math $...$
    # We must NOT modify display math $$...$$
    # Let's tokenize or replace $$...$$ temporarily
    display_math_blocks = []
    def save_display(m):
        display_math_blocks.append(m.group(0))
        return f"__DISPLAY_MATH_{len(display_math_blocks)-1}__"

    # Match $$...$$ (could span multiple lines or single line)
    content = re.sub(r'\$\$.*?\$\$', save_display, content, flags=re.DOTALL)

    # Now for inline math $...$
    # Rule: Ensure space before opening $ if preceded by non-space, non-$
    # and space after closing $ if followed by non-space, non-$
    # But beware of markdown table pipes `|`
    
    def fix_inline(m):
        math_content = m.group(1).strip()
        # Ensure no leading/trailing space INSIDE the math delimiters
        return f"${math_content}$"

    # First clean inside:
    content = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', fix_inline, content)

    # Now fix boundaries around $...$:
    # If preceded by any character other than whitespace, |, (, [, {, <, add space
    def add_space_before(m):
        prefix = m.group(1)
        dollar = m.group(2)
        # If prefix is not whitespace and not in exempt chars
        if prefix and not re.match(r'[\s\|\(\[\{\<]', prefix):
            return f"{prefix} {dollar}"
        return m.group(0)

    # If followed by any character other than whitespace, |, ), ], }, >, add space
    def add_space_after(m):
        dollar = m.group(1)
        suffix = m.group(2)
        if suffix and not re.match(r'[\s\|\)\]\}\>]', suffix):
            return f"{dollar} {suffix}"
        return m.group(0)

    # Preceded by non-space
    content = re.sub(r'([^\s\|\(\[\{\<])(\$(?!\$))', r'\1 \2', content)
    # Followed by non-space
    content = re.sub(r'((?<!\$)\$)([^\s\|\)\]\}\>])', r'\1 \2', content)

    # Restore display math blocks, ensuring they are on their own lines with empty lines
    for i, block in enumerate(display_math_blocks):
        # clean block: strip outer $$
        inner = block.strip()
        if inner.startswith('$$') and inner.endswith('$$'):
            inner_content = inner[2:-2].strip()
            fixed_block = f"\n\n$$\n{inner_content}\n$$\n\n"
        else:
            fixed_block = f"\n\n{block}\n\n"
        content = content.replace(f"__DISPLAY_MATH_{i}__", fixed_block)

    # Clean up any excessive newlines (more than 2 consecutive empty lines)
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Done fixing {filepath}.")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'docs/第4章_末端配送网络模型建立.md'
    fix_file(filepath)
