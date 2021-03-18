class Candle():
    def __init__(self, json_candle):
        self.candles = json_candle
        self.market = json_candle[0].get("market")
        self.candle_date_time_utc = json_candle[0].get("candle_date_time_utc")
        self.candle_date_time_kst = json_candle[0].get("candle_date_time_kst")
        self.opening_price = json_candle[0].get("opening_price") #시가
        self.high_price = json_candle[0].get("high_price")
        self.trade_price = json_candle[0].get("trade_price") #종가
        self.candle_acc_trade_price = json_candle[0].get("candle_acc_trade_price")
        self.candle_acc_trade_volume = json_candle[0].get("candle_acc_trade_volume")
        self.low_price = json_candle[0].get("low_price")

    def show(self):
        print("market : ", self.market)

    def get_market_name(self):
        return self.market

    def get_max_trade_candle(self):
        #종가가 최고점인 캔들 반환
        max_candle = None
        for candle in self.candles:
            if max_candle == None:
                max_candle = candle
                continue
            if max_candle.get("trade_price") < candle.get("trade_price"):
                max_candle = candle
        return max_candle

    def get_current_candle(self):
        return self.candles[0]

    def get_current_trade_price(self):
        return self.candles[0].get("trade_price")

    def get_bid_price(self):
        if self.candles[1].get("trade_price") > self.candles[0].get("trade_price"):
            return self.candles[0].get("trade_price")
        else : 
            margin = self.candles[0].get("trade_price") - self.candles[1].get("trade_price")
            ror = (margin / self.candles[0].get("trade_price")) * 100
            if ror >= 1.5 :
                return self.candles[1].get("trade_price")
            else :
                return self.candles[0].get("trade_price") 

    def is_pumped(self):
        margin = self.candles[0].get("high_price") - self.candles[1].get("trade_price")
        if margin <= 0:
            return False 

        ror = (margin / self.candles[0].get("high_price")) * 100
        if ror >= 2.2 : 
            print("this pumped")
            return True
        return False

    def is_low_price_goup(self):
        return self.candles[0].get("low_price") > self.candles[1].get("low_price") > self.candles[2].get("low_price")
    
    def is_trade_price_goup(self):
        return self.candles[0].get("trade_price") > self.candles[1].get("trade_price") > self.candles[2].get("trade_price")
    

