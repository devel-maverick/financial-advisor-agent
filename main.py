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


    system_prompt = """
        You are an elite financial reasoning engine.

        Your job is to explain WHY the portfolio moved today.

        STRICT RULES:

        1. Identify the SINGLE most impactful driver
        2. A sector can be a primary driver ONLY if it has BOTH meaningful exposure AND strong movement
        3. If no such sector exists, prioritize macro/news drivers
        4. Build causal chain:
        News/Event → Sector → Stocks → Portfolio impact
        5. Do NOT introduce any information not present in context
        6. Ignore minor signals
        7. End with ONE actionable suggestion
        8.If a sector has low exposure, justify why it still impacted the portfolio significantly.
        Do NOT introduce any information not present in the context.

        OUTPUT FORMAT:

        Summary:
        Primary Driver:
        Causal Chain:
        Key Risk:
        Action:
        """


    user_prompt = f"""
        Analyze this portfolio and explain what happened today:

        {context}
        """
    return context, system_prompt, user_prompt




