from dotenv import load_dotenv
load_dotenv(override=True)

from services.data_loader import DataLoader
from services.portfolio_analytics import PortfolioAnalytics
from services.market_intelligence import MarketIntelligence
from agent.financial_agent import Agent
from services.langfuse import langfuse
from services.evaluator import evaluate_response
from services.logger import logger

def build_context(analytics, market, sectors, news, historical):
    top_sectors = sorted(analytics['sector_allocation_percent'].items(), key=lambda x: -x[1])[:3]

    sector_lines = "\n".join(f"{sector} has {percent}% exposure" for sector, percent in top_sectors)

    losers = "\n".join(f"{s['symbol']}: {s['change_pct']}%" for s in analytics["top_losers"])

    negative_sectors="\n".join(f"{sec}: {data['change_percent']}%" for sec,data in sectors.items() if data['change_percent']<0)

    top_news_line = "\n".join(
        f"[{n['impact_level']}] {n.get('headline','No Headline')} | "
        f"Factors: {', '.join(n.get('causal_factors', [])[:2])}"
        for n in news
        if n['impact_level'] in ["HIGH", "MEDIUM"]
    )
    top_news_line = top_news_line or "No major news"

    #imp: Edge case and conflicting signal handling

    # case1: Positive news + Negative price action
    case1 = []
    for n in news:
        for stock in analytics.get('stocks', []):
            if stock['symbol'] in n.get('entities', {}).get('stocks', []):
                if n.get('sentiment_score', 0) > 0.3 and stock.get('day_change_percent', 0) < 0:
                    case1.append(f"{stock['symbol']}: positive news (score {n['sentiment_score']:+.2f}) but fell {stock['day_change_percent']:.2f}% — sector/macro overrode stock news")
    case1_lines = "\n".join(case1) or "None detected"

    # case2: Sector vs Stock divergence
    case2 = []
    for stock in analytics.get('stocks', []):
        sector_chg = sectors.get(stock.get('sector',''), {}).get('change_percent', 0)
        stock_chg = stock.get('day_change_percent', 0)
        if sector_chg < -0.5 and stock_chg > 0.3:
            case2.append(f"{stock['symbol']} +{stock_chg:.2f}% vs {stock['sector']} {sector_chg:.2f}% — indicating stock-specific factors performed better than sector")
        elif sector_chg > 0.5 and stock_chg < -0.3:
            case2.append(f"{stock['symbol']} {stock_chg:.2f}% vs {stock['sector']} +{sector_chg:.2f}% — indication stock underperformance despite positive sector momentum")
    case2_lines = "\n".join(case2) or "None detected"

    # case3: Mixed signals(unclear news)
    case3 = []
    for n in news:
        score = n.get('sentiment_score', 0)
        if -0.2 <= score <= 0.2 and n.get('impact_level') in ['HIGH', 'MEDIUM']:
            case3.append(f"{n.get('headline','')} (score {score:+.2f}) — unclear news — ambiguous signal with mixed positive and negative factors")
    case3_lines = "\n".join(case3) or "None detected"

    # Simple MF breakdown for prompt
    mf_text = []
    for mf in analytics.get("mf_breakdown", []):
        stocks_str = ", ".join(mf["top_stocks"]) or "N/A"
        sectors_str = ", ".join(f"{s}:{w}%" for s,w in mf["top_sectors"]) or "N/A"
        overlap = ", ".join(mf["overlap_with_stocks"]) or "None"
        mf_text.append(f"{mf['name']} ({mf['category']}): NAV {mf['nav_change']:+.2f}% | Weight: {mf['weight']}% | Stocks: {stocks_str} | Sectors: {sectors_str} | Overlap with direct: {overlap}")
    mf_section = "\n    ".join(mf_text) if mf_text else "No MFs"

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

    === MUTUAL FUND BREAKDOWN ===
    {mf_section}

    === EDGECASE1: Positive News + Negative Price ===
    {case1_lines}

    === EDGECASE2: Stock vs Sector Divergence ===
    {case2_lines}

    === EDGECASE3: Mixed Ambiguous Signals ===
    {case3_lines}

    === HISTORICAL TRENDS (Last 7 Days) ===
    Indices: {historical['market_trend']}
    Market breadth: {historical['market_breadth']}
    FII/DII Observation: {historical['fii_dii_observations']}
    Relevant Sector History: {historical['sector_weekly_performance']}
    """


    system_prompt = """
        You are an elite financial reasoning engine.

        Your job is to explain WHY the portfolio moved today.

        STRICT RULES:

        1. Identify the SINGLE most impactful driver
        2. A sector can be a primary driver ONLY if it has BOTH meaningful exposure AND strong movement
        3. If no such sector exists, prioritize macro/news drivers
        4. Build a step-by-step causal chain. Each step on a new line starting with a dash and ONE of these exact prefixes:
           [NEWS] for the triggering news/event
           [SECTOR] for sector-level impact
           [STOCK] for individual stock impact
           [PORTFOLIO] for final portfolio impact
           Example: - [NEWS] RBI holds rate steady → - [SECTOR] Banking fell -2.45% → - [STOCK] HDFCBANK -3.51% → - [PORTFOLIO] Portfolio lost -2.81%
        5. Do NOT introduce any information not present in context
        6. Ignore minor signals
        7. End with ONE actionable suggestion
        8.If a sector has low exposure, justify why it still impacted the portfolio significantly.
        9.Use specific numbers (% change, exposure, PnL) wherever possible.
        10.Only consider sectors with significant exposure (>10%) as primary drivers.
            Avoid attributing major impact to low-weight sectors.
        11. If you see conflicting signals, clearly state which one dominated the outcome and explain why the other was overridden.
        12. If a stock had positive news but still fell — don't skip this. Explain that sector-wide or macro pressure was stronger than the stock-specific good news.
        13. If a stock moved against its sector (e.g., stock up while sector is down), flag it as a divergence and identify the specific reason driving that stock independently.
        14. If any news has a sentiment score close to zero, treat it as ambiguous — acknowledge both sides briefly and avoid leaning positive or negative without evidence.
        15. If any single sector has >40% exposure, you MUST explicitly flag this as a "Concentration Risk" in the Key Risk section.
        16. Use the HISTORICAL TRENDS to contextualize today's movement. For example, if the market has been bearish for 7 days, today's fall might be a continuation of a trend rather than a one-off event.
        17. For MUTUAL FUNDS: explain their movement via underlying stocks and sectors. If MF stocks overlap with direct holdings, flag the compounded exposure.
        
        # OUTPUT FORMAT:
        You MUST respond in strict JSON format with these exact keys:
        {
          "summary": "Detailed 2-3 sentence overview of why the portfolio moved as it did, mentioning specific macro and sector factors.",
          "primary_driver": "In-depth explanation of the #1 most impactful factor, including the 'Why' behind its movement.",
          "causal_chain": ["list of strings starting with [NEWS], [SECTOR], [STOCK], or [PORTFOLIO] showing the flow"],
          "conflicting_signals": "Detailed explanation of any divergence or conflicting news vs price action.",
          "key_risk": "Specific risk identification (e.g. concentration, rate sensitivity) with numbers.",
          "action": "One specific, data-backed actionable suggestion for the investor.",
          "self_score": number (0-100) based on your confidence in this analysis,
          "justification": "A brief explanation of why you gave yourself this score, acknowledging any data gaps or uncertainties."
        }

        Do NOT include any markdown formatting like ```json or any other text outside the JSON object.
        """


    user_prompt = f"""
        Analyze this portfolio and explain what happened today:

        {context}
        """
    return context, system_prompt, user_prompt

def run(portfolio_id: str):

    logger.info(f"Starting analysis for portfolio: {portfolio_id}")

    loader=DataLoader("data")
    portfolio_engine = PortfolioAnalytics(loader)
    analytics = portfolio_engine.portfolio_analytics(portfolio_id)

    logger.info("Portfolio analytics generated.")

    market_engine = MarketIntelligence(loader)
    market = market_engine.analyze_market_sentiment()

    logger.info("Market sentiment analyzed.")
    
    sectors = market_engine.analyze_sector_performance()
    portfolio_sectors = list(analytics["sector_allocation_percent"].keys())
    historical = market_engine.analyze_historical_data(portfolio_sectors)
    
    portfolio_stocks = [s["symbol"] for s in analytics["top_gainers"]] + [s["symbol"] for s in analytics["top_losers"]]
    news = market_engine.analyze_relevant_news(portfolio_sectors, portfolio_stocks)
    
    logger.info(f"Extracted {len(news)} relevant news articles.")

    context, system_prompt, user_prompt = build_context(analytics,market,sectors,news,historical)

    logger.info("Context and prompts built successfully.")

    agent=Agent()
    logger.info("Getting output from LLM...")
    result=agent.analyze(user_prompt,system_prompt)
    
    logger.info("Evaluating reasoning quality...")
    eval_result=evaluate_response(result)   

    logger.info(f"Evaluation completed. Score: {eval_result.get('mixed_score', 0)}/100")

    print("\n====== FINAL ANALYSIS ======\n")
    print(result)
    
    grade_icon = {"EXCELLENT": "🏆", "GOOD": "✅", "POOR": "⚠️"}.get(eval_result.get("grade", "POOR"), "•")
    print(f"\n====== EVALUATION ======")
    print(f"Confidence Score : {eval_result['mixed_score']}/100")
    print(f"Grade : {grade_icon} {eval_result['grade']}")
    print("Checks:")
    for name, passed, reason in eval_result["checks"]:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name} — {reason}")

    return result

if __name__ == "__main__":
    run("PORTFOLIO_001")
    langfuse.flush()  # ensure all traces are sent before program exits


