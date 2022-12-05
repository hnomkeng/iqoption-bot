from email.message import EmailMessage
from iqoptionapi.stable_api import IQ_Option
from colorama import init, Fore, Back, Style
from datetime import datetime
from talib import *
import sys
import threading
import the
import numpy
import json, requests
import time
import talib

#from talib import MA_Type, EMA, BBANDS
the.system('cls')

print('\n\n= = = = = = = = = = = = = = = =')
email = str(input('\nTell me your Login: ') )
password = str(input('Tell me your Password: ') )
print('\n= = = = = = = = = = = = = = = = <TAG1')

Iq = IQ_Option(email, password)
Iq.connect( )


def profile( ):  # Displaying Profile data
    profile = json.loads(json.dumps(Iq.get_profile_ansyc( ) ) )
    return profile


#print ( Fore.BLUE + 'Bot RSI operating only in the binaries \ n Attention this bot uses RSI period 7 '
                  #'he enters the reversal' )
#print ( 'Input filters above 65:00 it enters with PUT or if it is below 35:00 it enters with CALL' )
#print (
    #'  Attention this bot doubles the entry after the loss you can disable in the variable double_entry' + Fore.RESET )
while True:
    print('\n - Account types:')
    MODE = int(input('  1 - Training'
                     '\n  2 - Real'
                     '\n  3 - Tournament'
                     '\n\nEnter the account number: ') )
    if MODE == 1:
        MODE = 'PRACTICE'
        break
    elif MODE == 2:
        MODE = 'REAL'
        break
    elif MODE == 3:
        MODE = 'TOURNAMENT'
        break
    else:
        print('  Invalid option - Enter an option from 1 to 3')
        continue

Iq.change_balance(MODE)
''' Config RSI'''
RSI_SOBRE_COMPRADO = 65.00
RSI_SOBRE_VENDA = 35.00
RSI_timeperiod = 7
double_entry = str(input('Dejesa doubles entry: ') )  # yes to double entry after loss or not to bend entrance

def payout(pair, type, timeframe=1):
    if type == 'turbo':
        the = Iq.get_all_profit( )
        return int(100 * the[pair] ['turbo'] )

    elif type == 'digital':

        Iq.subscribe_strike_list(pair, timeframe)
        while True:
            d = Iq.get_digital_current_profit(pair, timeframe)
            if d != False:
                d = int(d)
                break
            time.sleep(1)
        Iq.unsubscribe_strike_list(pair, timeframe)
        return d


def Ver_ativos_aberto_turbo_m1( ):
    print('\n\n Verifying open assets at BINARIAS')
    pair = Iq.get_all_open_time( )
    for parity in pair['turbo']:
        if pair['turbo'] [parity] ['open']:
            print('[ TURBO ]: ' + parity + ' | Payout: ' + str(payout(parity, 'turbo') ) )
            time.sleep(1)

''' print ( ''\ n Checking assets open in DIGITAL '' )
    pair = Iq.get_all_open_time ( )
    for par parity [ 'digital' ]:
        if par [ 'digital' ] [ parity ] [ 'open' ]:
            print ( '[ DIGITAL ]:' + parity + '| payout:' + str ( payout ( parity, 'digital' ) ) )'''

x = profile( )
print('\n\n= = = = = = = = = = = = = = = = <TAG1')
print('Hello:', x['name'] )
print("Your initial balance R $:", str(Iq.get_balance( ) ) )
print('= = = = = = = = = = = = = = = =')

Ver_ativos_aberto_turbo_m1( )
pair = input('\n Indicate a parity to operate: ').upper( )
value_input = float(input(' Indicate a value to enter: ''\n') )
value_input_b = float(value_input)


def put( ):
    global value_input
    dir = 'put'
    print('\nStarting operation!')
    print(datetime.now( ).strftime(' %d.% M.%Y% H:% M:% S'), end='\r')
    print('\n Direction =', dir, '', '\n Active: ', pair, ' Entry value: ', value_input)
    status, id = Iq.buy(value_input, pair, dir, 5)
    if isinstance(id, int):
        while True:
            _, profit = Iq.check_win_v3(id)
            if status:
                if profit > 0:
                    if profit == 0:
                        print('Your input impact will be the value of the Base entry')
                        value_input = value_input_b
                    print(Fore.LIGHTGREEN_EX + ' Win ✅ 😎  : ' + Fore.RESET + str(round(profit, 2) ) )
                    print(datetime.now( ).strftime('%D.% M.%Y% H:% M:% S'), end='\r')
                    value_input = value_input_b  # back value of the initial entry after win
                    print('= + = + = +' * 20)
                    print('Awaiting Next sign!!')
                    time.sleep(6)
                    break
                else:
                    print(Fore.RED + ' Loss ❌ 😖 !! : ' + Fore.RESET + str(round(profit, 2) ) )
                    if double_entry == 'Yes':
                        value_input = value_input * 2.3

                break


def call( ):
    global value_input
    dir = 'call'
    print('\nStarting operation!')
    print(datetime.now( ).strftime(' %d.% M.%Y% H:% M:% S'), end='\r')
    print('\n Direction =', dir, '', '\n Active: ', pair, ' Entry value: ', value_input)
    status, id = Iq.buy(value_input, pair, dir, 5)
    if isinstance(id, int):
        while True:
            _, profit = Iq.check_win_v3(id)
            if status:
                if profit > 0:
                    if profit == 0:
                        print('Your input impact will be the value of the Base entry')
                        value_input = value_input_b
                    print(Fore.LIGHTGREEN_EX + ' Win ✅ 😎  : ' + Fore.RESET + str(round(profit, 2) ) )
                    print(datetime.now( ).strftime('%D.% M.%Y% H:% M:% S'), end='\r')
                    value_input = value_input_b  # back value of the initial entry after win
                    print('= + = + = +' * 20)
                    print('Awaiting Next sign!!')

                    break
                else:
                    print(Fore.RED + ' Loss ❌ 😖 !! : ' + Fore.RESET + str(round(profit, 2) ) )
                    if double_entry == 'Yes':
                        value_input = value_input * 2.3

                break


def rsi1( ):
    ############# rsi ##############################
    bars = Iq.get_candles(pair, 60, 15, time.time( ) )
    close = [ ]
    for x in bars:
        close.append(x["close"] )

    closed_array = numpy.array(close)
    rsi = talib.RSI(closed_array, timeperiod=RSI_timeperiod)
    if rsi[-1] > RSI_SOBRE_COMPRADO:
        print('  ISPING ISLANDS OF 65.00 ..')
        print('\r  RSI - >% s' % rsi[-1] )
        put( )
        print('= = = = = = = = = = = = = = = =')
    elif rsi[-1] < RSI_SOBRE_VENDA:
        print('  RSI BELOWS OF 35.00 ..')
        print('\r  RSI - >% s' % rsi[-1] )
        call( )
        print('= = = = = = = = = = = = = = = =')

    else:
        sys.stdout.write('\r  RSI NEUTRO - >% s' % rsi[-1] )


while True:
    # time.sleep ( 0.5 )
    rsi1( )