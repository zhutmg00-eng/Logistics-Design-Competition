"""Compatibility adapter for the unified evaluation result.

The former module contained a second, hard-coded result set. The dashboard's
legacy ``/api/simulation`` shape is retained, but every number now comes from
``evaluation_results_v1.json`` through :class:`EvaluationEngine`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from core.evaluation_engine import EvaluationEngine


class SimulationEngine:
    SCENARIO_MAP = {
        "normal": "N", "peak": "P20", "disruption": "D-L",
        "N": "N", "P15": "P15", "P20": "P20",
        "D-R": "D-R", "D-V": "D-V", "D-L": "D-L",
    }

    def __init__(self, evaluation_engine: Optional[EvaluationEngine] = None):
        self.evaluation_engine = evaluation_engine or EvaluationEngine()

    def run_simulation(
        self,
        community_summaries=None,
        forecast_results=None,
        layout_results=None,
        routing_results=None,
        scenario: str = "normal",
    ) -> Dict[str, Any]:
        scenario_code = self.SCENARIO_MAP.get(scenario, scenario.upper())
        s0 = self.evaluation_engine.get_result("S0", scenario_code)
        s1 = self.evaluation_engine.get_result("S1", scenario_code)
        s2 = self.evaluation_engine.get_result("S2", scenario_code)
        config = self.evaluation_engine.config
        capacity = float(self.evaluation_engine.params["unmanned_capacity"])

        base_by_id = {row["community_id"]: row for row in s0["community_breakdown"]}
        community_results = []
        for row in s2["community_breakdown"]:
            base = base_by_id[row["community_id"]]
            trips = max(1, math.ceil(float(row["demand"]) / capacity))
            community_results.append({
                "community_id": row["community_id"], "name": row["name"],
                "daily_pkgs": row["demand"], "door_pkgs": row["door_demand"], "locker_pkgs": row["locker_demand"],
                "trips": trips, "uv_dist_km": row["unmanned_km"], "courier_walk_km": row["walk_km"],
                "sim_duration_min": s2["network_metrics"]["E06"],
                "labor_utilization_pct": round(row["labor_hours"] * 60 / 480 * 100, 1),
                "full_risk_baseline": "是" if base["full_minutes"] > 0 else "否",
                "full_risk_optimized": "是" if row["full_minutes"] > 0 else "否",
                "overflow_pkgs_baseline": base["overflow_pkgs"], "overflow_pkgs_optimized": row["overflow_pkgs"],
                "coverage_pct_baseline": base["coverage_pct"], "coverage_pct_optimized": row["coverage_pct"],
            })

        hours = list(config["arrival_weights"].keys())
        base_series = s0["time_series"]["locker_occupancy"]
        opt_series = s2["time_series"]["locker_occupancy"]
        timeline = {
            "hours": hours,
            "hourly_arrivals": [round(s2["source_and_assumptions"]["locker_total"] * config["arrival_weights"][hour], 1) for hour in hours],
            "locker_occupancy_baseline": [point["saturation_pct"] for point in base_series],
            "locker_occupancy_optimized": [point["saturation_pct"] for point in opt_series],
        }
        discrete_events = []
        for index, hour in enumerate(hours):
            base_sat, opt_sat = base_series[index]["saturation_pct"], opt_series[index]["saturation_pct"]
            discrete_events.append({
                "time": hour, "event": "分时到件与居民取件释放", "incoming_pkgs": timeline["hourly_arrivals"][index],
                "baseline_sat": "n.a." if base_sat is None else f"{base_sat:.1f}%",
                "optimized_sat": "n.a." if opt_sat is None else f"{opt_sat:.1f}%",
                "bottleneck_status": "基准存在未覆盖/溢出" if s0["service_metrics"]["S04"] > 0 else "容量正常",
            })

        return {
            "scenario": scenario_code, "scenario_name": s2["scenario_name"],
            "peak_factor": config["scenarios"][scenario_code]["demand_factor"],
            "is_disruption": scenario_code.startswith("D-"),
            "summary": {
                "total_pkgs": s2["source_and_assumptions"]["demand_total"],
                "total_door_pkgs": s2["source_and_assumptions"]["door_total"],
                "total_locker_pkgs": s2["source_and_assumptions"]["locker_total"],
                "courier_hours_saving_pct": self.evaluation_engine.improvement_rate(s0["resource_metrics"]["R01"], s2["resource_metrics"]["R01"]),
                "carbon_saving_pct": self.evaluation_engine.improvement_rate(s0["carbon_metrics"]["G02"], s2["carbon_metrics"]["G02"]),
                "cost_saved_annual_rmb": s2["cost_metrics"]["C05"], "payback_years": s2["cost_metrics"]["C06"],
                "scheme_status": {"S0": s0["status"], "S1": s1["status"], "S2": s2["status"]},
            },
            "community_results": community_results,
            "table_8_4": [
                {"item": "全网需求件量（件）", "value": s2["source_and_assumptions"]["demand_total"]},
                {"item": "S2完成率（%）", "value": s2["robustness_metrics"]["B01"]},
                {"item": "S2日终未完成（件）", "value": s2["service_metrics"]["S04"]},
                {"item": "S2满柜累计时长（min）", "value": s2["service_metrics"]["S05"]["full_minutes"]},
            ],
            "scenarios_comparison": [
                self._comparison_row("S0 现状基准", s0), self._comparison_row("S1 网络与设施优化", s1),
                self._comparison_row("S2 人机协同推荐", s2),
            ],
            "comparison_metrics": self.evaluation_engine.legacy_comparison_metrics(),
            "timeline": timeline, "community_timelines": {}, "gantt_schedule": self._gantt(community_results),
            "discrete_events": discrete_events,
            "solver_metrics": {"solver_name": "Unified-Evaluation-Engine", "solve_time_ms": s2["robustness_metrics"]["B05"], "time_steps": len(hours), "status": s2["status"]},
            "solver_logs": [
                f"[INPUT] {s2['input_version']} / {s2['source_and_assumptions']['demand_total']}件",
                "[SIM] 确定性情景推演：动态占用与取件释放，饱和度不截断",
                f"[CHECK] S2硬约束违反 {s2['robustness_metrics']['B03']} 次，状态={s2['status']}",
                "[OUTPUT] 结果来自 data/evaluation_results_v1.json，无手工指标覆盖",
            ],
            "math_formulation": {
                "model_code": "M8", "model_name": "动态柜体占用与释放确定性情景推演",
                "equations": [
                    {"title": "柜体占用状态转移", "latex": r"O_j(t+1)=\max(0,O_j(t)+A_j(t)-D_j(t))"},
                    {"title": "满柜判定", "latex": r"I_j(t)=\mathbb{1}[O_j(t)>C_j^{eff}]"},
                ],
            },
            "evaluation_result": s2,
        }

    @staticmethod
    def _comparison_row(name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "scenario": name, "trunk_km": result["network_metrics"]["E01"],
            "courier_walk_km": result["network_metrics"]["E02"], "courier_hours": result["resource_metrics"]["R01"],
            "annual_cost_rmb": result["cost_metrics"]["C02"], "annual_carbon_kg": result["carbon_metrics"]["G02"],
            "bottleneck": result["status"],
        }

    @staticmethod
    def _gantt(community_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks, cursor = [], 8 * 60
        for community in community_results:
            duration = max(25, int(community["uv_dist_km"] / 12 * 60 + community["trips"] * 5))
            end = min(21 * 60, cursor + duration)
            tasks.append({
                "entity": "无人配送车（统筹班次）", "type": "UV_TRIP",
                "label": f"{community['name']} {community['trips']}趟", "community": community["name"],
                "start_time": f"{cursor // 60:02d}:{cursor % 60:02d}", "end_time": f"{end // 60:02d}:{end % 60:02d}",
                "duration_min": end - cursor, "status": "COMPLETED" if community["overflow_pkgs_optimized"] == 0 else "INCOMPLETE",
            })
            cursor = min(20 * 60, end + 10)
        return tasks


if __name__ == "__main__":
    print(SimulationEngine().run_simulation(scenario="normal")["summary"])
