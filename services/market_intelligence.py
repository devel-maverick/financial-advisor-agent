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
    




        