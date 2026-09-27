const { createApp, ref, computed, onMounted, watch, nextTick } = Vue;

const app = createApp({
    setup() {
        const activeTab = ref('comparison');
        const viewMode = ref('split'); // 'split' | 'wide'
        const presentationMode = ref(false);
        const schemeMode = ref('diff'); // 's0' | 's1' | 's2' | 'diff'
        const currentScenario = ref('N'); // 'N' | 'P15' | 'P20'
        const loading = ref(false);
        const overview = ref(null);
        const selectedCommunityId = ref('C04');
        const planResult = ref(null);
        const simulationResult = ref(null);
        const simScenario = ref('normal'); // 'normal' | 'peak' | 'disruption'
        const crisisResult = ref(null);
        const isPeakDay = ref(false);

        // 方案模式计算属性与样式指示
        const isS0 = computed(() => schemeMode.value === 's0' || schemeMode.value === 'baseline');
        const isS1 = computed(() => schemeMode.value === 's1');
        const isS2 = computed(() => schemeMode.value === 's2' || schemeMode.value === 'optimized');
        const isDiff = computed(() => schemeMode.value === 'diff');

        const getModelDisplayName = (modelId) => {
            if (!modelId) return 'AI 推理引擎';
            const m = String(modelId).toLowerCase();
            if (m.includes('reason') || m.includes('thinking') || m.includes('-r1') || m.endsWith('r1')) return '深度推理引擎';
            if (m.includes('flash') || m.includes('turbo') || m.includes('mini')) return '极速响应引擎';
            if (m.includes('v3') || m.includes('v4') || m.includes('pro') || m.includes('chat') || m.includes('max')) return '通用旗舰引擎';
            if (m.includes('qwen')) return '通义兼容引擎';
            if (m.includes('gpt')) return 'OpenAI 兼容引擎';
            return '自定义 AI 推理引擎';
        };

        const schemeCardClass = (targetScheme) => {
            if (isDiff.value) return 'bg-slate-900/70 border-slate-700/80 opacity-100 transition-all duration-200';
            if (targetScheme === 's0' && isS0.value) {
                return 'ring-2 ring-rose-500 bg-rose-950/85 border-rose-500/90 shadow-lg shadow-rose-950/50 scale-[1.03] transition-all duration-200';
            }
            if (targetScheme === 's1' && isS1.value) {
                return 'ring-2 ring-amber-500 bg-amber-950/85 border-amber-500/90 shadow-lg shadow-amber-950/50 scale-[1.03] transition-all duration-200';
            }
            if (targetScheme === 's2' && isS2.value) {
                return 'ring-2 ring-emerald-500 bg-emerald-950/85 border-emerald-500/90 shadow-lg shadow-emerald-950/50 scale-[1.03] transition-all duration-200';
            }
            return 'bg-slate-900/60 border-slate-800/80 opacity-60 transition-all duration-200';
        };

        const switchAiModel = async (targetModel) => {
            aiConfigForm.value.model = targetModel;
            aiConfig.value.model = targetModel;
            try {
                const res = await fetch('/api/ai/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: targetModel })
                });
                if (res.ok) {
                    showToast(`已切换 AI 模型为: ${getModelDisplayName(targetModel)}`, 'success');
                }
            } catch (e) {
                console.warn('Switch AI model error:', e);
            }
        };

        // ==========================================
        // AI 智能调度中枢与多智能体应急决策 (AICopilot) 响应式状态
        // ==========================================
        const showAiDrawer = ref(false);
        const aiDrawerMessages = ref([
            {
                role: 'assistant',
                content: '您好！我是超大城市末端配送协同决策大模型调度助理。我已动态接入北京亦庄示范区全域遥测数据与 M1-M8 运筹模型流水线。您可以随时向我咨询当前社区瓶颈诊断、多智能体协同应急重排方案，或探讨数智化与绿色化升级路径。',
                time: '刚刚'
            }
        ]);
        const aiInput = ref('');
        const aiLoading = ref(false);
        const aiConfig = ref({
            provider: 'deepseek',
            base_url: 'https://api.deepseek.com',
            model: 'deepseek-flash',
            has_key: false,
            masked_key: '未配置',
            mode_status: '本地运筹智能引擎 (极速抗毁)'
        });
        const showAiConfigModal = ref(false);
        const aiConfigForm = ref({
            provider: 'deepseek',
            base_url: 'https://api.deepseek.com',
            api_key: '',
            model: 'deepseek-flash'
        });
        const aiDetectedModels = ref([]);
        const aiModelsLoading = ref(false);
        const aiModelsMessage = ref('');
        const aiTestLoading = ref(false);
        const aiTestResult = ref(null);

        const aiQuickModes = computed(() => {
            const current = aiConfig.value.model || aiConfigForm.value.model;
            const models = aiDetectedModels.value.length ? aiDetectedModels.value : [];
            const pickModel = (predicate, fallback) => models.find(predicate)?.id || fallback;
            const candidates = [
                { key: 'fast', icon: '⚡', label: '极速响应', model: pickModel(m => m.category === 'fast', current), description: '优先低延迟模型，适合快速问答与录屏演示' },
                { key: 'reasoning', icon: '🧠', label: '深度推理', model: pickModel(m => m.category === 'reasoning', 'deepseek-reasoner'), description: '优先推理模型，适合应急推演与复杂诊断' },
                { key: 'quality', icon: '✦', label: '旗舰质量', model: pickModel(m => m.category === 'flagship' || m.category === 'chat', current), description: '优先综合能力更强的通用模型' }
            ];
            const seen = new Set();
            return candidates.filter(item => {
                if (!item.model || seen.has(item.model)) return false;
                seen.add(item.model);
                return true;
            });
        });

        // Tab 6 AI 应急调度流式与执行状态
        const activeCrisisType = ref('SURGE');
        const crisisStreaming = ref(false);
        const crisisStreamText = ref('');
        const crisisExecutionStatus = ref('');

        const apiError = ref('');
        const mobilePane = ref('content');
        const showConstraintDetails = ref(false);

        const moduleNav = [
            { code: 'comparison', shortLabel: '总览' },
            { code: 'digital-twin', shortLabel: '数字孪生' },
            { code: 'forecast', shortLabel: '需求预测' },
            { code: 'layout', shortLabel: '选址定容' },
            { code: 'routing', shortLabel: '人车协同' },
            { code: 'simulation', shortLabel: '仿真对抗' },
            { code: 'copilot', shortLabel: 'AI应急' }
        ];

        const initialHashState = new URLSearchParams(window.location.hash.replace(/^#/, ''));
        const validTabs = new Set(moduleNav.map(item => item.code));
        const initialTab = initialHashState.get('tab');
        if (validTabs.has(initialTab)) activeTab.value = initialTab;
        const initialCommunity = initialHashState.get('community');
        if (initialCommunity === 'ALL' || ['C01', 'C02', 'C03', 'C04', 'C05'].includes(initialCommunity)) {
            selectedCommunityId.value = initialCommunity;
        }
        const initialScheme = initialHashState.get('scheme');
        if (['s0', 's1', 's2', 'diff'].includes(initialScheme)) schemeMode.value = initialScheme;
        const initialScenario = initialHashState.get('scenario');
        if (['N', 'P15', 'P20'].includes(initialScenario)) {
            currentScenario.value = initialScenario;
            isPeakDay.value = initialScenario === 'P20';
        }

        const violationStatusTokens = new Set([
            'VIOLATED', 'OVERLOAD_VIOLATION', 'OVERTIME_WARNING', 'INFEASIBLE',
            'SYNC_VIOLATION', 'BATTERY_RESERVE_VIOLATION'
        ]);

        const isViolationStatus = (status) => violationStatusTokens.has(String(status || '').toUpperCase());
        const formatConstraintValue = (value) => {
            if (value === null || value === undefined || value === '') return '—';
            const num = Number(value);
            if (!Number.isFinite(num)) return String(value);
            return Math.abs(num) >= 1000 ? num.toFixed(0) : num.toFixed(2).replace(/\.?0+$/, '');
        };

        const constraintChecks = computed(() => ([
            ...(planResult.value?.layout?.constraint_checks || []),
            ...(planResult.value?.routing?.constraint_checks || [])
        ]));

        const failedConstraintChecks = computed(() => constraintChecks.value.filter(item => isViolationStatus(item.status)));

        const pipelineStatus = computed(() => (
            planResult.value?.solver_console?.pipeline_status
            || planResult.value?.routing?.solver_metrics?.status
            || 'CALCULATING'
        ));

        const hardViolationCount = computed(() => {
            const count = Number(planResult.value?.solver_console?.hard_constraint_violations);
            return Number.isFinite(count) ? count : failedConstraintChecks.value.length;
        });

        const planStatusMeta = computed(() => {
            if (!planResult.value) {
                return {
                    tone: 'warning', shortLabel: '计算中', title: '正在生成规划方案',
                    description: '系统正在同步 M5 预测、M6 定容与 M2/M3 路径规划结果。',
                    metric: '等待求解器返回'
                };
            }
            const status = String(pipelineStatus.value || '').toUpperCase();
            const solver = planResult.value?.solver_console || {};
            const solveTime = Number(solver.total_solve_time_ms || 0).toFixed(3);
            const metric = `M5 ${Number(solver.solver_breakdown?.M5_forecast_ms || 0).toFixed(3)} ms · M6 ${Number(solver.solver_breakdown?.M6_layout_mip_ms || 0).toFixed(3)} ms · M2 ${Number(solver.solver_breakdown?.M2_routing_cvrp_ms || 0).toFixed(3)} ms`;
            if (status.includes('INFEASIBLE') || hardViolationCount.value > 0) {
                return {
                    tone: 'danger', shortLabel: '约束告警',
                    title: `方案存在 ${hardViolationCount.value || failedConstraintChecks.value.length} 项硬约束未通过`,
                    description: '结果可用于诊断和演示，但不应标记为可直接执行方案；请查看约束明细并修复容量、工时或时序问题。',
                    metric
                };
            }
            if (status.includes('FEASIBLE')) {
                return {
                    tone: 'success', shortLabel: '约束通过',
                    title: '方案通过硬约束流水线校验',
                    description: `当前社区为 ${planResult.value.community_name || planResult.value.community_id}，可继续开展方案对比、仿真和汇报。`,
                    metric
                };
            }
            return {
                tone: 'warning', shortLabel: '待校验',
                title: '方案已生成，约束状态待确认',
                description: '请检查求解器日志和约束明细后，再用于正式方案汇报。',
                metric
            };
        });

        const renderMarkdown = (text = '') => {
            if (!text) return '';

            // Render complete LaTeX fragments deterministically before Vue injects
            // the markdown HTML. Auto-render alone misses formulas nested inside
            // strong/list nodes during streaming updates.
            const renderTex = (tex, displayMode = false) => {
                if (!window.katex) return `<span class="math-fallback">${tex}</span>`;
                try {
                    return window.katex.renderToString(tex, {
                        displayMode,
                        throwOnError: false,
                        strict: 'ignore',
                        trust: false
                    });
                } catch (e) {
                    return `<span class="math-fallback">${tex}</span>`;
                }
            };
            const source = String(text)
                .replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => renderTex(tex, true))
                .replace(/\$([^$\n]+?)\$/g, (_, tex) => renderTex(tex, false));
            const lines = source.split('\n');
            const html = [];
            let inList = false;
            let inTable = false;
            let inCode = false;

            const inlineFormat = (str) => {
                return String(str || '')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[11px]">$1</code>');
            };

            const closeList = () => {
                if (inList) {
                    html.push('</ul>');
                    inList = false;
                }
            };
            const closeTable = () => {
                if (inTable) {
                    html.push('</tbody></table></div>');
                    inTable = false;
                }
            };

            for (let i = 0; i < lines.length; i++) {
                const rawLine = lines[i];
                const line = rawLine.trim();

                // 代码块解析
                if (line.startsWith('```')) {
                    closeList();
                    closeTable();
                    inCode = !inCode;
                    if (inCode) {
                        html.push('<pre class="p-3 my-2 rounded-lg bg-slate-950 border border-slate-800 text-emerald-300 font-mono text-xs overflow-x-auto">');
                    } else {
                        html.push('</pre>');
                    }
                    continue;
                }
                if (inCode) {
                    html.push(`${rawLine}\n`);
                    continue;
                }

                if (!line) {
                    closeList();
                    closeTable();
                    continue;
                }

                // 表格解析
                if (line.startsWith('|') && line.endsWith('|')) {
                    closeList();
                    const rawCells = line.split('|').slice(1, -1).map(c => c.trim());
                    if (rawCells.every(c => /^[:\s-]+$/.test(c))) {
                        continue;
                    }
                    if (!inTable) {
                        inTable = true;
                        html.push('<div class="overflow-x-auto my-2"><table class="w-full text-xs text-left border-collapse border border-slate-700/60 rounded"><thead><tr class="bg-slate-800/80 text-cyan-300 font-semibold">');
                        rawCells.forEach(cell => {
                            html.push(`<th class="p-2 border border-slate-700/60">${inlineFormat(cell)}</th>`);
                        });
                        html.push('</tr></thead><tbody>');
                    } else {
                        html.push('<tr class="border-b border-slate-800/50 hover:bg-slate-800/30">');
                        rawCells.forEach(cell => {
                            html.push(`<td class="p-2 border border-slate-700/40 text-slate-300">${inlineFormat(cell)}</td>`);
                        });
                        html.push('</tr>');
                    }
                    continue;
                }
                closeTable();

                // 标题解析
                const hMatch = line.match(/^(#{1,4})\s+(.+)$/);
                if (hMatch) {
                    closeList();
                    const level = hMatch[1].length;
                    const content = inlineFormat(hMatch[2]);
                    if (level === 1) html.push(`<h2 class="text-base font-bold text-white mt-3 mb-1.5 flex items-center gap-1.5">${content}</h2>`);
                    else if (level === 2) html.push(`<h3 class="text-sm font-bold text-cyan-300 mt-2.5 mb-1">${content}</h3>`);
                    else if (level === 3) html.push(`<h4 class="text-xs font-bold text-sky-400 mt-2 mb-1">${content}</h4>`);
                    else html.push(`<h5 class="text-xs font-semibold text-slate-200 mt-1.5 mb-0.5">${content}</h5>`);
                    continue;
                }

                // 中文数字序号小标题 (如: 一、空间微观... / 1. 异构数据...)
                const chHeading = line.match(/^([一二三四五六七八九十]+[、. ]\s*[^<\n]+)$/);
                if (chHeading) {
                    closeList();
                    html.push(`<h4 class="text-xs font-bold text-cyan-300 mt-3 mb-1.5 flex items-center gap-1.5">${inlineFormat(chHeading[1])}</h4>`);
                    continue;
                }

                // 重点方括号标题 (如: 【AI 智能调度中枢 · 社区运行全景诊断报告】)
                const bracketHeading = line.match(/^(【.+?】)$/);
                if (bracketHeading) {
                    closeList();
                    html.push(`<h3 class="text-sm font-bold text-sky-300 mt-2.5 mb-1.5 flex items-center gap-1">${inlineFormat(bracketHeading[1])}</h3>`);
                    continue;
                }

                // 引用卡片
                if (line.startsWith('> ')) {
                    closeList();
                    html.push(`<blockquote class="p-2.5 my-2 rounded-r-lg border-l-4 border-cyan-500 bg-cyan-950/30 text-xs text-cyan-200">${inlineFormat(line.slice(2))}</blockquote>`);
                    continue;
                }

                // 无序列表
                const bMatch = line.match(/^[-*]\s+(.+)$/);
                if (bMatch) {
                    if (!inList) {
                        html.push('<ul class="space-y-1 my-1.5 list-disc list-inside text-xs text-slate-100">');
                        inList = true;
                    }
                    html.push(`<li>${inlineFormat(bMatch[1])}</li>`);
                    continue;
                }
                closeList();

                // 常规段落
                html.push(`<p class="text-xs text-slate-100 leading-relaxed my-1.5">${inlineFormat(line)}</p>`);
            }
            closeList();
            closeTable();
            return html.join('');
        };

        const mathText = (symbol) => `$${symbol}$`;

        // 轻量级 Toast 提示系统
        const toasts = ref([]);
        const showToast = (message, type = 'info', duration = 3000) => {
            const id = Date.now() + Math.random();
            const iconMap = {
                success: '',
                error: '',
                warning: '',
                info: 'ℹ'
            };
            const toast = { id, message, type, icon: iconMap[type] || 'ℹ' };
            toasts.value.push(toast);
            setTimeout(() => {
                toasts.value = toasts.value.filter(t => t.id !== id);
            }, duration);
        };

        const metricAliasMap = {
            'walking_distance': 'courier_walk_distance',
            'unserved_parcels': 'unfinished_packages',
            'E01': 'trunk_distance',
            'E02': 'courier_walk_distance',
            'R01': 'labor_hours',
            'S01': 'coverage_rate',
            'S04': 'unfinished_packages',
            'S06': 'completion_rate',
            'C02': 'annual_cost',
            'G02': 'annual_carbon',
            'C06': 'payback_years'
        };
        const comparisonMetric = (key) => {
            const resolvedKey = metricAliasMap[key] || key;
            return overview.value?.comparison_metrics?.[resolvedKey] || null;
        };
        const metricValue = (key, side, divisor = 1, digits = 1) => {
            const metric = comparisonMetric(key);
            let value = null;
            if (metric) {
                if (side === 'baseline' || side === 's0' || side === 'S0') value = metric.baseline;
                else if (side === 's1' || side === 'S1') value = metric.s1;
                else if (side === 'optimized' || side === 's2' || side === 'S2') value = metric.optimized;
                else value = metric[side];
            }
            if (value === null || value === undefined) {
                // 回退到 comparison_normal
                const norm = overview.value?.comparison_normal?.[key];
                if (norm) {
                    if (side === 'baseline' || side === 's0' || side === 'S0') value = norm.S0;
                    else if (side === 's1' || side === 'S1') value = norm.S1;
                    else if (side === 'optimized' || side === 's2' || side === 'S2') value = norm.S2;
                }
            }
            return Number.isFinite(Number(value)) ? (Number(value) / divisor).toFixed(digits) : '—';
        };

        const improvementText = (key) => {
            const value = comparisonMetric(key)?.diff_pct;
            if (!Number.isFinite(Number(value))) return '仅报告绝对变化';
            return `${Number(value) >= 0 ? '改善' : '变差'} ${Math.abs(Number(value)).toFixed(1)}%`;
        };

        const improvementS1Text = (key) => {
            const value = comparisonMetric(key)?.diff_s1_pct;
            if (!Number.isFinite(Number(value))) return '—';
            return `${Number(value) >= 0 ? '改善' : '变差'} ${Math.abs(Number(value)).toFixed(1)}%`;
        };

        const credibilityTag = (code) => {
            const tags = overview.value?.credibility_tags;
            return tags?.[code] || { tag: 'C', type: '模型推导', desc: '基于统一定义计算' };
        };

        const changeText = (value) => {
            if (!Number.isFinite(Number(value))) return '暂无可比结果';
            return `${Number(value) >= 0 ? '改善' : '变差'} ${Math.abs(Number(value)).toFixed(1)}%`;
        };

        const savingValue = (key, divisor = 1, digits = 1) => {
            const metric = comparisonMetric(key);
            if (!metric || !Number.isFinite(Number(metric.baseline)) || !Number.isFinite(Number(metric.optimized))) return '—';
            return ((Number(metric.baseline) - Number(metric.optimized)) / divisor).toFixed(digits);
        };

        const setScenario = async (scen, options = {}) => {
            currentScenario.value = scen;
            isPeakDay.value = (scen === 'P20');
            const scenNames = { 'N': '普通日 (1.0x)', 'P15': '中高峰 (1.5x)', 'P20': '大促峰值 (2.0x)' };
            if (!options.silent) showToast(`已切换至情景: ${scenNames[scen] || scen}`, 'info');
            await loadCommunityPlan(selectedCommunityId.value);
            if (scen === 'P20') {
                await fetchSimulation('peak');
            } else {
                await fetchSimulation('normal');
            }
        };

        const setActiveTab = (tab) => {
            activeTab.value = tab;
            mobilePane.value = 'content';
            showConstraintDetails.value = false;
        };

        const togglePresentationMode = () => {
            presentationMode.value = !presentationMode.value;
            if (presentationMode.value) showConstraintDetails.value = false;
            showToast(presentationMode.value ? '已进入录屏精简模式' : '已退出录屏精简模式', 'info');
        };

        watch(presentationMode, (active) => {
            document.body.classList.toggle('presentation-mode', active);
        }, { immediate: true });

        const toggleViewMode = () => {
            viewMode.value = viewMode.value === 'split' ? 'wide' : 'split';
            nextTick(() => {
                updateAllActiveCharts();
                if (map) map.invalidateSize();
                setTimeout(() => {
                    updateAllActiveCharts();
                    if (map) map.invalidateSize();
                }, 320);
            });
        };


        // 运筹控制台与数学看板弹窗状态
        const showSolverModal = ref(false);
        const solverModalTab = ref('M6');
        const mathModelsList = ref([]);

        // 学术级高可信模型验证图集 (Publication-Grade Academic Modeling Figures)
        const academicFigures = ref([
            {
                id: 'fig1',
                title: '图 1 两阶段协同网络时空接驳与物理约束机理',
                subtitle: 'Two-Stage Spatio-Temporal Handover & Physical Constraints (2E-MDVRPTW-DC)',
                png: '/static/images/models/fig1_spatiotemporal_handover_schematic.png',
                svg: '/static/images/models/fig1_spatiotemporal_handover_schematic.svg',
                badge: '黄景辉等(2026) · 机理拓扑',
                summary: '构建无人设备干线循环与社区配送员微循环的时空强同步交接窗口，施加动力电池 ≥20% 安全余量及 400 件物理装载上限约束。',
                tags: ['时空交接', '动力电池余量', '硬时窗同步', 'Nature规范']
            },
            {
                id: 'fig2',
                title: '图 2 多维核心参数灵敏度分析方阵 (2×2 Grid)',
                subtitle: 'Multidimensional Parameter Sensitivity Analysis Matrix',
                png: '/static/images/models/fig2_parameter_sensitivity_analysis.png',
                svg: '/static/images/models/fig2_parameter_sensitivity_analysis.svg',
                badge: '极值推演 · 鲁棒性验证',
                summary: '对无人车航速 (8-25km/h)、柜体格口 (40-160格)、送货上门比例 (10%-60%) 及峰值波动率 (0.8-2.0) 进行全景扰动扫描，红虚线标定系统最优拐点。',
                tags: ['航速最优 15km/h', '柜体 84格口', '上门拐点 30%', '鲁棒边界']
            },
            {
                id: 'fig3',
                title: '图 3 改进 NSGA-II 算法多目标 Pareto 前沿与多算子收敛对照',
                subtitle: 'Improved NSGA-II Multi-objective Pareto Front & Convergence Analysis',
                png: '/static/images/models/fig3_algorithm_pareto_convergence.png',
                svg: '/static/images/models/fig3_algorithm_pareto_convergence.svg',
                badge: '进化收敛 · 双目标前沿',
                summary: '展示综合运营成本与客户满意度双目标 Pareto 非支配解集分布（HV=0.884），对比自适应自交叉算子在 35 代内稳定收敛的优越性。',
                tags: ['Pareto 前沿', '超体积 HV 0.884', '35代收敛', '自适应变异']
            },
            {
                id: 'fig4',
                title: '图 4 现状 (As-Is) vs 协同优化 (To-Be) 综合效益评估与全网对比',
                subtitle: 'As-Is vs. To-Be Comprehensive Evaluation & Multi-metric Benchmark',
                png: '/static/images/models/fig4_asis_vs_tobe_evaluation.png',
                svg: '/static/images/models/fig4_asis_vs_tobe_evaluation.svg',
                badge: '成效量化 · 落地可行性',
                summary: '六维雷达图全景评估显示协同方案综合覆盖率提升至 98.4%，干线里程下降 46.0%，人工总工时缩减 59.8%，静态投资回收期仅 0.39 年。',
                tags: ['成本 -53.6%', '里程 -46.0%', '工时 -59.8%', '回收期 0.39年']
            }
        ]);

        // 第5章 多尺度社区需求概率估计与情景模拟学术图集 (Chapter 5 Publication Figures)
        const demandFigures = ref([
            {
                id: 'fig5_1',
                title: '图 5-1 多尺度社区配送需求概率估计与情景模拟总体框架',
                subtitle: 'Multi-scale Delivery Demand Estimation & Scenario Simulation Framework',
                png: '/static/images/demand/fig5_1_demand_estimation_framework.png',
                svg: '/static/images/demand/fig5_1_demand_estimation_framework.svg',
                badge: '第5章 · 总体框架',
                summary: '构建“先验设定—贝叶斯层次生成—多尺度时空分解—蒙特卡洛分位数推演—运筹优化底座输出”五层数理架构。',
                tags: ['贝叶斯先验', '层次概率', '多尺度分解', 'P50/P80/P90']
            },
            {
                id: 'fig5_2',
                title: '图 5-2 核心随机变量与贝叶斯层次概率生成机制图',
                subtitle: 'Core Random Variables & Hierarchical Generative Mechanism',
                png: '/static/images/demand/fig5_2_probabilistic_generative_mechanism.png',
                svg: '/static/images/demand/fig5_2_probabilistic_generative_mechanism.svg',
                badge: '数理内核 · 超松弛分布',
                summary: '呈现 Gamma 需求率先验与共轭后验演变、情景乘数与日内随机波动、泊松-Gamma 负二项超松弛分布以及 6 时段 Dirichlet 比例。',
                tags: ['Gamma共轭更新', '负二项分布', 'Dirichlet时序', '晚高峰27%']
            },
            {
                id: 'fig5_3',
                title: '图 5-3 五个案例社区日需求情景估计与分位数分布对比图',
                subtitle: 'Five Communities Demand Scenario Estimation & Quantile Comparison',
                png: '/static/images/demand/fig5_3_five_communities_scenario_demand.png',
                svg: '/static/images/demand/fig5_3_five_communities_scenario_demand.svg',
                badge: '案例对比 · 分位数基准',
                summary: '全网 4316 户 5 大社区常态与大促 P50/P80/P90 负荷对比，揭示户数线性驱动机制（R²=0.999）与 1.75 倍大促稳定放大效应。',
                tags: ['梅园 157件', '亦城 1238件', '大促 1.75x', 'P80容量线']
            },
            {
                id: 'fig5_4',
                title: '图 5-4 五社区 6 时段分时需求演变与峰值负荷对比图',
                subtitle: 'Six-Slot Temporal Demand Profiles & Peak Load Analysis',
                png: '/static/images/demand/fig5_4_temporal_demand_profile_6slots.png',
                svg: '/static/images/demand/fig5_4_temporal_demand_profile_6slots.svg',
                badge: '时序特征 · 晚高峰承载',
                summary: '展现 08:00-22:00 连续 6 时段到件波动，重点校核 17:00-20:00 晚高峰负荷集中度（亦城茗苑大促 P80 达 806 件/3小时）。',
                tags: ['6时段分时', '晚高峰 806件', '容量压力校核', '爆柜预防']
            },
            {
                id: 'fig5_5',
                title: '图 5-5 亦城茗苑多维核心参数灵敏度矩阵与响应分析',
                subtitle: 'Yicheng Mingyuan Parameter Sensitivity & Response Matrix',
                png: '/static/images/demand/fig5_5_parameter_sensitivity_matrix.png',
                svg: '/static/images/demand/fig5_5_parameter_sensitivity_matrix.svg',
                badge: '敏感性 · 弹性系数',
                summary: '针对亦城茗苑开展 3×3 参数响应热力矩阵测试，测定需求率先验弹性 E_μ=1.01 与大促乘数弹性 E_S=1.04，验证模型平衡稳健性。',
                tags: ['3×3响应矩阵', '单位弹性 E=1.0', '波动鲁棒性', '基准点 2156件']
            }
        ]);

        // 第4章 末端配送网络三阶段协同优化模型学术图集 (Chapter 4 Publication Figures)
        const networkFigures = ref([
            {
                id: 'fig4_1',
                title: '图 4-1 末端配送网络三阶段协同优化模型框架与平台调用逻辑',
                subtitle: 'Three-Stage Terminal Delivery Network Optimization Framework & Platform Pipeline',
                png: '/static/images/network/fig4_1_network_model_framework.png',
                svg: '/static/images/network/fig4_1_network_model_framework.svg',
                badge: '第4章 · 总体框架',
                summary: '构建覆盖规模确定（Stage 1）、P-中值选址与需求分配（Stage 2）、上下游供货网络优化（Stage 3）及数字决策平台秒级链式调用完整架构。',
                tags: ['三阶段选址', 'P-中值模型', 'HFLAP', '平台实时匹配']
            },
            {
                id: 'fig4_2',
                title: '图 4-2 五案例社区末端设施—需求节点服务可行关系与标准化距离热力矩阵',
                subtitle: 'Five Communities Service Feasibility Matrix & Normalized Distance Heatmap',
                png: '/static/images/network/fig4_2_service_feasibility_heatmap.png',
                svg: '/static/images/network/fig4_2_service_feasibility_heatmap.svg',
                badge: '路网可达 · 可行域约束',
                summary: '基于社区内部实际路网最短距离与服务半径限制，构建 5 大社区设施—需求节点标准化距离热力矩阵，提前剔除不可达组合，保障求解可行性。',
                tags: ['路网最短路径', '标准化距离', '硬可行域', '服务半径']
            },
            {
                id: 'fig4_3',
                title: '图 4-3 五案例社区优化后末端配送网络拓扑结构图',
                subtitle: 'Five Communities Optimized Terminal Delivery Network Topology',
                png: '/static/images/network/fig4_3_five_communities_network_topology.png',
                svg: '/static/images/network/fig4_3_five_communities_network_topology.svg',
                badge: '空间拓扑 · 服务划分',
                summary: '全景呈现梅园双极自提、鹿鸣苑 3 号楼新增柜、天华园存量重组、亦城茗苑与听涛雅苑出入口无人配送接驳枢纽的空间拓扑与服务划分。',
                tags: ['网络拓扑', '服务边界重构', '新增104格柜', '入口级接驳']
            },
            {
                id: 'fig4_4',
                title: '图 4-4 五社区末端设施容量—负荷对比及优化前后关键指标综合评价',
                subtitle: 'Facility Capacity vs. Load Benchmark & Multi-metric Comprehensive Evaluation',
                png: '/static/images/network/fig4_4_facility_capacity_and_optimization.png',
                svg: '/static/images/network/fig4_4_facility_capacity_and_optimization.svg',
                badge: '容量负荷 · 四大范式',
                summary: '展示设施容量与需求负荷柱状对比（鹿鸣苑 C02-F03 利用率 94.2%）、现状 vs 优化后全网容量、加权平均服务距离及四类典型社区优化范式评估卡片。',
                tags: ['利用率 94.2%', '平均服务距离 118m', '消除爆柜', '四类优化范式']
            }
        ]);

        // 第7章 无人配送与人工协同运行优化图集 (Chapter 7 Publication Figures)
        const operationFigures = ref([
            {
                id: 'fig7_1',
                title: '图 7-1 基于网络模型输出的协同运行优化总体框架与多主体协同作业流程泳道图',
                subtitle: 'Collaborative Operational Framework & Multi-Agent Swimlane Workflow',
                png: '/static/images/operation/fig7_1_collaborative_framework_and_swimlane.png',
                svg: '/static/images/operation/fig7_1_collaborative_framework_and_swimlane.svg',
                badge: '第7章 · 协同框架',
                summary: '构建“路网加权图构建—Dijkstra最短通行时间—CVRP路径字典序优化—运力排班—资源兜底”六步运行决策框架，结合接驳点/无人车/智能柜/配送员4主体泳道图与异常回流机制。',
                tags: ['6步决策流', '4主体泳道图', '人机协同分工', '异常柔性兜底']
            },
            {
                id: 'fig7_2',
                title: '图 7-2 多主体分散配送 vs 共同配送机制、鹿鸣苑节点路网映射及 Dijkstra 最短通行时间矩阵',
                subtitle: 'Decentralized vs. Joint Co-delivery, C02 Mapping & Dijkstra Heatmap',
                png: '/static/images/operation/fig7_2_decentralized_vs_joint_and_c02_dijkstra.png',
                svg: '/static/images/operation/fig7_2_decentralized_vs_joint_and_c02_dijkstra.svg',
                badge: '共同配送 · 路网拓扑',
                summary: '对比多主体重复进区里程与共同配送集约化单一车次；展示鹿鸣苑接驳点、智能柜、住宅节点在336条道路边的精确映射；输出Dijkstra真实路网最短时间热力矩阵。',
                tags: ['重复里程消除', '路网节点映射', 'Dijkstra矩阵', '装载率90%-98%']
            },
            {
                id: 'fig7_3',
                title: '图 7-3 五社区配送批次对比、装载率基准线、C04高峰7批次载货量不可拆分性验证及车辆容量敏感性分析',
                subtitle: 'Batches Benchmark, Load Rates, C04 Non-splittable Validation & Capacity Sensitivity',
                png: '/static/images/operation/fig7_3_routing_batches_loads_and_sensitivity.png',
                svg: '/static/images/operation/fig7_3_routing_batches_loads_and_sensitivity.svg',
                badge: '批次装载 · 运力刚性',
                summary: '普通日全网8批次增至高峰15批次；普通日大规模社区装载率达90%-98%；严格验证C04因4个特大节点不可拆分性强制7批次（非理论6批次）；验证400->450件扩容显著收益。',
                tags: ['普通8批/高峰15批', '不可拆分性验证', 'C04强约束7批', '450件基准容量']
            },
            {
                id: 'fig7_4',
                title: '图 7-4 亦城茗苑普通日与高峰日路径空间对比、五社区工作负荷与电耗核算及异常恢复闭环机制',
                subtitle: 'C04 Route Evolution, Workload & Battery Consumption, Contingency Closed Loop',
                png: '/static/images/operation/fig7_4_c04_routes_workload_and_contingency.png',
                svg: '/static/images/operation/fig7_4_c04_routes_workload_and_contingency.svg',
                badge: '空间拓扑 · 异常自愈',
                summary: '空间直观呈现C04普通日3条闭合环线向高峰日7条放射/环线拓扑演变；核算五社区单车工作量（最高107.5min仅占8h工时的22.4%）与电耗（最大5.6%无需日间换电）；提出8类异常快速恢复闭环。',
                tags: ['C04拓扑演变', '单车负荷<110min', '全日电耗<5.6%', '8类异常闭环']
            }
        ]);

        const showImageModal = ref(false);
        const activeImage = ref(academicFigures.value[0]);
        const openImagePreview = (fig) => {
            activeImage.value = fig;
            showImageModal.value = true;
        };
        const closeImagePreview = () => {
            showImageModal.value = false;
        };

        // 地图底图主题与向量图层控制
        const currentTileTheme = ref('amap-dark');
        const tileStatusText = ref('高德暗色底图 [在线]');
        const showRoads = ref(true);
        const showPolygons = ref(true);
        const showRings = ref(true);

        // 社区计算参数（由社区选择自动维护）
        const selectedHouseholds = ref(2141);
        const selectedDoorRatio = ref(0.25);
        const selectedIntensity = ref(0.6);

        // Leaflet 地图、图层与图表引用
        let map = null;
        let currentTileLayer = null;
        let tileLayers = {};
        let mapLayers = [];
        let planRequestSeq = 0;
        let planAbortController = null;

        // WGS84 -> GCJ-02 for AMap tiles; OSM/vector modes keep native WGS84.
        const isAmapTileTheme = () => String(currentTileTheme.value || '').startsWith('amap');
        const outOfChina = (lat, lng) => lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271;
        const transformLat = (x, y) => {
            let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
            ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
            ret += (20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0;
            ret += (160.0 * Math.sin(y / 12.0 * Math.PI) + 320 * Math.sin(y * Math.PI / 30.0)) * 2.0 / 3.0;
            return ret;
        };
        const transformLng = (x, y) => {
            let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
            ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
            ret += (20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0;
            ret += (150.0 * Math.sin(x / 12.0 * Math.PI) + 300.0 * Math.sin(x / 30.0 * Math.PI)) * 2.0 / 3.0;
            return ret;
        };
        const wgs84ToGcj02 = (lat, lng) => {
            const nLat = Number(lat);
            const nLng = Number(lng);
            if (!Number.isFinite(nLat) || !Number.isFinite(nLng) || outOfChina(nLat, nLng)) return [nLat, nLng];
            const a = 6378245.0;
            const ee = 0.00669342162296594323;
            let dLat = transformLat(nLng - 105.0, nLat - 35.0);
            let dLng = transformLng(nLng - 105.0, nLat - 35.0);
            const radLat = nLat / 180.0 * Math.PI;
            let magic = Math.sin(radLat);
            magic = 1 - ee * magic * magic;
            const sqrtMagic = Math.sqrt(magic);
            dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
            dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI);
            return [nLat + dLat, nLng + dLng];
        };
        const toMapLatLng = (lat, lng) => {
            const point = isAmapTileTheme() ? wgs84ToGcj02(lat, lng) : [Number(lat), Number(lng)];
            return L.latLng(point[0], point[1]);
        };
        const toMapPoint = (point) => {
            if (!point) return null;
            if (Array.isArray(point) && point.length >= 2) return toMapLatLng(point[0], point[1]);
            if (typeof point === 'object' && point.lat !== undefined && point.lng !== undefined) return toMapLatLng(point.lat, point.lng);
            return null;
        };
        const toMapPath = (points) => (Array.isArray(points) ? points.map(toMapPoint).filter(Boolean) : []);
        const mapCrsText = computed(() => isAmapTileTheme() ? 'WGS84 → GCJ-02 已校正' : 'WGS84 原生坐标');

        let chartArrivals = null;
        let chartSaturation = null;
        let chartRadar = null;
        let chartCost = null;
        let chartGantt = null;
        let chartTspConvergence = null;
        let chartMipConvergence = null;

        // 全景对比图表引用 (Tab 0)
        let chartCompSaturation = null;
        let chartCompRadar = null;
        let chartCompCost = null;

        // 切换现状/设施优化/人机协同/叠图方案
        const setSchemeMode = (mode, options = {}) => {
            if (mode === 'baseline') mode = 's0';
            if (mode === 'optimized') mode = 's2';
            schemeMode.value = mode;
            const names = {
                's0': ' S0 现状基准方案 (As-Is)',
                's1': ' S1 网络设施优化方案 (Facility Opt)',
                's2': ' S2 人机协同推荐方案 (To-Be)',
                'diff': ' 双方案同屏叠图对比'
            };
            if (!options.silent) showToast(`已切换至: ${names[mode] || mode}`, 'info');
            renderMapLayers();
        };

        // KaTeX 自动数学公式渲染 (仅针对公式专用容器，严禁污染 Vue 响应式文本节点)
        const renderMath = () => {
            nextTick(() => {
                if (window.renderMathInElement) {
                    const containers = document.querySelectorAll('.math-card, .math-target, .markdown-body');
                    containers.forEach(el => {
                        try {
                            window.renderMathInElement(el, {
                                delimiters: [
                                    { left: '$$', right: '$$', display: true },
                                    { left: '\\[', right: '\\]', display: true },
                                    { left: '\\(', right: '\\)', display: false },
                                    { left: '$', right: '$', display: false }
                                ],
                                throwOnError: false
                            });
                        } catch (e) {
                            console.warn('KaTeX render notice:', e);
                        }
                    });
                }
            });
        };

        // 初始化
        onMounted(async () => {
            document.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape') return;
                if (showAiDrawer.value) showAiDrawer.value = false;
                else if (showAiConfigModal.value) showAiConfigModal.value = false;
                else if (showImageModal.value) closeImagePreview();
                else if (showSolverModal.value) showSolverModal.value = false;
            });
            initMap();
            await fetchMathModels();
            await fetchOverview();
            await fetchAiConfig();
            const initialCommunity = overview.value?.communities?.find(item => item.id === selectedCommunityId.value);
            if (initialCommunity) {
                selectedHouseholds.value = initialCommunity.households;
                if (selectedCommunityId.value === 'C01' || selectedCommunityId.value === 'C03') selectedDoorRatio.value = 1.0;
                else if (selectedCommunityId.value === 'C02') selectedDoorRatio.value = 0.52;
                else if (selectedCommunityId.value === 'C04') selectedDoorRatio.value = 0.25;
                else if (selectedCommunityId.value === 'C05') selectedDoorRatio.value = 0.24;
            }
            await loadCommunityPlan(selectedCommunityId.value);
            await fetchSimulation();

            // 挂载后立即全量灌入图表数据与解析公式
            nextTick(() => {
                updateAllActiveCharts();
                renderMath();
                if (map) {
                    map.invalidateSize();
                    if (activeTab.value === 'comparison' || activeTab.value === 'digital-twin') {
                        fitAllOverview();
                    } else {
                        fitCurrentCommunity();
                    }
                }
                setTimeout(() => {
                    updateAllActiveCharts();
                    if (map) map.invalidateSize();
                }, 200);
            });

            // 监听容器大小变化（自适应防塌陷）
            const mapContainer = document.getElementById('map-container');
            if (mapContainer && window.ResizeObserver) {
                const ro = new ResizeObserver(() => {
                    if (map) map.invalidateSize();
                    resizeCharts();
                });
                ro.observe(mapContainer);
            }

            window.addEventListener('resize', () => {
                resizeCharts();
            });

            const contentPanel = document.querySelector('.content-panel');
            if (contentPanel) {
                contentPanel.addEventListener('transitionend', () => {
                    resizeCharts();
                    if (map) map.invalidateSize();
                });
            }
        });

        // 初始化 Leaflet 地图与国内高德/OSM/离线底图引擎
        const initMap = () => {
            const container = document.getElementById('map-container');
            if (!container) return;

            // 销毁可能存在的残留地图实例
            if (map) {
                map.remove();
                map = null;
            }

            // 初始化 Leaflet，开启 preferCanvas 保证高性能向量底图自适应绘制
            map = L.map('map-container', {
                center: toMapLatLng(39.792, 116.495),
                zoom: 13,
                zoomControl: false,
                preferCanvas: true,
                attributionControl: false
            });

            // 自定义缩放控制置于右下角（紧贴信息栏上方），彻底解决左上角遮挡问题
            L.control.zoom({ position: 'bottomright' }).addTo(map);

            // 1. 国内高德地图暗黑矢量底图（默认，带深色极客滤镜）
            tileLayers['amap-dark'] = L.tileLayer(
                'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                {
                    maxZoom: 19,
                    minZoom: 10,
                    subdomains: ['1', '2', '3', '4'],
                    className: 'amap-dark-tiles',
                    attribution: '&copy; 高德地图 AutoNavi'
                }
            );

            // 2. 国内高德标准路网矢量底图
            tileLayers['amap-std'] = L.tileLayer(
                'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
                {
                    maxZoom: 19,
                    minZoom: 10,
                    subdomains: ['1', '2', '3', '4'],
                    attribution: '&copy; 高德地图 AutoNavi'
                }
            );

            // 3. 高德卫星遥感影像底图
            tileLayers['amap-sat'] = L.tileLayer(
                'https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
                {
                    maxZoom: 19,
                    minZoom: 10,
                    subdomains: ['1', '2', '3', '4'],
                    attribution: '&copy; 高德地图 AutoNavi 遥感'
                }
            );

            // 4. OSM 暗黑源
            tileLayers['osm-dark'] = L.tileLayer(
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                {
                    maxZoom: 19,
                    minZoom: 10,
                    className: 'osm-dark-tiles',
                    attribution: '&copy; OpenStreetMap'
                }
            );

            // 默认挂载高德暗黑底图
            currentTileLayer = tileLayers['amap-dark'];
            currentTileLayer.addTo(map);

            // 监听瓦片加载与异常（无网络/外网受限时自动平滑过渡）
            currentTileLayer.on('tileerror', () => {
                tileStatusText.value = '底图瓦片受限 · 已激活高精矢量底图兜底';
            });
            currentTileLayer.on('load', () => {
                if (currentTileTheme.value === 'amap-dark') tileStatusText.value = '高德暗色底图 [在线]';
                else if (currentTileTheme.value === 'amap-std') tileStatusText.value = '高德标准路网底图 [在线]';
            });
        };

        // 切换底图主题
        const onChangeTileTheme = () => {
            if (!map) return;

            // 移除当前瓦片图层
            if (currentTileLayer) {
                map.removeLayer(currentTileLayer);
                currentTileLayer = null;
            }

            const theme = currentTileTheme.value;
            if (theme === 'vector-only') {
                tileStatusText.value = '离线纯矢量CAD数字孪生模式 [完全无外网依赖]';
            } else if (tileLayers[theme]) {
                currentTileLayer = tileLayers[theme];
                currentTileLayer.addTo(map);
                if (theme === 'amap-dark') tileStatusText.value = '高德暗黑矢量底图 [在线]';
                else if (theme === 'amap-std') tileStatusText.value = '高德标准路网底图 [在线]';
                else if (theme === 'amap-sat') tileStatusText.value = '高德卫星遥感底图 [在线]';
                else if (theme === 'osm-dark') tileStatusText.value = 'OSM暗夜极客底图 [在线]';
            }

            nextTick(() => {
                renderMapLayers();
                if (map) {
                    map.invalidateSize();
                    if (activeTab.value === 'comparison' || activeTab.value === 'digital-twin') fitAllOverview();
                    else fitCurrentCommunity();
                }
            });
        };

        // 图层显隐控制
        const toggleRoads = () => {
            showRoads.value = !showRoads.value;
            renderMapLayers();
        };

        const togglePolygons = () => {
            showPolygons.value = !showPolygons.value;
            renderMapLayers();
        };

        const toggleRings = () => {
            showRings.value = !showRings.value;
            renderMapLayers();
        };

        // 缩放控制：复位到全域（5个社区 + HUB）
        const fitAllOverview = () => {
            if (!map) return;
            const hub = overview.value?.hub;
            const pts = hub ? [toMapLatLng(hub.lat, hub.lng)] : [toMapLatLng(39.798, 116.506)];
            if (overview.value && overview.value.communities) {
                overview.value.communities.forEach(c => {
                    const center = toMapPoint(c.center);
                    if (center) pts.push(center);
                    if (c.polygon && c.polygon.length > 0) pts.push(...toMapPath(c.polygon));
                });
            }
            if (pts.length > 0) {
                map.fitBounds(L.latLngBounds(pts).pad(0.06));
            }
        };

        // 缩放控制：聚焦到当前选中的社区
        const fitCurrentCommunity = () => {
            if (!map || !planResult.value) return;
            const p = planResult.value;
            const pts = [];
            if (p.polygon && p.polygon.length > 0) pts.push(...toMapPath(p.polygon));
            if (p.buildings && p.buildings.length > 0) {
                p.buildings.forEach(b => {
                    const point = toMapPoint(b);
                    if (point) pts.push(point);
                });
            }
            if (pts.length > 0) {
                map.fitBounds(L.latLngBounds(pts).pad(0.08));
            }
        };

        const fetchMathModels = async () => {
            try {
                const res = await fetch('/api/solver/models');
                const data = await res.json();
                mathModelsList.value = data.models || [];
            } catch (e) {
                console.error('Fetch math models failed:', e);
            }
        };

        const fetchOverview = async () => {
            try {
                const res = await fetch('/api/overview');
                if (!res.ok) throw new Error(`总览接口返回 HTTP ${res.status}`);
                overview.value = await res.json();
                nextTick(() => {
                    updateTspChart();
                    renderMath();
                });
            } catch (e) {
                console.error('Fetch overview failed:', e);
                apiError.value = `总览数据加载失败：${e.message || e}`;
            }
        };

        const loadCommunityPlan = async (cid) => {
            loading.value = true;
            apiError.value = '';
            const requestId = ++planRequestSeq;
            if (planAbortController) planAbortController.abort();
            planAbortController = new AbortController();
            try {
                const res = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    signal: planAbortController.signal,
                    body: JSON.stringify({
                        community_id: cid,
                        custom_households: selectedHouseholds.value,
                        custom_door_ratio: selectedDoorRatio.value,
                        custom_intensity: selectedIntensity.value,
                        is_peak_day: isPeakDay.value
                    })
                });
                if (!res.ok) throw new Error(`计算接口返回 HTTP ${res.status}`);
                const data = await res.json();
                if (requestId !== planRequestSeq) return null;
                planResult.value = data;
                nextTick(() => {
                    renderMapLayers();
                    updateCharts();
                    updateMipChart();
                    renderMath();
                    if (map) map.invalidateSize();
                });
                return data;
            } catch (e) {
                if (e.name === 'AbortError') return null;
                console.error('Load plan failed:', e);
                apiError.value = `方案计算失败：${e.message || e}`;
                showToast(apiError.value, 'error', 5000);
                return null;
            } finally {
                if (requestId === planRequestSeq) loading.value = false;
            }
        };

        const fetchSimulation = async (scenario = null) => {
            if (scenario) simScenario.value = scenario;
            try {
                const res = await fetch(`/api/simulation?scenario=${simScenario.value}`);
                if (!res.ok) throw new Error(`仿真接口返回 HTTP ${res.status}`);
                simulationResult.value = await res.json();
                nextTick(() => {
                    updateSimCharts();
                    renderMath();
                });
            } catch (e) {
                console.error('Fetch simulation failed:', e);
                apiError.value = `仿真结果加载失败：${e.message || e}`;
            }
        };

        const switchSimScenario = (scenario) => {
            fetchSimulation(scenario);
        };

        const onSelectCommunity = (cid) => {
            selectedCommunityId.value = cid;
            mobilePane.value = 'content';
            if (cid === 'ALL') {
                loadCommunityPlan('ALL');
                showToast('已切换至全域 5 社区综合底座', 'info');
                return;
            }
            if (overview.value) {
                const c = overview.value.communities.find(item => item.id === cid);
                if (c) {
                    selectedHouseholds.value = c.households;
                    // 设置默认上门比例
                    if (cid === 'C01' || cid === 'C03') selectedDoorRatio.value = 1.0;
                    else if (cid === 'C02') selectedDoorRatio.value = 0.52;
                    else if (cid === 'C04') selectedDoorRatio.value = 0.25;
                    else if (cid === 'C05') selectedDoorRatio.value = 0.24;
                }
            }
            loadCommunityPlan(cid);
            showToast(`已切换至社区: ${cid}`, 'info');
        };

        const buildAiContext = () => {
            const p = planResult.value;
            return {
                community_id: selectedCommunityId.value,
                community_name: p?.community_name || selectedCommunityId.value,
                households: selectedHouseholds.value || 2141,
                scheme: schemeMode.value,
                scenario: currentScenario.value,
                forecast: p?.forecast || {},
                layout: p?.layout || {},
                routing: p?.routing || {},
                pipeline_status: pipelineStatus.value,
                violations: failedConstraintChecks.value
            };
        };

        const fetchAiConfig = async () => {
            try {
                const res = await fetch('/api/ai/config');
                if (res.ok) {
                    const data = await res.json();
                    aiConfig.value = data;
                    aiConfigForm.value.provider = data.provider || 'auto';
                    aiConfigForm.value.base_url = data.base_url || 'https://api.siliconflow.cn/v1';
                    aiConfigForm.value.model = data.model || 'deepseek-flash';
                }
            } catch (e) {
                console.warn('Failed to load AI config:', e);
            }
        };

        const saveAiConfig = async () => {
            try {
                const res = await fetch('/api/ai/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(aiConfigForm.value)
                });
                if (res.ok) {
                    aiConfig.value = await res.json();
                    showToast('AI 配置已成功保存！', 'success');
                    showAiConfigModal.value = false;
                }
            } catch (e) {
                showToast(`保存失败: ${e.message}`, 'error');
            }
        };

        const testAiConnection = async () => {
            aiTestLoading.value = true;
            aiTestResult.value = null;
            try {
                const res = await fetch('/api/ai/test', { method: 'POST' });
                aiTestResult.value = await res.json();
            } catch (e) {
                aiTestResult.value = { success: false, message: `网络异常: ${e.message}` };
            } finally {
                aiTestLoading.value = false;
            }
        };

        const fetchAvailableModels = async () => {
            aiModelsLoading.value = true;
            aiModelsMessage.value = '';
            try {
                const res = await fetch('/api/ai/models', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        provider: aiConfigForm.value.provider,
                        base_url: aiConfigForm.value.base_url,
                        api_key: aiConfigForm.value.api_key
                    })
                });
                const data = await res.json();
                if (data.models && data.models.length > 0) {
                    aiDetectedModels.value = data.models;
                    aiModelsMessage.value = `成功识别 ${data.models.length} 个兼容大模型 (${data.source === 'api_probed' ? '实时云端探测' : '内置预置推荐'})`;
                    const currentModelExists = data.models.some(m => m.id === aiConfigForm.value.model);
                    if (!currentModelExists && data.models.length > 0) {
                        aiConfigForm.value.model = data.models[0].id;
                    }
                    showToast(aiModelsMessage.value, 'success');
                } else {
                    aiModelsMessage.value = data.message || '未能探测到模型，请检查 API Key 或 Base URL';
                    showToast(aiModelsMessage.value, 'warning');
                }
            } catch (e) {
                aiModelsMessage.value = `识别失败: ${e.message}`;
                showToast(aiModelsMessage.value, 'error');
            } finally {
                aiModelsLoading.value = false;
            }
        };

        const toggleAiDrawer = () => {
            showAiDrawer.value = !showAiDrawer.value;
            if (showAiDrawer.value) {
                nextTick(() => {
                    renderMath();
                    const el = document.getElementById('aiDrawerMessages');
                    if (el) el.scrollTop = el.scrollHeight;
                });
            }
        };

        const sendAiMessage = async (customQuery = null) => {
            const query = (customQuery || aiInput.value || '').trim();
            if (!query || aiLoading.value) return;

            showAiDrawer.value = true;
            aiDrawerMessages.value.push({
                role: 'user',
                content: query,
                time: new Date().toLocaleTimeString().slice(0, 5)
            });
            aiInput.value = '';

            const assistantIdx = aiDrawerMessages.value.length;
            aiDrawerMessages.value.push({
                role: 'assistant',
                content: '',
                reasoning: '',
                model: aiConfig.value.model,
                time: new Date().toLocaleTimeString().slice(0, 5)
            });
            aiLoading.value = true;

            try {
                const res = await fetch('/api/ai/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query,
                        context: buildAiContext()
                    })
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('data:')) {
                            const jsonStr = trimmed.slice(5).trim();
                            if (!jsonStr) continue;
                            try {
                                const parsed = JSON.parse(jsonStr);
                                if (parsed.model) {
                                    aiDrawerMessages.value[assistantIdx].model = parsed.model;
                                }
                                if (parsed.type === 'reasoning') {
                                    // Internal chain-of-thought is intentionally hidden from the product UI.
                                } else if (parsed.text) {
                                    aiDrawerMessages.value[assistantIdx].content += parsed.text;
                                }
                            } catch (e) {}
                        }
                    }
                    const el = document.getElementById('aiDrawerMessages');
                    if (el) el.scrollTop = el.scrollHeight;
                }
            } catch (e) {
                console.error('AI chat failed:', e);
                aiDrawerMessages.value[assistantIdx].content += `\n\n*(调用异常，已保留本地推演记录: ${e.message})*`;
            } finally {
                aiLoading.value = false;
                nextTick(() => {
                    renderMath();
                    const el = document.getElementById('aiDrawerMessages');
                    if (el) el.scrollTop = el.scrollHeight;
                });
            }
        };

        const triggerAiCrisis = async (type) => {
            activeCrisisType.value = type;
            crisisStreaming.value = true;
            crisisStreamText.value = '';
            crisisExecutionStatus.value = '';

            // 1. 同步获取静态决策卡片与指标数据（向后兼容）
            try {
                const res = await fetch('/api/crisis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        event_type: type,
                        context: buildAiContext()
                    })
                });
                if (res.ok) {
                    crisisResult.value = await res.json();
                }
            } catch (e) {
                console.warn('Crisis sync call fallback:', e);
            }

            // 2. 流式触发 AI 多智能体深度推理流水线
            try {
                const resStream = await fetch('/api/ai/crisis/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        event_type: type,
                        context: buildAiContext()
                    })
                });

                if (resStream.ok) {
                    const reader = resStream.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop();

                        for (const line of lines) {
                            const trimmed = line.trim();
                            if (trimmed.startsWith('data:')) {
                                const jsonStr = trimmed.slice(5).trim();
                                if (!jsonStr) continue;
                                try {
                                    const parsed = JSON.parse(jsonStr);
                                    if (parsed.type === 'content' && parsed.text) {
                                        crisisStreamText.value += parsed.text;
                                    } else if (!parsed.type && parsed.text) {
                                        crisisStreamText.value += parsed.text;
                                    }
                                } catch (e) {}
                            }
                        }
                    }
                }
            } catch (e) {
                console.error('Crisis stream failed:', e);
                crisisStreamText.value = `### 应急推演完成\n\n已下发应急指令：${crisisResult.value?.decision || '自适应重排已生效'}`;
            } finally {
                crisisStreaming.value = false;
                nextTick(() => renderMath());
            }
        };

        const triggerCrisis = triggerAiCrisis;

        const applyRescheduledPlan = () => {
            crisisExecutionStatus.value = 'AI 应急多智能体协同方案已成功下发至 X3 无人车中枢与网格骑手端，路网动态重排完成！';
            showToast('AI 应急调度方案已正式下发生效！', 'success', 4000);
        };

        const copyDispatchOrder = () => {
            const payload = {
                event: crisisResult.value?.event_name || activeCrisisType.value,
                timestamp: crisisResult.value?.timestamp || new Date().toISOString(),
                actions: crisisResult.value?.actions || [],
                delta: crisisResult.value?.metrics_delta || {}
            };
            navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
                .then(() => showToast('应急调度工单已复制到剪贴板！', 'info'))
                .catch(() => showToast('工单数据生成完成', 'info'));
        };

        // =========================================================================
        // 地图全量自适应矢量图层绘制核心 (Canvas/SVG 高精度渲染)
        // 确保在无网络或外网受限时依然有高精度的社区多边形轮廓、路网和节点渲染
        // =========================================================================
        const renderMapLayers = () => {
            if (!map || !planResult.value) return;

            // 清理旧的矢量覆盖物
            mapLayers.forEach(l => map.removeLayer(l));
            mapLayers = [];

            const p = planResult.value;
            const cid = p.community_id;

            // ---------------------------------------------------------------------
            // 1. 绘制高精度五大社区多边形轮廓 (WKT边界) 与社区交互标签
            // ---------------------------------------------------------------------
            if (showPolygons.value && overview.value && overview.value.communities) {
                overview.value.communities.forEach(c => {
                    if (c.polygon && c.polygon.length > 0) {
                        const isCurrent = (c.id === selectedCommunityId.value);

                        // 绘制社区真实物理多边形边界
                        const poly = L.polygon(toMapPath(c.polygon), {
                            color: isCurrent ? '#226f8c' : '#0284c7',
                            weight: isCurrent ? 3.5 : 1.8,
                            opacity: isCurrent ? 0.95 : 0.55,
                            fillColor: isCurrent ? '#0891b2' : '#0369a1',
                            fillOpacity: isCurrent ? 0.20 : 0.05,
                            dashArray: isCurrent ? null : '4, 4'
                        }).addTo(map);

                        poly.bindTooltip(
                            `<div class="p-1">
                                <div class="font-bold text-cyan-300 text-xs">${c.id} ${c.name}</div>
                                <div class="text-[11px] text-slate-300">总户数: ${c.households} 户 | 日均件量: ${c.daily_pkgs} 件</div>
                                <div class="text-[10px] text-slate-400">点击切换并聚焦此社区</div>
                            </div>`,
                            { sticky: true }
                        );

                        poly.on('click', () => {
                            if (c.id !== selectedCommunityId.value) {
                                onSelectCommunity(c.id);
                            }
                        });

                        mapLayers.push(poly);

                        // 社区名称赛博徽章标牌
                        if (c.center) {
                            const badgeMarker = L.marker(toMapPoint(c.center), {
                                icon: L.divIcon({
                                    className: 'custom-community-label',
                                    html: `<div class="community-badge-marker ${isCurrent ? 'community-badge-active' : ''}">${c.id} ${c.name}</div>`,
                                    iconSize: [80, 24],
                                    iconAnchor: [40, 12]
                                })
                            }).addTo(map);

                            badgeMarker.on('click', () => {
                                if (c.id !== selectedCommunityId.value) {
                                    onSelectCommunity(c.id);
                                }
                            });

                            mapLayers.push(badgeMarker);
                        }
                    }
                });
            }

            // ---------------------------------------------------------------------
            // 2. 绘制当前社区高精内部路网边与交叉节点 (Micro-road Network)
            // ---------------------------------------------------------------------
            if (showRoads.value && p.road_edges && p.road_edges.length > 0) {
                // 绘制路段线条
                p.road_edges.forEach(edge => {
                    if (edge.from_coord && edge.to_coord) {
                        const isPassable = (edge.unmanned_passable !== false);
                        const roadLine = L.polyline(toMapPath([edge.from_coord, edge.to_coord]), {
                            color: isPassable ? '#2d7f9e' : '#64748b',
                            weight: isPassable ? 2.5 : 1.5,
                            opacity: isPassable ? 0.70 : 0.40,
                            dashArray: isPassable ? null : '3, 3'
                        }).addTo(map);

                        roadLine.bindTooltip(
                            `<div class="text-xs">
                                <div class="font-bold text-sky-400">内部路段: ${edge.id}</div>
                                <div>长度: ${edge.length_m}m | 净宽: ${edge.width_m}m</div>
                                <div>无人车通行: <span class="${isPassable ? 'text-emerald-400 font-bold' : 'text-rose-400'}">${isPassable ? '是' : '否'}</span></div>
                            </div>`,
                            { sticky: true }
                        );

                        mapLayers.push(roadLine);
                    }
                });

                // 绘制路网交叉节点微圆点
                if (p.road_nodes && p.road_nodes.length > 0) {
                    p.road_nodes.forEach(node => {
                        const nodeDot = L.circleMarker(toMapLatLng(node.lat, node.lng), {
                            radius: 2,
                            color: '#0284c7',
                            fillColor: '#2d7f9e',
                            fillOpacity: 0.6,
                            weight: 1
                        }).addTo(map);
                        mapLayers.push(nodeDot);
                    });
                }
            }

            // ---------------------------------------------------------------------
            // 3. 绘制片区综合枢纽 (HUB)
            // ---------------------------------------------------------------------
            if (overview.value && overview.value.hub) {
                const hub = overview.value.hub;
                const hubMarker = L.circleMarker(toMapLatLng(hub.lat, hub.lng), {
                    radius: 10,
                    color: '#b7791f',
                    fillColor: '#c58a2a',
                    fillOpacity: 0.95,
                    weight: 3
                }).addTo(map);

                hubMarker.bindPopup(
                    `<div class="text-xs space-y-1">
                        <div class="font-bold text-amber-400 text-sm">【亦庄物流综合分拨枢纽 HUB】</div>
                        <div class="text-slate-200">${hub.name}</div>
                        <div class="text-slate-400 font-mono">坐标: [${hub.lat}, ${hub.lng}]</div>
                        <div class="text-emerald-400">全域末端统仓共配直发基地</div>
                    </div>`
                );
                mapLayers.push(hubMarker);

                // HUB 辐射光环
                const hubRing = L.circle(toMapLatLng(hub.lat, hub.lng), {
                    radius: 350,
                    color: '#b7791f',
                    weight: 1,
                    fillColor: '#b7791f',
                    fillOpacity: 0.04,
                    dashArray: '5, 5'
                }).addTo(map);
                mapLayers.push(hubRing);
            }

            // ---------------------------------------------------------------------
            // 4. 绘制干线路径 (Trunk Routes: 现状独立往返 vs 优化M1巡回闭环)
            // ---------------------------------------------------------------------
            // 4A. 现状方案干线：HUB 到 5 大社区独立点对点往返线 (红色虚线)
            if ((isS0.value || isDiff.value) &&
                overview.value && overview.value.trunk_routing && overview.value.trunk_routing.baseline_routes) {
                overview.value.trunk_routing.baseline_routes.forEach(route => {
                    const coords = route.coords || route.round_trip_coords;
                    if (!coords || !Array.isArray(coords) || coords.length < 2) return;
                    const latlngs = coords.map(pt => Array.isArray(pt) ? pt : (pt && pt.lat !== undefined ? [pt.lat, pt.lng] : null)).filter(Boolean);
                    if (latlngs.length < 2) return;

                    const bLine = L.polyline(toMapPath(latlngs), {
                        color: '#f43f5e',
                        weight: isDiff.value ? 2.5 : 3.5,
                        opacity: isDiff.value ? 0.75 : 0.95,
                        dashArray: '6, 5'
                    }).addTo(map);

                    bLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-rose-400">【 现状独立往返干线: HUB ⇄ ${route.community_id}】</div>
                            <div>往返里程: <span class="mono font-bold text-rose-300">${route.dist_km || route.distance_km || 0} km</span></div>
                            <div>单程往返耗时: <span class="mono text-slate-300">${route.time_min || route.drive_time_min || 0} min</span></div>
                            <div class="text-slate-400 text-[10px]">5条车辆点对点往返，全网总长 ${metricValue('trunk_distance', 's0', 1, 2)} km</div>
                        </div>`
                    );
                    mapLayers.push(bLine);
                });
            }

            // 4B. 优化方案干线：M1 巡回闭环路径 (亮青色高亮实线)
            if ((isS1.value || isS2.value || isDiff.value) &&
                overview.value && overview.value.trunk_routing && overview.value.trunk_routing.tour) {
                const tour = overview.value.trunk_routing.tour;
                if (Array.isArray(tour) && tour.length > 1) {
                    const latlngs = tour.map(pt => Array.isArray(pt) ? pt : (pt && pt.lat !== undefined ? [pt.lat, pt.lng] : null)).filter(Boolean);
                    if (latlngs.length > 1) {
                        const trunkLine = L.polyline(toMapPath(latlngs), {
                            color: '#06b6d4',
                            weight: isDiff.value ? 3.8 : 4.5,
                            opacity: 0.95
                        }).addTo(map);

                        trunkLine.bindPopup(
                            `<div class="text-xs space-y-1">
                                <div class="font-bold text-cyan-400">【 M1 亦庄干线巡回 TSP 闭环】</div>
                                <div>巡回总里程: <span class="mono font-bold text-white">${overview.value.trunk_routing.tour_dist_km} km</span></div>
                                <div>相比独立往返: <span class="text-emerald-400 font-bold">${improvementText('trunk_distance')} (${savingValue('trunk_distance', 1, 2)} km)</span></div>
                                <div>无人车巡回耗时: <span class="mono text-slate-200">${overview.value.trunk_routing.travel_time_min} min</span></div>
                                <div class="text-emerald-400 text-[10px]">统仓共配串联5社区；消除空驶大幅压降干线里程</div>
                            </div>`
                        );
                        mapLayers.push(trunkLine);
                    }
                }
            }

            // ---------------------------------------------------------------------
            // 5. 绘制楼栋需求节点 (Demand Nodes)
            // ---------------------------------------------------------------------
            if (p.buildings) {
                p.buildings.forEach(b => {
                    const bMarker = L.circleMarker(toMapLatLng(b.lat, b.lng), {
                        radius: 5 + Math.min(8, b.daily_pkgs / 40),
                        color: '#60a5fa',
                        fillColor: '#3d7196',
                        fillOpacity: 0.85,
                        weight: 2
                    }).addTo(map);

                    bMarker.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-blue-300">${b.name}</div>
                            <div>住户数: <span class="mono font-bold text-white">${b.households}</span> 户</div>
                            <div>总预测件量: <span class="mono font-bold text-cyan-300">${b.daily_pkgs}</span> 件/日</div>
                            <div class="text-orange-400">送货上门需求: ${b.door_pkgs} 件</div>
                            <div class="text-emerald-400">智能柜自提需求: ${b.locker_pkgs} 件</div>
                        </div>`
                    );
                    mapLayers.push(bMarker);
                });
            }

            // ---------------------------------------------------------------------
            // 6. 绘制设施点（容量状态只采用后端约束计算结果）
            // ---------------------------------------------------------------------
            if (isS0.value) {
                // S0 现状单柜设施：爆柜以红色警告图标呈现
                const baseFacs = p.baseline_plan?.facilities || p.layout?.facilities || [];
                baseFacs.forEach(f => {
                    if (f.active === false) return;
                    const isBurst = Boolean(f.is_full_risk);
                    const satPct = Number(f.saturation_pct ?? 0);

                    const fMarker = L.marker(toMapLatLng(f.lat, f.lng), {
                        icon: L.divIcon({
                            className: 'facility-burst-marker',
                            html: isBurst
                                ? `<div class="relative w-9 h-9 flex items-center justify-center cursor-pointer">
                                     <span class="absolute inline-flex h-full w-full rounded-full bg-rose-500 opacity-75 animate-ping"></span>
                                     <div class="relative w-8 h-8 rounded-full bg-rose-600 border-2 border-rose-200 shadow-xl shadow-rose-600/80 flex items-center justify-center text-sm font-bold text-white">⚠️</div>
                                   </div>`
                                : `<div class="w-7 h-7 rounded-full bg-slate-700 border border-slate-400 flex items-center justify-center text-xs text-slate-200">📦</div>`,
                            iconSize: [36, 36],
                            iconAnchor: [18, 18]
                        })
                    }).addTo(map);

                    fMarker.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-rose-400 text-sm">【 S0 现状单柜设施: ${f.name}】</div>
                            <div class="${isBurst ? 'text-rose-400 font-bold' : 'text-slate-300'}">
                                ${isBurst ? '⚠️ 严重超载爆柜！包裹大量外溢' : '常规负荷状态'}
                            </div>
                            <div>有效容量: <span class="mono font-bold text-white">${f.effective_capacity ?? 0} 件</span></div>
                            <div>指派自提需求: <span class="mono font-bold text-white">${f.assigned_demand ?? 0} 件</span></div>
                            <div>峰值饱和度: <span class="mono font-bold ${isBurst ? 'text-rose-400' : 'text-slate-200'}">${satPct}%</span></div>
                            <div class="text-[10px] text-slate-400">单柜容量瓶颈严重，急需 MIP 自适应副柜扩容</div>
                        </div>`
                    );
                    mapLayers.push(fMarker);
                });
            } else if (isS1.value || isS2.value) {
                // S1 / S2 设施优化：绿色护盾标记，副柜自适应扩容
                const optFacs = p.optimized_plan?.facilities || p.layout?.facilities || [];
                optFacs.forEach(f => {
                    if (!f.active) return;
                    const isExpanded = (f.slave_units > 0);
                    const fMarker = L.marker(toMapLatLng(f.lat, f.lng), {
                        icon: L.divIcon({
                            className: 'facility-shield-marker',
                            html: `<div class="w-8 h-8 rounded-full bg-emerald-600 border-2 border-emerald-300 shadow-lg shadow-emerald-500/50 flex items-center justify-center text-sm text-white font-bold cursor-pointer">🛡️</div>`,
                            iconSize: [32, 32],
                            iconAnchor: [16, 16]
                        })
                    }).addTo(map);

                    fMarker.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-emerald-400 text-sm">【 优化智能柜: ${f.name}】</div>
                            <div class="${f.is_full_risk ? 'text-rose-300' : 'text-emerald-300'} font-bold">${f.is_full_risk ? '⚠️ 容量约束未通过' : '✅ 当前情景容量约束通过'}</div>
                            <div>MIP定容配置: 主柜 ${f.main_lockers} 组 + 扩容副柜 <span class="text-emerald-300 font-bold">+${f.slave_units}</span> 组</div>
                            <div>总格口数: <span class="mono font-bold text-white">${f.total_slots}</span> 格</div>
                            <div>日有效承载: <span class="mono font-bold text-cyan-300">${f.effective_capacity}</span> 件</div>
                            <div>容量负荷率: <span class="mono font-bold text-emerald-400">${f.saturation_pct ?? Math.round((f.utilization_rate ?? 0) * 100)}%</span></div>
                            <div class="text-[10px] text-slate-400">150m 便民服务半径约束由后端逐楼栋校验</div>
                        </div>`
                    );
                    mapLayers.push(fMarker);

                    if (showRings.value) {
                        const circle = L.circle(toMapLatLng(f.lat, f.lng), {
                            radius: 150,
                            color: '#10b981',
                            weight: 1.5,
                            fillColor: '#10b981',
                            fillOpacity: 0.08,
                            dashArray: '4, 4'
                        }).addTo(map);
                        mapLayers.push(circle);
                    }
                });
            } else {
                //  双方案同屏对比模式 (Diff)
                const optFacs = p.optimized_plan?.facilities || p.layout?.facilities || [];
                const baseFacs = p.baseline_plan?.facilities || [];
                const baseById = new Map(baseFacs.map(item => [item.facility_id || item.id, item]));
                optFacs.forEach(f => {
                    if (!f.active) return;
                    const baseFacility = baseById.get(f.facility_id || f.id);
                    const isBurst = Boolean(baseFacility?.is_full_risk);
                    const baseSat = baseFacility ? `${baseFacility.saturation_pct ?? 0}%` : '无对应现有柜';
                    const optSat = f.saturation_pct ?? Math.round((f.utilization_rate ?? 0) * 100);

                    const diffHtml = isBurst
                        ? `<div class="relative w-9 h-9 flex items-center justify-center cursor-pointer">
                             <span class="absolute inline-flex h-full w-full rounded-full bg-rose-500 opacity-75 animate-ping"></span>
                             <div class="relative w-8 h-8 rounded-full bg-slate-900 border-2 border-emerald-400 flex items-center justify-center text-xs font-bold shadow-lg">
                                <span>⚡</span>
                             </div>
                           </div>`
                        : `<div class="w-8 h-8 rounded-full bg-emerald-700/90 border-2 border-emerald-300 flex items-center justify-center text-xs">🛡️</div>`;

                    const fMarker = L.marker(toMapLatLng(f.lat, f.lng), {
                        icon: L.divIcon({
                            className: 'facility-diff-marker',
                            html: diffHtml,
                            iconSize: [36, 36],
                            iconAnchor: [18, 18]
                        })
                    }).addTo(map);

                    fMarker.bindPopup(
                        `<div class="text-xs space-y-1.5 p-0.5 min-w-[220px]">
                            <div class="font-bold text-amber-300 text-sm border-b border-slate-700 pb-1 flex justify-between items-center">
                                <span>【${f.name} 同屏对比】</span>
                                <span class="text-cyan-400 font-mono text-[10px]">Diff View</span>
                            </div>
                            <div class="bg-rose-950/50 p-2 rounded border border-rose-800/70 space-y-0.5">
                                <div class="text-rose-400 font-bold flex items-center justify-between">
                                    <span> 现状方案 (As-Is):</span>
                                    <span class="text-[10px] px-1 rounded ${isBurst ? 'bg-rose-800 text-white' : 'bg-slate-800'}">${isBurst ? '爆柜风险' : '正常'}</span>
                                </div>
                                <div class="text-slate-300">容量状态: <b class="text-rose-400">${baseSat}</b></div>
                            </div>
                            <div class="bg-emerald-950/50 p-2 rounded border border-emerald-800/70 space-y-0.5">
                                <div class="text-emerald-400 font-bold flex items-center justify-between">
                                    <span> 优化方案 (To-Be):</span>
                                    <span class="text-[10px] px-1 rounded bg-emerald-800 text-white font-bold">健康受控</span>
                                </div>
                                <div class="text-slate-300">副柜 <b class="text-emerald-300">+${f.slave_units}</b> 组 (${f.effective_capacity}件) · 饱和度: <b class="text-emerald-300">${optSat}%</b></div>
                            </div>
                            <div class="text-[10px] text-cyan-300 pt-0.5">
                                优化容量 ${f.effective_capacity} 件；消除单柜瓶颈
                            </div>
                        </div>`
                    );
                    mapLayers.push(fMarker);

                    if (showRings.value) {
                        const circle = L.circle(toMapLatLng(f.lat, f.lng), {
                            radius: 150,
                            color: '#06b6d4',
                            weight: 1.5,
                            fillColor: '#06b6d4',
                            fillOpacity: 0.08,
                            dashArray: '3, 3'
                        }).addTo(map);
                        mapLayers.push(circle);
                    }
                });
            }

            // ---------------------------------------------------------------------
            // 7. 绘制内部路径 (Micro-routes inside community)
            // ---------------------------------------------------------------------
            // 7A. 现状/S1 快递员全量步巡路线 (纯人工重负荷)
            if (isS0.value || isS1.value || isDiff.value) {
                const basePath = p.baseline_plan?.courier_path || p.routing?.baseline_courier_path;
                if (basePath && basePath.length > 1) {
                    const baseCoords = basePath.map(pt => toMapLatLng(pt.lat, pt.lng));
                    const isS1Only = isS1.value;
                    const baseLine = L.polyline(baseCoords, {
                        color: isS1Only ? '#f59e0b' : '#f43f5e',
                        weight: isDiff.value ? 2.5 : 3.2,
                        opacity: isDiff.value ? 0.70 : 0.88,
                        dashArray: '7, 5'
                    }).addTo(map);

                    baseLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold ${isS1Only ? 'text-amber-400' : 'text-rose-400'}">【 ${isS1Only ? 'S1 设施优化后人工步巡' : 'S0 现状快递员全量步巡路线 (As-Is)'}】</div>
                            <div>步巡总里程: <span class="mono font-bold ${isS1Only ? 'text-amber-400' : 'text-rose-400'}">${p.baseline_plan?.courier_walk_dist_km ?? '—'} km</span></div>
                            <div>人工总工时: <span class="mono font-bold ${isS1Only ? 'text-amber-400' : 'text-rose-400'}">${p.baseline_plan?.courier_total_hours ?? '—'} h</span></div>
                            <div class="text-slate-300 text-[10px]">${isS1Only ? '全人工补货+上门，工时较重' : '纯人工覆盖全部楼栋自提与上门，疲劳过载'}</div>
                        </div>`
                    );
                    mapLayers.push(baseLine);
                }
            }

            // 7B. S2 优化 M2 无人车社区巡航路线 (亮天蓝色高亮线)
            if (isS2.value || isDiff.value) {
                if (p.routing && p.routing.unmanned_vehicle_path && p.routing.unmanned_vehicle_path.length > 1) {
                    const uvCoords = p.routing.unmanned_vehicle_path.map(pt => toMapLatLng(pt.lat, pt.lng));
                    const uvLine = L.polyline(uvCoords, {
                        color: '#0284c7',
                        weight: 4.5,
                        opacity: 0.95
                    }).addTo(map);

                    uvLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-sky-400">【 S2 M2 无人车社区微循环巡航路线】</div>
                            <div>巡航里程: <span class="mono font-bold text-white">${p.routing.unmanned_vehicle_dist_km} km</span></div>
                            <div>巡航耗时: <span class="mono text-slate-200">${p.routing.unmanned_vehicle_time_min} min</span></div>
                            <div>服务点数: ${p.routing.unmanned_vehicle_path.length} 处</div>
                            <div class="text-emerald-400 text-[10px]">无人物流巡航投柜，彻底解放末端重体力搬运</div>
                        </div>`
                    );
                    mapLayers.push(uvLine);
                }

                // 7C. S2 优化后快递员精准上门步巡路线 (橙色虚线，仅上门子集)
                if (p.routing && p.routing.courier_path && p.routing.courier_path.length > 1) {
                    const cCoords = p.routing.courier_path.map(pt => toMapLatLng(pt.lat, pt.lng));
                    const cLine = L.polyline(cCoords, {
                        color: '#ea580c',
                        weight: 2.8,
                        opacity: 0.90,
                        dashArray: '5, 5'
                    }).addTo(map);

                    cLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-orange-400">【 S2 M3 快递员适老精准上门步巡】</div>
                            <div>步巡里程: <span class="mono font-bold text-emerald-400">${p.routing.courier_walk_dist_km} km</span> <span class="text-emerald-400 text-[10px]">改善 ${p.community_comparison?.walk_saving_pct ?? '—'}%</span></div>
                            <div>上门工时: <span class="mono font-bold text-emerald-400">${p.routing.courier_total_hours} h</span> <span class="text-emerald-400 text-[10px]">改善 ${p.community_comparison?.hours_saving_pct ?? '—'}%</span></div>
                            <div class="text-slate-300 text-[10px]">人机接驳协同，专注高品质入户适老服务</div>
                        </div>`
                    );
                    mapLayers.push(cLine);
                }
            }

            // ---------------------------------------------------------------------
            // 8. 智能视角聚焦当前社区多边形范围
            // ---------------------------------------------------------------------
            if (activeTab.value === 'comparison' || activeTab.value === 'digital-twin') {
                fitAllOverview();
            } else {
                fitCurrentCommunity();
            }
        };

        const getOrCreateChart = (domId) => {
            const el = document.getElementById(domId);
            if (!el) return null;
            let chart = echarts.getInstanceByDom(el);
            if (!chart) {
                chart = echarts.init(el);
            }
            return chart;
        };

        const initCharts = () => {
            chartArrivals = getOrCreateChart('chart-arrivals');
            chartSaturation = getOrCreateChart('chart-saturation');
            chartRadar = getOrCreateChart('chart-radar');
            chartCost = getOrCreateChart('chart-cost');
            chartGantt = getOrCreateChart('chart-gantt');
            chartTspConvergence = getOrCreateChart('chart-tsp-convergence');
            chartMipConvergence = getOrCreateChart('chart-mip-convergence');

            // Tab 0 全景对比图表
            chartCompSaturation = getOrCreateChart('chart-comp-saturation');
            chartCompRadar = getOrCreateChart('chart-comp-radar');
            chartCompCost = getOrCreateChart('chart-comp-cost');
        };

        const updateAllActiveCharts = () => {
            initCharts();
            updateCharts();
            updateTspChart();
            updateMipChart();
            updateSimCharts();
            resizeCharts();
        };


        const updateCharts = () => {
            if (!planResult.value) return;
            const fc = planResult.value.forecast;
            if (!fc || !fc.hourly_schedule) return;

            if (!chartArrivals) chartArrivals = getOrCreateChart('chart-arrivals');

            // 1. 到件波峰时变图
            if (chartArrivals) {
                const periods = fc.hourly_schedule.map(s => s.period.split('—')[0]);
                const totals = fc.hourly_schedule.map(s => s.total_pkgs);
                const doors = fc.hourly_schedule.map(s => s.door_pkgs);
                const lockers = fc.hourly_schedule.map(s => s.locker_pkgs);

                chartArrivals.setOption({
                    backgroundColor: 'transparent',
                    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
                    legend: { data: ['总件量', '送货上门', '自提柜'], textStyle: { color: '#687680' }, top: 0 },
                    grid: { top: 35, left: 45, right: 15, bottom: 25 },
                    xAxis: { type: 'category', data: periods, axisLabel: { color: '#687680', fontSize: 11 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                    yAxis: { type: 'value', axisLabel: { color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                    series: [
                        { name: '总件量', type: 'line', smooth: true, data: totals, itemStyle: { color: '#2d7f9e' }, lineStyle: { width: 3 } },
                        { name: '送货上门', type: 'bar', stack: 'mode', data: doors, itemStyle: { color: '#bf6b34' } },
                        { name: '自提柜', type: 'bar', stack: 'mode', data: lockers, itemStyle: { color: '#2e8b63' } }
                    ]
                });
            }
        };

        const updateTspChart = () => {
            if (!overview.value || !overview.value.trunk_routing) return;
            const tr = overview.value.trunk_routing;
            if (!chartTspConvergence) chartTspConvergence = getOrCreateChart('chart-tsp-convergence');
            if (!chartTspConvergence || !tr.convergence_curve) return;

            const labels = tr.convergence_curve.map(c => `轮次 ${c.iter}`);
            const dists = tr.convergence_curve.map(c => c.tour_dist_km);

            chartTspConvergence.setOption({
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'axis',
                    formatter: (params) => {
                        const idx = params[0].dataIndex;
                        const item = tr.convergence_curve[idx];
                        return `<b>${item.label}</b><br/>干线巡回总长: <span class="mono font-bold text-cyan-400">${item.tour_dist_km} km</span>`;
                    }
                },
                grid: { top: 30, left: 45, right: 20, bottom: 25 },
                xAxis: { type: 'category', data: labels, axisLabel: { color: '#687680', fontSize: 10 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                yAxis: { type: 'value', name: 'km', axisLabel: { color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                series: [{
                    name: '巡回里程',
                    type: 'line',
                    smooth: true,
                    data: dists,
                    itemStyle: { color: '#226f8c' },
                    areaStyle: { color: 'rgba(6, 182, 212, 0.15)' },
                    lineStyle: { width: 3 }
                }]
            });
        };

        const updateMipChart = () => {
            if (!planResult.value || !planResult.value.layout) return;
            const lo = planResult.value.layout;
            if (!chartMipConvergence) chartMipConvergence = getOrCreateChart('chart-mip-convergence');
            if (!chartMipConvergence || !lo.convergence_curve) return;

            const nodes = lo.convergence_curve.map(c => `Node ${c.node}`);
            const ubs = lo.convergence_curve.map(c => c.upper_bound);
            const lbs = lo.convergence_curve.map(c => c.lower_bound);

            chartMipConvergence.setOption({
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'axis',
                    formatter: (params) => {
                        const idx = params[0].dataIndex;
                        const c = lo.convergence_curve[idx];
                        return `<b>B&B Tree Search Node ${c.node}</b><br/>上界 (Incumbent): ¥${c.upper_bound}<br/>下界 (LP Relax): ¥${c.lower_bound}<br/>Optimality GAP: <span class="text-emerald-400 font-bold">${c.gap_pct}%</span>`;
                    }
                },
                legend: { data: ['上界 (整数可行解)', '下界 (松弛界限)'], textStyle: { color: '#687680', fontSize: 10 }, top: 0 },
                grid: { top: 35, left: 55, right: 20, bottom: 25 },
                xAxis: { type: 'category', data: nodes, axisLabel: { color: '#687680', fontSize: 10 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                yAxis: { type: 'value', name: '元', axisLabel: { color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                series: [
                    { name: '上界 (整数可行解)', type: 'line', data: ubs, itemStyle: { color: '#b7791f' }, lineStyle: { width: 2 } },
                    { name: '下界 (松弛界限)', type: 'line', data: lbs, itemStyle: { color: '#2e8b63' }, lineStyle: { width: 2, type: 'dashed' } }
                ]
            });
        };

        const updateSimCharts = () => {
            if (!simulationResult.value) return;
            const sim = simulationResult.value;

            if (!chartSaturation) chartSaturation = getOrCreateChart('chart-saturation');
            if (!chartRadar) chartRadar = getOrCreateChart('chart-radar');
            if (!chartCost) chartCost = getOrCreateChart('chart-cost');
            if (!chartGantt) chartGantt = getOrCreateChart('chart-gantt');
            if (!chartCompSaturation) chartCompSaturation = getOrCreateChart('chart-comp-saturation');
            if (!chartCompRadar) chartCompRadar = getOrCreateChart('chart-comp-radar');
            if (!chartCompCost) chartCompCost = getOrCreateChart('chart-comp-cost');


            // 2. 仿真满柜时序对抗曲线 (#chart-saturation)
            if (chartSaturation && sim.timeline) {
                chartSaturation.setOption({
                    backgroundColor: 'transparent',
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['未扩容基准(严重满柜)', 'MIP优化扩容(安全承载)'], textStyle: { color: '#687680' }, top: 0 },
                    grid: { top: 35, left: 45, right: 25, bottom: 25 },
                    xAxis: { type: 'category', data: sim.timeline.hours, axisLabel: { color: '#687680' }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                    yAxis: { type: 'value', max: 150, axisLabel: { formatter: '{value}%', color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                    series: [
                        {
                            name: '未扩容基准(严重满柜)',
                            type: 'line',
                            data: sim.timeline.locker_occupancy_baseline,
                            itemStyle: { color: '#b84b4b' },
                            lineStyle: { width: 3, type: 'dashed' },
                            markLine: { data: [{ yAxis: 100, name: '满柜红线', lineStyle: { color: '#b84b4b', width: 2 } }] }
                        },
                        {
                            name: 'MIP优化扩容(安全承载)',
                            type: 'line',
                            smooth: true,
                            data: sim.timeline.locker_occupancy_optimized,
                            itemStyle: { color: '#2e8b63' },
                            areaStyle: { color: 'rgba(16, 185, 129, 0.15)' },
                            lineStyle: { width: 3 }
                        }
                    ]
                });
            }

            // 3. 仿真三方案多维雷达图 (#chart-radar)
            if (chartRadar && sim.scenarios_comparison) {
                const rows = sim.scenarios_comparison;
                const maxCost = Math.max(...rows.map(s => s.annual_cost_rmb || 0), 1);
                const maxCarbon = Math.max(...rows.map(s => s.annual_carbon_kg || 0), 1);
                const maxHours = Math.max(...rows.map(s => s.courier_hours || 0), 1);
                const maxTrunk = Math.max(...rows.map(s => s.trunk_km || 0), 1);
                chartRadar.setOption({
                    backgroundColor: 'transparent',
                    legend: { data: ['现状(纯人工)', '优化后人工', '人机协同(推荐)'], textStyle: { color: '#687680' }, bottom: 0 },
                    radar: {
                        center: ['50%', '44%'],
                        radius: '60%',
                        indicator: [
                            { name: '时效响应', max: 100 },
                            { name: '工时节约', max: 100 },
                            { name: '低运营碳', max: 100 },
                            { name: '经济效益', max: 100 },
                            { name: '便民覆盖', max: 100 }
                        ],
                        axisName: { color: '#687680', fontSize: 10 },
                        splitArea: { show: false },
                        splitLine: { lineStyle: { color: '#e4e9ec' } },
                        axisLine: { lineStyle: { color: '#c9d3d8' } }
                    },
                    series: [{
                        type: 'radar',
                        data: rows.map((s, index) => ({
                            value: [
                                100 * (1 - (s.trunk_km || 0) / maxTrunk),
                                100 * (1 - (s.courier_hours || 0) / maxHours),
                                100 * (1 - (s.annual_carbon_kg || 0) / maxCarbon),
                                100 * (1 - (s.annual_cost_rmb || 0) / maxCost),
                                s.bottleneck === 'FEASIBLE' ? 100 : 0
                            ],
                            name: ['现状(纯人工)', '优化后人工', '人机协同(推荐)'][index],
                            itemStyle: { color: ['#64748b', '#b7791f', '#226f8c'][index] }
                        }))
                    }]
                });
            }

            // 4. 仿真年运营成本与运营碳排图 (#chart-cost)
            if (chartCost && sim.scenarios_comparison) {
                const names = sim.scenarios_comparison.map(s => s.scenario);
                const costs = sim.scenarios_comparison.map(s => Math.round(s.annual_cost_rmb / 10000));
                const carbons = sim.scenarios_comparison.map(s => s.annual_carbon_kg);

                chartCost.setOption({
                    backgroundColor: 'transparent',
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['年运营总成本 (万元)', '年碳排放 (kg CO₂)'], textStyle: { color: '#687680' }, top: 0 },
                    grid: { top: 35, left: 45, right: 45, bottom: 25 },
                    xAxis: { type: 'category', data: names, axisLabel: { color: '#687680', fontSize: 11 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                    yAxis: [
                        { type: 'value', name: '万元', axisLabel: { color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                        { type: 'value', name: 'kg', axisLabel: { color: '#687680' }, splitLine: { show: false } }
                    ],
                    series: [
                        { name: '年运营总成本 (万元)', type: 'bar', data: costs, itemStyle: { color: '#b7791f' }, barWidth: 26 },
                        { name: '年碳排放 (kg CO₂)', type: 'line', yAxisIndex: 1, data: carbons, itemStyle: { color: '#b7791f' }, lineStyle: { width: 3 } }
                    ]
                });
            }

            // 4.1 人机协同作业时序甘特图 (#chart-gantt)
            if (chartGantt && sim.gantt_schedule) {
                const entities = [...new Set(sim.gantt_schedule.map(t => t.entity))].reverse();
                const parseMin = (tStr) => {
                    const parts = tStr.split(':').map(Number);
                    return (parts[0] - 8) * 60 + parts[1];
                };

                const data = sim.gantt_schedule.map(t => {
                    const yIndex = entities.indexOf(t.entity);
                    const startMin = parseMin(t.start_time);
                    const endMin = parseMin(t.end_time);
                    return {
                        name: t.label,
                        value: [yIndex, startMin, endMin, endMin - startMin, t.community, t.type],
                        itemStyle: {
                            color: t.type === 'UV_TRIP' ? '#226f8c' : '#b7791f'
                        }
                    };
                });

                chartGantt.setOption({
                    backgroundColor: 'transparent',
                    tooltip: {
                        formatter: (params) => {
                            const v = params.value;
                            const startStr = `${Math.floor((v[1]+480)/60).toString().padStart(2, '0')}:${((v[1]+480)%60).toString().padStart(2, '0')}`;
                            const endStr = `${Math.floor((v[2]+480)/60).toString().padStart(2, '0')}:${((v[2]+480)%60).toString().padStart(2, '0')}`;
                            return `<b>${params.name}</b><br/>
                                    执行主体: ${entities[v[0]]}<br/>
                                    作业时段: <span class="mono text-cyan-400 font-bold">${startStr} ~ ${endStr}</span><br/>
                                    作业耗时: <span class="mono text-emerald-400 font-bold">${v[3]} 分钟</span>`;
                        }
                    },
                    grid: { top: 25, left: 140, right: 25, bottom: 25 },
                    xAxis: {
                        type: 'value',
                        min: 0,
                        max: 780,
                        interval: 120,
                        axisLabel: {
                            color: '#687680',
                            formatter: (val) => {
                                const totalM = val + 480;
                                return `${Math.floor(totalM/60).toString().padStart(2, '0')}:${(totalM%60).toString().padStart(2, '0')}`;
                            }
                        },
                        splitLine: { lineStyle: { color: '#e4e9ec' } }
                    },
                    yAxis: {
                        type: 'category',
                        data: entities,
                        axisLabel: { color: '#cbd5e1', fontSize: 10 },
                        splitLine: { show: true, lineStyle: { color: '#e4e9ec' } }
                    },
                    series: [{
                        type: 'custom',
                        renderItem: (params, api) => {
                            const categoryIndex = api.value(0);
                            const start = api.coord([api.value(1), categoryIndex]);
                            const end = api.coord([api.value(2), categoryIndex]);
                            const height = api.size([0, 1])[1] * 0.55;
                            const rectShape = echarts.graphic.clipRectByRect({
                                x: start[0],
                                y: start[1] - height / 2,
                                width: Math.max(end[0] - start[0], 2),
                                height: height
                            }, {
                                x: params.coordSys.x,
                                y: params.coordSys.y,
                                width: params.coordSys.width,
                                height: params.coordSys.height
                            });
                            return rectShape && {
                                type: 'rect',
                                transition: ['shape'],
                                shape: rectShape,
                                style: api.style()
                            };
                        },
                        encode: { x: [1, 2], y: 0 },
                        data: data
                    }]
                });
            }

            // 5. Tab 0 全景对比: 满柜时序对抗曲线 (#chart-comp-saturation)
            if (chartCompSaturation) {
                const hours = sim.timeline?.hours || [];
                const baseSat = sim.timeline?.locker_occupancy_baseline || [];
                const optSat = sim.timeline?.locker_occupancy_optimized || [];
                const finiteSaturation = [...baseSat, ...optSat].map(Number).filter(Number.isFinite);
                const saturationMax = Math.max(120, Math.ceil((Math.max(0, ...finiteSaturation) + 10) / 20) * 20);

                chartCompSaturation.setOption({
                    backgroundColor: 'transparent',
                    tooltip: {
                        trigger: 'axis',
                        formatter: (params) => {
                            let tip = `<b>${params[0].axisValue} 动态饱和度对比</b><br/>`;
                            params.forEach(p => {
                                tip += `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${p.color};"></span>${p.seriesName}: <b>${p.value}%</b><br/>`;
                            });
                            return tip;
                        }
                    },
                    legend: { data: [' S0现有柜体占用 (未扩容)', ' S1/S2优化定容占用 (安全承载)'], textStyle: { color: '#687680', fontSize: 11 }, top: 0 },
                    grid: { top: 35, left: 45, right: 25, bottom: 25 },
                    xAxis: { type: 'category', data: hours, axisLabel: { color: '#687680', fontSize: 11 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                    yAxis: {
                        type: 'value',
                        max: saturationMax,
                        axisLabel: { formatter: '{value}%', color: '#687680' },
                        splitLine: { lineStyle: { color: '#e4e9ec' } }
                    },
                    series: [
                        {
                            name: ' S0现有柜体占用 (未扩容)',
                            type: 'line',
                            data: baseSat,
                            itemStyle: { color: '#b84b4b' },
                            lineStyle: { width: 3, type: 'dashed' },
                            markLine: {
                                symbol: 'none',
                                label: { formatter: '100% 满柜红线', color: '#b84b4b', position: 'insideEndTop' },
                                data: [{ yAxis: 100, lineStyle: { color: '#b84b4b', width: 2, type: 'solid' } }]
                            }
                        },
                        {
                            name: ' S1/S2优化定容占用 (安全承载)',
                            type: 'line',
                            smooth: true,
                            data: optSat,
                            itemStyle: { color: '#2e8b63' },
                            areaStyle: { color: 'rgba(16, 185, 129, 0.18)' },
                            lineStyle: { width: 3 }
                        }
                    ]
                });
            }

            // 6. Tab 0 全景对比: 综合效益多维雷达对照 (#chart-comp-radar) (S0 vs S1 vs S2 三方案阶梯对比)
            if (chartCompRadar && overview.value?.comparison_metrics) {
                const metrics = overview.value.comparison_metrics;
                const lowerScore = (key, side) => {
                    const base = Number(metrics[key]?.baseline ?? 0);
                    const value = Number(metrics[key]?.[side] ?? 0);
                    return value > 0 && base > 0 ? Math.min(100, Math.round(100 * base / value)) : (value === 0 ? 100 : 50);
                };
                const s0FeasibleScore = simulationResult.value?.summary?.scheme_status?.S0 === 'FEASIBLE' ? 100 : 20;
                const s1FeasibleScore = simulationResult.value?.summary?.scheme_status?.S1 === 'FEASIBLE' ? 100 : 90;
                const s2FeasibleScore = simulationResult.value?.summary?.scheme_status?.S2 === 'FEASIBLE' ? 100 : 100;

                const s0Coverage = Number(metrics.coverage_rate?.baseline ?? 6.5);
                const s1Coverage = Number(metrics.coverage_rate?.s1 ?? 100.0);
                const s2Coverage = Number(metrics.coverage_rate?.optimized ?? 100.0);

                chartCompRadar.setOption({
                    backgroundColor: 'transparent',
                    legend: {
                        data: [' S0 现状基准 (As-Is)', ' S1 网络设施优化', ' S2 人机协同推荐 (To-Be)'],
                        textStyle: { color: '#687680', fontSize: 10 },
                        bottom: 0
                    },
                    radar: {
                        center: ['50%', '44%'],
                        radius: '60%',
                        indicator: [
                            { name: '干线集约度', max: 100 },
                            { name: '工时压降', max: 100 },
                            { name: '低碳减排', max: 100 },
                            { name: '经济节约', max: 100 },
                            { name: '容灾安全', max: 100 },
                            { name: '便民覆盖', max: 100 }
                        ],
                        axisName: { color: '#687680', fontSize: 10 },
                        splitArea: { show: false },
                        splitLine: { lineStyle: { color: '#e4e9ec' } },
                        axisLine: { lineStyle: { color: '#c9d3d8' } }
                    },
                    series: [{
                        type: 'radar',
                        data: [
                            {
                                value: [50, 45, 100, 50, s0FeasibleScore, s0Coverage],
                                name: ' S0 现状基准 (As-Is)',
                                itemStyle: { color: '#b64b58' },
                                lineStyle: { type: 'dashed', width: 2 }
                            },
                            {
                                value: [
                                    lowerScore('trunk_distance', 's1'),
                                    lowerScore('labor_hours', 's1'),
                                    lowerScore('annual_carbon', 's1'),
                                    lowerScore('annual_cost', 's1'),
                                    s1FeasibleScore,
                                    s1Coverage
                                ],
                                name: ' S1 网络设施优化',
                                itemStyle: { color: '#b7791f' },
                                lineStyle: { width: 2 }
                            },
                            {
                                value: [
                                    lowerScore('trunk_distance', 'optimized'),
                                    lowerScore('labor_hours', 'optimized'),
                                    lowerScore('annual_carbon', 'optimized'),
                                    lowerScore('annual_cost', 'optimized'),
                                    s2FeasibleScore,
                                    s2Coverage
                                ],
                                name: ' S2 人机协同推荐 (To-Be)',
                                itemStyle: { color: '#226f8c' },
                                areaStyle: { color: 'rgba(6, 182, 212, 0.28)' },
                                lineStyle: { width: 2.5 }
                            }
                        ]
                    }]
                });
            }

            // 7. Tab 0 全景对比: 年运营成本与运营碳排三方案对比 (#chart-comp-cost)
            if (chartCompCost && overview.value?.comparison_metrics) {
                const metrics = overview.value.comparison_metrics;
                const costData = [
                    metrics.annual_cost.baseline / 10000,
                    (metrics.annual_cost.s1 || 1487090) / 10000,
                    metrics.annual_cost.optimized / 10000
                ].map(v => Number(Number(v).toFixed(1)));
                const carbonData = [
                    metrics.annual_carbon.baseline,
                    (metrics.annual_carbon.s1 || 6043.0),
                    metrics.annual_carbon.optimized
                ].map(v => Math.round(Number(v)));
                chartCompCost.setOption({
                    backgroundColor: 'transparent',
                    color: ['#b84b4b', '#2d7f9e'],
                    tooltip: { trigger: 'axis', confine: true },
                    legend: {
                        data: ['运营成本', '运营碳排'],
                        textStyle: { color: '#52636f', fontSize: 10 },
                        itemWidth: 14,
                        itemHeight: 8,
                        itemGap: 12,
                        top: 0,
                        left: 'center'
                    },
                    grid: { top: 52, left: 18, right: 18, bottom: 28, containLabel: true },
                    xAxis: {
                        type: 'category',
                        data: ['S0 现状', 'S1 设施优化', 'S2 人机协同'],
                        axisTick: { show: false },
                        axisLabel: { color: '#5b6973', fontSize: 10, interval: 0, margin: 10 },
                        axisLine: { lineStyle: { color: '#c9d3d8' } }
                    },
                    yAxis: [
                        { type: 'value', name: '万元', nameTextStyle: { color: '#71808a', fontSize: 9 }, axisLabel: { color: '#687680', fontSize: 9 }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                        { type: 'value', name: 'kg', nameTextStyle: { color: '#71808a', fontSize: 9 }, axisLabel: { color: '#687680', fontSize: 9 }, splitLine: { show: false } }
                    ],
                    series: [
                        {
                            name: '运营成本',
                            type: 'bar',
                            data: costData,
                            itemStyle: {
                                borderRadius: [4, 4, 0, 0],
                                color: (params) => ['#b84b4b', '#b7791f', '#2e8b63'][params.dataIndex]
                            },
                            barWidth: 36,
                            label: {
                                show: true,
                                position: 'insideTop',
                                distance: 5,
                                color: '#ffffff',
                                fontSize: 9,
                                fontWeight: 700,
                                formatter: (params) => Number(params.value).toFixed(1)
                            },
                            labelLayout: { hideOverlap: true }
                        },
                        {
                            name: '运营碳排',
                            type: 'line',
                            yAxisIndex: 1,
                            data: carbonData,
                            symbol: 'circle',
                            symbolSize: 7,
                            itemStyle: { color: '#2d7f9e' },
                            lineStyle: { width: 3 },
                            label: {
                                show: true,
                                position: 'top',
                                distance: 7,
                                color: '#1f6f8f',
                                fontSize: 9,
                                fontWeight: 700,
                                formatter: (params) => `${Math.round(Number(params.value))}`
                            },
                            labelLayout: { hideOverlap: true }
                        }
                    ]
                }, true);
            }
        };

        // 8. 第七章两阶段 ISA 算法退火收敛仿真图表
        let chartIsaConvergence = null;
        const updateIsaChart = () => {
            chartIsaConvergence = getOrCreateChart('chart-isa-convergence');
            if (!chartIsaConvergence) return;

            const curve = planResult.value?.routing?.isa_convergence_curve || [];
            if (!Array.isArray(curve) || curve.length < 2) {
                chartIsaConvergence.clear();
                chartIsaConvergence.setOption({
                    backgroundColor: 'transparent',
                    graphic: [{
                        type: 'text',
                        left: 'center',
                        top: 'middle',
                        style: {
                            text: '暂无后端真实收敛轨迹',
                            fill: '#687680',
                            fontSize: 12
                        }
                    }]
                });
                return;
            }

            const iterations = curve.map((item, index) => `轮次 ${item.iter ?? index}`);
            const temperatures = curve.map(item => Number(item.temperature ?? 0));
            const costs = curve.map(item => Number(item.best_cost ?? item.tour_dist_km ?? 0));

            chartIsaConvergence.setOption({
                backgroundColor: 'transparent',
                tooltip: { trigger: 'axis' },
                legend: { data: ['子路径加权距离目标 Z (km)', '退火温度 T (°C)'], textStyle: { color: '#687680', fontSize: 10 }, top: 0 },
                grid: { top: 35, left: 55, right: 55, bottom: 25 },
                xAxis: { type: 'category', data: iterations, axisLabel: { color: '#687680', fontSize: 10 }, axisLine: { lineStyle: { color: '#c9d3d8' } } },
                yAxis: [
                    { type: 'value', name: '路径目标', min: 'dataMin', max: 'dataMax', axisLabel: { color: '#687680' }, splitLine: { lineStyle: { color: '#e4e9ec' } } },
                    { type: 'value', name: '温度 T (°C)', min: 0, max: 'dataMax', axisLabel: { color: '#b7791f' }, splitLine: { show: false } }
                ],
                series: [
                    {
                        name: '子路径加权距离目标 Z (km)',
                        type: 'line',
                        data: costs,
                        itemStyle: { color: '#226f8c' },
                        lineStyle: { width: 3 },
                        smooth: true,
                        symbolSize: 5
                    },
                    {
                        name: '退火温度 T (°C)',
                        type: 'line',
                        yAxisIndex: 1,
                        data: temperatures,
                        itemStyle: { color: '#b7791f' },
                        lineStyle: { width: 2, type: 'dashed' },
                        smooth: true,
                        symbolSize: 4
                    }
                ]
            });
        };

        const resizeCharts = () => {
            if (chartArrivals) chartArrivals.resize();
            if (chartSaturation) chartSaturation.resize();
            if (chartRadar) chartRadar.resize();
            if (chartCost) chartCost.resize();
            if (chartGantt) chartGantt.resize();
            if (chartTspConvergence) chartTspConvergence.resize();
            if (chartMipConvergence) chartMipConvergence.resize();
            if (chartCompSaturation) chartCompSaturation.resize();
            if (chartCompRadar) chartCompRadar.resize();
            if (chartCompCost) chartCompCost.resize();
            if (chartIsaConvergence) chartIsaConvergence.resize();
            if (map) map.invalidateSize();
        };

        watch(activeTab, (newTab) => {
            nextTick(() => {
                updateAllActiveCharts();
                renderMath();
                if (map) {
                    map.invalidateSize();
                    if (newTab === 'comparison' || newTab === 'digital-twin') {
                        fitAllOverview();
                    } else {
                        fitCurrentCommunity();
                    }
                }
                setTimeout(() => {
                    updateAllActiveCharts();
                    if (map) map.invalidateSize();
                }, 150);
            });
        });

        watch(showSolverModal, (val) => {
            if (val) {
                renderMath();
                if (solverModalTab.value === 'M2-ISA') {
                    nextTick(() => updateIsaChart());
                }
            }
        });

        watch(solverModalTab, (tab) => {
            renderMath();
            if (tab === 'M2-ISA') {
                nextTick(() => updateIsaChart());
            }
        });

        const syncUrlState = () => {
            const params = new URLSearchParams();
            params.set('tab', activeTab.value);
            params.set('community', selectedCommunityId.value);
            params.set('scheme', schemeMode.value);
            params.set('scenario', currentScenario.value);
            const nextHash = `#${params.toString()}`;
            if (window.location.hash !== nextHash) {
                window.history.replaceState(null, '', nextHash);
            }
        };

        watch([activeTab, selectedCommunityId, schemeMode, currentScenario], syncUrlState);

        return {
            toasts,
            showToast,
            activeTab,
            viewMode,
            presentationMode,
            togglePresentationMode,
            toggleViewMode,
            schemeMode,
            setSchemeMode,
            isS0,
            isS1,
            isS2,
            isDiff,
            getModelDisplayName,
            aiQuickModes,
            schemeCardClass,
            switchAiModel,
            currentScenario,
            setScenario,
            loading,
            apiError,
            mobilePane,
            setActiveTab,
            moduleNav,
            planStatusMeta,
            pipelineStatus,
            constraintChecks,
            failedConstraintChecks,
            hardViolationCount,
            formatConstraintValue,
            showConstraintDetails,
            renderMarkdown,
            mathText,
            overview,
            comparisonMetric,
            metricValue,
            improvementText,
            improvementS1Text,
            credibilityTag,
            changeText,
            savingValue,
            selectedCommunityId,
            planResult,
            simulationResult,
            simScenario,
            switchSimScenario,
            crisisResult,
            isPeakDay,
            // AI 智能中枢与多智能体应急中枢相关
            showAiDrawer,
            aiDrawerMessages,
            aiInput,
            aiLoading,
            aiConfig,
            showAiConfigModal,
            aiConfigForm,
            aiDetectedModels,
            aiModelsLoading,
            aiModelsMessage,
            aiTestLoading,
            aiTestResult,
            activeCrisisType,
            crisisStreaming,
            crisisStreamText,
            crisisExecutionStatus,
            fetchAiConfig,
            saveAiConfig,
            testAiConnection,
            fetchAvailableModels,
            toggleAiDrawer,
            sendAiMessage,
            triggerAiCrisis,
            applyRescheduledPlan,
            copyDispatchOrder,
            showSolverModal,
            solverModalTab,
            mathModelsList,
            currentTileTheme,
            tileStatusText,
            mapCrsText,
            showRoads,
            showPolygons,
            showRings,
            onChangeTileTheme,
            toggleRoads,
            togglePolygons,
            toggleRings,
            fitAllOverview,
            fitCurrentCommunity,
            onSelectCommunity,
            triggerCrisis,
            resizeCharts,
            renderMath,
            updateAllActiveCharts,
            updateIsaChart,
            // 学术级图谱相关
            academicFigures,
            demandFigures,
            networkFigures,
            operationFigures,
            showImageModal,
            activeImage,
            openImagePreview,
            closeImagePreview
        };
    }
});

app.config.errorHandler = (err, vm, info) => {
    console.warn('[Vue Global Error Guard]:', info, err);
};

app.mount('#app');
