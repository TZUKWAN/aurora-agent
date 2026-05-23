"""敏感性分析."""

from typing import Dict, List
import numpy as np


class SensitivityAnalysis:
    """财务敏感性分析."""

    def single_variable_analysis(self, base_case: Dict, variable: str, range_pct: List[float]) -> List[Dict]:
        base_value = base_case.get(variable, 0)
        base_npv = self._calculate_metric(base_case)
        results = []

        for pct in range_pct:
            new_value = base_value * (1 + pct)
            new_case = base_case.copy()
            new_case[variable] = new_value
            new_npv = self._calculate_metric(new_case)
            results.append({
                "variable": variable,
                "change_pct": pct * 100,
                "new_value": new_value,
                "metric_value": new_npv,
                "difference": new_npv - base_npv,
            })
        return results

    def scenario_analysis(self, scenarios: Dict) -> Dict:
        result = {}
        for name, params in scenarios.items():
            result[name] = self._calculate_metric(params)
        return result

    def _calculate_metric(self, params: Dict) -> float:
        revenue = params.get("revenue", 0)
        costs = params.get("costs", 0)
        return revenue - costs
