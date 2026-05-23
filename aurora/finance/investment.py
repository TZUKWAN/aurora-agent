"""投资回报分析."""

from typing import Dict, List
import numpy as np


class InvestmentAnalysis:
    """投资回报分析工具."""

    def calculate_roi(self, investment: float, returns: List[float]) -> float:
        total_return = sum(returns)
        return (total_return - investment) / investment * 100 if investment > 0 else 0

    def calculate_npv(self, investment: float, cashflows: List[float], discount_rate: float = 0.08) -> float:
        pv = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cashflows))
        return pv - investment

    def calculate_irr(self, investment: float, cashflows: List[float]) -> float:
        flows = [-investment] + cashflows
        try:
            return np.irr(flows) * 100
        except:
            return 0.0

    def calculate_payback(self, investment: float, annual_returns: List[float]) -> float:
        cumulative = 0
        for i, ret in enumerate(annual_returns):
            cumulative += ret
            if cumulative >= investment:
                fraction = (investment - (cumulative - ret)) / ret if ret > 0 else 0
                return i + fraction
        return float("inf")

    def breakeven_analysis(self, fixed_costs: float, price: float, variable_cost: float) -> Dict:
        if price <= variable_cost:
            return {"breakeven_units": float("inf"), "breakeven_revenue": float("inf")}
        be_units = fixed_costs / (price - variable_cost)
        return {"breakeven_units": be_units, "breakeven_revenue": be_units * price}

    def full_analysis(self, project_info: Dict) -> Dict:
        investment = project_info.get("investment", 0)
        cashflows = project_info.get("cashflows", [])
        discount_rate = project_info.get("discount_rate", 0.08)

        return {
            "roi": self.calculate_roi(investment, cashflows),
            "npv": self.calculate_npv(investment, cashflows, discount_rate),
            "payback_years": self.calculate_payback(investment, cashflows),
            "total_return": sum(cashflows),
        }
