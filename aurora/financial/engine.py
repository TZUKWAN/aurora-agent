"""Financial Sandbox Engine for deterministic calculations."""

class FinancialSandbox:
    """Calculates deterministic financial projections (3-year)."""

    @classmethod
    def calculate_projection(cls, unit_price: float, initial_monthly_vol: int, 
                             monthly_growth_rate: float, fixed_monthly_cost: float, 
                             unit_variable_cost: float) -> dict:
        """
        Calculate a 3-year projection based on core metrics.
        growth rate should be like 0.05 for 5%
        """
        years = []
        cumulative_cash = 0.0
        current_vol = initial_monthly_vol
        break_even_month = -1
        total_months = 0
        
        for year in range(1, 4):
            yearly_revenue = 0.0
            yearly_cost = 0.0
            yearly_vol = 0
            
            for month in range(12):
                total_months += 1
                rev = current_vol * unit_price
                cost = fixed_monthly_cost + (current_vol * unit_variable_cost)
                
                yearly_revenue += rev
                yearly_cost += cost
                yearly_vol += current_vol
                cumulative_cash += (rev - cost)
                
                if cumulative_cash > 0 and break_even_month == -1:
                    break_even_month = total_months
                    
                # Apply growth
                current_vol = int(current_vol * (1 + monthly_growth_rate))
                
            gross_profit = yearly_revenue - (yearly_vol * unit_variable_cost)
            net_profit = yearly_revenue - yearly_cost
            
            years.append({
                "year": year,
                "revenue": round(yearly_revenue, 2),
                "total_cost": round(yearly_cost, 2),
                "gross_profit": round(gross_profit, 2),
                "net_profit": round(net_profit, 2),
                "gross_margin": round(gross_profit / yearly_revenue if yearly_revenue else 0, 4),
                "volume": yearly_vol
            })
            
        return {
            "projections": years,
            "break_even_month": break_even_month if break_even_month > 0 else "36+",
            "total_3yr_revenue": sum(y["revenue"] for y in years),
            "total_3yr_profit": sum(y["net_profit"] for y in years)
        }
