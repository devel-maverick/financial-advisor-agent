from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import re
from dotenv import load_dotenv
load_dotenv(override=True)
from main import build_context, Agent, DataLoader, PortfolioAnalytics, MarketIntelligence, evaluate_response, logger
from services.langfuse import langfuse

app = FastAPI(title="DalalAI Financial Advisor API")

class AnalysisRequest(BaseModel):
    portfolio_id: str

@app.get("/")
def read_root():
    return {"message": "Welcome to DalalAI Financial Advisor API", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/portfolio/{portfolio_id}")
def get_portfolio_data(portfolio_id: str):
    logger.info(f"API: Fetching dashboard data for {portfolio_id}")
    try:
        loader = DataLoader("data")
        portfolio_engine = PortfolioAnalytics(loader)
        analytics = portfolio_engine.portfolio_analytics(portfolio_id)
        if not analytics or isinstance(analytics, str):
            logger.warning(f"⚠️ Portfolio {portfolio_id} not found")
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        market_engine = MarketIntelligence(loader)
        market = market_engine.analyze_market_sentiment()
        sectors = market_engine.analyze_sector_performance()
        portfolio_sectors = list(analytics["sector_allocation_percent"].keys())
        historical = market_engine.analyze_historical_data(portfolio_sectors)
        
        portfolio_stocks = [s["symbol"] for s in analytics["top_gainers"]] + [s["symbol"] for s in analytics["top_losers"]]
        news = market_engine.analyze_relevant_news(portfolio_sectors, portfolio_stocks)
        
        return {
            "analytics": analytics,
            "market": market,
            "sectors": sectors,
            "news": news,
            "historical": historical
        }
    except Exception as e:
        logger.error(f"API Data Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_portfolio(request: AnalysisRequest):
    portfolio_id = request.portfolio_id
    logger.info(f"API: Received analysis request for {portfolio_id}")
    
    try:
        loader = DataLoader("data")
        portfolio_engine = PortfolioAnalytics(loader)
        analytics = portfolio_engine.portfolio_analytics(portfolio_id)
        if not analytics or isinstance(analytics, str):
            logger.warning(f"⚠️ Portfolio {portfolio_id} not found for analysis")
            raise HTTPException(status_code=404, detail="Portfolio not found")
        market_engine = MarketIntelligence(loader)
        market = market_engine.analyze_market_sentiment()
        sectors = market_engine.analyze_sector_performance()
        portfolio_sectors = list(analytics["sector_allocation_percent"].keys())
        historical = market_engine.analyze_historical_data(portfolio_sectors)
        
        portfolio_stocks = [s["symbol"] for s in analytics["top_gainers"]] + [s["symbol"] for s in analytics["top_losers"]]
        news = market_engine.analyze_relevant_news(portfolio_sectors, portfolio_stocks)
        
        context, system_prompt, user_prompt = build_context(analytics, market, sectors, news, historical)
        
        agent = Agent()
        result = agent.analyze(user_prompt, system_prompt)
        eval_result = evaluate_response(result)
        
        langfuse.flush()
        
        import json
        try:
            clean_result = re.sub(r"```json\s*|\s*```", "", result.strip())
            analysis_json = json.loads(clean_result)
        except:
            analysis_json = result 
            
        return {
            "portfolio_id": portfolio_id,
            "analysis": analysis_json,
            "evaluation": eval_result,
            "metadata": {
                "score": eval_result.get("score"),
                "grade": eval_result.get("grade")
            }
        }
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
