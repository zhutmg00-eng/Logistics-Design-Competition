"""
FastAPI Backend Server for Logistics Digital Twin & Optimization Platform
(超大城市末端配送数智化与协同规划平台服务端)
"""

import os
import sys

# Ensure local core packages are importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.data_manager import DataManager
from core.forecast_model import DemandForecastEngine
from core.layout_optimizer import LayoutOptimizer
from core.routing_engine import RoutingEngine
from core.simulation_engine import SimulationEngine
from core.evaluation_engine import EvaluationEngine
from core.ai_copilot import AICopilot
from core.amap_client import AmapClient

app = FastAPI(title="面向超大城市的末端配送协同网络规划与数智化平台", version="1.2.0")

# Initialize core modules
data_manager = DataManager()
forecast_engine = DemandForecastEngine()
layout_optimizer = LayoutOptimizer()
routing_engine = RoutingEngine()
evaluation_engine = EvaluationEngine()
simulation_engine = SimulationEngine(evaluation_engine)
ai_copilot = AICopilot()
amap_client = AmapClient()

# Static files directory
static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Server is running. Please add static/index.html"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

GLOBAL_COMPARISON_METRICS = evaluation_engine.legacy_comparison_metrics()


def _community_facilities_status():
    s0 = evaluation_engine.get_result("S0", "N")
    s2 = evaluation_engine.get_result("S2", "N")
    baseline = {row["community_id"]: row for row in s0["community_breakdown"]}
    optimized = {row["community_id"]: row for row in s2["community_breakdown"]}
    status = {}
    for cid, base in baseline.items():
        opt = optimized[cid]
        status[cid] = {
            "community_name": base["name"],
            "baseline": {
                "capacity": base["locker_capacity"], "demand": base["locker_demand"],
                "saturation": base["peak_occupancy_pct"], "full_risk": base["full_minutes"] > 0,
                "coverage_pct": base["coverage_pct"], "overflow_pkgs": base["overflow_pkgs"],
                "desc": "动态占用结果；覆盖不足单独列示"
            },
            "optimized": {
                "capacity": opt["locker_capacity"], "demand": opt["locker_demand"],
                "saturation": opt["peak_occupancy_pct"], "full_risk": opt["full_minutes"] > 0,
                "coverage_pct": opt["coverage_pct"], "overflow_pkgs": opt["overflow_pkgs"],
                "desc": "P20定容、普通日动态占用结果"
            }
        }
    return status

@app.get("/api/overview")
def get_overview():
    facilities_status = _community_facilities_status()
    communities = data_manager.get_all_overview()
    for c in communities:
        cid = c["id"]
        status = facilities_status.get(cid, {})
        c["baseline_facility"] = status.get("baseline", {"capacity": 50, "saturation": 0, "full_risk": False})
        c["optimized_facility"] = status.get("optimized", {"capacity": 50, "saturation": 0, "full_risk": False})
        c["full_risk_baseline"] = c["baseline_facility"]["full_risk"]
        c["full_risk_optimized"] = c["optimized_facility"]["full_risk"]

    trunk_result = routing_engine.solve_trunk_m1(communities)
    official = evaluation_engine.load_results()
    trunk_result["baseline_dist_km"] = official["results"]["S0-N"]["network_metrics"]["E01"]
    trunk_result["tour_dist_km"] = official["results"]["S2-N"]["network_metrics"]["E01"]
    return {
        "communities": communities,
        "trunk_routing": trunk_result,
        "facilities_status": facilities_status,
        "comparison_metrics": GLOBAL_COMPARISON_METRICS,
        "evaluation": {
            "input_version": official["input_version"],
            "normal_day_total": official["frozen_input_summary"]["normal_day_total"],
            "scheme_status": {code: official["results"][f"{code}-N"]["status"] for code in ("S0", "S1", "S2")},
            "source": "data/evaluation_results_v1.json"
        },
        "hub": routing_engine.hub
    }

@app.get("/api/community/{cid}")
def get_community_detail(cid: str):
    if cid not in data_manager.communities:
        raise HTTPException(status_code=404, detail="Community not found")
    summary = data_manager.get_community_summary(cid)
    return summary

class CalculationRequest(BaseModel):
    community_id: str
    custom_households: Optional[int] = None
    custom_door_ratio: Optional[float] = None
    custom_intensity: Optional[float] = None
    is_peak_day: Optional[bool] = False

@app.post("/api/calculate")
def calculate_plan(req: CalculationRequest):
    cid = req.community_id
    summary = data_manager.get_community_summary(cid)
    if not summary["info"] and cid not in ["CUSTOM", "NEW"]:
        raise HTTPException(status_code=404, detail="Community not found")

    households = req.custom_households or summary["total_households"] or 500
    custom_params = {}
    if req.custom_door_ratio is not None:
        custom_params["door_ratio"] = req.custom_door_ratio
    if req.custom_intensity is not None:
        custom_params["intensity"] = req.custom_intensity

    # 1. 需求预测 (第5章 M5)
    forecast = forecast_engine.predict_community(cid, households, custom_params)
    if req.is_peak_day:
        forecast["daily_total"] = forecast["peak_total"]
        forecast["daily_door"] = forecast["peak_door"]
        forecast["daily_locker"] = forecast["peak_locker"]

    buildings_forecast = forecast_engine.predict_buildings(summary["demand_nodes"], forecast)

    # 2. 选址与定容优化 (第6章 M6)
    layout = layout_optimizer.optimize(cid, buildings_forecast, summary["facilities"])

    # 3. 协同路径规划 (第7章 M2)
    active_facilities = layout["facilities"]
    routing = routing_engine.solve_community_m2(cid, buildings_forecast, active_facilities)

    # 4. AI 智能诊断建议
    ai_report = ai_copilot.generate_community_diagnosis(summary["info"], forecast, layout, routing)

    # 5. 求解控制台综合遥测指标汇总
    t_fc = forecast["solver_metrics"]["solve_time_ms"]
    t_lo = layout["solver_metrics"]["solve_time_ms"]
    t_ro = routing["solver_metrics"]["solve_time_ms"]
    total_solve_time = round(t_fc + t_lo + t_ro, 3)

    aggregated_logs = []
    aggregated_logs.append(f"====== [OR SOLVER PIPELINE INITIATED: COMMUNITY {cid}] ======")
    aggregated_logs.extend(forecast.get("solver_logs", []))
    aggregated_logs.extend(layout.get("solver_logs", []))
    aggregated_logs.extend(routing.get("solver_logs", []))
    aggregated_constraints = []
    if "constraint_checks" in layout:
        aggregated_constraints.extend(layout["constraint_checks"])
    if "constraint_checks" in routing:
        aggregated_constraints.extend(routing["constraint_checks"])

    violation_tokens = ("VIOLATED", "OVERLOAD_VIOLATION", "OVERTIME_WARNING", "INFEASIBLE")
    violation_count = sum(
        1 for item in aggregated_constraints
        if str(item.get("status", "")).upper() in violation_tokens
    )
    pipeline_status = "INFEASIBLE" if violation_count else "FEASIBLE_HEURISTIC"
    aggregated_logs.append(
        f"====== [OR PIPELINE COMPLETED IN {total_solve_time} ms | STATUS: {pipeline_status}] ======"
    )

    solver_console = {
        "total_solve_time_ms": total_solve_time,
        "pipeline_status": pipeline_status,
        "hard_constraint_violations": violation_count,
        "solver_breakdown": {
            "M5_forecast_ms": t_fc,
            "M6_layout_mip_ms": t_lo,
            "M2_routing_cvrp_ms": t_ro
        },
        "aggregated_logs": aggregated_logs,
        "constraint_checks": aggregated_constraints
    }

    # 构建现状方案 (As-Is Baseline) 与 优化方案 (To-Be Optimized) 完整结构
    base_facs = layout.get("baseline_facilities", [])
    opt_facs = layout.get("facilities", [])
    base_risk = layout.get("full_risk_baseline", False)
    base_walk = routing.get("baseline_courier_walk_dist_km", 0)
    opt_walk = routing.get("courier_walk_dist_km", 0)
    base_hours = routing.get("baseline_courier_total_hours", 0)
    opt_hours = routing.get("courier_total_hours", 0)

    max_base_sat = round(max([f.get("saturation_pct", 0) for f in base_facs if f.get("active")] or [0]), 1)
    max_opt_sat = round(max([f.get("saturation_pct", 0) for f in opt_facs if f.get("active")] or [0]), 1)

    baseline_plan = {
        "facilities": base_facs,
        "courier_walk_dist_km": base_walk,
        "courier_total_hours": base_hours,
        "courier_path": routing.get("baseline_courier_path", []),
        "is_full_risk": base_risk,
        "total_capacity": layout.get("baseline_total_capacity", 50),
        "saturation_pct": max_base_sat
    }

    optimized_plan = {
        "facilities": opt_facs,
        "courier_walk_dist_km": opt_walk,
        "courier_total_hours": opt_hours,
        "courier_path": routing.get("courier_path", []),
        "unmanned_vehicle_dist_km": routing.get("unmanned_vehicle_dist_km", 0),
        "unmanned_vehicle_time_min": routing.get("unmanned_vehicle_time_min", 0),
        "unmanned_vehicle_path": routing.get("unmanned_vehicle_path", []),
        "trips_needed": routing.get("trips_needed", 1),
        "loading_plan": routing.get("loading_plan", []),
        "is_full_risk": layout.get("full_risk_optimized", False),
        "total_capacity": layout.get("total_effective_capacity", 50),
        "saturation_pct": max_opt_sat if max_opt_sat > 0 else round(layout.get("overall_utilization", 0.65) * 100, 1)
    }

    community_comparison = {
        "walk_saving_km": round(base_walk - opt_walk, 2),
        "walk_saving_pct": round((base_walk - opt_walk) / base_walk * 100, 1) if base_walk > 0 else 0,
        "hours_saving_h": round(base_hours - opt_hours, 2),
        "hours_saving_pct": round((base_hours - opt_hours) / base_hours * 100, 1) if base_hours > 0 else 0,
        "capacity_gain": layout.get("total_effective_capacity", 0) - layout.get("baseline_total_capacity", 50),
        "full_risk_eliminated": base_risk
    }

    return {
        "community_id": cid,
        "community_name": summary["info"].get("name", cid),
        "polygon": summary["info"].get("polygon", []),
        "road_nodes": summary.get("road_nodes", []),
        "road_edges": summary.get("road_edges", []),
        "forecast": forecast,
        "buildings": buildings_forecast,
        "layout": layout,
        "routing": routing,
        "baseline_plan": baseline_plan,
        "optimized_plan": optimized_plan,
        "community_comparison": community_comparison,
        "comparison_metrics": evaluation_engine.legacy_comparison_metrics(),
        "ai_report": ai_report,
        "solver_console": solver_console
    }

@app.get("/api/simulation")
def run_full_simulation(scenario: str = "normal"):
    return simulation_engine.run_simulation(scenario=scenario)


@app.get("/api/evaluation")
def get_evaluation(scheme: str = "S2", scenario: str = "N"):
    try:
        return evaluation_engine.get_result(scheme, scenario)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown scheme/scenario combination")


@app.get("/api/evaluation/matrix")
def get_evaluation_matrix():
    return evaluation_engine.load_results()

@app.get("/api/solver/models")
def get_all_math_models():
    """返回大赛核心数学模型库与LaTeX标准定义"""
    return {
        "models": [
            {
                "code": "M1",
                "chapter": "第7章 7.3",
                "name": "干线多社区协同巡回旅行商模型 (Trunk Tour TSP)",
                "type": "整数规划 / 组合优化 (IP / TSP)",
                "objective": r"\min Z_1 = \sum_{i \in V} \sum_{j \in V} c_{ij} \cdot x_{ij}",
                "description": "以亦庄片区物流综合枢纽 (HUB) 为起讫点，连接5个典型社区接驳点，消除现状独立往返的空驶浪费。",
                "variables": [
                    {"symbol": "x_{ij}", "type": "0-1 决策变量", "meaning": "是否从节点 i 直接前往节点 j"},
                    {"symbol": "u_i", "type": "连续辅助变量", "meaning": "MTZ 阶梯计数，消除非连通子回路"}
                ],
                "constraints": [
                    {"name": "各节点唯一离开约束", "formula": r"\sum_{j \in V, j \ne i} x_{ij} = 1, \quad \forall i \in V"},
                    {"name": "各节点唯一到达约束", "formula": r"\sum_{i \in V, i \ne j} x_{ij} = 1, \quad \forall j \in V"},
                    {"name": "MTZ 子回路消除约束", "formula": r"u_i - u_j + |V| \cdot x_{ij} \le |V| - 1, \quad \forall i, j \ne \text{HUB}"}
                ]
            },
            {
                "code": "M2",
                "chapter": "第7章 7.3",
                "name": "社区人机协同双层路径规划模型 (Bi-level Intra-Community CVRP)",
                "type": "带容量约束车辆路径规划 (CVRP)",
                "objective": r"\min Z_2 = \sum_{k \in \mathcal{K}} \left( \sum_{i,j \in \mathcal{N}} d_{ij} x_{ijk} + \tau n_k \right) + \omega \sum_{i,j \in \mathcal{B}_{\text{door}}} d_{ij} w_{ij}",
                "description": "无人车承担干线接驳与社区智能柜巡航投柜；人工快递员从接驳点出发，仅对上门需求楼栋开展精细化步巡交付。",
                "variables": [
                    {"symbol": "x_{ijk}", "type": "0-1 决策变量", "meaning": "无人车班次 k 是否在节点 i, j 之间行驶"},
                    {"symbol": "w_{ij}", "type": "0-1 决策变量", "meaning": "快递员步巡上门是否在楼栋 i, j 之间步行"}
                ],
                "constraints": [
                    {"name": "无人车单车次载重体积双约束", "formula": r"\sum_{i \in \mathcal{N}} q_i \cdot y_{ik} \le \text{CAP} \; (400\,\text{件}), \quad \forall k \in \mathcal{K}"},
                    {"name": "节点被访唯一性约束", "formula": r"\sum_{k \in \mathcal{K}} y_{ik} = 1, \quad \forall i \in \mathcal{N}"},
                    {"name": "快递员工时与劳动强度约束", "formula": r"T_{\text{walk}} + T_{\text{service}} \le T_{\max} \; (480\,\text{min})"}
                ]
            },
            {
                "code": "M5",
                "chapter": "第5章 5.3",
                "name": "多尺度需求预测与Logit离散选择模型 (Multi-scale Forecast & MNL)",
                "type": "非线性效用模型 / 空间降尺度 (RUM / MNL)",
                "objective": r"P(\text{door} \mid i) = \frac{\exp(V_{\text{door}, i})}{\exp(V_{\text{door}, i}) + \exp(V_{\text{locker}, i})}",
                "description": "融合社区空间形态、老龄化率与取件便利度，精确解耦自提柜件与送货上门件的微观需求分布。",
                "variables": [
                    {"symbol": "V_{m, i}", "type": "确定性效用", "meaning": "社区 i 居民对配送方式 m 的系统效用"},
                    {"symbol": "d_{ib}", "type": "连续件量", "meaning": "楼栋 b 的日均预测快件量"}
                ],
                "constraints": [
                    {"name": "上门服务效用函数", "formula": r"V_{\text{door}, i} = \beta_0 + \beta_{\text{age}} \cdot \text{AgeRatio}_i + \beta_{\text{stair}} \cdot (1 - \text{HighRise}_i)"},
                    {"name": "智能柜自提效用函数", "formula": r"V_{\text{locker}, i} = \beta_1 - \beta_{\text{walk}} \cdot \frac{D_{\text{walk}, i}}{100} + \beta_{\text{flex}} \cdot \text{YoungRatio}_i"},
                    {"name": "空间降尺度守恒约束", "formula": r"\sum_{b \in \mathcal{B}_i} d_{ib} = D_i"}
                ]
            },
            {
                "code": "M6",
                "chapter": "第6章 6.4",
                "name": "容量受限选址定容混合整数规划模型 (Capacitated Facility Location & Sizing MIP)",
                "type": "混合整数线性规划 (MILP)",
                "objective": r"\min Z_6 = \sum_{j \in \mathcal{F}} \left( f_j y_j + c_s s_j \right) + \rho \sum_{i \in \mathcal{B}} \sum_{j \in \mathcal{F}} d_{ij} q_i x_{ij}",
                "description": "自适应决策保留/激活智能柜设施点及配置扩容副柜数量，并通过容量、覆盖与动态占用校验判断方案是否可行。",
                "variables": [
                    {"symbol": "y_j", "type": "0-1 变量", "meaning": "候选设施点 j 是否激活开启"},
                    {"symbol": "s_j", "type": "非负整数", "meaning": "设施点 j 安装扩容副柜组数"},
                    {"symbol": "x_{ij}", "type": "0-1 变量", "meaning": "楼栋 i 的自提快件是否指派给设施点 j 承接"}
                ],
                "constraints": [
                    {"name": "楼栋需求全覆盖指派约束", "formula": r"\sum_{j \in \mathcal{F}} x_{ij} = 1, \quad \forall i \in \mathcal{B}"},
                    {"name": "便民步行距离国家红线约束", "formula": r"d_{ij} \cdot x_{ij} \le R_{\max} \; (150\,\text{m}), \quad \forall i, j"},
                    {"name": "动态有效容量与翻台约束", "formula": r"\sum_{i \in \mathcal{B}} q_i \cdot x_{ij} \le \left( C_{\text{main}} y_j + C_{\text{slave}} s_j \right) \cdot \theta_{\text{turnover}}"},
                    {"name": "设施激活逻辑耦合约束", "formula": r"x_{ij} \le y_j, \quad s_j \le S_{\max} \cdot y_j"}
                ]
            },
            {
                "code": "M8",
                "chapter": "第8章 8.2",
                "name": "配送系统动态占用确定性情景推演模型",
                "type": "确定性状态转移 / 压力测试",
                "objective": r"\text{State Equation: } O_j(t + \Delta t) = \max\big(0, \; O_j(t) + A_j(t) - D_j(t)\big)",
                "description": "按冻结的分时到件权重与取件释放率推演08:00至21:00柜体占用；占用不按容量截断，因而可直接识别满柜时段与溢出量。",
                "variables": [
                    {"symbol": "O_j(t)", "type": "系统状态", "meaning": "时刻 t 设施点 j 内暂存快件占用量"},
                    {"symbol": r"A_j(t)", "type": "确定性到件量", "meaning": "时间步内按冻结情景权重分配的投递包裹数"}
                ],
                "constraints": [
                    {"name": "分时到件守恒", "formula": r"A_j(t)=Q_j\,w_t,\quad \sum_t w_t=1"},
                    {"name": "确定性取件释放", "formula": r"D_j(t)=O_j(t)\,p_t\,\gamma_s"},
                    {"name": "满柜与溢出判定", "formula": r"I_j(t)=\mathbb{1}[O_j(t)>C_j^{\text{eff}}],\quad U_j=\max_t\max(0,O_j(t)-C_j^{\text{eff}})"}
                ]
            }
        ]
    }

class CrisisRequest(BaseModel):
    event_type: str

@app.post("/api/crisis")
def handle_crisis(req: CrisisRequest):
    return ai_copilot.handle_crisis_event(req.event_type)

# ==========================================
# 高德开放平台 (Amap LBS / MCP) 接口
# ==========================================

class AmapKeyRequest(BaseModel):
    key: str

@app.get("/api/amap/config")
def get_amap_config():
    is_conf = amap_client.is_configured()
    test_res = amap_client.test_key() if is_conf else {"valid": False, "info": "尚未配置Key"}
    return {
        "configured": is_conf,
        "masked_key": amap_client.get_masked_key(),
        "status": test_res
    }

@app.post("/api/amap/config")
def save_amap_key(req: AmapKeyRequest):
    amap_client.save_key_to_config(req.key)
    test_res = amap_client.test_key()
    return {
        "configured": amap_client.is_configured(),
        "masked_key": amap_client.get_masked_key(),
        "test_result": test_res
    }

class AmapSearchRequest(BaseModel):
    keyword: str
    city: Optional[str] = "北京"

@app.post("/api/amap/search")
def search_community_amap(req: AmapSearchRequest):
    if not amap_client.is_configured():
        return {"success": False, "info": "高德 Key 尚未配置，请先在右上角填入您的 Key"}
    geo_res = amap_client.geocode(req.keyword, req.city)
    if not geo_res.get("success"):
        return {"success": False, "info": geo_res.get("info", "未找到该地点")}
    
    lng = geo_res["lng"]
    lat = geo_res["lat"]
    pois = amap_client.search_around_logistics(lng, lat, radius=800)
    weather = amap_client.get_weather(geo_res.get("adcode", "110100"))
    
    return {
        "success": True,
        "location": geo_res,
        "pois": pois,
        "weather": weather
    }

class AmapExploreRequest(BaseModel):
    community_name: str
    households: Optional[int] = 1200
    door_ratio: Optional[float] = 0.35
    intensity: Optional[float] = 0.6
    city: Optional[str] = "北京"

@app.post("/api/amap/explore")
def explore_community_with_amap(req: AmapExploreRequest):
    """
    高德全要素驱动的全新小区数智化规划流水线：
    1. 高德地理编码定位坐标
    2. 高德周边搜检索现存网点/快递柜
    3. 合成楼栋拓扑
    4. 驱动第5-8章全套运筹优化模型与AI诊断
    """
    import math
    if not amap_client.is_configured():
        return {"success": False, "info": "高德 Key 尚未配置，请先在右上角填入您的 Key"}
    
    geo_res = amap_client.geocode(req.community_name, req.city)
    if not geo_res.get("success"):
        return {"success": False, "info": f"未能解析小区【{req.community_name}】的坐标"}
    
    center_lng = geo_res["lng"]
    center_lat = geo_res["lat"]
    
    # 拉取周边现存快递设施
    nearby_pois = amap_client.search_around_logistics(center_lng, center_lat, radius=800)
    weather = amap_client.get_weather(geo_res.get("adcode", "110100"))
    
    # 动态合成 8-10 个微观楼栋节点（分布在小区中心周围 40-120米）
    building_count = 8
    buildings_raw = []
    households_per_b = req.households // building_count
    for b_idx in range(building_count):
        angle = (2 * math.pi / building_count) * b_idx
        radius_deg = 0.0008 + (b_idx % 3) * 0.0003 # 约 60-120 米
        b_lng = center_lng + radius_deg * math.cos(angle)
        b_lat = center_lat + radius_deg * math.sin(angle)
        buildings_raw.append({
            "id": f"AMAP-B{b_idx+1:02d}",
            "name": f"{b_idx+1}号楼",
            "lng": round(b_lng, 6),
            "lat": round(b_lat, 6),
            "households": households_per_b
        })
    
    # 动态构建设施点：以高德搜索到的周边真实驿站/快递柜为基础，若不足则在出入口生成候选点
    facilities_raw = []
    if nearby_pois:
        for p_idx, poi in enumerate(nearby_pois[:4]):
            facilities_raw.append({
                "id": f"AMAP-F{p_idx+1:02d}",
                "name": poi["name"][:16],
                "lng": poi["lng"],
                "lat": poi["lat"],
                "type": "智能柜/驿站"
            })
    else:
        # 默认南北门两座候选柜
        facilities_raw = [
            {"id": "AMAP-F01", "name": "东出入口智能接驳主柜", "lng": center_lng + 0.0005, "lat": center_lat, "type": "智能柜"},
            {"id": "AMAP-F02", "name": "西出入口智能备用柜", "lng": center_lng - 0.0005, "lat": center_lat, "type": "智能柜"}
        ]
    
    # 1. 需求预测 (第5章)
    cid = f"AMAP-{req.community_name}"
    forecast = forecast_engine.predict_community(cid, req.households, {
        "type_name": f"高德实景社区 ({geo_res.get('district', '')})",
        "door_ratio": req.door_ratio,
        "intensity": req.intensity
    })
    buildings_forecast = forecast_engine.predict_buildings(buildings_raw, forecast)
    
    # 2. 选址与定容优化 (第6章)
    layout = layout_optimizer.optimize(cid, buildings_forecast, facilities_raw)
    
    # 3. 协同路径规划 (第7章)
    routing = routing_engine.solve_community_m2(cid, buildings_forecast, layout["facilities"])
    
    # 4. AI 智能诊断
    comm_info = {
        "id": cid,
        "name": req.community_name,
        "address": geo_res["formatted_address"],
        "households": req.households,
        "center": [center_lat, center_lng]
    }
    ai_report = ai_copilot.generate_community_diagnosis(comm_info, forecast, layout, routing)
    
    return {
        "success": True,
        "community_name": req.community_name,
        "geo": geo_res,
        "weather": weather,
        "nearby_pois_count": len(nearby_pois),
        "forecast": forecast,
        "layout": layout,
        "routing": routing,
        "buildings": buildings_forecast,
        "ai_report": ai_report
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Server at http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
