import threading
from tradingview_ta import TA_Handler, Interval, Exchange
import json
from talib.abstract import *
from pyiqoptionapi import *
from datetime import datetime
import time
import ta
import numpy as np
import pandas as pd
import psycopg2
from iqoptionapi.stable_api import IQ_Option
from .. import credentials

def mini_analysis():
    # EURUSD = TA_Handler(symbol="EURUSD", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    GBPJPY = TA_Handler(symbol="GBPJPY", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    # USDCHF = TA_Handler(symbol="USDCHF", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    # GBPCHF = TA_Handler(symbol="GBPCHF", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    GBPUSD = TA_Handler(symbol="GBPUSD", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    EURGBP = TA_Handler(symbol="EURGBP", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    # AUDCAD = TA_Handler(symbol="AUDCAD", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)
    # AUDUSD = TA_Handler(symbol="AUDUSD", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_1_MINUTE)

    listToAnalyse = []
    # listMonnaie = ["EURUSD", "GBPJPY", "USDCHF", "GBPUSD", "EURGBP", "AUDCAD", "AUDUSD"]
    listMonnaie = ["EURGBP","GBPJPY","GBPUSD"]
    listegagnante = []
    # dictAction = {"EURUSD" : "", "GBPJPY" : "", "USDCHF" : "", "GBPUSD" : "", "EURGBP" : "", "AUDCAD": "", "AUDUSD": ""}
    dictAction = {"EURGBP" : "", "GBPJPY" : "", "GBPUSD" : ""}
    
    for money in listMonnaie:
        globals()["g_result"  + money]  = eval( money).get_analysis().summary["RECOMMENDATION"]
        globals()["o_result"  + money]  = eval( money).get_analysis().oscillators["RECOMMENDATION"]
        globals()["ma_result"  + money] = eval( money).get_analysis().moving_averages["RECOMMENDATION"]
        # rsi = eval(money).get_analysis().indicators["RSI"]
        
        # print(money, globals()["g_result"  + money], globals()["ma_result"  + money], globals()["o_result"  + money])
        if ("STRONG_SELL" in  globals()["g_result"  + money] and "SELL" in globals()["o_result"  + money]  and "STRONG_SELL" in globals()["ma_result"  + money]):
            listegagnante.append(money)
            newDictVal =  {money:"put"}
            dictAction.update(newDictVal)
        elif ("STRONG_BUY" in  globals()["g_result"  + money] and "BUY" in globals()["o_result"  + money]  and "STRONG_BUY" in globals()["ma_result"  + money]):
            listegagnante.append(money)
            newDictVal =  {money:"call"}
            dictAction.update(newDictVal)

    for objectToKeep in listegagnante:

        listToAnalyse.append(
            {   
                "action" : dictAction[objectToKeep],
                "monnaie" : objectToKeep,
                "type" : eval(objectToKeep).get_analysis().summary["RECOMMENDATION"],
                "g_sell" : eval(objectToKeep).get_analysis().summary["SELL"],
                "g_buy" : eval(objectToKeep).get_analysis().summary["BUY"],
                "g_neutral" : eval(objectToKeep).get_analysis().summary["NEUTRAL"],

                "o_sell" : eval(objectToKeep).get_analysis().oscillators["SELL"],
                "o_buy" : eval(objectToKeep).get_analysis().oscillators["BUY"],
                "o_neutral" : eval(objectToKeep).get_analysis().oscillators["NEUTRAL"],

                "ma_sell" : eval(objectToKeep).get_analysis().moving_averages["SELL"],
                "ma_buy" : eval(objectToKeep).get_analysis().moving_averages["BUY"],
                "ma_neutral" : eval(objectToKeep).get_analysis().moving_averages["NEUTRAL"]
                
            }
        )
    output = ""
    currency = ""
    maximum = 2
    sommeMaEtGen = 0
    
    for i in range(len(listToAnalyse)):
        currentTypeTrade = listToAnalyse[i]["type"].lower()
        if "strong_" in currentTypeTrade:
            currentTypeTrade = currentTypeTrade.replace("strong_", "")
        
        currentNameTrade = "o_" + str(currentTypeTrade)
        currentOscilatteur = listToAnalyse[i][currentNameTrade]
        currentNeutral = listToAnalyse[i]["o_neutral"]
        currentSomme = listToAnalyse[i]["ma_" + str(currentTypeTrade)] + listToAnalyse[i]["g_" + str(currentTypeTrade)] 

        if currentOscilatteur > currentNeutral + 2:
            maximum = currentOscilatteur
            sommeMaEtGen = currentSomme
            output = listToAnalyse[i]["action"]
            currency = listToAnalyse[i]["monnaie"]
        elif currentOscilatteur > maximum and currentOscilatteur == maximum:
            if ( currentSomme > sommeMaEtGen):
                output = listToAnalyse[i]["action"]
                currency = listToAnalyse[i]["monnaie"]
    
    out = {"output": output, "monnaie": currency, "listToAnalyse": listToAnalyse}
    return out

def get_rsi(data):
    close = []
    # Iq = IQOption(credentials.login, credentials.mdp3)
    time.sleep(1)
    end_from_time=time.time()
    for el in data:
        close.append(el['close'])
    df=pd.DataFrame(close, columns=['close']) 
    rsi = ta.momentum.rsi(df['close'], 14)
    return rsi[13]



def loopPrediction():
    I_want_money = IQ_Option(credentials.login, credentials.mdp3)
    time.sleep(1)
    end_from_time=time.time()
    I_want_money.connect()#connect to iqoption
    
    # threading.Timer(60, loopPrediction).start()
    outFunc = mini_analysis()
    ACTIVES=outFunc["monnaie"]
    duration=1#minute 1 or 5

    amount = 10
    # rsi = 0
    # if (outFunc["monnaie"] != ""):
    #     getRsi = TA_Handler(symbol=outFunc["monnaie"], screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_5_MINUTES)
    #     rsi = getRsi.get_analysis().indicators["RSI"]
    # exchangeDollarsEuros5 = TA_Handler(symbol="GBPJPY", screener="forex", exchange=Exchange.FOREX, interval=Interval.INTERVAL_5_MINUTES)
    # g_result_fin =  exchangeDollarsEuros5.get_analysis().summary["RECOMMENDATION"]
    # o_result_fin =  exchangeDollarsEuros5.get_analysis().oscillators["RECOMMENDATION"]
    # ma_result_fin =  exchangeDollarsEuros5.get_analysis().moving_averages["RECOMMENDATION"]
    action = outFunc["output"]
    # if ("SELL" in  g_result_fin and "SELL" in ma_result_fin  and "SELL" in o_result_fin):
    #     o_sell = exchangeDollarsEuros5.get_analysis().oscillators["SELL"]
    #     if o_sell >= 3:
    #         action="put"#put
    # elif ("BUY" in  g_result_fin and "BUY" in ma_result_fin  and "BUY" in o_result_fin):
    #     o_buy = exchangeDollarsEuros5.get_analysis().oscillators["BUY"]
    #     if o_buy >= 3:
    #         action="call"
    # I_want_money = IQ_Option(credentials.login, credentials.mdp3)
    # time.sleep(1)
    # end_from_time=time.time()
    # I_want_money.connect()#connect to iqoption
    # print("monnaie : ", ACTIVES)
    # if (ACTIVES != ""):
    #     data=I_want_money.get_candles(ACTIVES, 60, 14, end_from_time)
    #     rsi = get_rsi(data)
    #     print("get rsi : ", rsi, " / action : ", outFunc["output"])
    #     if ("put" == outFunc["output"] and rsi <= 65):
    #         action = ""
    #     elif ("call" == outFunc["output"] and rsi >= 40):
    #         action = ""
 
    if action != "" :
        I_want_money.subscribe_strike_list(ACTIVES,duration)
        # startTrade = time.time()
        _,id=I_want_money.buy_digital_spot(ACTIVES,amount,action,duration) 
        time.sleep(3)
        # start_time = time.time()
        # print( " here go start trading a ", action, " on / ", ACTIVES, ' / at ', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # print( "error  : ", ACTIVES, " / ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), outFunc["listToAnalyse"])
        # print("currentTrade : ", I_want_money.get_digital_position(id))
        getPosition = I_want_money.get_digital_position(id)
        currentTrade=getPosition['msg']['position']['status']
        
        
        while currentTrade == 'open':
            # PL=I_want_money.get_digital_spot_profit_after_sale(id)
            # percent = PL/amount * 100
            # if PL!=None and percent > 10 :
            #     I_want_money.close_digital_option(id)
            #     print("percentage gain : ", percent)
            # elif PL!=None and percent < -49: #and time.time() - startTrade > 200:
            #     I_want_money.close_digital_option(id)
            currentTrade=I_want_money.get_digital_position(id)['msg']['position']['status']
        print("End of trade", ACTIVES, " / ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), outFunc["listToAnalyse"], " / time exec code : ", time.time()- end_from_time)
    else :
        print( "didn't enter in trade  : ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "time exec code : ", time.time()- end_from_time)
        print("analyse :", outFunc["listToAnalyse"])
        # time.sleep(50)
startBot = True
while startBot == True:
    loopPrediction()



