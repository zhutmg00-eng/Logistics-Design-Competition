"""Unified S0/S1/S2 evaluation engine.

This module is the only owner of formal comparison numbers.  It uses one frozen
input object for every scheme, simulates cabinet occupancy without clipping it
at capacity, and exposes traceable metric/formula metadata for the paper, API
and dashboard.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from core.data_manager import DataManager
from core.forecast_model import DemandForecastEngine


METRIC_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "E01": {"name": "干线运输总里程", "unit": "km/日", "formula": "Σ执行干线路段距离"},
    "E02": {"name": "人工社区内行走里程", "unit": "km/日", "formula": "Σ人工步巡闭环里程"},
    "E03": {"name": "无人车运行里程", "unit": "km/日", "formula": "Σ无人车实际班次路径"},
    "E04": {"name": "机动车总里程", "unit": "km/日", "formula": "燃油与电动车里程分别累计"},
    "E05": {"name": "发车趟次", "unit": "次/日", "formula": "Σ实际执行班次"},
    "E06": {"name": "系统完成时间", "unit": "min/日", "formula": "末件完成时刻-首件可出库时刻"},
    "E07": {"name": "人均小时处理效率", "unit": "件/人时", "formula": "完成件量/人工总工时"},
    "E08": {"name": "准时完成率", "unit": "%", "formula": "时限内完成件量/到达件量"},
    "R01": {"name": "人工总工时", "unit": "人时/日", "formula": "Σ每名人员实际工作分钟/60"},
    "R02": {"name": "最低配置人数", "unit": "人", "formula": "ceil(人工总分钟/480)并校验时间窗"},
    "R03": {"name": "无人车配置数", "unit": "台", "formula": "满足班次时序且含1台故障备用"},
    "R04": {"name": "单趟装载率", "unit": "%", "formula": "q_k/CAP"},
    "R05": {"name": "柜体有效容量", "unit": "件", "formula": "Σ启用柜体有效容量"},
    "S01": {"name": "加权平均取件距离", "unit": "m", "formula": "Σ(q_i*d_i)/Σq_i，仅统计已指派自提件"},
    "S02": {"name": "95分位取件距离", "unit": "m", "formula": "需求加权P95"},
    "S03": {"name": "150m覆盖率", "unit": "%", "formula": "150m内已服务自提需求/全部自提需求"},
    "S04": {"name": "日终未完成件量", "unit": "件", "formula": "21:00仍未入柜或未交付件量"},
    "S05": {"name": "满柜风险", "unit": "个、min、件", "formula": "动态占用超过容量的社区数、时长与溢出件量"},
    "S06": {"name": "峰值柜体占用率", "unit": "%", "formula": "max_t O(t)/C_eff；不截断"},
    "S07": {"name": "上门件履约率", "unit": "%", "formula": "已完成上门件/应上门件"},
    "C01": {"name": "新增初始投资CAPEX", "unit": "元", "formula": "新增车辆+柜体+换电+系统"},
    "C02": {"name": "年现金运营成本OPEX", "unit": "元/年", "formula": "人工+能源+保险+维保+平台+柜运维"},
    "C03": {"name": "年化总成本", "unit": "元/年", "formula": "OPEX+年折旧"},
    "C04": {"name": "单件履约成本", "unit": "元/件", "formula": "年化总成本/年完成件量"},
    "C05": {"name": "年运营节约额", "unit": "元/年", "formula": "OPEX_S0-OPEX_方案"},
    "C06": {"name": "静态投资回收期", "unit": "年", "formula": "增量CAPEX/年度现金节约；节约<=0时不可用"},
    "G01": {"name": "年能源消耗", "unit": "L、kWh/年", "formula": "Σ里程*单位能耗*运营日"},
    "G02": {"name": "年运营碳排放", "unit": "kgCO2e/年", "formula": "燃油量*EF_fuel+用电量*EF_grid"},
    "G03": {"name": "年碳减排量", "unit": "kgCO2e/年", "formula": "CO2_S0-CO2_方案"},
    "G04": {"name": "单件碳排放", "unit": "kgCO2e/件", "formula": "年运营碳排放/年完成件量"},
    "B01": {"name": "需求承载率", "unit": "%", "formula": "完成件量/到达件量"},
    "B02": {"name": "异常恢复时间", "unit": "min", "formula": "异常发生至积压恢复到正常阈值"},
    "B03": {"name": "约束违反次数", "unit": "次", "formula": "容量、工时、距离、时间窗硬约束违反总数"},
    "B04": {"name": "算法稳定性", "unit": "km", "formula": "30个固定种子结果的均值、标准差、最好和最差"},
    "B05": {"name": "求解时间", "unit": "ms", "formula": "统一输入至方案结果的墙钟时间"},
}


class EvaluationEngine:
    def __init__(self, project_root: Optional[str] = None, results_path: Optional[str] = None):
        root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        self.project_root = root
        self.config_path = root / "data" / "evaluation_input_v1.json"
        self.default_results_path = Path(results_path) if results_path else root / "data" / "evaluation_results_v1.json"
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.params = {key: item["value"] for key, item in self.config["parameters"].items()}
        self.dm = DataManager(str(root / self.config["source_workbook"]))
        self.forecast = DemandForecastEngine(base_intensity=float(self.params["demand_intensity"]), peak_multiplier=2.0)
        self._prepared: Optional[Dict[str, Any]] = None
        self._optimized_facilities: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._loaded_results: Optional[Dict[str, Any]] = None

    @staticmethod
    def _round(value: Optional[float], digits: int = 2) -> Optional[float]:
        return None if value is None else round(float(value), digits)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _haversine_km(a: Dict[str, Any], b: Dict[str, Any], factor: float) -> float:
        radius = 6371.0
        lat1, lon1, lat2, lon2 = map(math.radians, [a["lat"], a["lng"], b["lat"], b["lng"]])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return radius * 2 * math.atan2(math.sqrt(h), math.sqrt(max(0.0, 1 - h))) * factor

    def _route_km(self, depot: Dict[str, Any], points: Sequence[Dict[str, Any]], factor: float) -> float:
        unique = []
        seen = set()
        for point in points:
            key = point.get("id") or (point["lat"], point["lng"])
            if key not in seen:
                unique.append(point)
                seen.add(key)
        if not unique:
            return 0.0
        remaining = list(unique)
        route = [depot]
        while remaining:
            nxt = min(remaining, key=lambda p: self._haversine_km(route[-1], p, factor))
            route.append(nxt)
            remaining.remove(nxt)
        route.append(depot)

        def length(seq: Sequence[Dict[str, Any]]) -> float:
            return sum(self._haversine_km(seq[i], seq[i + 1], factor) for i in range(len(seq) - 1))

        improved = True
        while improved and len(route) > 4:
            improved = False
            current = length(route)
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    candidate = route[:i] + list(reversed(route[i : j + 1])) + route[j + 1 :]
                    candidate_length = length(candidate)
                    if candidate_length + 1e-9 < current:
                        route, current, improved = candidate, candidate_length, True
        return length(route)

    def _trunk_exact(self, communities: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        hub = {"id": "HUB", "name": "亦庄片区物流综合枢纽", "lat": 39.798, "lng": 116.506}
        factor = float(self.params["road_detour_factor"])
        points = [{"id": c["id"], "name": c["name"], "lat": c["center"][0], "lng": c["center"][1]} for c in communities]
        baseline = 2 * sum(self._haversine_km(hub, p, factor) for p in points)
        best_route: Optional[Tuple[Dict[str, Any], ...]] = None
        best_distance = float("inf")
        for order in itertools.permutations(points):
            seq = (hub,) + order + (hub,)
            dist = sum(self._haversine_km(seq[i], seq[i + 1], factor) for i in range(len(seq) - 1))
            if dist < best_distance:
                best_distance, best_route = dist, seq
        return {
            "baseline_distance_km": round(baseline, 2),
            "tour_distance_km": round(best_distance, 2),
            "tour": [p["id"] for p in best_route or ()],
            "distance_method": "WGS84直线距离×1.25备用绕行系数（D类）",
        }

    def _stability(self, communities: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        hub = {"id": "HUB", "lat": 39.798, "lng": 116.506}
        factor = float(self.params["road_detour_factor"])
        points = [{"id": c["id"], "lat": c["center"][0], "lng": c["center"][1]} for c in communities]
        values = []
        for seed in self.config["random_seeds"]:
            rng = random.Random(seed)
            order = list(points)
            rng.shuffle(order)
            route = [hub] + order + [hub]
            improved = True
            while improved:
                improved = False
                current = sum(self._haversine_km(route[i], route[i + 1], factor) for i in range(len(route) - 1))
                for i in range(1, len(route) - 2):
                    for j in range(i + 1, len(route) - 1):
                        candidate = route[:i] + list(reversed(route[i : j + 1])) + route[j + 1 :]
                        dist = sum(self._haversine_km(candidate[k], candidate[k + 1], factor) for k in range(len(candidate) - 1))
                        if dist + 1e-9 < current:
                            route, current, improved = candidate, dist, True
            values.append(current)
        mean = statistics.fmean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0.0
        ci = 1.96 * std / math.sqrt(len(values)) if values else 0.0
        return {
            "repetitions": len(values),
            "seeds": self.config["random_seeds"],
            "mean_km": round(mean, 4),
            "std_km": round(std, 4),
            "best_km": round(min(values), 4),
            "worst_km": round(max(values), 4),
            "ci95_low_km": round(mean - ci, 4),
            "ci95_high_km": round(mean + ci, 4),
        }

    @staticmethod
    def _number_from_text(value: Any) -> float:
        import re

        match = re.search(r"(\d+(?:\.\d+)?)", str(value or ""))
        return float(match.group(1)) if match else 0.0

    def _facility_capacity(self, facility: Dict[str, Any]) -> float:
        text = facility.get("capacity_str", "")
        raw = self._number_from_text(text)
        if raw <= 0:
            return 0.0
        if "格" in text:
            return raw * float(self.params["effective_slot_factor"])
        if "件" in text and ("驿站" in facility.get("type", "") or "快递" in facility.get("name", "")):
            return raw * float(self.params["effective_slot_factor"])
        return 0.0

    def _prepare(self) -> Dict[str, Any]:
        if self._prepared is not None:
            return self._prepared
        communities = []
        for overview in self.dm.get_all_overview():
            cid = overview["id"]
            summary = self.dm.get_community_summary(cid)
            forecast = self.forecast.predict_community(
                cid,
                summary["total_households"],
                {"intensity": float(self.params["demand_intensity"])},
            )
            buildings = self.forecast.predict_buildings(summary["demand_nodes"], forecast)
            communities.append({
                **overview,
                "daily_total": float(forecast["daily_total"]),
                "daily_door": float(forecast["daily_door"]),
                "daily_locker": float(forecast["daily_locker"]),
                "door_ratio": float(forecast["door_ratio"]),
                "buildings": buildings,
                "facilities": summary["facilities"],
            })
        self._prepared = {"communities": communities, "trunk": self._trunk_exact(communities)}
        return self._prepared

    def _distance_m(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        return self._haversine_km(a, b, float(self.params["community_detour_factor"])) * 1000

    def _assign_to_facilities(
        self, buildings: Sequence[Dict[str, Any]], facilities: Sequence[Dict[str, Any]]
    ) -> Tuple[Dict[str, Dict[str, Any]], float]:
        assignments: Dict[str, Dict[str, Any]] = {}
        uncovered = 0.0
        limit = float(self.params["max_pickup_distance_m"])
        for building in buildings:
            demand = float(building.get("locker_pkgs", 0))
            if demand <= 0:
                continue
            if not facilities:
                uncovered += demand
                continue
            nearest = min(facilities, key=lambda f: self._distance_m(building, f))
            distance = self._distance_m(building, nearest)
            if distance > limit:
                uncovered += demand
                continue
            assignments[building["building_id"]] = {
                "facility_id": nearest["id"],
                "distance_m": distance,
                "demand": demand,
            }
        return assignments, uncovered

    def _occupancy(self, demand: float, capacity: float, pickup_factor: float = 1.0) -> Dict[str, Any]:
        occupancy = 0.0
        peak = 0.0
        full_minutes = 0
        series = []
        for hour, weight in self.config["arrival_weights"].items():
            pickup_rate = min(1.0, float(self.config["pickup_rates"][hour]) * pickup_factor)
            released = occupancy * pickup_rate
            occupancy = max(0.0, occupancy - released + demand * float(weight))
            peak = max(peak, occupancy)
            if capacity <= 0 and occupancy > 0:
                full_minutes += 60
                saturation = None
            else:
                saturation = occupancy / capacity * 100 if capacity > 0 else 0.0
                if saturation > 100:
                    full_minutes += 60
            series.append({"time": hour, "occupancy": occupancy, "saturation_pct": saturation})
        overflow = max(0.0, peak - capacity) if capacity > 0 else peak
        return {"peak": peak, "overflow": overflow, "full_minutes": full_minutes, "series": series, "end": occupancy}

    def _existing_facilities(self, community: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        for facility in community["facilities"]:
            if "现有" not in facility.get("status", ""):
                continue
            capacity = self._facility_capacity(facility)
            if capacity <= 0:
                continue
            result.append({
                "id": facility["id"],
                "name": facility["name"],
                "lat": facility["lat"],
                "lng": facility["lng"],
                "effective_capacity": capacity,
                "existing_capacity": capacity,
                "new_units": [],
                "capex": 0.0,
                "source": "现有设施（部分为待核验/推定）",
            })
        return result

    def _design_facilities(self) -> Dict[str, List[Dict[str, Any]]]:
        if self._optimized_facilities is not None:
            return self._optimized_facilities
        prepared = self._prepare()
        output: Dict[str, List[Dict[str, Any]]] = {}
        limit = float(self.params["max_pickup_distance_m"])
        main_slots = int(self.params["main_locker_slots"])
        slave_slots = int(self.params["slave_locker_slots"])
        eff = float(self.params["effective_slot_factor"])
        target = float(self.params["facility_design_saturation"])

        for community in prepared["communities"]:
            demand_buildings = [b for b in community["buildings"] if float(b.get("locker_pkgs", 0)) > 0]
            if not demand_buildings:
                output[community["id"]] = self._existing_facilities(community)
                continue
            candidates = []
            for facility in community["facilities"]:
                if not facility.get("lat") or not facility.get("lng"):
                    continue
                if "快递柜" not in facility.get("type", "") and "驿站" not in facility.get("type", ""):
                    continue
                candidates.append({
                    "id": facility["id"], "name": facility["name"], "lat": facility["lat"], "lng": facility["lng"],
                    "existing_capacity": self._facility_capacity(facility) if "现有" in facility.get("status", "") else 0.0,
                    "source": facility.get("status", "候选设施"),
                })
            for building in demand_buildings:
                candidates.append({
                    "id": f"{community['id']}-OPT-{building['building_id']}",
                    "name": f"{building['name']}副柜候选点",
                    "lat": building["lat"], "lng": building["lng"], "existing_capacity": 0.0,
                    "source": "模型生成楼栋侧候选点（D类）",
                })

            uncovered = {b["building_id"]: b for b in demand_buildings}
            selected: List[Dict[str, Any]] = []
            while uncovered:
                best = max(
                    candidates,
                    key=lambda c: sum(float(b.get("locker_pkgs", 0)) for b in uncovered.values() if self._distance_m(b, c) <= limit),
                )
                covered_ids = [bid for bid, b in uncovered.items() if self._distance_m(b, best) <= limit]
                if not covered_ids:
                    building = next(iter(uncovered.values()))
                    best = next(c for c in candidates if c["id"] == f"{community['id']}-OPT-{building['building_id']}")
                    covered_ids = [building["building_id"]]
                selected.append(dict(best))
                for bid in covered_ids:
                    uncovered.pop(bid, None)
                candidates = [c for c in candidates if c["id"] != best["id"]]

            assignments, _ = self._assign_to_facilities(demand_buildings, selected)
            assigned_by_facility = {f["id"]: 0.0 for f in selected}
            for item in assignments.values():
                assigned_by_facility[item["facility_id"]] += item["demand"] * 2.0
            for facility in selected:
                design_demand = assigned_by_facility[facility["id"]]
                peak = self._occupancy(design_demand, 10**12)["peak"]
                required = peak / target if design_demand > 0 else 0.0
                capacity = float(facility.get("existing_capacity", 0.0))
                new_units: List[int] = []
                if capacity + 1e-9 < required:
                    new_units.append(main_slots)
                    capacity += main_slots * eff
                while capacity + 1e-9 < required:
                    new_units.append(slave_slots)
                    capacity += slave_slots * eff
                capex = sum(float(self.params["locker_fixed_cost"]) + float(self.params["locker_slot_cost"]) * slots for slots in new_units)
                facility.update({
                    "effective_capacity": capacity,
                    "new_units": new_units,
                    "capex": capex,
                    "design_demand_p20": design_demand,
                })
            output[community["id"]] = selected
        self._optimized_facilities = output
        return output

    @staticmethod
    def _weighted_percentile(values: Sequence[Tuple[float, float]], percentile: float) -> Optional[float]:
        if not values:
            return None
        ordered = sorted(values, key=lambda item: item[0])
        target = sum(weight for _, weight in ordered) * percentile
        cumulative = 0.0
        for value, weight in ordered:
            cumulative += weight
            if cumulative >= target:
                return value
        return ordered[-1][0]

    def _evaluate_scheme(
        self,
        scheme: str,
        scenario_code: str,
        stability: Dict[str, Any],
        s0_reference: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        prepared = self._prepare()
        scenario = self.config["scenarios"][scenario_code]
        factor = float(scenario["demand_factor"])
        road_factor = float(scenario["road_time_factor"])
        pickup_factor = float(scenario["pickup_rate_factor"])
        optimized_plans = self._design_facilities()
        trunk = prepared["trunk"]
        trunk_km = trunk["baseline_distance_km"] if scheme == "S0" else trunk["tour_distance_km"]
        trunk_km *= 1.18 if scenario_code == "D-R" else 1.0

        total_demand = total_door = total_locker = 0.0
        total_walk = total_uv = total_labor_min = 0.0
        total_unfinished = total_overflow = 0.0
        total_capacity = total_capex_locker = 0.0
        total_locker_units = 0
        all_pickup_distances: List[Tuple[float, float]] = []
        covered_locker = 0.0
        full_communities = 0
        full_minutes = 0
        peak_saturation = 0.0
        aggregate_occ = [0.0] * len(self.config["arrival_weights"])
        aggregate_cap = 0.0
        community_breakdown = []
        community_vehicle_runs = []
        constraint_checks = []
        completed_door = 0.0

        for community in prepared["communities"]:
            cid = community["id"]
            buildings = []
            for original in community["buildings"]:
                building = dict(original)
                building["daily_pkgs"] = float(original.get("daily_pkgs", 0)) * factor
                building["door_pkgs"] = float(original.get("door_pkgs", 0)) * factor
                building["locker_pkgs"] = float(original.get("locker_pkgs", 0)) * factor
                buildings.append(building)
            demand = sum(b["daily_pkgs"] for b in buildings)
            door = sum(b["door_pkgs"] for b in buildings)
            locker = sum(b["locker_pkgs"] for b in buildings)
            total_demand += demand
            total_door += door
            total_locker += locker
            completed_door += door

            if scheme == "S0":
                facilities = self._existing_facilities(community)
            else:
                facilities = [dict(item) for item in optimized_plans[cid]]
            assignments, unassigned = self._assign_to_facilities(buildings, facilities)
            demand_by_facility = {f["id"]: 0.0 for f in facilities}
            for item in assignments.values():
                scaled_demand = item["demand"] * factor if scheme != "S0" else item["demand"]
                # item demand was created from the already scaled building list.
                scaled_demand = item["demand"]
                demand_by_facility[item["facility_id"]] += scaled_demand
                all_pickup_distances.append((item["distance_m"], scaled_demand))
                covered_locker += scaled_demand

            community_overflow = unassigned
            community_full_minutes = 0
            community_peak_sat = 0.0
            for facility in facilities:
                capacity = float(facility.get("effective_capacity", 0.0))
                occ = self._occupancy(demand_by_facility[facility["id"]], capacity, pickup_factor)
                community_overflow += occ["overflow"]
                community_full_minutes += occ["full_minutes"]
                if capacity > 0:
                    facility_peak_sat = occ["peak"] / capacity * 100
                    community_peak_sat = max(community_peak_sat, facility_peak_sat)
                    peak_saturation = max(peak_saturation, facility_peak_sat)
                    aggregate_cap += capacity
                    for index, point in enumerate(occ["series"]):
                        aggregate_occ[index] += point["occupancy"]
                elif demand_by_facility[facility["id"]] > 0:
                    community_peak_sat = max(community_peak_sat, 999.0)
                    peak_saturation = max(peak_saturation, 999.0)
            if community_full_minutes > 0:
                full_communities += 1
            full_minutes += community_full_minutes
            total_overflow += community_overflow

            depot = {
                "id": f"{cid}-DEPOT",
                "lat": facilities[0]["lat"] if facilities else community["center"][0],
                "lng": facilities[0]["lng"] if facilities else community["center"][1],
            }
            active_buildings = [b for b in buildings if b["daily_pkgs"] > 0]
            door_buildings = [b for b in buildings if b["door_pkgs"] > 0]
            base_route = self._route_km(depot, active_buildings, float(self.params["community_detour_factor"]))
            door_route = self._route_km(depot, door_buildings, float(self.params["community_detour_factor"]))
            facility_route = self._route_km(depot, facilities[1:], float(self.params["community_detour_factor"])) if facilities else 0.0
            if scheme == "S0":
                walk_km = base_route
                service_min = demand * float(self.params["baseline_service_min"])
                uv_km = 0.0
            elif scheme == "S1":
                walk_km = door_route + facility_route
                service_min = door * float(self.params["door_service_min"]) + locker * float(self.params["locker_handling_min"])
                uv_km = 0.0
            else:
                walk_km = door_route
                service_min = door * float(self.params["door_service_min"])
                trips = max(1, math.ceil(demand / float(self.params["unmanned_capacity"])))
                uv_km = max(facility_route, 0.15) * trips
                community_vehicle_runs.append({"community_id": cid, "trips": trips, "distance_km": uv_km, "demand": demand})
            walk_min = walk_km / float(self.params["courier_walk_speed_kmh"]) * 60
            labor_min = service_min + walk_min
            total_walk += walk_km
            total_uv += uv_km
            total_labor_min += labor_min

            capacity = sum(float(f.get("effective_capacity", 0)) for f in facilities)
            capex = sum(float(f.get("capex", 0)) for f in facilities)
            # 柜体运维与日耗电按“一个主控点/组合”计费；副柜模块只增加
            # CAPEX和有效容量，不能误按每个副柜重复计一整组年运维。
            units = len([f for f in facilities if float(f.get("effective_capacity", 0)) > 0])
            total_capacity += capacity
            total_capex_locker += capex
            total_locker_units += units
            total_unfinished += community_overflow
            community_breakdown.append({
                "community_id": cid,
                "name": community["name"],
                "demand": round(demand, 1),
                "door_demand": round(door, 1),
                "locker_demand": round(locker, 1),
                "walk_km": round(walk_km, 2),
                "unmanned_km": round(uv_km, 2),
                "labor_hours": round(labor_min / 60, 2),
                "locker_capacity": round(capacity, 1),
                "peak_occupancy_pct": round(community_peak_sat, 1) if community_peak_sat else 0.0,
                "full_minutes": community_full_minutes,
                "overflow_pkgs": round(community_overflow, 1),
                "coverage_pct": round((locker - unassigned) / locker * 100, 1) if locker > 0 else 100.0,
            })

        trunk_speed = float(self.params["courier_drive_speed_kmh"] if scheme != "S2" else self.params["unmanned_speed_kmh"])
        trunk_runtime = trunk_km / trunk_speed * 60 * road_factor + len(prepared["communities"]) * float(self.params["stop_service_min"])
        if scheme in {"S0", "S1"}:
            total_labor_min += trunk_runtime
        else:
            total_labor_min += (trunk_runtime + total_uv / float(self.params["unmanned_speed_kmh"]) * 60 * road_factor)
        labor_hours = total_labor_min / 60
        staff = max(1, math.ceil(total_labor_min / float(self.params["shift_minutes"])))
        vehicle_runtime = trunk_runtime + (total_uv / float(self.params["unmanned_speed_kmh"]) * 60 * road_factor if scheme == "S2" else 0)
        if scheme == "S2":
            vehicle_count = max(2, math.ceil(vehicle_runtime / float(self.params["service_window_minutes"])) + 1)
            vehicle_runtime += float(scenario["vehicle_failure_delay_min"])
        else:
            vehicle_count = 0
        makespan = max(total_labor_min / staff, vehicle_runtime)
        if total_unfinished > 0:
            makespan = float(self.params["service_window_minutes"])
        makespan = min(float(self.params["service_window_minutes"]), makespan)
        completed = max(0.0, total_demand - total_unfinished)

        avg_pickup = sum(distance * weight for distance, weight in all_pickup_distances) / sum(weight for _, weight in all_pickup_distances) if all_pickup_distances else None
        p95 = self._weighted_percentile(all_pickup_distances, 0.95)
        coverage = covered_locker / total_locker * 100 if total_locker > 0 else 100.0

        hard_checks = [
            {
                "constraint": "DEMAND_CONSERVATION",
                "lhs": round(completed + total_unfinished, 3),
                "rhs": round(total_demand, 3),
                "status": "FEASIBLE" if abs(completed + total_unfinished - total_demand) < 1e-6 else "VIOLATED",
            },
            {
                "constraint": "LOCKER_CAPACITY_DYNAMIC",
                "lhs": round(total_overflow, 3),
                "rhs": 0,
                "status": "FEASIBLE" if total_overflow <= 1e-6 else "VIOLATED",
            },
            {
                "constraint": "PICKUP_DISTANCE_150M",
                "lhs": round(coverage, 3),
                "rhs": 100,
                "status": "FEASIBLE" if coverage >= 99.999 else "VIOLATED",
            },
            {
                "constraint": "STAFF_SHIFT_480MIN",
                "lhs": round(total_labor_min / staff, 3),
                "rhs": float(self.params["shift_minutes"]),
                "status": "FEASIBLE" if total_labor_min / staff <= float(self.params["shift_minutes"]) + 1e-6 else "VIOLATED",
            },
            {
                "constraint": "SERVICE_WINDOW_780MIN",
                "lhs": round(makespan, 3),
                "rhs": float(self.params["service_window_minutes"]),
                "status": "FEASIBLE" if total_unfinished <= 1e-6 and makespan <= float(self.params["service_window_minutes"]) else "VIOLATED",
            },
        ]
        constraint_checks.extend(hard_checks)
        violations = sum(1 for item in constraint_checks if item["status"] == "VIOLATED")

        operating_days = float(self.params["operating_days"])
        fuel_km = trunk_km if scheme in {"S0", "S1"} else 0.0
        electric_km = trunk_km + total_uv if scheme == "S2" else 0.0
        fuel_liters = fuel_km * float(self.params["fuel_l_per_km"]) * operating_days
        vehicle_kwh = electric_km * float(self.params["unmanned_energy_kwh_km"]) * operating_days
        locker_kwh = total_locker_units * float(self.params["locker_energy_kwh_day"]) * operating_days
        labor_cost = labor_hours * float(self.params["hourly_labor_cost"]) * operating_days
        fuel_cost = fuel_liters * float(self.params["fuel_price"])
        electricity_cost = (vehicle_kwh + locker_kwh) * float(self.params["electricity_price"])
        fixed_vehicle_opex = float(self.params["fuel_vehicle_fixed_opex"]) if scheme in {"S0", "S1"} else vehicle_count * (
            float(self.params["unmanned_insurance"]) + float(self.params["unmanned_maintenance"]) + float(self.params["map_platform_cost"])
        )
        locker_opex = total_locker_units * float(self.params["locker_opex"])
        opex = labor_cost + fuel_cost + electricity_cost + fixed_vehicle_opex + locker_opex
        capex = 0.0
        if scheme in {"S1", "S2"}:
            capex += total_capex_locker
        if scheme == "S2":
            capex += vehicle_count * float(self.params["unmanned_vehicle_price"]) + float(self.params["swap_station_capex"]) + float(self.params["platform_capex"])
        residual = float(self.params["residual_rate"])
        locker_depreciation = total_capex_locker * (1 - residual) / float(self.params["locker_life_years"]) if scheme != "S0" else 0.0
        vehicle_depreciation = vehicle_count * float(self.params["unmanned_vehicle_price"]) * (1 - residual) / float(self.params["vehicle_life_years"]) if scheme == "S2" else 0.0
        other_depreciation = (float(self.params["swap_station_capex"]) + float(self.params["platform_capex"])) * (1 - residual) / float(self.params["locker_life_years"]) if scheme == "S2" else 0.0
        annual_cost = opex + locker_depreciation + vehicle_depreciation + other_depreciation
        annual_completed = completed * operating_days

        fuel_carbon = fuel_liters * float(self.params["fuel_emission_factor"])
        electric_carbon = (vehicle_kwh + locker_kwh) * float(self.params["grid_emission_factor"])
        annual_carbon = fuel_carbon + electric_carbon
        baseline_opex = s0_reference["cost_metrics"]["C02"] if s0_reference else opex
        baseline_carbon = s0_reference["carbon_metrics"]["G02"] if s0_reference else annual_carbon
        saving = baseline_opex - opex
        payback = capex / saving if capex > 0 and saving > 0 else None

        loads = [min(float(self.params["trunk_vehicle_capacity"]), total_demand) / float(self.params["trunk_vehicle_capacity"]) * 100]
        if scheme == "S2":
            for run in community_vehicle_runs:
                trips = run["trips"]
                loads.extend([min(float(self.params["unmanned_capacity"]), run["demand"] - i * float(self.params["unmanned_capacity"])) / float(self.params["unmanned_capacity"]) * 100 for i in range(trips)])
        trips_total = 5 if scheme == "S0" else 1
        if scheme == "S2":
            trips_total += sum(run["trips"] for run in community_vehicle_runs)

        aggregate_series = []
        for index, hour in enumerate(self.config["arrival_weights"]):
            aggregate_series.append({
                "time": hour,
                "occupancy": round(aggregate_occ[index], 2),
                "capacity": round(aggregate_cap, 2),
                "saturation_pct": round(aggregate_occ[index] / aggregate_cap * 100, 1) if aggregate_cap > 0 else None,
            })
        recovery = 0.0
        if scenario_code in {"D-R", "D-V"}:
            recovery = max(0.0, vehicle_runtime - (trunk_km / trunk_speed * 60))
        elif scenario_code == "D-L":
            recovery = min(720.0, total_overflow / max(total_capacity * 0.5, 1.0) * 60)

        result = {
            "input_version": self.config["input_version"],
            "scenario_code": scenario_code,
            "scenario_name": scenario["name"],
            "scheme_code": scheme,
            "scheme_name": {"S0": "现状基准方案", "S1": "网络与设施优化方案", "S2": "人机协同推荐方案"}[scheme],
            "status": "INFEASIBLE" if violations else "FEASIBLE",
            "network_metrics": {
                "E01": self._round(trunk_km, 2), "E02": self._round(total_walk, 2), "E03": self._round(total_uv, 2),
                "E04": {"fuel_km": self._round(fuel_km, 2), "electric_km": self._round(electric_km, 2), "total_km": self._round(fuel_km + electric_km, 2)},
                "E05": trips_total, "E06": self._round(makespan, 1),
                "E07": self._round(completed / labor_hours if labor_hours > 0 else None, 2),
                "E08": self._round(completed / total_demand * 100 if total_demand > 0 else 100.0, 1),
            },
            "resource_metrics": {
                "R01": self._round(labor_hours, 2), "R02": staff, "R03": vehicle_count,
                "R04": {"average_pct": self._round(statistics.fmean(loads), 1), "max_pct": self._round(max(loads), 1)},
                "R05": self._round(total_capacity, 1),
            },
            "service_metrics": {
                "S01": self._round(avg_pickup, 1), "S02": self._round(p95, 1), "S03": self._round(coverage, 1),
                "S04": self._round(total_unfinished, 1),
                "S05": {"community_count": full_communities, "full_minutes": full_minutes, "overflow_pkgs": self._round(total_overflow, 1)},
                "S06": self._round(peak_saturation, 1),
                "S07": self._round(completed_door / total_door * 100 if total_door > 0 else 100.0, 1),
            },
            "cost_metrics": {
                "C01": self._round(capex, 0), "C02": self._round(opex, 0), "C03": self._round(annual_cost, 0),
                "C04": self._round(annual_cost / annual_completed if annual_completed > 0 else None, 2),
                "C05": self._round(saving, 0), "C06": self._round(payback, 2),
                "breakdown": {"labor": self._round(labor_cost, 0), "energy": self._round(fuel_cost + electricity_cost, 0), "vehicle_fixed": self._round(fixed_vehicle_opex, 0), "locker_opex": self._round(locker_opex, 0)},
            },
            "carbon_metrics": {
                "G01": {"fuel_liters": self._round(fuel_liters, 1), "electricity_kwh": self._round(vehicle_kwh + locker_kwh, 1)},
                "G02": self._round(annual_carbon, 1), "G03": self._round(baseline_carbon - annual_carbon, 1),
                "G04": self._round(annual_carbon / annual_completed if annual_completed > 0 else None, 4),
            },
            "robustness_metrics": {
                "B01": self._round(completed / total_demand * 100 if total_demand > 0 else 100.0, 1),
                "B02": self._round(recovery, 1), "B03": violations, "B04": stability,
                "B05": self._round((time.perf_counter() - started) * 1000, 3),
            },
            "community_breakdown": community_breakdown,
            "time_series": {"locker_occupancy": aggregate_series},
            "constraint_checks": constraint_checks,
            "source_and_assumptions": {
                "input_file": str(self.config_path.relative_to(self.project_root)).replace("\\", "/"),
                "demand_total": self._round(total_demand, 1),
                "door_total": self._round(total_door, 1),
                "locker_total": self._round(total_locker, 1),
                "distance_quality": "D：当前正式比较仍使用直线距离×绕行系数；接入高德OD后须重新冻结版本",
                "simulation_type": "确定性情景推演（动态占用与释放），不冒充随机离散事件仿真",
            },
        }
        return result

    @staticmethod
    def _metric_value(result: Dict[str, Any], path: str) -> Optional[float]:
        group, code = path.split(".")
        value = result[group][code]
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def improvement_rate(base: Optional[float], optimized: Optional[float], higher_is_better: bool = False) -> Optional[float]:
        if base is None or optimized is None or base == 0:
            return None
        raw = (optimized - base) / base * 100 if higher_is_better else (base - optimized) / base * 100
        return round(raw, 1)

    def generate_all(self) -> Dict[str, Any]:
        prepared = self._prepare()
        stability = self._stability(prepared["communities"])
        results: Dict[str, Dict[str, Any]] = {}
        for scenario_code in self.config["scenarios"]:
            s0 = self._evaluate_scheme("S0", scenario_code, stability)
            results[f"S0-{scenario_code}"] = s0
            results[f"S1-{scenario_code}"] = self._evaluate_scheme("S1", scenario_code, stability, s0)
            results[f"S2-{scenario_code}"] = self._evaluate_scheme("S2", scenario_code, stability, s0)

        s0n, s1n, s2n = results["S0-N"], results["S1-N"], results["S2-N"]
        comparison_paths = {
            "E01": "network_metrics.E01", "E02": "network_metrics.E02", "E06": "network_metrics.E06",
            "E07": "network_metrics.E07", "R01": "resource_metrics.R01", "S01": "service_metrics.S01",
            "S03": "service_metrics.S03", "S04": "service_metrics.S04", "S06": "service_metrics.S06",
            "C02": "cost_metrics.C02", "C03": "cost_metrics.C03", "C04": "cost_metrics.C04",
            "G02": "carbon_metrics.G02", "G04": "carbon_metrics.G04", "B01": "robustness_metrics.B01",
        }
        higher = {"E07", "S03", "B01"}
        comparison = {}
        for code, path in comparison_paths.items():
            base = self._metric_value(s0n, path)
            s1 = self._metric_value(s1n, path)
            s2 = self._metric_value(s2n, path)
            comparison[code] = {
                "name": METRIC_DEFINITIONS[code]["name"], "unit": METRIC_DEFINITIONS[code]["unit"],
                "S0": base, "S1": s1, "S2": s2,
                "S1_vs_S0_pct": self.improvement_rate(base, s1, code in higher),
                "S2_vs_S0_pct": self.improvement_rate(base, s2, code in higher),
            }
        comparison["S05"] = {
            "name": METRIC_DEFINITIONS["S05"]["name"], "unit": METRIC_DEFINITIONS["S05"]["unit"],
            "S0": s0n["service_metrics"]["S05"], "S1": s1n["service_metrics"]["S05"], "S2": s2n["service_metrics"]["S05"],
        }
        comparison["C06"] = {"name": METRIC_DEFINITIONS["C06"]["name"], "unit": "年", "S0": None, "S1": s1n["cost_metrics"]["C06"], "S2": s2n["cost_metrics"]["C06"]}
        comparison["G03"] = {"name": METRIC_DEFINITIONS["G03"]["name"], "unit": "kgCO2e/年", "S0": 0.0, "S1": s1n["carbon_metrics"]["G03"], "S2": s2n["carbon_metrics"]["G03"]}

        workbook = self.project_root / self.config["source_workbook"]
        parameter_workbook = self.project_root / self.config["source_parameter_workbook"]
        total_normal = round(sum(c["daily_total"] for c in prepared["communities"]), 1)
        artifact = {
            "evaluation_version": "1.0.0",
            "generated_at": "2026-09-19",
            "input_version": self.config["input_version"],
            "input_digest": hashlib.sha256(self.config_path.read_bytes()).hexdigest(),
            "source_digests": {
                self.config["source_workbook"]: self._sha256(workbook),
                self.config["source_parameter_workbook"]: self._sha256(parameter_workbook),
            },
            "frozen_input_summary": {
                "community_count": len(prepared["communities"]),
                "households": {c["id"]: c["households"] for c in prepared["communities"]},
                "normal_day_total": total_normal,
                "normal_day_by_community": {c["id"]: round(c["daily_total"], 1) for c in prepared["communities"]},
                "distance_method": prepared["trunk"]["distance_method"],
                "operating_days": self.params["operating_days"],
            },
            "scheme_definitions": {
                "S0": "现状独立往返+现有设施+全人工社区作业",
                "S1": "优化巡回干线+优化节点容量+人工执行",
                "S2": "与S1相同网络设施+无人车巡航+人工上门及异常",
            },
            "metric_definitions": METRIC_DEFINITIONS,
            "required_main_results": ["S0-N", "S1-N", "S2-N", "S0-P20", "S2-P20"],
            "comparison_normal": comparison,
            "results": results,
            "audit": {
                "same_input_for_all_schemes": True,
                "official_normal_day_total": total_normal,
                "stability_test": stability,
                "hard_constraint_status_rule": "任一硬约束VIOLATED时，方案状态只能为INFEASIBLE",
                "dynamic_occupancy_unclipped": True,
                "manual_improvement_entries": False,
            },
        }
        return artifact

    def write_results(self, path: Optional[str] = None) -> Path:
        target = Path(path) if path else self.default_results_path
        target.parent.mkdir(parents=True, exist_ok=True)
        artifact = self.generate_all()
        target.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._loaded_results = artifact
        return target

    def load_results(self, refresh: bool = False) -> Dict[str, Any]:
        if refresh or not self.default_results_path.exists():
            self.write_results()
        if self._loaded_results is None:
            self._loaded_results = json.loads(self.default_results_path.read_text(encoding="utf-8"))
        return self._loaded_results

    def get_result(self, scheme: str, scenario: str) -> Dict[str, Any]:
        key = f"{scheme.upper()}-{scenario.upper()}"
        results = self.load_results()
        if key not in results["results"]:
            raise KeyError(key)
        return results["results"][key]

    def legacy_comparison_metrics(self) -> Dict[str, Any]:
        data = self.load_results()
        comp = data["comparison_normal"]

        def item(code: str, label: str, unit: str) -> Dict[str, Any]:
            row = comp[code]
            base, s1_val, optimized = row["S0"], row.get("S1"), row["S2"]
            return {
                "label": label, "unit": unit, "baseline": base, "s1": s1_val, "optimized": optimized,
                "diff": round(optimized - base, 2) if isinstance(base, (int, float)) and isinstance(optimized, (int, float)) else None,
                "diff_pct": row.get("S2_vs_S0_pct"),
                "diff_s1_pct": row.get("S1_vs_S0_pct"),
                "desc": "由统一评价结果自动生成",
            }

        full = comp["S05"]
        return {
            "trunk_distance": item("E01", "干线运输总里程", "km"),
            "courier_walk_distance": item("E02", "社区内步巡总里程", "km"),
            "labor_hours": item("R01", "全网人工投入工时", "h"),
            "coverage_rate": item("S03", "150m覆盖率", "%"),
            "unfinished_packages": item("S04", "日终未完成件量", "件"),
            "completion_rate": item("B01", "需求承载率", "%"),
            "full_risk_count": {
                "label": "满柜风险社区数", "unit": "个",
                "baseline": full["S0"]["community_count"],
                "s1": full["S1"]["community_count"],
                "optimized": full["S2"]["community_count"],
                "diff": full["S2"]["community_count"] - full["S0"]["community_count"],
                "diff_pct": self.improvement_rate(float(full["S0"]["community_count"]), float(full["S2"]["community_count"])),
                "desc": "按动态占用与释放过程计算",
            },
            "annual_cost": item("C02", "年现金运营成本", "元"),
            "annual_carbon": item("G02", "年运营碳排放量", "kgCO2e"),
            "payback_years": {"label": "静态投资回收期", "unit": "年", "s1": comp["C06"]["S1"], "value": comp["C06"]["S2"], "desc": "年度现金节约为正时计算"},
        }
