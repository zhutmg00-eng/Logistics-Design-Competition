# -*- coding: utf-8 -*-
import os
import re

GREEK_AND_SYMBOLS = {
    r'\rightarrow': '→',
    r'\leftarrow': '←',
    r'\to': '→',
    r'\sim': '~',
    r'\le': '≤',
    r'\ge': '≥',
    r'\leq': '≤',
    r'\geq': '≥',
    r'\pm': '±',
    r'\times': '×',
    r'\cdot': '·',
    r'\approx': '≈',
    r'\neq': '≠',
    r'\alpha': 'α',
    r'\beta': 'β',
    r'\gamma': 'γ',
    r'\lambda': 'λ',
    r'\mu': 'μ',
    r'\eta': 'η',
    r'\theta': 'θ',
    r'\tau': 'τ',
    r'\sigma': 'σ',
    r'\epsilon': 'ε',
    r'\phi': 'φ',
    r'\kappa': 'κ',
    r'\delta': 'δ',
    r'\Delta': 'Δ',
    r'\Sigma': 'Σ',
    r'\Lambda': 'Λ',
    r'\infty': '∞',
    r'\%': '%',
}

def clean_table_math(cell):
    """Clean LaTeX math expressions inside table cells so they render as clean text/unicode on GitHub."""
    text = cell
    # First replace known symbols
    for tex, uni in GREEK_AND_SYMBOLS.items():
        text = text.replace(tex, uni)
    
    # Remove $ delimiters inside cell
    # e.g. $ Q_{veh} $ -> Q_veh, $ 100% $ -> 100%
    def replace_dollar(m):
        inner = m.group(1).strip()
        for tex, uni in GREEK_AND_SYMBOLS.items():
            inner = inner.replace(tex, uni)
        # remove \text{...}
        inner = re.sub(r'\\text\{(.*?)\}', r'\1', inner)
        inner = re.sub(r'\\mathrm\{(.*?)\}', r'\1', inner)
        # remove remaining backslashes
        inner = inner.replace('\\', '')
        return inner

    text = re.sub(r'\$(.*?)\$', replace_dollar, text)
    return text

def fix_table_line(line):
    if not line.strip().startswith('|'):
        return line
    parts = line.split('|')
    new_parts = []
    for p in parts:
        new_parts.append(clean_table_math(p))
    return '|'.join(new_parts)

def fix_document(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Temporarily isolate block math $$...$$
    blocks = []
    def save_block(m):
        blocks.append(m.group(0))
        return f"__BLOCK_MATH_{len(blocks)-1}__"

    # Match $$...$$
    content = re.sub(r'\$\$.*?\$\$', save_block, content, flags=re.DOTALL)

    lines = content.splitlines()
    new_lines = []

    for line in lines:
        # If table line, clean math in table
        if line.strip().startswith('|'):
            new_lines.append(fix_table_line(line))
        else:
            # Fix inline math outside tables
            # GitHub rule: if inline math contains underscore '_', use $`...`$ to prevent cmark-gfm italics
            # Also ensure space before $` or $ if preceded by CJK/word, and space after `$ or $ if followed by CJK/word
            def replace_inline(m):
                inner = m.group(1).strip()
                if '_' in inner:
                    return f"$`{inner}`$"
                else:
                    return f"${inner}$"

            # Replace standard $...$ (not preceded or followed by $)
            # Be careful not to touch already backtick-wrapped $`...`$
            # First match any existing $`...`$ and protect
            protected_code_math = []
            def save_code_math(m):
                protected_code_math.append(m.group(0))
                return f"__CODE_MATH_{len(protected_code_math)-1}__"

            l = re.sub(r'\$`.*?`\$', save_code_math, line)
            
            # Now replace $...$ with underscore to $`...`$
            l = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', replace_inline, l)

            # Restore protected code math
            for idx, cm in enumerate(protected_code_math):
                l = l.replace(f"__CODE_MATH_{idx}__", cm)

            # Ensure proper spacing around inline math:
            # Add space before $ or $` if preceded by non-space, non-punctuation
            l = re.sub(r'([^\s\|\(\[\{\<（【])(\$(?:`|\b))', r'\1 \2', l)
            # Add space after $ or `$ if followed by non-space, non-punctuation
            l = re.sub(r'((?:`\$|\$))([^\s\|\)\]\}\>）】])', r'\1 \2', l)

            new_lines.append(l)

    content = '\n'.join(new_lines)

    # Step 2: Restore and sanitize block math $$...$$
    for i, b in enumerate(blocks):
        # strip outer $$
        inner = b.strip()
        if inner.startswith('$$') and inner.endswith('$$'):
            inner = inner[2:-2].strip()
        # Ensure no empty lines inside block math (replaces \n\s*\n with single \n)
        inner = re.sub(r'\n\s*\n', '\n', inner)
        clean_block = f"\n\n$$\n{inner}\n$$\n\n"
        content = content.replace(f"__BLOCK_MATH_{i}__", clean_block)

    # Clean up excessive newlines
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully sanitized {filepath}.")

if __name__ == '__main__':
    for fp in [
        'docs/第4章_末端配送网络模型建立.md',
        'docs/第5章_多尺度社区配送需求概率估计与情景模拟模型.md',
        'docs/第7章_无人配送与人工协同运行优化.md',
        'README.md'
    ]:
        if os.path.exists(fp):
            fix_document(fp)
