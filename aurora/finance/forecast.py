"""财务预测模型."""

import json
from typing import Dict, List, Optional
import numpy as np


class FinancialForecast:
    """3-5年财务预测模型."""

    def __init__(self, years: int = 3):
        self.years = years
        self.revenue_model = {"type": "subscription", "initial": 0, "growth_rate": 0.3}
        self.cost_structure = {"fixed": {}, "variable_rate": 0.5}
        self._forecast = None

    def set_revenue_model(self, model_type: str, initial_revenue: float, growth_rate: float):
        self.revenue_model = {"type": model_type, "initial": initial_revenue, "growth_rate": growth_rate}

    def set_cost_structure(self, fixed_costs: Dict, variable_cost_rate: float):
        self.cost_structure = {"fixed": fixed_costs, "variable_rate": variable_cost_rate}

    def forecast(self) -> Dict:
        years = list(range(1, self.years + 1))
        initial = self.revenue_model["initial"]
        growth = self.revenue_model["growth_rate"]
        var_rate = self.cost_structure["variable_rate"]
        fixed_total = sum(self.cost_structure["fixed"].values())

        revenues = [initial * ((1 + growth) ** y) for y in years]
        variable_costs = [r * var_rate for r in revenues]
        fixed_costs = [fixed_total] * self.years
        total_costs = [v + f for v, f in zip(variable_costs, fixed_costs)]
        gross_profits = [r - v for r, v in zip(revenues, variable_costs)]
        net_profits = [r - c for r, c in zip(revenues, total_costs)]
        gross_margins = [g / r * 100 if r > 0 else 0 for g, r in zip(gross_profits, revenues)]
        net_margins = [n / r * 100 if r > 0 else 0 for n, r in zip(net_profits, revenues)]

        self._forecast = {
            "years": years,
            "revenue": revenues,
            "variable_costs": variable_costs,
            "fixed_costs": fixed_costs,
            "total_costs": total_costs,
            "gross_profit": gross_profits,
            "net_profit": net_profits,
            "gross_margin": gross_margins,
            "net_margin": net_margins,
        }
        return self._forecast

    def get_kpis(self) -> Dict:
        if not self._forecast:
            self.forecast()
        f = self._forecast
        return {
            "cagr": ((f["revenue"][-1] / f["revenue"][0]) ** (1 / (self.years - 1)) - 1) * 100 if f["revenue"][0] > 0 else 0,
            "avg_gross_margin": sum(f["gross_margin"]) / len(f["gross_margin"]),
            "avg_net_margin": sum(f["net_margin"]) / len(f["net_margin"]),
            "total_revenue": sum(f["revenue"]),
            "total_profit": sum(f["net_profit"]),
        }

    def export_to_json(self, filepath: str):
        if not self._forecast:
            self.forecast()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._forecast, f, ensure_ascii=False, indent=2)
        print(f"财务预测已导出: {filepath}")
