from services.data_loader import DataLoader

class MarketIntelligence:
    def __init__(self,loader:DataLoader):
        self.loader=loader
    def analyze_market_sentiment(self):
        #analyzing sentiments of complete market indices
        indices=self.loader.get_market_data()["indices"]
        changes=[indice['change_percent'] for indice in indices.values()]
        avg_change=sum(changes)/len(changes)
        if avg_change > 0.5:
            sentiment = "BULLISH"
        elif avg_change < -0.5:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

        key_indices=["NIFTY50","SENSEX","BANKNIFTY","NIFTYIT","NIFTYPHARMA"]
        important_indices={}
        for name in key_indices:
            if name in indices:
                important_indices[name]=indices[name]['change_percent']
        
        return {
            "market_sentiment":sentiment,
            "average_change_percent":round(avg_change,2),
            "important_indices":important_indices
            }
    def analyze_sector_performance(self):
        #analyzing performance of each sector
        sectors=self.loader.get_market_data()["sector_performance"]
        sector_trend={}
        for sector,data in sectors.items():
            sector_trend[sector]={
                "change_percent":data['change_percent'],
                "sentiment":data['sentiment'],
                "top_gainers":data.get('top_gainers',[]),
                "top_losers":data.get('top_losers',[]),
                "key_drivers":data.get('key_drivers',[])
            }
        return sector_trend

    def analyze_relevant_news(self,portfolio_sectors,portfolio_stocks):
        news=self.loader.get_news_data()
        important_news=[]
        for n in news:
            entities=n.get("entities",{})
            news_sectors=entities.get("sectors",[])
            news_stocks=entities.get("stocks",[])
            scope=n.get("scope","")
            impact=n.get("impact_level","")
            if scope=="MARKET_WIDE" and impact in ["HIGH","MEDIUM"]:
                important_news.append(n)
            elif any(sec in portfolio_sectors for sec in news_sectors) or any(stock in portfolio_stocks for stock in news_stocks):
                important_news.append(n)
        impact_level={"HIGH":0,"MEDIUM":1,"LOW":2}
        important_news.sort(key=lambda x: (impact_level.get(x.get("impact_level"),3),-abs(x.get("sentiment_score",0))))
        return important_news[:7]


    def analyze_historical_data(self,portfolio_sectors):
        hist_data=self.loader.get_historical_data()
        nifty=hist_data.get("index_history",{}).get("NIFTY50",{})
        bank=hist_data.get("index_history",{}).get("BANKNIFTY",{})
        sensex=hist_data.get("index_history",{}).get("SENSEX",{})


        breadth_data=hist_data.get("market_breadth",{})
        fii_dii_data=hist_data.get("fii_dii_data",{})

        sector_weekly_performance=hist_data.get("sector_weekly_performance",{})
        only_portfolio_sectors={
            sector:data for sector,data in sector_weekly_performance.items() if sector in portfolio_sectors
        }
        return {
            "market_trend":{
                "NIFTY50": nifty.get('cumulative_change_percent', 0),
                "BANKNIFTY": bank.get('cumulative_change_percent', 0),
                "SENSEX": sensex.get('cumulative_change_percent', 0)
                },
            "market_breadth": breadth_data,
            "fii_dii_data": fii_dii_data,
            "fii_dii_observations": fii_dii_data.get("observation", ""),
            "sector_weekly_performance":only_portfolio_sectors,
        }