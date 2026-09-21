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
    r'\dots': '...',
    r'\ldots': '...',
    r'\forall': '∀',
    r'\in': '∈',
    r'\subset': '⊂',
    r'\cup': '∪',
    r'\cap': '∩',
    r'\mathbb{E}': 'E',
    r'\mathrm{Var}': 'Var',
    r'\mathrm{Poisson}': 'Poisson',
    r'\mathrm{Gamma}': 'Gamma',
    r'\mathrm{NegBin}': 'NegBin',
    r'\mathrm{Dirichlet}': 'Dirichlet',
    r'\mathrm{Multinomial}': 'Multinomial',
    r'\mathrm{Triang}': 'Triang',
    r'\mathcal{N}': 'N',
}

def clean_table_math(cell):
    """Convert LaTeX math inside Markdown table cell to clean text / unicode."""
    text = cell
    for tex, uni in GREEK_AND_SYMBOLS.items():
        text = text.replace(tex, uni)
    
    def replace_dollar(m):
        inner = m.group(1).strip()
        for tex, uni in GREEK_AND_SYMBOLS.items():
            inner = inner.replace(tex, uni)
        # remove \text{...}, \mathrm{...}, \mathbf{...}, \mathcal{...}
        inner = re.sub(r'\\(?:text|mathrm|mathbf|mathcal|mathbb)\{(.*?)\}', r'\1', inner)
        # replace subscripts/superscripts brackets: _{...} -> _...
        inner = re.sub(r'_\{(.*?)\}', r'_\1', inner)
        inner = re.sub(r'\^\{(.*?)\}', r'^\1', inner)
        # remove remaining backslashes
        inner = inner.replace('\\', '')
        return inner

    text = re.sub(r'\$(.*?)\$', replace_dollar, text)
    return text

def fix_table_line(line):
    if not line.strip().startswith('|'):
        return line
    parts = line.split('|')
    new_parts = [clean_table_math(p) for p in parts]
    return '|'.join(new_parts)

def clean_inline_math_in_line(line):
    """
    Format inline math for GitHub Markdown:
    1. Protect existing code spans and display math
    2. If inline math contains '_', convert to $`...`$ to prevent cmark-gfm italics
    3. Trim any internal whitespace: '$ x $' -> '$x$' or '$`x`$'
    4. Ensure external spacing around math delimiters so they separate from words/CJK
    """
    if line.strip().startswith('|'):
        return line

    # Protect code spans: `...`
    code_spans = []
    def save_code(m):
        code_spans.append(m.group(0))
        return f"__CODE_SPAN_{len(code_spans)-1}__"

    # Protect existing $`...`$ first
    line = re.sub(r'\$`.*?`\$', save_code, line)
    # Protect any standard `...`
    line = re.sub(r'`[^`]+`', save_code, line)

    # Process standard $...$
    def replace_dollar(m):
        inner = m.group(1).strip()
        # if empty
        if not inner:
            return "$$"
        if '_' in inner:
            return f"$`{inner}`$"
        else:
            return f"${inner}$"

    # Match single $...$ (not preceded or followed by $)
    line = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', replace_dollar, line)

    # Restore code spans
    for i, cs in enumerate(code_spans):
        # if the code span was $`...`$, ensure it's trimmed
        if cs.startswith('$`') and cs.endswith('`$'):
            inner = cs[2:-2].strip()
            cs = f"$`{inner}`$"
        line = line.replace(f"__CODE_SPAN_{i}__", cs)

    # Add space before $ or $` if preceded by CJK / alphanumeric (excluding markdown symbols like * _ [ ( )
    line = re.sub(r'([\u4e00-\u9fa5a-zA-Z0-9])(\$`|\$(?!\$))', r'\1 \2', line)
    # Add space after $ or `$ if followed by CJK / alphanumeric
    line = re.sub(r'(`\$|(?<!\$)\$(?!\$))([\u4e00-\u9fa5a-zA-Z0-9])', r'\1 \2', line)

    return line

def sanitize_content(content):
    # Step 1: isolate block math $$...$$
    blocks = []
    def save_block(m):
        blocks.append(m.group(0))
        return f"__BLOCK_MATH_{len(blocks)-1}__"

    content = re.sub(r'\$\$.*?\$\$', save_block, content, flags=re.DOTALL)

    # Step 2: process lines
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith('|'):
            new_lines.append(fix_table_line(line))
        else:
            new_lines.append(clean_inline_math_in_line(line))

    content = '\n'.join(new_lines)

    # Step 3: restore and format block math
    for i, b in enumerate(blocks):
        inner = b.strip()
        if inner.startswith('$$') and inner.endswith('$$'):
            inner = inner[2:-2].strip()
        # collapse internal empty lines
        inner = re.sub(r'\n\s*\n', '\n', inner)
        clean_block = f"\n\n$$\n{inner}\n$$\n\n"
        content = content.replace(f"__BLOCK_MATH_{i}__", clean_block)

    # clean excessive newlines
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    return content

def embed_chapter4_images(content):
    # 1. 原图 4-1
    if "fig4_1_original_network_topology.png" not in content:
        pattern = r"(5\.\s*\$[^$]+\$)\s*\n"
        replacement = r"\1\n\n![原图 4-1 社区末端配送网络拓扑结构示意图](images/network/fig4_1_original_network_topology.png)\n\n"
        content = re.sub(pattern, replacement, content, count=1)

    # 2. 原图 4-2
    if "fig4_2_original_methodology_flowchart.png" not in content:
        target = "![图 4-1 末端配送网络三阶段协同优化模型框架与平台调用逻辑](images/network/fig4_1_network_model_framework.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 4-2 三阶段末端配送网络规划技术路线与总体框架图](images/network/fig4_2_original_methodology_flowchart.png)")

    # 3. 原图 4-5
    if "fig4_5_original_service_feasibility.png" not in content:
        target = "![图 4-2 五案例社区末端设施—需求节点服务可行关系与标准化距离热力矩阵](images/network/fig4_2_service_feasibility_heatmap.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 4-5 五社区设施—需求节点服务可行性热力图](images/network/fig4_5_original_service_feasibility.png)")

    # 4. 原图 4-3
    if "fig4_3_original_facility_sizing_mechanism.png" not in content:
        target = "代表满足覆盖和容量约束所需的最低新增设施数量，该值将作为第二阶段模型的硬约束输入。"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 4-3 服务设施规模确定机制图](images/network/fig4_3_original_facility_sizing_mechanism.png)")

    # 5. 原图 4-4
    if "fig4_4_original_weighted_median_partition.png" not in content:
        target = "实际需求负荷 $ W_j $ 将作为第三阶段计算设施间转运周转量的关键输入。"
        target2 = "实际需求负荷 $`W_j`$ 将作为第三阶段计算设施间转运周转量的关键输入。"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 4-4 需求加权选址与服务分区示意图](images/network/fig4_4_original_weighted_median_partition.png)")
        elif target2 in content:
            content = content.replace(target2, target2 + "\n\n![原图 4-4 需求加权选址与服务分区示意图](images/network/fig4_4_original_weighted_median_partition.png)")

    return content

def embed_chapter5_images(content):
    # 1. 原图 5-1
    if "fig5_1_original_framework.png" not in content:
        target = "![图 5-1 多尺度社区配送需求概率估计与情景模拟总体框架](images/demand/fig5_1_demand_estimation_framework.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 5-1 社区配送需求概率估计与情景模拟总体框架](images/demand/fig5_1_original_framework.png)")

    # 2. 原图 5-2
    if "fig5_2_original_generative_mechanism.png" not in content:
        target = "![图 5-2 核心随机变量与贝叶斯层次概率生成机制图](images/demand/fig5_2_probabilistic_generative_mechanism.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 5-2 核心随机变量与概率生成机制图](images/demand/fig5_2_original_generative_mechanism.png)")

    # 3. 原图 5-3
    if "fig5_3_original_probability_distribution.png" not in content:
        target = "为高分位数容量规划提供严谨的统计底座。"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 5-3 需求概率分布示意图（以代表性社区为例）](images/demand/fig5_3_original_probability_distribution.png)")

    # 4. 原图 5-4 & 5-5
    if "fig5_4_original_beijing_benchmarks.png" not in content:
        target = "![图 5-3 五个案例社区日需求情景估计与分位数分布对比图](images/demand/fig5_3_five_communities_scenario_demand.png)"
        if target in content:
            replacement = target + "\n\n![原图 5-4 北京公开资料样本社区需求情景比较](images/demand/fig5_4_original_beijing_benchmarks.png)\n\n![原图 5-5 五社区日需求分位数与促销高峰需求](images/demand/fig5_5_original_five_communities_quantiles.png)"
            content = content.replace(target, replacement)

    # 5. 原图 5-6
    if "fig5_6_original_hourly_curves.png" not in content:
        target = "![图 5-4 五社区 6 时段分时需求演变与峰值负荷对比图](images/demand/fig5_4_temporal_demand_profile_6slots.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 5-6 五社区分时需求曲线](images/demand/fig5_6_original_hourly_curves.png)")

    # 6. 原图 5-7
    if "fig5_7_original_sensitivity_matrix.png" not in content:
        target = "![图 5-5 亦城茗苑多维核心参数灵敏度矩阵与响应分析](images/demand/fig5_5_parameter_sensitivity_matrix.png)"
        if target in content:
            content = content.replace(target, target + "\n\n![原图 5-7 户均需求率与促销系数敏感性](images/demand/fig5_7_original_sensitivity_matrix.png)")

    return content

def main():
    # Chapter 4
    c4_path = 'docs/第4章_末端配送网络模型建立.md'
    if os.path.exists(c4_path):
        print(f"Processing {c4_path}...")
        with open(c4_path, 'r', encoding='utf-8') as f:
            c4 = f.read()
        c4 = embed_chapter4_images(c4)
        c4 = sanitize_content(c4)
        with open(c4_path, 'w', encoding='utf-8') as f:
            f.write(c4)
        print(f"Done {c4_path}.")

    # Chapter 5
    c5_path = 'docs/第5章_多尺度社区配送需求概率估计与情景模拟模型.md'
    if os.path.exists(c5_path):
        print(f"Processing {c5_path}...")
        with open(c5_path, 'r', encoding='utf-8') as f:
            c5 = f.read()
        c5 = embed_chapter5_images(c5)
        c5 = sanitize_content(c5)
        with open(c5_path, 'w', encoding='utf-8') as f:
            f.write(c5)
        print(f"Done {c5_path}.")

    # Chapter 7
    c7_path = 'docs/第7章_无人配送与人工协同运行优化.md'
    if os.path.exists(c7_path):
        print(f"Processing {c7_path}...")
        with open(c7_path, 'r', encoding='utf-8') as f:
            c7 = f.read()
        c7 = sanitize_content(c7)
        with open(c7_path, 'w', encoding='utf-8') as f:
            f.write(c7)
        print(f"Done {c7_path}.")

    # README.md
    readme_path = 'README.md'
    if os.path.exists(readme_path):
        print(f"Processing {readme_path}...")
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()
        readme = sanitize_content(readme)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        print(f"Done {readme_path}.")

if __name__ == '__main__':
    main()
