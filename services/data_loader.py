import json
from pathlib import Path

class DataLoader:
    def __init__(self,data_path:str):
        self.data_path=Path(data_path)
        self.cache={}
    def load(self,filename:str):
        if filename not in self.cache:
            with open(self.data_path/filename) as f:
                self.cache[filename]=json.load(f)
        return self.cache[filename]
    def get_market_data(self):
        return self.load("market_data.json")
    def get_news_data(self):
        return self.load("news_data.json")["news"]
    def get_all_portfolios(self):
        return self.load("portfolios.json")["portfolios"]
    def get_single_portfolio(self,portfolio_id:str):
        return self.get_all_portfolios().get(portfolio_id,None)
    def get_historical_data(self):
        return self.load("historical_data.json")
    def get_sector_data(self):
        return self.load("sector_mapping.json")

