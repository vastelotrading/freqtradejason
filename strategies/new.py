# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from freqtrade.strategy.hyper import IntParameter
from freqtrade.strategy.interface import IStrategy
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class newstrat(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_buy_trend, populate_sell_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Buy hyperspace params:
    buy_params = {
        "buy_ma_count": 4,
        "buy_ma_gap": 15,
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_ma_count": 12,
        "sell_ma_gap": 68,
    }

    # ROI table:
    minimal_roi = {
        "0": 0.523,
        "1553": 0.123,
        "2332": 0.076,
        "3169": 0
    }

    # Stoploss:
    stoploss = -0.345

    # Trailing stop:
    trailing_stop = False  # value loaded from strategy
    trailing_stop_positive = None  # value loaded from strategy
    trailing_stop_positive_offset = 0.0  # value loaded from strategy
    trailing_only_offset_is_reached = False  # value loaded from strategy

    # Opimal Timeframe
    timeframe = "4h"

    count_max = 20
    gap_max = 100

    buy_ma_count = IntParameter(1, count_max, default=7, space="buy")
    buy_ma_gap = IntParameter(1, gap_max, default=7, space="buy")

    sell_ma_count = IntParameter(1, count_max, default=7, space="sell")
    sell_ma_gap = IntParameter(1, gap_max, default=94, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for count in range(self.count_max):
            for gap in range(self.gap_max):
                if count*gap > 1 and count*gap not in dataframe.keys():
                    dataframe[count*gap] = ta.TEMA(
                        dataframe, timeperiod=int(count*gap)
                    )
        print(" ", metadata['pair'], end="\t\r")

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # I used range(self.buy_ma_count.value) instade of self.buy_ma_count.range
        # Cuz it returns range(7,8) but we need range(8) for all modes hyperopt, backtest and etc

        for ma_count in range(self.buy_ma_count.value):
            key = ma_count*self.buy_ma_gap.value
            past_key = (ma_count-1)*self.buy_ma_gap.value
            if past_key > 1 and key in dataframe.keys() and past_key in dataframe.keys():
                conditions.append(dataframe[key] < dataframe[past_key])

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        for ma_count in range(self.sell_ma_count.value):
            key = ma_count*self.sell_ma_gap.value
            past_key = (ma_count-1)*self.sell_ma_gap.value
            if past_key > 1 and key in dataframe.keys() and past_key in dataframe.keys():
                conditions.append(dataframe[key] > dataframe[past_key])

        if conditions:
            dataframe.loc[reduce(lambda x, y: x | y, conditions), "sell"] = 1
        return dataframe