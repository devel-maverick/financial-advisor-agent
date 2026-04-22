import json
from pathlib import Path

class DataLoader:
    def __init__(self,data_path):
        self.data_path=Path(data_path)
    def load(self,filename):
        with open(self.data_path/filename) as f:
            return json.load(f)
    def get_market_data(self):
        return self.load("market_data.json")
    def get_news_data(self):
        return self.load("news_data.json")["news"]
    def get_all_portfolios(self):
        return self.load("portfolios.json")["portfolios"]
    def get_single_portfolio(self,portfolio_id):
        return self.get_all_portfolios().get(portfolio_id,None)
loader = DataLoader("data")

data = loader.get_all_portfolios()

print(type(data))
print(data.keys())