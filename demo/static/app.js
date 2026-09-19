const { createApp, ref, onMounted, watch, nextTick } = Vue;

const app = createApp({
    setup() {
        const activeTab = ref('comparison');
        const viewMode = ref('split'); // 'split' | 'wide'
        const schemeMode = ref('diff'); // 'baseline' | 'optimized' | 'diff'
        const loading = ref(false);
        const overview = ref(null);
        const selectedCommunityId = ref('C04');
        const planResult = ref(null);
        const simulationResult = ref(null);
        const simScenario = ref('normal'); // 'normal' | 'peak' | 'disruption'
        const crisisResult = ref(null);
        const isPeakDay = ref(false);

        const comparisonMetric = (key) => overview.value?.comparison_metrics?.[key] || null;
        const metricValue = (key, side, divisor = 1, digits = 1) => {
            const value = comparisonMetric(key)?.[side];
            return Number.isFinite(Number(value)) ? (Number(value) / divisor).toFixed(digits) : '—';
        };
        const improvementText = (key) => {
            const value = comparisonMetric(key)?.diff_pct;
            if (!Number.isFinite(Number(value))) return '仅报告绝对变化';
            return `${Number(value) >= 0 ? '改善' : '变差'} ${Math.abs(Number(value)).toFixed(1)}%`;
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

        const toggleViewMode = () => {
            viewMode.value = viewMode.value === 'split' ? 'wide' : 'split';
            nextTick(() => {
                updateAllActiveCharts();
                if (map) map.invalidateSize();
                setTimeout(() => {
                    updateAllActiveCharts();
                    if (map) map.invalidateSize();
                }, 150);
            });
        };


        // 运筹控制台与数学看板弹窗状态
        const showSolverModal = ref(false);
        const solverModalTab = ref('M6');
        const mathModelsList = ref([]);

        // 高德开放平台 API Key 与实时搜索状态
        const amapConfig = ref({ configured: false, masked_key: '加载中...' });
        const showAmapModal = ref(false);
        const amapKeyInput = ref('');
        const amapKeyMsg = ref('');
        const amapSearchKeyword = ref('海淀远大园');
        const amapExploring = ref(false);
        const amapExploreResult = ref(null);

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
        const tileStatusText = ref('高德暗黑矢量底图 [在线]');
        const showRoads = ref(true);
        const showPolygons = ref(true);
        const showRings = ref(true);

        // 自定义沙盒参数
        const customHouseholds = ref(2141);
        const customDoorRatio = ref(0.25);
        const customIntensity = ref(0.6);

        // Leaflet 地图、图层与图表引用
        let map = null;
        let currentTileLayer = null;
        let tileLayers = {};
        let mapLayers = [];

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

        // 切换现状/优化/叠图方案
        const setSchemeMode = (mode) => {
            schemeMode.value = mode;
            renderMapLayers();
        };

        // KaTeX 自动数学公式渲染 (仅针对公式专用容器，严禁污染 Vue 响应式文本节点)
        const renderMath = () => {
            nextTick(() => {
                if (window.renderMathInElement) {
                    const containers = document.querySelectorAll('.math-card, .math-target');
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
            initMap();
            await fetchAmapConfig();
            await fetchMathModels();
            await fetchOverview();
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
                center: [39.792, 116.495],
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
                if (currentTileTheme.value === 'amap-dark') {
                    tileStatusText.value = '高德暗黑矢量底图 [在线]';
                }
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
                if (map) map.invalidateSize();
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
            const pts = [[39.798, 116.506]]; // HUB
            if (overview.value && overview.value.communities) {
                overview.value.communities.forEach(c => {
                    if (c.center) pts.push(c.center);
                    if (c.polygon && c.polygon.length > 0) {
                        c.polygon.forEach(pt => pts.push(pt));
                    }
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
            if (p.polygon && p.polygon.length > 0) {
                p.polygon.forEach(pt => pts.push(pt));
            }
            if (p.buildings && p.buildings.length > 0) {
                p.buildings.forEach(b => pts.push([b.lat, b.lng]));
            }
            if (pts.length > 0) {
                map.fitBounds(L.latLngBounds(pts).pad(0.08));
            }
        };

        // 高德开放平台 API 交互与全要素社区探索
        const fetchAmapConfig = async () => {
            try {
                const res = await fetch('/api/amap/config');
                amapConfig.value = await res.json();
            } catch (e) {
                console.error('Fetch Amap config failed:', e);
            }
        };

        const saveAmapKey = async () => {
            if (!amapKeyInput.value.trim()) {
                amapKeyMsg.value = '请输入有效的Key';
                return;
            }
            try {
                const res = await fetch('/api/amap/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: amapKeyInput.value.trim() })
                });
                const data = await res.json();
                amapConfig.value = {
                    configured: data.configured,
                    masked_key: data.masked_key
                };
                if (data.test_result && data.test_result.valid) {
                    amapKeyMsg.value = '✅ 验证成功！已接入高德开放平台Web服务';
                    setTimeout(() => {
                        showAmapModal.value = false;
                        amapKeyMsg.value = '';
                    }, 1200);
                } else {
                    amapKeyMsg.value = '⚠️ 保存成功，高德测试提示: ' + (data.test_result ? data.test_result.info : '无法验证');
                }
            } catch (e) {
                amapKeyMsg.value = '❌ 保存失败: ' + e;
            }
        };

        const searchAndExploreCommunity = async () => {
            if (!amapSearchKeyword.value.trim()) return;
            amapExploring.value = true;
            try {
                const res = await fetch('/api/amap/explore', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        community_name: amapSearchKeyword.value.trim(),
                        households: customHouseholds.value || 1200,
                        door_ratio: customDoorRatio.value || 0.35,
                        intensity: customIntensity.value || 0.6
                    })
                });
                const data = await res.json();
                if (data.success) {
                    amapExploreResult.value = data;
                    selectedCommunityId.value = `AMAP-${data.community_name}`;
                    planResult.value = {
                        community_id: `AMAP-${data.community_name}`,
                        community_name: data.community_name,
                        forecast: data.forecast,
                        layout: data.layout,
                        routing: data.routing,
                        buildings: data.buildings,
                        ai_report: data.ai_report,
                        weather: data.weather
                    };
                    renderAmapExploredMap(data);
                    nextTick(() => {
                        updateCharts();
                        renderMath();
                    });
                } else {
                    alert(data.info || '高德解析失败，请检查Key');
                }
            } catch (e) {
                alert('高德探索失败: ' + e);
            } finally {
                amapExploring.value = false;
            }
        };

        const renderAmapExploredMap = (data) => {
            if (!map) return;
            mapLayers.forEach(l => map.removeLayer(l));
            mapLayers = [];

            const center = [data.geo.lat, data.geo.lng];
            
            // 绘制小区中心辐射圆
            const centerCircle = L.circle(center, {
                radius: 180,
                color: '#06b6d4',
                weight: 2,
                fillColor: '#06b6d4',
                fillOpacity: 0.1,
                dashArray: '5, 5'
            }).addTo(map);
            mapLayers.push(centerCircle);

            const centerMarker = L.circleMarker(center, {
                radius: 10,
                color: '#06b6d4',
                fillColor: '#38bdf8',
                fillOpacity: 0.9,
                weight: 3
            }).addTo(map);
            centerMarker.bindPopup(`<b>【高德实时定位】${data.community_name}</b><br>${data.geo.formatted_address}<br>周边已扫描物流设施: ${data.nearby_pois_count} 处`);
            mapLayers.push(centerMarker);

            // 绘制楼栋
            if (data.buildings) {
                data.buildings.forEach(b => {
                    const bMarker = L.circleMarker([b.lat, b.lng], {
                        radius: 6,
                        color: '#60a5fa',
                        fillColor: '#3b82f6',
                        fillOpacity: 0.85,
                        weight: 2
                    }).addTo(map);
                    bMarker.bindPopup(`<b>${b.name}</b><br>户数: ${b.households} 户<br>预测件量: ${b.daily_pkgs} 件 (上门${b.door_pkgs} / 自提${b.locker_pkgs})`);
                    mapLayers.push(bMarker);
                });
            }

            // 绘制智能柜设施
            if (data.layout && data.layout.facilities) {
                data.layout.facilities.forEach(f => {
                    const fMarker = L.circleMarker([f.lat, f.lng], {
                        radius: 8,
                        color: f.slave_units > 0 ? '#10b981' : '#a855f7',
                        fillColor: f.slave_units > 0 ? '#34d399' : '#c084fc',
                        fillOpacity: 0.95,
                        weight: 3
                    }).addTo(map);
                    fMarker.bindPopup(`<b>${f.name}</b><br>配置: 主柜${f.main_lockers} + 副柜${f.slave_units}组 (${f.total_slots}格)<br>有效容量: ${f.effective_capacity}件 | 负荷: ${f.assigned_demand}件<br>状态: ${f.is_full_risk ? '❌有爆柜风险' : '✅容量安全'}`);
                    mapLayers.push(fMarker);

                    const ring = L.circle([f.lat, f.lng], {
                        radius: 100,
                        color: '#10b981',
                        weight: 1,
                        fillColor: '#10b981',
                        fillOpacity: 0.08,
                        dashArray: '3, 3'
                    }).addTo(map);
                    mapLayers.push(ring);
                });
            }

            // 绘制无人车路线
            if (data.routing && data.routing.unmanned_vehicle_path && data.routing.unmanned_vehicle_path.length > 1) {
                const uvCoords = data.routing.unmanned_vehicle_path.map(pt => [pt.lat, pt.lng]);
                const uvLine = L.polyline(uvCoords, {
                    color: '#38bdf8',
                    weight: 4,
                    opacity: 0.9
                }).addTo(map);
                mapLayers.push(uvLine);
            }

            // 绘制快递员上门路线
            if (data.routing && data.routing.courier_path && data.routing.courier_path.length > 1) {
                const cCoords = data.routing.courier_path.map(pt => [pt.lat, pt.lng]);
                const cLine = L.polyline(cCoords, {
                    color: '#f97316',
                    weight: 2,
                    opacity: 0.8,
                    dashArray: '4, 4'
                }).addTo(map);
                mapLayers.push(cLine);
            }

            map.setView(center, 16);
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
                overview.value = await res.json();
                nextTick(() => {
                    updateTspChart();
                    renderMath();
                });
            } catch (e) {
                console.error('Fetch overview failed:', e);
            }
        };

        const loadCommunityPlan = async (cid) => {
            loading.value = true;
            try {
                const res = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        community_id: cid,
                        custom_households: customHouseholds.value,
                        custom_door_ratio: customDoorRatio.value,
                        custom_intensity: customIntensity.value,
                        is_peak_day: isPeakDay.value
                    })
                });
                planResult.value = await res.json();
                nextTick(() => {
                    renderMapLayers();
                    updateCharts();
                    updateMipChart();
                    renderMath();
                    if (map) map.invalidateSize();
                });
            } catch (e) {
                console.error('Load plan failed:', e);
            } finally {
                loading.value = false;
            }
        };

        const fetchSimulation = async (scenario = null) => {
            if (scenario) simScenario.value = scenario;
            try {
                const res = await fetch(`/api/simulation?scenario=${simScenario.value}`);
                simulationResult.value = await res.json();
                nextTick(() => {
                    updateSimCharts();
                    renderMath();
                });
            } catch (e) {
                console.error('Fetch simulation failed:', e);
            }
        };

        const switchSimScenario = (scenario) => {
            fetchSimulation(scenario);
        };

        const onSelectCommunity = (cid) => {
            selectedCommunityId.value = cid;
            if (overview.value) {
                const c = overview.value.communities.find(item => item.id === cid);
                if (c) {
                    customHouseholds.value = c.households;
                    // 设置默认上门比例
                    if (cid === 'C01' || cid === 'C03') customDoorRatio.value = 1.0;
                    else if (cid === 'C02') customDoorRatio.value = 0.52;
                    else if (cid === 'C04') customDoorRatio.value = 0.25;
                    else if (cid === 'C05') customDoorRatio.value = 0.24;
                }
            }
            loadCommunityPlan(cid);
        };

        const onTweakParams = () => {
            loadCommunityPlan(selectedCommunityId.value);
        };

        const triggerCrisis = async (type) => {
            try {
                const res = await fetch('/api/crisis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ event_type: type })
                });
                crisisResult.value = await res.json();
                renderMath();
            } catch (e) {
                console.error('Crisis trigger failed:', e);
            }
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
                        const poly = L.polygon(c.polygon, {
                            color: isCurrent ? '#06b6d4' : '#0284c7',
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
                            const badgeMarker = L.marker(c.center, {
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
                        const roadLine = L.polyline([edge.from_coord, edge.to_coord], {
                            color: isPassable ? '#38bdf8' : '#64748b',
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
                        const nodeDot = L.circleMarker([node.lat, node.lng], {
                            radius: 2,
                            color: '#0284c7',
                            fillColor: '#38bdf8',
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
                const hubMarker = L.circleMarker([hub.lat, hub.lng], {
                    radius: 10,
                    color: '#f59e0b',
                    fillColor: '#fbbf24',
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
                const hubRing = L.circle([hub.lat, hub.lng], {
                    radius: 350,
                    color: '#f59e0b',
                    weight: 1,
                    fillColor: '#f59e0b',
                    fillOpacity: 0.04,
                    dashArray: '5, 5'
                }).addTo(map);
                mapLayers.push(hubRing);
            }

            // ---------------------------------------------------------------------
            // 4. 绘制干线路径 (Trunk Routes: 现状独立往返 vs 优化M1巡回闭环)
            // ---------------------------------------------------------------------
            // 4A. 现状方案干线：HUB 到 5 大社区独立点对点往返线 (红色虚线)
            if ((schemeMode.value === 'baseline' || schemeMode.value === 'diff') &&
                overview.value && overview.value.trunk_routing && overview.value.trunk_routing.baseline_routes) {
                overview.value.trunk_routing.baseline_routes.forEach(route => {
                    const coords = route.coords || route.round_trip_coords;
                    if (!coords || !Array.isArray(coords) || coords.length < 2) return;
                    const latlngs = coords.map(pt => Array.isArray(pt) ? pt : (pt && pt.lat !== undefined ? [pt.lat, pt.lng] : null)).filter(Boolean);
                    if (latlngs.length < 2) return;

                    const bLine = L.polyline(latlngs, {
                        color: '#ef4444',
                        weight: schemeMode.value === 'diff' ? 2.5 : 3.2,
                        opacity: schemeMode.value === 'diff' ? 0.75 : 0.90,
                        dashArray: '6, 5'
                    }).addTo(map);

                    bLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-rose-400">【🔴 现状独立往返干线: HUB ⇄ ${route.community_id}】</div>
                            <div>往返里程: <span class="mono font-bold text-rose-300">${route.dist_km || route.distance_km || 0} km</span></div>
                            <div>单程往返耗时: <span class="mono text-slate-300">${route.time_min || route.drive_time_min || 0} min</span></div>
                            <div class="text-slate-400 text-[10px]">5条车辆点对点往返，全网总长 ${metricValue('trunk_distance', 'baseline', 1, 2)} km</div>
                        </div>`
                    );
                    mapLayers.push(bLine);
                });
            }

            // 4B. 优化方案干线：M1 巡回闭环路径 (亮青色高亮实线)
            if ((schemeMode.value === 'optimized' || schemeMode.value === 'diff') &&
                overview.value && overview.value.trunk_routing && overview.value.trunk_routing.tour) {
                const tour = overview.value.trunk_routing.tour;
                if (Array.isArray(tour) && tour.length > 1) {
                    const latlngs = tour.map(pt => Array.isArray(pt) ? pt : (pt && pt.lat !== undefined ? [pt.lat, pt.lng] : null)).filter(Boolean);
                    if (latlngs.length > 1) {
                        const trunkLine = L.polyline(latlngs, {
                            color: '#06b6d4',
                            weight: 4.5,
                            opacity: 0.95
                        }).addTo(map);

                        trunkLine.bindPopup(
                            `<div class="text-xs space-y-1">
                                <div class="font-bold text-cyan-400">【🟢 M1 亦庄干线巡回 TSP 闭环】</div>
                                <div>巡回总里程: <span class="mono font-bold text-white">${overview.value.trunk_routing.tour_dist_km} km</span></div>
                                <div>相比独立往返: <span class="text-emerald-400 font-bold">${improvementText('trunk_distance')} (${savingValue('trunk_distance', 1, 2)} km)</span></div>
                                <div>无人车巡回耗时: <span class="mono text-slate-200">${overview.value.trunk_routing.travel_time_min} min</span></div>
                                <div class="text-emerald-400 text-[10px]">统仓共配串联5社区；距离为直线距离乘绕行系数估算</div>
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
                    const bMarker = L.circleMarker([b.lat, b.lng], {
                        radius: 5 + Math.min(8, b.daily_pkgs / 40),
                        color: '#60a5fa',
                        fillColor: '#3b82f6',
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
            if (schemeMode.value === 'baseline') {
                const baseFacs = p.baseline_plan?.facilities || p.layout?.facilities || [];
                baseFacs.forEach(f => {
                    if (f.active === false) return;
                    const isBurst = Boolean(f.is_full_risk);
                    const satPct = Number(f.saturation_pct ?? 0);

                    const fMarker = L.marker([f.lat, f.lng], {
                        icon: L.divIcon({
                            className: 'facility-burst-marker',
                            html: isBurst
                                ? `<div class="w-8 h-8 rounded-full bg-rose-600 border-2 border-rose-300 shadow-lg shadow-rose-600/70 flex items-center justify-center text-sm animate-bounce cursor-pointer">💥</div>`
                                : `<div class="w-7 h-7 rounded-full bg-slate-700 border border-slate-400 flex items-center justify-center text-xs">📦</div>`,
                            iconSize: [32, 32],
                            iconAnchor: [16, 16]
                        })
                    }).addTo(map);

                    fMarker.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-rose-400 text-sm">【🔴 现状单柜设施: ${f.name}】</div>
                            <div class="${isBurst ? 'text-rose-400 font-bold' : 'text-slate-300'}">
                                ${isBurst ? '⚠️ 严重超载爆柜！包裹大量外溢' : '常规负荷状态'}
                            </div>
                            <div>有效容量: <span class="mono font-bold text-white">${f.effective_capacity ?? 0} 件</span></div>
                            <div>指派自提需求: <span class="mono font-bold text-white">${f.assigned_demand ?? 0} 件</span></div>
                            <div>峰值饱和度: <span class="mono font-bold ${isBurst ? 'text-rose-400' : 'text-slate-200'}">${satPct}%</span></div>
                            <div class="text-[10px] text-slate-400">状态由当前社区容量约束计算，不按社区编号预设</div>
                        </div>`
                    );
                    mapLayers.push(fMarker);
                });
            } else if (schemeMode.value === 'optimized') {
                const optFacs = p.optimized_plan?.facilities || p.layout?.facilities || [];
                optFacs.forEach(f => {
                    if (!f.active) return;
                    const isExpanded = (f.slave_units > 0);
                    const fMarker = L.marker([f.lat, f.lng], {
                        icon: L.divIcon({
                            className: 'facility-shield-marker',
                            html: `<div class="w-8 h-8 rounded-full bg-emerald-600 border-2 border-emerald-300 shadow-lg shadow-emerald-500/50 flex items-center justify-center text-sm cursor-pointer">🛡️</div>`,
                            iconSize: [32, 32],
                            iconAnchor: [16, 16]
                        })
                    }).addTo(map);

                    fMarker.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-emerald-400 text-sm">【🟢 优化智能柜: ${f.name}】</div>
                            <div class="${f.is_full_risk ? 'text-rose-300' : 'text-emerald-300'} font-bold">${f.is_full_risk ? '⚠️ 容量约束未通过' : '✅ 当前情景容量约束通过'}</div>
                            <div>MIP定容配置: 主柜 ${f.main_lockers} 组 + 扩容副柜 <span class="text-emerald-300 font-bold">${f.slave_units}</span> 组</div>
                            <div>总格口数: <span class="mono font-bold text-white">${f.total_slots}</span> 格</div>
                            <div>日有效承载: <span class="mono font-bold text-cyan-300">${f.effective_capacity}</span> 件</div>
                            <div>容量负荷率: <span class="mono font-bold text-emerald-400">${f.saturation_pct ?? Math.round((f.utilization_rate ?? 0) * 100)}%</span></div>
                            <div class="text-[10px] text-slate-400">150m服务约束由后端逐楼栋校验</div>
                        </div>`
                    );
                    mapLayers.push(fMarker);

                    if (showRings.value) {
                        const circle = L.circle([f.lat, f.lng], {
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
                // ⚡ 双方案同屏对比模式 (Diff)
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

                    const fMarker = L.marker([f.lat, f.lng], {
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
                                    <span>🔴 现状方案 (As-Is):</span>
                                    <span class="text-[10px] px-1 rounded ${isBurst ? 'bg-rose-800 text-white' : 'bg-slate-800'}">${isBurst ? '爆柜风险' : '正常'}</span>
                                </div>
                                <div class="text-slate-300">容量状态: <b class="text-rose-400">${baseSat}</b></div>
                            </div>
                            <div class="bg-emerald-950/50 p-2 rounded border border-emerald-800/70 space-y-0.5">
                                <div class="text-emerald-400 font-bold flex items-center justify-between">
                                    <span>🟢 优化方案 (To-Be):</span>
                                    <span class="text-[10px] px-1 rounded bg-emerald-800 text-white font-bold">健康受控</span>
                                </div>
                                <div class="text-slate-300">副柜 <b class="text-emerald-300">+${f.slave_units}</b> 组 (${f.effective_capacity}件) · 饱和度: <b class="text-emerald-300">${optSat}%</b></div>
                            </div>
                            <div class="text-[10px] text-cyan-300 pt-0.5">
                                优化容量 ${f.effective_capacity} 件；是否可行以约束校验为准
                            </div>
                        </div>`
                    );
                    mapLayers.push(fMarker);

                    if (showRings.value) {
                        const circle = L.circle([f.lat, f.lng], {
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
            // 7A. 现状快递员全量步巡路线 (红色虚线，纯人工重负荷)
            if (schemeMode.value === 'baseline' || schemeMode.value === 'diff') {
                const basePath = p.baseline_plan?.courier_path || p.routing?.baseline_courier_path;
                if (basePath && basePath.length > 1) {
                    const baseCoords = basePath.map(pt => [pt.lat, pt.lng]);
                    const baseLine = L.polyline(baseCoords, {
                        color: '#f43f5e',
                        weight: 3.2,
                        opacity: schemeMode.value === 'diff' ? 0.70 : 0.88,
                        dashArray: '7, 5'
                    }).addTo(map);

                    baseLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-rose-400">【🔴 现状快递员全量步巡路线 (As-Is)】</div>
                            <div>步巡总里程: <span class="mono font-bold text-rose-400">${p.baseline_plan?.courier_walk_dist_km ?? '—'} km</span></div>
                            <div>人工总工时: <span class="mono font-bold text-rose-400">${p.baseline_plan?.courier_total_hours ?? '—'} h</span></div>
                            <div class="text-slate-300 text-[10px]">纯人工覆盖全部楼栋自提与上门，疲劳过载</div>
                        </div>`
                    );
                    mapLayers.push(baseLine);
                }
            }

            // 7B. 优化 M2 无人车社区巡航路线 (亮天蓝色高亮线)
            if (schemeMode.value === 'optimized' || schemeMode.value === 'diff') {
                if (p.routing && p.routing.unmanned_vehicle_path && p.routing.unmanned_vehicle_path.length > 1) {
                    const uvCoords = p.routing.unmanned_vehicle_path.map(pt => [pt.lat, pt.lng]);
                    const uvLine = L.polyline(uvCoords, {
                        color: '#38bdf8',
                        weight: 4.5,
                        opacity: 0.95
                    }).addTo(map);

                    uvLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-sky-400">【🟢 优化 M2 无人车社区巡航路线】</div>
                            <div>巡航里程: <span class="mono font-bold text-white">${p.routing.unmanned_vehicle_dist_km} km</span></div>
                            <div>巡航耗时: <span class="mono text-slate-200">${p.routing.unmanned_vehicle_time_min} min</span></div>
                            <div>服务点数: ${p.routing.unmanned_vehicle_path.length} 处</div>
                            <div class="text-emerald-400 text-[10px]">无人物流巡航投柜，解放末端重搬运</div>
                        </div>`
                    );
                    mapLayers.push(uvLine);
                }

                // 7C. 优化后快递员精准上门步巡路线 (橙色虚线，仅上门子集)
                if (p.routing && p.routing.courier_path && p.routing.courier_path.length > 1) {
                    const cCoords = p.routing.courier_path.map(pt => [pt.lat, pt.lng]);
                    const cLine = L.polyline(cCoords, {
                        color: '#f97316',
                        weight: 2.5,
                        opacity: 0.88,
                        dashArray: '5, 5'
                    }).addTo(map);

                    cLine.bindPopup(
                        `<div class="text-xs space-y-1">
                            <div class="font-bold text-orange-400">【🟢 优化后快递员精准上门步巡】</div>
                            <div>步巡里程: <span class="mono font-bold text-emerald-400">${p.routing.courier_walk_dist_km} km</span> <span class="text-emerald-400 text-[10px]">改善 ${p.community_comparison?.walk_saving_pct ?? '—'}%</span></div>
                            <div>上门工时: <span class="mono font-bold text-emerald-400">${p.routing.courier_total_hours} h</span> <span class="text-emerald-400 text-[10px]">改善 ${p.community_comparison?.hours_saving_pct ?? '—'}%</span></div>
                            <div class="text-slate-300 text-[10px]">人机接驳协同，专注高品质入户服务</div>
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
                    legend: { data: ['总件量', '送货上门', '自提柜'], textStyle: { color: '#94a3b8' }, top: 0 },
                    grid: { top: 35, left: 45, right: 15, bottom: 25 },
                    xAxis: { type: 'category', data: periods, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisLine: { lineStyle: { color: '#334155' } } },
                    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
                    series: [
                        { name: '总件量', type: 'line', smooth: true, data: totals, itemStyle: { color: '#38bdf8' }, lineStyle: { width: 3 } },
                        { name: '送货上门', type: 'bar', stack: 'mode', data: doors, itemStyle: { color: '#f97316' } },
                        { name: '自提柜', type: 'bar', stack: 'mode', data: lockers, itemStyle: { color: '#10b981' } }
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
                xAxis: { type: 'category', data: labels, axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
                yAxis: { type: 'value', name: 'km', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
                series: [{
                    name: '巡回里程',
                    type: 'line',
                    smooth: true,
                    data: dists,
                    itemStyle: { color: '#06b6d4' },
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
                legend: { data: ['上界 (整数可行解)', '下界 (松弛界限)'], textStyle: { color: '#94a3b8', fontSize: 10 }, top: 0 },
                grid: { top: 35, left: 55, right: 20, bottom: 25 },
                xAxis: { type: 'category', data: nodes, axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
                yAxis: { type: 'value', name: '元', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
                series: [
                    { name: '上界 (整数可行解)', type: 'line', data: ubs, itemStyle: { color: '#f59e0b' }, lineStyle: { width: 2 } },
                    { name: '下界 (松弛界限)', type: 'line', data: lbs, itemStyle: { color: '#10b981' }, lineStyle: { width: 2, type: 'dashed' } }
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
                    legend: { data: ['未扩容基准(严重满柜)', 'MIP优化扩容(安全承载)'], textStyle: { color: '#94a3b8' }, top: 0 },
                    grid: { top: 35, left: 45, right: 25, bottom: 25 },
                    xAxis: { type: 'category', data: sim.timeline.hours, axisLabel: { color: '#94a3b8' }, axisLine: { lineStyle: { color: '#334155' } } },
                    yAxis: { type: 'value', max: 150, axisLabel: { formatter: '{value}%', color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
                    series: [
                        {
                            name: '未扩容基准(严重满柜)',
                            type: 'line',
                            data: sim.timeline.locker_occupancy_baseline,
                            itemStyle: { color: '#ef4444' },
                            lineStyle: { width: 3, type: 'dashed' },
                            markLine: { data: [{ yAxis: 100, name: '满柜红线', lineStyle: { color: '#ef4444', width: 2 } }] }
                        },
                        {
                            name: 'MIP优化扩容(安全承载)',
                            type: 'line',
                            smooth: true,
                            data: sim.timeline.locker_occupancy_optimized,
                            itemStyle: { color: '#10b981' },
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
                    legend: { data: ['现状(纯人工)', '优化后人工', '人机协同(推荐)'], textStyle: { color: '#94a3b8' }, bottom: 0 },
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
                        axisName: { color: '#94a3b8', fontSize: 10 },
                        splitArea: { show: false },
                        splitLine: { lineStyle: { color: '#1e293b' } },
                        axisLine: { lineStyle: { color: '#334155' } }
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
                            itemStyle: { color: ['#64748b', '#f59e0b', '#06b6d4'][index] }
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
                    legend: { data: ['年运营总成本 (万元)', '年碳排放 (kg CO₂)'], textStyle: { color: '#94a3b8' }, top: 0 },
                    grid: { top: 35, left: 45, right: 45, bottom: 25 },
                    xAxis: { type: 'category', data: names, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisLine: { lineStyle: { color: '#334155' } } },
                    yAxis: [
                        { type: 'value', name: '万元', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
                        { type: 'value', name: 'kg', axisLabel: { color: '#94a3b8' }, splitLine: { show: false } }
                    ],
                    series: [
                        { name: '年运营总成本 (万元)', type: 'bar', data: costs, itemStyle: { color: '#f59e0b' }, barWidth: 26 },
                        { name: '年碳排放 (kg CO₂)', type: 'line', yAxisIndex: 1, data: carbons, itemStyle: { color: '#f59e0b' }, lineStyle: { width: 3 } }
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
                            color: t.type === 'UV_TRIP' ? '#06b6d4' : '#f59e0b'
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
                            color: '#94a3b8',
                            formatter: (val) => {
                                const totalM = val + 480;
                                return `${Math.floor(totalM/60).toString().padStart(2, '0')}:${(totalM%60).toString().padStart(2, '0')}`;
                            }
                        },
                        splitLine: { lineStyle: { color: '#1e293b' } }
                    },
                    yAxis: {
                        type: 'category',
                        data: entities,
                        axisLabel: { color: '#cbd5e1', fontSize: 10 },
                        splitLine: { show: true, lineStyle: { color: '#1e293b' } }
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
                    legend: { data: ['🔴 S0现有柜体占用', '🟢 S2优化柜体占用'], textStyle: { color: '#94a3b8', fontSize: 11 }, top: 0 },
                    grid: { top: 35, left: 45, right: 25, bottom: 25 },
                    xAxis: { type: 'category', data: hours, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisLine: { lineStyle: { color: '#334155' } } },
                    yAxis: { 
                        type: 'value', 
                        max: saturationMax,
                        axisLabel: { formatter: '{value}%', color: '#94a3b8' }, 
                        splitLine: { lineStyle: { color: '#1e293b' } } 
                    },
                    series: [
                        {
                            name: '🔴 S0现有柜体占用',
                            type: 'line',
                            data: baseSat,
                            itemStyle: { color: '#ef4444' },
                            lineStyle: { width: 3, type: 'dashed' },
                            markLine: {
                                symbol: 'none',
                                label: { formatter: '100% 满柜红线', color: '#ef4444', position: 'insideEndTop' },
                                data: [{ yAxis: 100, lineStyle: { color: '#ef4444', width: 2, type: 'solid' } }]
                            }
                        },
                        {
                            name: '🟢 S2优化柜体占用',
                            type: 'line',
                            smooth: true,
                            data: optSat,
                            itemStyle: { color: '#10b981' },
                            areaStyle: { color: 'rgba(16, 185, 129, 0.18)' },
                            lineStyle: { width: 3 }
                        }
                    ]
                });
            }

            // 6. Tab 0 全景对比: 综合效益多维雷达对照 (#chart-comp-radar)
            if (chartCompRadar && overview.value?.comparison_metrics) {
                const metrics = overview.value.comparison_metrics;
                const lowerScore = (key, side) => {
                    const base = Number(metrics[key]?.baseline ?? 0);
                    const value = Number(metrics[key]?.[side] ?? 0);
                    return value > 0 && base > 0 ? Math.min(100, 100 * base / value) : 0;
                };
                const s0FeasibleScore = simulationResult.value?.summary?.scheme_status?.S0 === 'FEASIBLE' ? 100 : 0;
                const feasibleScore = simulationResult.value?.summary?.scheme_status?.S2 === 'FEASIBLE' ? 100 : 0;
                chartCompRadar.setOption({
                    backgroundColor: 'transparent',
                    legend: { data: ['🔴 现状纯人工 (As-Is)', '🟢 人机协同 (To-Be)'], textStyle: { color: '#94a3b8', fontSize: 10 }, bottom: 0 },
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
                        axisName: { color: '#94a3b8', fontSize: 10 },
                        splitArea: { show: false },
                        splitLine: { lineStyle: { color: '#1e293b' } },
                        axisLine: { lineStyle: { color: '#334155' } }
                    },
                    series: [{
                        type: 'radar',
                        data: [
                            { value: [100, 100, 100, 100, s0FeasibleScore, Number(metrics.coverage_rate?.baseline ?? 0)], name: '🔴 现状纯人工 (As-Is)', itemStyle: { color: '#f43f5e' }, lineStyle: { type: 'dashed', width: 2 } },
                            { value: [lowerScore('trunk_distance', 'optimized'), lowerScore('labor_hours', 'optimized'), lowerScore('annual_carbon', 'optimized'), lowerScore('annual_cost', 'optimized'), feasibleScore, Number(metrics.coverage_rate?.optimized ?? 0)], name: '🟢 人机协同 (To-Be)', itemStyle: { color: '#06b6d4' }, areaStyle: { color: 'rgba(6, 182, 212, 0.28)' }, lineStyle: { width: 2.5 } }
                        ]
                    }]
                });
            }

            // 7. Tab 0 全景对比: 年运营成本与运营碳排对比 (#chart-comp-cost)
            if (chartCompCost && overview.value?.comparison_metrics) {
                const metrics = overview.value.comparison_metrics;
                const costData = [metrics.annual_cost.baseline / 10000, metrics.annual_cost.optimized / 10000];
                const carbonData = [metrics.annual_carbon.baseline, metrics.annual_carbon.optimized];
                chartCompCost.setOption({
                    backgroundColor: 'transparent',
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['年运营成本 (万元)', '年运营碳排 (kg CO₂e)'], textStyle: { color: '#94a3b8', fontSize: 10 }, top: 0 },
                    grid: { top: 35, left: 45, right: 45, bottom: 25 },
                    xAxis: { type: 'category', data: ['🔴 现状方案 (As-Is)', '🟢 优化协同 (To-Be)'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
                    yAxis: [
                        { type: 'value', name: '万元', axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b' } } },
                        { type: 'value', name: 'kg', axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false } }
                    ],
                    series: [
                        { 
                            name: '年运营成本 (万元)', 
                            type: 'bar', 
                            data: costData,
                            itemStyle: { 
                                color: (params) => params.dataIndex === 0 ? '#ef4444' : '#10b981' 
                            }, 
                            barWidth: 32,
                            label: { show: true, position: 'top', color: '#fff', fontSize: 11, formatter: '{c} 万' }
                        },
                        { 
                            name: '年运营碳排 (kg CO₂e)',
                            type: 'line', 
                            yAxisIndex: 1, 
                            data: carbonData,
                            itemStyle: { color: '#38bdf8' }, 
                            lineStyle: { width: 3 },
                            label: { show: true, position: 'top', color: '#38bdf8', fontSize: 10, formatter: '{c} kg' }
                        }
                    ]
                });
            }
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
            }
        });

        watch(solverModalTab, () => {
            renderMath();
        });

        return {
            activeTab,
            viewMode,
            toggleViewMode,
            schemeMode,
            setSchemeMode,
            loading,
            overview,
            comparisonMetric,
            metricValue,
            improvementText,
            changeText,
            savingValue,
            selectedCommunityId,
            planResult,
            simulationResult,
            simScenario,
            switchSimScenario,
            crisisResult,
            isPeakDay,
            showSolverModal,
            solverModalTab,
            mathModelsList,
            currentTileTheme,
            tileStatusText,
            showRoads,
            showPolygons,
            showRings,
            onChangeTileTheme,
            toggleRoads,
            togglePolygons,
            toggleRings,
            fitAllOverview,
            fitCurrentCommunity,
            customHouseholds,
            customDoorRatio,
            customIntensity,
            onSelectCommunity,
            onTweakParams,
            triggerCrisis,
            resizeCharts,
            renderMath,
            updateAllActiveCharts,
            // 高德相关
            amapConfig,
            showAmapModal,
            amapKeyInput,
            amapKeyMsg,
            amapSearchKeyword,
            amapExploring,
            amapExploreResult,
            saveAmapKey,
            searchAndExploreCommunity,
            // 学术级图谱相关
            academicFigures,
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
