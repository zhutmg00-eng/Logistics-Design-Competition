import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
if str(DEMO) not in sys.path:
    sys.path.insert(0, str(DEMO))

from core.data_manager import DataManager
from core.evaluation_engine import EvaluationEngine
from core.forecast_model import DemandForecastEngine
from core.routing_engine import RoutingEngine


class UnifiedEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = EvaluationEngine(project_root=str(ROOT))
        cls.artifact = json.loads(
            (ROOT / "data" / "evaluation_results_v1.json").read_text(encoding="utf-8")
        )

    def test_matrix_contains_all_schemes_scenarios_and_required_results(self):
        expected = {
            f"{scheme}-{scenario}"
            for scheme in ("S0", "S1", "S2")
            for scenario in ("N", "P15", "P20", "D-R", "D-V", "D-L")
        }
        self.assertEqual(expected, set(self.artifact["results"]))
        self.assertEqual(
            ["S0-N", "S1-N", "S2-N", "S0-P20", "S2-P20"],
            self.artifact["required_main_results"],
        )

    def test_normal_day_demand_is_identical_and_frozen(self):
        values = {
            self.artifact["results"][f"{scheme}-N"]["source_and_assumptions"]["demand_total"]
            for scheme in ("S0", "S1", "S2")
        }
        self.assertEqual({2589.6}, values)
        self.assertEqual(
            {"C01": 163.2, "C02": 259.8, "C03": 252.0, "C04": 1284.6, "C05": 630.0},
            self.artifact["frozen_input_summary"]["normal_day_by_community"],
        )

    def test_improvement_rates_are_derived_from_results(self):
        comparison = self.artifact["comparison_normal"]
        higher_is_better = {"E07", "S03", "B01"}
        for code, row in comparison.items():
            if code in {"S05", "C06", "G03"}:
                continue
            expected = self.engine.improvement_rate(
                row["S0"], row["S2"], code in higher_is_better
            )
            self.assertEqual(expected, row["S2_vs_S0_pct"], code)
        self.assertFalse(self.artifact["audit"]["manual_improvement_entries"])

    def test_dynamic_occupancy_is_not_clipped_at_capacity(self):
        occupancy = self.engine._occupancy(demand=1000.0, capacity=50.0, pickup_factor=0.1)
        self.assertGreater(occupancy["peak"], 50.0)
        self.assertGreater(max(point["saturation_pct"] for point in occupancy["series"]), 100.0)
        self.assertGreater(occupancy["overflow"], 0.0)
        self.assertTrue(self.artifact["audit"]["dynamic_occupancy_unclipped"])

    def test_hard_constraint_violations_force_infeasible_status(self):
        for key, result in self.artifact["results"].items():
            violated = any(
                check["status"] == "VIOLATED" for check in result["constraint_checks"]
            )
            self.assertEqual("INFEASIBLE" if violated else "FEASIBLE", result["status"], key)

    def test_fixed_seed_stability_statistics_are_complete(self):
        stability = self.artifact["audit"]["stability_test"]
        self.assertEqual(30, stability["repetitions"])
        self.assertEqual(30, len(stability["seeds"]))
        self.assertEqual(30, len(set(stability["seeds"])))
        for field in ("mean_km", "std_km", "best_km", "worst_km", "ci95_low_km", "ci95_high_km"):
            self.assertIn(field, stability)

    def test_results_include_formulas_sources_and_input_digests(self):
        self.assertIn("E01", self.artifact["metric_definitions"])
        self.assertIn("formula", self.artifact["metric_definitions"]["E01"])
        self.assertEqual(64, len(self.artifact["input_digest"]))
        self.assertEqual(2, len(self.artifact["source_digests"]))
        for result in self.artifact["results"].values():
            self.assertEqual("data/evaluation_input_v1.json", result["source_and_assumptions"]["input_file"])
            self.assertIn("distance_quality", result["source_and_assumptions"])
            self.assertIn("simulation_type", result["source_and_assumptions"])

    def test_formal_surfaces_do_not_contain_retired_result_values(self):
        files = [
            ROOT / "README.md",
            ROOT / "docs" / "two_stage_isa_algorithm_chapter7.md",
            ROOT / "demo" / "server.py",
            ROOT / "demo" / "static" / "app.js",
            ROOT / "demo" / "static" / "index.html",
            ROOT / "generate_report_figures.py",
        ]
        retired = ("2935", "13.78", "9.07", "151.2", "60.8", "283.4", "131.4", "1459.2", "187.3")
        for path in files:
            text = path.read_text(encoding="utf-8")
            for value in retired:
                self.assertNotIn(value, text, f"{value} remains in {path.relative_to(ROOT)}")

    def test_routing_is_reproducible_with_the_same_seed(self):
        communities = DataManager().get_all_overview()
        first = RoutingEngine(random_seed=20260919).solve_trunk_m1(communities)
        second = RoutingEngine(random_seed=20260919).solve_trunk_m1(communities)
        self.assertEqual(first["tour"], second["tour"])
        self.assertEqual(first["tour_dist_km"], second["tour_dist_km"])
        self.assertEqual("HEURISTIC_FEASIBLE", first["solver_metrics"]["optimality_status"])

    def test_2e_mdvrptw_dc_collaborative_routing(self):
        dm = DataManager()
        fe = DemandForecastEngine()
        eng = RoutingEngine(random_seed=20260919)
        comm = dm.get_community_summary("C01")
        fc = fe.predict_community("C01", comm["total_households"])
        bldgs = fe.predict_buildings(comm["demand_nodes"], fc)
        res = eng.solve_community_m2("C01", bldgs, comm["facilities"])
        
        self.assertIn("satisfaction_score", res)
        self.assertIn("handover_sync_valid", res)
        self.assertIn("battery_reserve_pct", res)
        self.assertIn("penalty_cost", res)
        self.assertTrue(res["handover_sync_valid"])
        self.assertGreaterEqual(res["satisfaction_score"], 90.0)
        self.assertGreaterEqual(res["battery_reserve_pct"], 20.0)


if __name__ == "__main__":
    unittest.main()
