# from lumibot.brokers import Alpaca #BROKER
# from lumibot.backtesting import YahooDataBacktesting #data for testing
# from lumibot.strategies.strategy import Strategy #trading bot
# from lumibot.traders import Trader
# from datetime import datetime
# from alpaca_trade_api import REST
# from timedelta import Timedelta

# API_KEY = 'PKQ8BGAPI4M9L87I3RGB'
# API_SECRET = 'cghhtZCVK09wGK0hnW9mV6mcif77B3KsCN5htYyC'
# BASE_URL= 'https://paper-api.alpaca.markets/v2'

# ALPACA_CREDS = {
#   "API_KEY" : API_KEY,
#   "API_SECRET" : API_SECRET,
#   "PAPER" : True
# }

# class MLTrader(Strategy):
#   def initialize(self, symbol:str="SPY", cash_as_risk:float=.5):
#     self.symbol = symbol
#     self.sleeptime = "24H"
#     self.last_trade = None
#     self.cash_at_risk = cash_as_risk
#     self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

#   def posistion_sizing(self):
#     cash = self.get_cash()
#     last_price = self.get_last_price(self.symbol)
#     quantity = round(cash * self.cash_at_risk / last_price, 0)
#     return cash, last_price, quantity
  
#   def get_dates(self):
#     today = self.get_datetime()
#     three_days_before = today - Timedelta(days=3)
#     return today.strftime('%Y-%m-%d'), three_days_before.strftime('%Y-%m-%d')
  
#   def get_news(self):
#     today, three_days_before = self.get_dates()
#     news = self.api.get_news(symbol=self.symbol, start=three_days_before, end=today)
#     news = [ev.__dict__["_raw"]["Headline"] for ev in news]
#     return news


#   def on_trading_iteration(self):
#     cash, last_price, quantity = self.posistion_sizing()

#     if cash > last_price:
#       if self.last_trade == None:
#         news = self.get_news()
#         print(news)
#         order = self.create_order(
#            self.symbol,
#            quantity,
#            "buy",
#            type="bracket",
#            take_profit_price = last_price*1.20,
#            stop_loss_price = last_price*0.95
#         )
#         self.submit_order(order)
#         self.last_trade = "buy"

# start_date = datetime(2023,12,15)
# end_date = datetime(2023,12,31)
# broker = Alpaca(ALPACA_CREDS)
# strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol":"SPY", "cash_as_risk" : .5})

# strategy.backtest(
#   YahooDataBacktesting,
#   start_date,
#   end_date,
#   parameters={"symbol":"SPY", "cash_as_risk" : .5}
# )
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 
from timedelta import Timedelta 
from finbert_utils import estimate_sentiment

API_KEY = 'PKQ8BGAPI4M9L87I3RGB'
API_SECRET = 'cghhtZCVK09wGK0hnW9mV6mcif77B3KsCN5htYyC'
BASE_URL= 'https://paper-api.alpaca.markets/v2'

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
    "PAPER": True
}

class MLTrader(Strategy): 
    def initialize(self, symbol:str="SPY", cash_at_risk:float=.5): 
        self.symbol = symbol
        self.sleeptime = "24H" 
        self.last_trade = None 
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self): 
        cash = self.get_cash() 
        last_price = self.get_last_price(self.symbol)
        quantity = cash * self.cash_at_risk // last_price
        return cash, last_price, quantity

    def get_dates(self): 
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self): 
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, 
                                 start=three_days_prior, 
                                 end=today) 
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment 

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing() 
        probability, sentiment = self.get_sentiment()

        if cash > last_price: 
            if sentiment == "positive" and probability > .999: 
                if self.last_trade == "sell": 
                    self.sell_all() 
                order = self.create_order(
                    self.symbol, 
                    quantity, 
                    "buy", 
                    type="bracket", 
                    take_profit_price=last_price*1.20, 
                    stop_loss_price=last_price*.95
                )
                self.submit_order(order) 
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > .999: 
                if self.last_trade == "buy": 
                    self.sell_all() 
                order = self.create_order(
                    self.symbol, 
                    quantity, 
                    "sell", 
                    type="bracket", 
                    take_profit_price=last_price*.8, 
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order) 
                self.last_trade = "sell"

start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31) 
broker = Alpaca(ALPACA_CREDS) 
strategy = MLTrader(name='mlstrat', broker=broker, 
                    parameters={"symbol":"SPY", 
                                "cash_at_risk":.5})
strategy.backtest(
    YahooDataBacktesting, 
    start_date, 
    end_date, 
    parameters={"symbol":"SPY", "cash_at_risk":.5}
)
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()