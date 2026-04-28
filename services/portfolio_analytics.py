from services.data_loader import DataLoader

class PortfolioAnalytics:
    def __init__(self,loader:DataLoader):
        self.loader = loader
    def portfolio_analytics(self,portfolio_id:str):
        portfolio = self.loader.get_single_portfolio(portfolio_id)
        if not portfolio:
            return "Portfolio not found"
        stocks = portfolio["holdings"]['stocks']
        mutual_funds = portfolio["holdings"]['mutual_funds']
        # Total current portfolio value (stocks + MFs)
        total_current_value=portfolio["current_value"]

        stocks_daily_Pnl=sum(s['day_change'] for s in stocks)
        mfs_daily_Pnl=sum(m['day_change'] for m in mutual_funds)

        # Total daily PnL (₹)
        total_daily_pnl=stocks_daily_Pnl+mfs_daily_Pnl
        # Convert PnL into percentage (relative to total portfolio value)
        daily_pnl_percent=total_daily_pnl/total_current_value*100
        
        #So Goal: how much money is invested in each sector (in stocks)
        sector_allocation={}
        for s in stocks:
            sector=s['sector']
            amount=s['current_value']
            sector_allocation[sector]=sector_allocation.get(sector,0)+amount

        # Convert Rupee to percentage of total portfolio
        sector_allocation_percent={}
        for sector,amount in sector_allocation.items():
            sector_allocation_percent[sector]=round(amount/total_current_value*100,2)

        #check for risks
        risks=[]
        for sector,percent in sector_allocation_percent.items():
            if percent>40:
                risks.append(f"CRITICAL: {sector} has {percent}% allocation")
            elif percent>25:
                risks.append(f"HIGH RISK: {sector} has {percent}% allocation")
        
        #Top Performing and worst performing stocks
        sorted_stocks=sorted(stocks,key=lambda x:x['day_change_percent'],reverse=True)
        top_scorer_stocks=sorted_stocks[:3]
        worst_scorer_stocks=sorted_stocks[-3:][::-1]

        #asset allocation analysis
        assets_total_current=sum(s['current_value'] for s in stocks)
        mf_total_current=sum(m['current_value'] for m in mutual_funds)
        asset_breakdown={
            "stocks":round(assets_total_current/total_current_value*100,2),
            "mutual_funds":round(mf_total_current/total_current_value*100,2),
        }

        #PostDeadline: Break down each MF into its underlying stocks and sectors
        mf_details = self.loader.get_mutual_funds_data()
        direct_symbols = {s["symbol"] for s in stocks}
        mf_breakdown = []
        for mf in mutual_funds:
            info = mf_details.get(mf.get("scheme_code",""), {})
            holdings = info.get("top_holdings", [])
            sectors = info.get("sector_allocation", {})
            # Here we extract the top holdings and sectors from the MF data
            overlap = [h["stock"] for h in holdings if h.get("stock") in direct_symbols]
            mf_breakdown.append({
                "name": mf.get("scheme_name",""),
                "category": info.get("category", mf.get("category","")),
                "nav_change": info.get("nav_change_percent", mf.get("day_change_percent",0)),
                "weight": mf.get("weight_in_portfolio",0),
                "top_stocks": [h.get("stock","") for h in holdings[:5] if h.get("stock")],
                "top_sectors": sorted(sectors.items(), key=lambda x:-x[1])[:3],
                "overlap_with_stocks": overlap,
            })
        

        return {
            "portfolio_id":portfolio_id,
            "user_name":portfolio["user_name"],
            "portfolio_type":portfolio["portfolio_type"],
            "risk_profile":portfolio["risk_profile"],

            "total_current_value":total_current_value,
            "total_daily_pnl":total_daily_pnl,
            "daily_pnl_percent":daily_pnl_percent,

            "sector_allocation_percent":sector_allocation_percent,

            "risks":risks,
            "top_gainers": [{"symbol": s["symbol"], "change_pct": s["day_change_percent"]} for s in top_scorer_stocks],
            "top_losers": [{"symbol": s["symbol"], "change_pct": s["day_change_percent"]} for s in worst_scorer_stocks],
            "asset_breakdown":asset_breakdown,
            "stocks":stocks,
            "mutual_funds":mutual_funds,
            "mf_breakdown":mf_breakdown
        }
        