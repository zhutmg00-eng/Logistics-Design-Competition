# -*- coding: utf-8 -*-
import os
import re
import sys
import shutil
import tempfile
import subprocess
import markdown

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
DESKTOP_DIR = r'C:\Users\zhutmg\Desktop'

FILES_TO_RENDER = [
    ('docs/第4章_末端配送网络模型建立.md', '第4章_末端配送网络模型建立.pdf'),
    ('docs/第5章_多尺度社区配送需求概率估计与情景模拟模型.md', '第5章_多尺度社区配送需求概率估计与情景模拟模型.pdf'),
    ('docs/第6-7章_两阶段协同网络优化模型.md', '第6-7章_两阶段协同网络优化模型.pdf'),
    ('docs/第7章_无人配送与人工协同运行优化.md', '第7章_无人配送与人工协同运行优化.pdf'),
]

CSS_STYLE = '''
@page {
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
}

body {
    font-family: "PingFang SC", "Microsoft YaHei", "SimSun", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 10.5pt;
    line-height: 1.7;
    color: #1e293b;
    margin: 0;
    padding: 0;
    background: #ffffff;
}

h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 2.5px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 18px;
    page-break-after: avoid;
}

h2 {
    font-size: 14.5pt;
    font-weight: 600;
    color: #1e40af;
    border-bottom: 1.5px solid #93c5fd;
    padding-bottom: 5px;
    margin-top: 24px;
    margin-bottom: 12px;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #0f172a;
    margin-top: 18px;
    margin-bottom: 10px;
    page-break-after: avoid;
}

h4, h5, h6 {
    font-size: 11pt;
    font-weight: 600;
    color: #334155;
    margin-top: 14px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
    text-justify: inter-ideograph;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
}

th {
    background-color: #f1f5f9;
    font-weight: 600;
    color: #0f172a;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

img {
    max-width: 96%;
    height: auto;
    display: block;
    margin: 16px auto 6px auto;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    page-break-inside: avoid;
}

em {
    font-style: italic;
    color: #475569;
}

blockquote {
    border-left: 4px solid #3b82f6;
    margin: 14px 0;
    padding: 10px 16px;
    background: #eff6ff;
    color: #1e3a8a;
    font-size: 10pt;
    border-radius: 0 6px 6px 0;
}

code {
    font-family: Consolas, "Courier New", monospace;
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 9pt;
    color: #0f172a;
}

pre {
    background: #0f172a;
    color: #f8fafc;
    border: 1px solid #1e293b;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 8.5pt;
    line-height: 1.5;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 14px 0;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
}

.katex-display {
    margin: 12px 0 !important;
    page-break-inside: avoid;
}

.katex {
    font-size: 1.08em;
}
'''

def preprocess_markdown(content):
    """
    Safely protect LaTeX formulas from markdown parser:
    Replace display math ($$...$$) and inline math ($`...`$ or $...$) with
    strictly alphanumeric placeholders containing ZERO underscores or asterisks.
    """
    placeholders = []

    # 1. Display math $$...$$
    def save_display(m):
        inner = m.group(1).strip()
        idx = len(placeholders)
        placeholders.append(f'<div class="katex-display">\\[{inner}\\]</div>')
        return f"MATHBLOCK{idx}XYZ"

    content = re.sub(r'\$\$(.*?)\$\$', save_display, content, flags=re.DOTALL)

    # 2. Code-span math $`...`$
    def save_codespan_math(m):
        inner = m.group(1).strip()
        idx = len(placeholders)
        placeholders.append(f'<span class="katex-inline">\\({inner}\\)</span>')
        return f"MATHINLINE{idx}XYZ"

    content = re.sub(r'\$`(.*?)`\$', save_codespan_math, content)

    # 3. Standard inline math $...$
    def save_inline(m):
        inner = m.group(1).strip()
        if not inner:
            return '$$'
        idx = len(placeholders)
        placeholders.append(f'<span class="katex-inline">\\({inner}\\)</span>')
        return f"MATHINLINE{idx}XYZ"

    content = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', save_inline, content)

    return content, placeholders

def restore_math(html, placeholders):
    for idx, ph in enumerate(placeholders):
        html = html.replace(f"MATHBLOCK{idx}XYZ", ph)
        html = html.replace(f"MATHINLINE{idx}XYZ", ph)
    return html

def render_markdown_to_html(md_path, temp_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Preprocess math
    processed_md, placeholders = preprocess_markdown(md_text)

    # Convert to HTML
    html_body = markdown.markdown(
        processed_md,
        extensions=[
            'tables',
            'fenced_code',
            'attr_list',
            'def_list'
        ]
    )

    # Restore math
    html_body = restore_math(html_body, placeholders)

    # Wrap in complete HTML document
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{os.path.basename(md_path)}</title>
<link rel="stylesheet" href="katex/katex.min.css">
<script src="katex/katex.min.js"></script>
<script src="katex/auto-render.min.js"></script>
<style>
{CSS_STYLE}
</style>
</head>
<body>
{html_body}
<script>
renderMathInElement(document.body, {{
    delimiters: [
        {{left: '\\\\[', right: '\\\\]', display: true}},
        {{left: '\\\\(', right: '\\\\)', display: false}},
        {{left: '$$', right: '$$', display: true}},
        {{left: '$`', right: '`$', display: false}},
        {{left: '$', right: '$', display: false}}
    ],
    throwOnError: false
}});
</script>
</body>
</html>'''
    return full_html

def main():
    print("=== Starting Batch PDF Rendering ===")
    if not os.path.exists(CHROME_PATH):
        print(f"Error: Chrome not found at {CHROME_PATH}")
        sys.exit(1)

    os.makedirs(DESKTOP_DIR, exist_ok=True)

    # Create temporary isolated working directory in pure ASCII path
    temp_dir = tempfile.mkdtemp(prefix="pdf_render_")
    print(f"Working in temp directory: {temp_dir}")

    # Copy KaTeX library to temp_dir
    katex_src = os.path.abspath(r'demo\static\libs\katex')
    katex_dst = os.path.join(temp_dir, 'katex')
    print("Copying KaTeX library...")
    shutil.copytree(katex_src, katex_dst)

    # Copy images directory to temp_dir
    images_src = os.path.abspath(r'docs\images')
    images_dst = os.path.join(temp_dir, 'images')
    print("Copying docs/images...")
    shutil.copytree(images_src, images_dst)

    results = []

    for src_rel, pdf_name in FILES_TO_RENDER:
        src_path = os.path.abspath(src_rel)
        if not os.path.exists(src_path):
            print(f"Warning: File {src_path} does not exist. Skipping.")
            continue

        print(f"\n--- Rendering: {os.path.basename(src_path)} ---")
        html_content = render_markdown_to_html(src_path, temp_dir)

        # Write HTML in temp_dir
        safe_html_name = f"doc_{len(results)}.html"
        safe_pdf_name = f"doc_{len(results)}.pdf"
        temp_html_path = os.path.join(temp_dir, safe_html_name)
        temp_pdf_path = os.path.join(temp_dir, safe_pdf_name)

        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        file_url = 'file:///' + temp_html_path.replace('\\', '/')

        cmd = [
            CHROME_PATH,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            '--run-all-compositor-stages-before-draw',
            f'--print-to-pdf={temp_pdf_path}',
            file_url
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
            if res.returncode == 0 and os.path.exists(temp_pdf_path):
                # Copy to Desktop
                final_dest = os.path.join(DESKTOP_DIR, pdf_name)
                shutil.copy(temp_pdf_path, final_dest)
                size_kb = os.path.getsize(final_dest) / 1024.0
                print(f"SUCCESS: Generated {pdf_name} ({size_kb:.1f} KB)")
                print(f"Saved to: {final_dest}")
                results.append((pdf_name, final_dest, size_kb, True))
            else:
                print(f"FAILURE: Return code {res.returncode}")
                print(f"Stderr: {res.stderr}")
                results.append((pdf_name, None, 0, False))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((pdf_name, None, 0, False))

    print("\n=== Summary ===")
    for pdf_name, path, size, success in results:
        status = f"OK ({size:.1f} KB)" if success else "FAILED"
        print(f"- {pdf_name}: {status}")

if __name__ == '__main__':
    main()
