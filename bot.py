#   Binance Bot V1

# IMPORTS
#-------------------------------------------#
import time
import datetime
from math import ceil, floor
import requests, json
import sqlite3

# pip install pandas
import pandas as pd
# pip install numpy
import numpy as np
# pip install python-binance
from binance.client import Client
#-------------------------------------------#

# FUNCTIONS
#-------------------------------------------#

# - BOT TIME
def bottime():
    bottime = time.strftime('%c')
    return bottime

# - RSI DATA
def computeRSI(data, time_window):
    diff = np.diff(data)
    up_chg = 0 * diff
    down_chg = 0 * diff

    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[diff > 0]

    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[diff < 0]

    up_chg = pd.DataFrame(up_chg)
    down_chg = pd.DataFrame(down_chg)

    up_chg_avg = up_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window - 1, min_periods=time_window).mean()

    rs = abs(up_chg_avg / down_chg_avg)
    rsi = 100 - 100 / (1 + rs)
    rsi = int(rsi[0].iloc[-1])
    return rsi

# -
def fn_round(pair, num, direction = floor):
    URL = "https://www.binance.com/api/v3/exchangeInfo?symbols=[%22" + str(pair) + "%22]"
    result = requests.get(URL).json()

    stepSize = result['symbols'][0]['filters'][2]['stepSize']
    zeros = 0
    number = float(stepSize)
    while number < 0.1:
        number *= 10
        zeros += 1
    if float(stepSize) > 0.1:
        places = zeros
    else:
        places = zeros + 1
    return direction(num * (10**places)) / float(10**places)

# - BALANCE CHECK
def balanceCheck(pair):
    balance = client.get_asset_balance(asset=pair)
    return balance

# - COIN PRICE
def coinPriceCheck(pair):
    priceData = client.get_ticker(symbol=pair)
    price = priceData["askPrice"]
    return price

# - LAST TRANSACTION AND REMINDER
def lastTransactionRemainder(pairs):
    trades = {}
    for pair in pairs:
        myTrades = client.get_my_trades(symbol=pair, limit=1)
        if myTrades != []:
            trades[myTrades[0]["time"]] = [myTrades[0]["symbol"], myTrades[0]["commissionAsset"], myTrades[0]["price"]]
    return trades.get(max(trades.keys()), "Error!!! Last transaction not found")

# - SINGLE PAIR SIGNAL
def single_signalSearch(pair):
    klines = client.get_klines(symbol=pair, interval='5m', limit='500')
    close = [float(entry[4]) for entry in klines]
    close_array = np.asarray(close)
    close_finished = close_array[:-1]
    rsi = computeRSI(close_finished, 14)
    return rsi

# - ALL PAIRS SIGNAL
def all_signalSearch(pairs):
    pairSignals = {}
    pairSignal = {}
    for pair in pairs:
        klines = client.get_klines(symbol=pair, interval='5m', limit='500')
        close = [float(entry[4]) for entry in klines]
        close_array = np.asarray(close)
        close_finished = close_array[:-1]
        rsi = computeRSI(close_finished, 14)
        pairSignals[rsi] = pair
    pairSignal["signals"] = pairSignals
    pairSignal["best_signal"] = [pairSignals[min(pairSignals.keys())], min(pairSignals.keys())]
    return pairSignal

# - WIN RATE CALCULATION
def winRateCalculation(lastPrice):
    process = float(lastPrice) * 2 / 100
    lastprocess = float(lastPrice) + float(process)
    return lastprocess
# - LOSS RATE CALCULATION
def loseRateCalculation(lastPrice):
    process = float(lastPrice) * 2 / 100
    lastprocess = float(lastPrice) - float(process)
    return lastprocess
# - PROFIT RATE CALCULATION
def profitRateCalculation(buyPrice, sellPrice):
    profitRate = (sellPrice - buyPrice) * 100 / buyPrice
    return profitRate

# - SEND SQL CODE
def sendSQLCode(sqlCode):
    sql = (sqlCode)
    im.execute(sql)
    database.commit()
# - SQL DATA QUERY
def sqlQuery(table , limit):
    im.execute("SELECT * FROM " + str(table) + " ORDER BY ID DESC LIMIT " + str(limit) + "")
    query = im.fetchall()
    return query

#-------------------------------------------#

# SETTINGS
#-------------------------------------------#
api_key = '' # BINANCE API KEY
api_secret = '' # BINANCE SECRET KEY

pairs = ['AVAXUSDT', 'ETHUSDT', 'DOTUSDT', 'SOLUSDT', 'CHZUSDT', 'ADAUSDT', 'THETAUSDT', 'SANDUSDT', 'MATICUSDT']

# Connect Api
client = Client(api_key, api_secret)
#-------------------------------------------#

# DATABASE
#-------------------------------------------#
database = sqlite3.connect('bot_log.sqlite')
im = database.cursor()

im.execute("CREATE TABLE IF NOT EXISTS bot_logs (Process, Balance, Pair, BuyPrice, SellPrice, BuyCountorSellCount, RSI, Time)")
im.execute("CREATE TABLE IF NOT EXISTS bot_profitloss (ID INTEGER PRIMARY KEY AUTOINCREMENT, Balance, Pair, BuyPrice, SellPrice, BuyCountorSellCount, BRSI, SRSI, ProfitLoss, ProfitLossRate, OpeningTime, ClosingTime)")
im.execute("CREATE TABLE IF NOT EXISTS bot_status (ID, Status, Time)")
im.execute("CREATE TABLE IF NOT EXISTS bot_signals (ID INTEGER PRIMARY KEY AUTOINCREMENT, Signals, Time)")

im.execute("SELECT * FROM bot_status WHERE ID = '1'")
statusControle = im.fetchall()
if statusControle == [] :
    sendSQLCode("INSERT INTO bot_status VALUES ('1' , 'Open' , '" + str(bottime()) + "')")
else:
    sendSQLCode("UPDATE bot_status SET Status = 'Open', Time = '" + str(bottime()) + "' WHERE ID = '1'")

#-------------------------------------------#

# BOT CODE
print("------------- BINANCE BOT START -------------")

print("Database connection successful...")

while True:
    try:
        im.execute("SELECT * FROM bot_status WHERE ID = '1'")
        botStatus = im.fetchall()
        botStatus = str(botStatus[0][1])
        if botStatus == 'Open':
            sendSQLCode("UPDATE bot_status SET Time = '" + str(bottime()) + "' WHERE ID = '1'")

            waitTime = 30
            lastTransactionData = lastTransactionRemainder(pairs)
            lastPair = lastTransactionData[0]
            lastCoin = lastTransactionData[1]
            lastPrice = lastTransactionData[2]

            profitlossData = sqlQuery("bot_profitloss", 1)

            if lastCoin == 'USDT':
                balanceData = balanceCheck(lastCoin)
                lastBalance = balanceData["free"]
                print("Last operation ( " + lastCoin + " )")
                allSignals = all_signalSearch(pairs)
                print("--- Signal --- | Best RSI Signal = " + str(allSignals["best_signal"]) + " - Other RSI Signals" + str(allSignals["signals"]))

                signalResult = str(allSignals["signals"])
                signalResult = signalResult.replace("{", "")
                signalResult = signalResult.replace("}", "")
                signalSQLData = signalResult.replace("'", "")
                sendSQLCode("INSERT INTO bot_signals (Signals, Time) VALUES ('" + str(signalSQLData) + "' , '" + str(bottime()) + "')")

                bestSignalPair = allSignals["best_signal"][0]
                bestSignalRSI = allSignals["best_signal"][1]
                # BUY
                if bestSignalRSI <= 26:
                    buyCoinPrice = coinPriceCheck(bestSignalPair)
                    calculateBuy = float(lastBalance) / float(buyCoinPrice)
                    buyCount = fn_round(bestSignalPair, calculateBuy)

                    order = client.order_market_buy(
                        symbol=bestSignalPair,
                        quantity=buyCount
                    )

                    sendSQLCode("INSERT INTO bot_logs VALUES ('BUY', '" + str(lastBalance) + "', '" + str(bestSignalPair) + "', '" + str(buyCoinPrice) + "', '', '" + str(buyCount) + "', '" + str(bestSignalRSI) + "', '" + str(bottime()) + "')")
                    sendSQLCode("INSERT INTO bot_profitloss VALUES (NULL, '" + str(lastBalance) + "', '" + str(bestSignalPair) + "', '" + str(buyCoinPrice) + "', '', '" + str(buyCount) + "', '" + str(bestSignalRSI) + "', '', '', '', '" + str(bottime()) + "', '')")

                    waitTime = 300

                    print("---------- PURCHASED ---------- Total : " + str(buyCount) + "BUY!!! - Time:" + str(bottime()))

                else:
                    print("--- Waiting to buy ---")

            else:
                balanceData = balanceCheck(lastCoin)
                lastBalance = balanceData["free"]
                coinPrice = coinPriceCheck(lastPair)
                print("Last operation ( " + str(lastCoin) + " )")
                signal = single_signalSearch(lastPair)
                exampleProfitRate = profitRateCalculation(float(profitlossData[0][3]), float(coinPrice))
                print("--- Signal --- | Pair : " + str(lastPair) + " - Balance : " + str(format(float(lastBalance), '.4f')) + " - RSI Signals : " + str(signal) + " - Price at purchase : " + str(format(float(lastPrice), '.4f')) + " - Coin Price : " + str(format(float(coinPrice), '.4f')) + " - Profit Rate : %" + str(format(float(exampleProfitRate), '.2f')) + " - Time : " + str(bottime()))

                # SELL
                if float(coinPrice) > winRateCalculation(lastPrice) or signal > 68:
                    sellCount = fn_round(lastPair, float(lastBalance))

                    order = client.order_market_sell(
                        symbol=lastPair,
                        quantity=sellCount
                    )

                    sendSQLCode("INSERT INTO bot_logs VALUES ('SELL', '" + str(lastBalance) + "', '" + str(lastPair) + "', '', '" + str(coinPrice) + "', '" + str(sellCount) + "', '" + str(signal) + "', '" + str(bottime()) + "')")

                    profitRate = profitRateCalculation(float(profitlossData[0][3]), float(coinPrice))

                    sendSQLCode("UPDATE bot_profitloss SET SellPrice = '" + str(coinPrice) + "', SRSI = '" + str(signal) + "', ProfitLoss = 'Profit', ProfitLossRate = '" + str(format(float(profitRate), '.2f')) + "', ClosingTime = '" + str(bottime()) + "' WHERE ID = '" + str(profitlossData[0][0]) + "'")

                    print("---------- SOLD ---------- Total : " + str(sellCount) + " SELL!!! - Profit Rate : %" + str(format(float(profitRate), '.2f')) + "  - Time : " + str(bottime()))

                elif float(coinPrice) < loseRateCalculation(lastPrice):
                    sellCount = fn_round(lastPair, float(lastBalance))

                    order = client.order_market_sell(
                        symbol=lastPair,
                        quantity=sellCount
                    )

                    sendSQLCode("INSERT INTO bot_logs VALUES ('HF-SELL', '" + str(lastBalance) + "', '" + str(lastPair) + "', '', '" + str(coinPrice) + "', '" + str(sellCount) + "', '" + str(signal) + "', '" + str(bottime()) + "')")

                    profitRate = profitRateCalculation(float(profitlossData[0][3]), float(coinPrice))
                    sendSQLCode("UPDATE bot_profitloss SET SellPrice = '" + str(coinPrice) + "', SRSI = '" + str(signal) + "', ProfitLoss = 'Loss', ProfitLossRate = '" + str(format(profitRate, '.2f')) + "', ClosingTime = '" + str(bottime()) + "' WHERE ID = '" + str(profitlossData[0][0]) + "'")

                    print("---------- High fall ---------- The bot has been stopped. (1 Hours) - Loss Rate : " + str(format(profitRate, '.2f')) + " - Time : " + str(bottime()))
                    waitTime = 3600
                    sendSQLCode("UPDATE bot_status SET Status = 'Wait', Time = '" + str(bottime()) + "' WHERE ID = '1'")
                else:
                    print("--- Waiting to sell ---")
        else:
            print("Bot stopped !!!")

    except Exception as e:
        print(str(e))

    time.sleep(waitTime)

    im.execute("SELECT * FROM bot_status WHERE ID = '1'")
    botStatusData = im.fetchall()
    if botStatusData[0][1] == "Wait":
        sendSQLCode("UPDATE bot_status SET Status = 'Open', Time = '" + str(bottime()) + "' WHERE ID = '1'")
