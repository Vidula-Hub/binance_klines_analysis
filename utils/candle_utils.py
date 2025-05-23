from datetime import datetime
import pandas as pd
import numpy as np
from datetime import datetime, timezone


class CandleStick:
    def __init__(self):
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.volume = 0
        self.open_time = 0
        self.close_time = 0
        self.symbol = ''
        self.interval = ''
        self.is_bullish = False
        self.body_top = 0
        self.body_bottom = 0
        self.upper_wick_percentage = 0
        self.lower_wick_percentage = 0
        self.date = None
        self.type = ''
        self.type_two = ''
        self.type_three = ''
        self.moving_average = 0
        self.is_high_formed_first = False
        self.high_time = 0
        self.low_time = 0
        self.isCrossed = False
    
    def to_dict(self):
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "open_time": self.open_time,
            "close_time": self.close_time,
            "symbol": self.symbol,
            "interval": self.interval,
            "is_bullish": self.is_bullish,
            "body_top": self.body_top,
            "body_bottom": self.body_bottom,
            "upper_wick_percentage": self.upper_wick_percentage,
            "lower_wick_percentage": self.lower_wick_percentage,
            "date": self.date,
            "type": self.type,
            "type_two": self.type_two,
            "type_three": self.type_three,
            "moving_average": self.moving_average,
            "is_high_formed_first": self.is_high_formed_first,
            "high_time": self.high_time,
            "low_time": self.low_time,
            "isCrossed": self.isCrossed
        }



def is_white_marubozu(candle):
    return candle.open == candle.low and candle.close == candle.high

def is_inverted_hammer(candle):
    upper_shadow = candle.high - max(candle.open, candle.close)
    body_length = abs(candle.close - candle.open)
    return upper_shadow >= 2 * body_length and body_length <= (candle.high - candle.low) * 0.3

def is_hanging_man(candle):
    body_length = abs(candle.close - candle.open)
    lower_shadow = min(candle.open, candle.close) - candle.low
    return lower_shadow >= 2 * body_length and body_length <= (candle.high - candle.low) * 0.3

def is_black_marubozu(candle):
    return candle.open == candle.high and candle.close == candle.low

def is_shooting_star(candle):
    upper_shadow = candle.high - max(candle.open, candle.close)
    body_length = abs(candle.close - candle.open)
    return upper_shadow >= 2 * body_length and body_length <= (candle.high - candle.low) * 0.3

def is_doji(candle):
    body_length = abs(candle.close - candle.open)
    return body_length <= (candle.high - candle.low) * 0.1

def is_spinning_top(candle):
    body_length = abs(candle.close - candle.open)
    return body_length >= (candle.high - candle.low) * 0.2 and body_length <= (candle.high - candle.low) * 0.5

def is_high_wave(candle):
    body_length = abs(candle.close - candle.open)
    total_length = candle.high - candle.low
    return body_length <= total_length * 0.1 and (candle.high - max(candle.open, candle.close) + min(candle.open, candle.close) - candle.low) >= total_length * 0.7

# Identify pattern function
def identify_pattern(candle):
    # print("candle",candle.open)
    if is_white_marubozu(candle):
        return 'White Marubozu'
    elif is_inverted_hammer(candle):
        return 'Inverted Hammer'
    elif is_hanging_man(candle):
        return 'Hanging Man'
    elif is_black_marubozu(candle):
        return 'Black Marubozu'
    elif is_shooting_star(candle):
        return 'Shooting Star'
    elif is_doji(candle):
        return 'Doji'
    elif is_spinning_top(candle):
        return 'Spinning Top'
    elif is_high_wave(candle):
        return 'high Wave'
    else:
        return '-'

# # Example usage
# candle = {'open': 100, 'high': 110, 'low': 95, 'close': 96}

# pattern = identify_pattern(candle)
# print(pattern)

# Example usage
# data = pd.DataFrame({
#     'open': [100, 102, 101, 105, 107, 110, 115],
#     'high': [103, 103, 102, 108, 110, 116, 117],
#     'low': [95, 101, 100, 104, 106, 109, 115],
#     'close': [96, 101, 105, 106, 109, 114, 116]
# })

# data.Candle Type = data.apply(identify_candle_type, axis=1)
# print(data.Candle Type)
    
# import pandas as pd
# import numpy as np

def is_piercing_pattern(candles):
    first, second = candles
    return first.close < first.open and \
           second.open < first.close and \
           second.close > first.open and \
           second.close >= first.low + (first.high - first.low) / 2

def is_bullish_engulfing(candles):
    first, second = candles
    return first.close < first.open and \
           second.open < first.close and \
           second.close > first.open

def is_bullish_harami(candles):
    first, second = candles
    return first.close < first.open and \
           second.open > first.close and \
           second.close < first.open

def is_tweezer_bottom(candles):
    first, second = candles
    return first.low == second.low and \
           is_bearish_candle(first) and is_bullish_candle(second)

def is_three_inside_up(candles):
    first, second, third = candles
    return is_bullish_harami([first, second]) and \
           third.close > first.high

def is_on_neck_pattern(candles):
    first, second = candles
    return is_bearish_candle(first) and \
           is_bullish_candle(second) and \
           np.isclose(second.close, first.low, atol=0.02 * (first.high - first.low))

def is_bullish_counterattack(candles):
    first, second = candles
    return first.close < first.open and \
           second.close > second.open and \
           np.isclose(second.close, first.close)

def is_dark_cloud_cover(candles):
    first, second = candles
    return first.close > first.open and \
           second.open > first.close and \
           second.close < first.open and \
           second.close < first.close - (first.high - first.low) / 2

def is_bearish_engulfing(candles):
    first, second = candles
    return first.close > first.open and \
           second.open > second.close and \
           second.open > first.close and \
           second.close < first.open

def is_bearish_harami(candles):
    first, second = candles
    return first.close > first.open and \
           second.open < first.close and \
           second.close > first.open

def is_tweezer_top(candles):
    first, second = candles
    return first.high == second.high and \
           is_bullish_candle(first) and is_bearish_candle(second)

def is_three_inside_down(candles):
    first, second, third = candles
    return is_bearish_harami([first, second]) and \
           third.close < first.low

def is_bearish_counterattack(candles):
    first, second = candles
    return first.close > first.open and \
           second.close < second.open and \
           np.isclose(second.close, first.close)

def is_upside_tasuki_gap(candles):
    first, second, third = candles
    return first.close > first.open and \
           second.open > first.close and \
           second.close > second.open and \
           third.open < third.close and \
           third.open < second.close and \
           third.close < second.open

def is_downside_tasuki_gap(candles):
    first, second, third = candles
    return first.close < first.open and \
           second.open < first.close and \
           second.close < second.open and \
           third.open > third.close and \
           third.open > second.close and \
           third.close > second.open

# Helper functions
def is_bullish_candle(candle):
    return candle.close > candle.open

def is_bearish_candle(candle):
    return candle.open > candle.close

# Identify pattern function
def identify_pattern_two(candles):
    if len(candles) == 2:
        if is_piercing_pattern(candles):
            return 'Piercing Pattern'
        elif is_bullish_engulfing(candles):
            return 'Bullish Engulfing'
        elif is_bullish_harami(candles):
            return 'Bullish Harami'
        elif is_tweezer_bottom(candles):
            return 'Tweezer Bottom'
        elif is_on_neck_pattern(candles):
            return 'On-Neck Pattern'
        elif is_bullish_counterattack(candles):
            return 'Bullish Counterattack'
        elif is_dark_cloud_cover(candles):
            return 'Dark Cloud Cover'
        elif is_bearish_engulfing(candles):
            return 'Bearish Engulfing'
        elif is_bearish_harami(candles):
            return 'Bearish Harami'
        elif is_tweezer_top(candles):
            return 'Tweezer Top'
        elif is_bearish_counterattack(candles):
            return 'Bearish Counterattack'
    elif len(candles) == 3:
        if is_three_inside_up(candles):
            return 'Three Inside Up'
        elif is_three_inside_down(candles):
            return 'Three Inside Down'
        elif is_upside_tasuki_gap(candles):
            return 'Upside Tasuki Gap'
        elif is_downside_tasuki_gap(candles):
            return 'Downside Tasuki Gap'
    return '-'

# # Example usage
# candles = [
#     {'open': 100, 'high': 103, 'low': 95, 'close': 96},
#     {'open': 97, 'high': 102, 'low': 96, 'close': 101}
# ]

# pattern = identify_pattern(candles)
# print(pattern)


# # Example usage
# data = pd.DataFrame({
#     'open': [100, 102, 101, 105, 107, 110, 115],
#     'high': [103, 103, 102, 108, 110, 116, 117],
#     'low': [95, 101, 100, 104, 106, 109, 115],
#     'close': [96, 101, 105, 106, 109, 114, 116]
# })

# patterns = identify_pattern(data)
# print(patterns)

# import pandas as pd
# import numpy as np


def is_morning_star(candles):
    first, second, third = candles
    return first.close < first.open and \
           abs(second.close - second.open) < (first.open - first.close) / 3 and \
           third.close > third.open and \
           third.close > first.open

def is_three_white_soldiers(candles):
    return all([
        candle.close > candle.open and
        candle.open > prev_candle.close
        for candle, prev_candle in zip(candles, candles[1:])
    ])

def is_three_outside_up(candles):
    first, second, third = candles
    return is_bearish_candle(first) and \
           is_bullish_engulfing([second, first]) and \
           third.close > second.close

def is_evening_star(candles):
    first, second, third = candles
    return first.close > first.open and \
           abs(second.close - second.open) < (first.close - first.open) / 3 and \
           third.close < third.open and \
           third.close < first.open

def is_three_black_crows(candles):
    return all([
        candle.close < candle.open and
        candle.open < prev_candle.close
        for candle, prev_candle in zip(candles, candles[1:])
    ])

def is_three_outside_down(candles):
    first, second, third = candles
    return is_bullish_candle(first) and \
           is_bearish_engulfing([second, first]) and \
           third.close < second.close

def is_falling_three_methods(candles):
    first, second, third, fourth, fifth = candles
    return is_bearish_candle(first) and \
           is_bearish_candle(fifth) and \
           all(is_bullish_candle(candle) for candle in [second, third, fourth]) and \
           fifth.close < first.open

def is_rising_three_methods(candles):
    first, second, third, fourth, fifth = candles
    return is_bullish_candle(first) and \
           is_bullish_candle(fifth) and \
           all(is_bearish_candle(candle) for candle in [second, third, fourth]) and \
           fifth.close > first.open

def is_mat_hold(candles):
    # Complex pattern, needs specific criteria based on trend analysis
    # Placeholder function
    return False

def is_rising_window(candles):
    first, second = candles[0], candles[1]
    return second.low > first.high

def is_falling_window(candles):
    first, second = candles[0], candles[1]
    return second.high < first.low

# Helper functions
def is_bullish_candle(candle):
    return candle.close > candle.open

def is_bearish_candle(candle):
    return candle.open > candle.close

# def is_bullish_engulfing(candle, prev_candle):
#     return prev_candle.open > prev_candle.close and \
#            candle.open < candle.close and \
#            candle.open < prev_candle.close and \
#            candle.close > prev_candle.open

# def is_bearish_engulfing(candle, prev_candle):
#     return prev_candle.open < prev_candle.close and \
#            candle.open > candle.close and \
#            candle.open > prev_candle.close and \
#            candle.close < prev_candle.open

# Identify pattern function
def identify_pattern_three(candles):
    if len(candles) == 3:
        if is_morning_star(candles):
            return 'Morning Star'
        elif is_three_white_soldiers(candles):
            return 'Three White Soldiers'
        elif is_three_outside_up(candles):
            return 'Three Outside Up'
        elif is_evening_star(candles):
            return 'Evening Star'
        elif is_three_black_crows(candles):
            return 'Three Black Crows'
        elif is_three_outside_down(candles):
            return 'Three Outside Down'
    elif len(candles) == 5:
        if is_falling_three_methods(candles):
            return 'Falling Three Methods'
        elif is_rising_three_methods(candles):
            return 'Rising Three Methods'
        elif is_mat_hold(candles):
            return 'Mat Hold'
    elif len(candles) == 2:
        if is_rising_window(candles):
            return 'Rising Window'
        elif is_falling_window(candles):
            return 'Falling Window'
    return '-'

# # Example usage
# candles = [
#     {'open': 100, 'high': 103, 'low': 95, 'close': 96},
#     {'open': 97, 'high': 102, 'low': 96, 'close': 101},
#     {'open': 102, 'high': 108, 'low': 100, 'close': 107}
# ]

# pattern = identify_pattern(candles)
# print(pattern)

def binanceToCandleData(candlestick,SYMBOL,PERIOD):
    candlestick_data = CandleStick()  
    candlestick_data.open = float(candlestick[1])
    candlestick_data.high = float(candlestick[2])
    candlestick_data.low = float(candlestick[3])
    candlestick_data.close = float(candlestick[4])
    candlestick_data.volume = float(candlestick[5])
    candlestick_data.open_time = int(candlestick[0])
    candlestick_data.close_time = int(candlestick[6])
    candlestick_data.symbol = SYMBOL
    candlestick_data.interval = PERIOD
    candlestick_data.is_bullish = candlestick_data.close > candlestick_data.open
    candlestick_data.body_top = candlestick_data.open if candlestick_data.open > candlestick_data.close else candlestick_data.close
    candlestick_data.body_bottom = candlestick_data.close if candlestick_data.open > candlestick_data.close else candlestick_data.open
    # Calculate Upper Wick Percentage
    candlestick_data.upper_wick_percentage = round(((candlestick_data.high - candlestick_data.body_top) / (candlestick_data.high - candlestick_data.low)) * 100,2)
    # Calculate Lower Wick Percentage
    candlestick_data.lower_wick_percentage = round(((candlestick_data.body_bottom - candlestick_data.low) / (candlestick_data.high - candlestick_data.low)) * 100,2)
    
    #date to UTC date
    candlestick_data.date = datetime.fromtimestamp(candlestick[0] / 1000, tz=timezone.utc)
    # print('candlestick_data.date',candlestick_data.date)
    candlestick_data.type = identify_pattern(candlestick_data)
    return candlestick_data

def binanceArrayToCandleStickArray(data,SYMBOL,PERIOD):
    allCandlesticks = []
    for candlestick in data:
        allCandlesticks.append(binanceToCandleData(candlestick,SYMBOL,PERIOD))
    return allCandlesticks

def updateCandlePattern(data):
    currentCandles = []
    allCandlesticks = data
    for candlestick in allCandlesticks:
        lengthOFCurrentCandles = len(currentCandles)

        if(lengthOFCurrentCandles >= 3):
                currentCandles.pop(0)
        currentCandles.append(candlestick)

        if(lengthOFCurrentCandles >= 2):
                last_two_candles = currentCandles[-2:]
                pattern = identify_pattern_two(last_two_candles)
                if(pattern != '-'):
                    allCandlesticks[-1].type_two = pattern
               
                    
        if(lengthOFCurrentCandles >= 3):
                pattern = identify_pattern_three(currentCandles)
                if(pattern != '-'):
                    allCandlesticks[-1].type_three = pattern

       
    return allCandlesticks

def calculate_moving_average(candlesticks, period):
    moving_averages = []
    for i in range(len(candlesticks)):
        if i >= period - 1:
            sum_close = sum(candle.close for candle in candlesticks[i - period + 1:i + 1])
            moving_average = round(sum_close / period,2)
            candlesticks[i].moving_average = moving_average
            moving_averages.append(moving_average)
        else:
            candlesticks[i].moving_average = 0.0
    return candlesticks

from datetime import timedelta
from datetime import timedelta

def analyze_hourly_data(candlesticks):
    if not candlesticks:
        return None
    
    high_time = None
    low_time = None
    high_price = candlesticks[0].high
    low_price = candlesticks[0].low
    
    for candle in candlesticks:
        if candle.high >= high_price:
            high_price = candle.high
            high_time = candle.close_time
        if candle.low <= low_price:
            low_price = candle.low
            low_time = candle.close_time
    
    is_crossed = True if high_time is not None and low_time is not None else False
    is_high_formed_first = True if high_time is not None and (low_time is None or high_time < low_time) else False
    
    if is_high_formed_first:
        high_time_diff = (high_time - candlesticks[0].close_time) // 1000 // 60
        low_time_diff = (low_time - candlesticks[0].close_time) // 1000 // 60
    else:
        low_time_diff = (low_time - candlesticks[0].close_time) // 1000 // 60
        high_time_diff = (high_time - candlesticks[0].close_time) // 1000 // 60
    
    return {
        "isCrossed": is_crossed,
        "is_high_formed_first": is_high_formed_first,
        "high_time": high_time_diff,
        "low_time": low_time_diff
    }
  

