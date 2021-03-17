class Candle():
    def __init__(self, json_candle):
        self.market = json_candle[0].get("market")
        self.candle_date_time_utc = json_candle[0].get("candle_date_time_utc")
        self.candle_date_time_kst = json_candle[0].get("candle_date_time_kst")
        self.opening_price = json_candle[0].get("opening_price")
        self.high_price = json_candle[0].get("high_price")
        self.trade_price = json_candle[0].get("trade_price")
        self.candle_acc_trade_price = json_candle[0].get("candle_acc_trade_price")
        self.candle_acc_trade_volume = json_candle[0].get("candle_acc_trade_volume")
        self.low_price = json_candle[0].get("low_price")

    def show(self):
        print("market : ", self.market)

    def get_market_name(self):
        return self.market

    def is_nice(self, want_ror):        
        margin = self.high_price - self.opening_price
       # print("market, margin : ", self.market , margin)
        if margin > 0:
            ror = (margin / self.opening_price) * 100
            print("self.ror : ", ror)
            if ror >= want_ror:
                return True
        return False


