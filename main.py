from services.data_loader import DataLoader
from services.portfolio_analytics import PortfolioAnalytics
from services.market_intelligence import MarketIntelligence
from agent.financial_agent import Agent
# from services.evaluator import evaluate_response
# from services.logger import log


def build_context(analytics, market, sectors, news):
    top_sectors = sorted(analytics['sector_allocation_percent'].items(), key=lambda x: -x[1])[:3]

    sector_lines = "\n".join(f"{sector} has {percent}% exposure" for sector, percent in top_sectors)

    losers = "\n".join(f"{s['symbol']}: {s['change_pct']}%" for s in analytics["top_losers"])

    negative_sectors="\n".join(f"{sec}: {data['change_percent']}%" for sec,data in sectors.items() if data['change_percent']<0)

    top_news_line = "\n".join(
    f"[{n['impact_level']}] {n.get('headline','No Headline')} | "
    f"Factors: {', '.join(n.get('causal_factors', [])[:2])}"
    for n in news
    if n['impact_level'] == "HIGH"
)
    top_news_line=top_news_line or "No major news"

    context = f"""
    === PORTFOLIO ===
    Value: ₹{analytics['total_current_value']}
    PnL: ₹{analytics['total_daily_pnl']} ({analytics['daily_pnl_percent']:.2f}%)

    === HIGH EXPOSURE SECTORS ===
    {sector_lines}

    === BIGGEST LOSERS ===
    {losers}

    === NEGATIVE SECTOR TRENDS ===
    {negative_sectors}

    === MARKET CONTEXT ===
    Sentiment: {market['market_sentiment']}
    Indices: {market['important_indices']}

    === HIGH IMPACT NEWS ===
    {top_news_line}

    === RISKS ===
    {analytics['risks']}
    """
