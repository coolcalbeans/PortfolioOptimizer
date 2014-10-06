# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 14:32:53 2014

@author: Viju
@summary:   Portfoilio Optimizer project submitted as a part of Computational Investing Coursera Course 
            Offered by Prof. Tucker Balch from Georgia Tech. 
@References: Using snippets of code from tutorial1.py written by Sourabh Bajaj

"""
from __future__ import division
from math import sqrt
# QSTK Imports - Qunat Software Tool Kit is a set of Equity analysis toolkit created by Georgia Tech
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import itertools
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def simulate(dt_start, dt_end, ls_symbols, ls_initPort):
    # Create a Dataframe with normalized prices
    df_prices = getNormalizedTickerReturns(dt_start, dt_end, ls_symbols)
    df_prices['Portfolio'] = 0.0
    df_prices['Port_Return'] = 0.0

    # d_prtfoliofWght is a dictionary with the Tickers/Symbols above.
    d_prtfoliofWght = dict(zip(ls_symbols,ls_initPort))
    for symb in ls_symbols:
        df_prices[symb] = d_prtfoliofWght[symb] * df_prices[symb]
        df_prices['Portfolio'] += df_prices[symb]

    df_prices['Port_Return'] = (df_prices['Portfolio']/df_prices['Portfolio'].shift(1)) - 1
    df_prices['Port_Return'].fillna(method = 'ffill', inplace = True)
    #df_prices['Port_Return'].fillna(method = 'bfill', inplace = True)
    #df_prices['Port_Return'].fillna(0, inplace = True)
    i_cumPortReturn = df_prices['Portfolio'].iloc[-1]


    i_portfolioRet = df_prices['Port_Return'].mean()
    i_portfolioStd = df_prices['Port_Return'].std()
    #i_portLength = len(df_prices.index)
    #i_sharpeRatio = sqrt(i_portLength) *(i_portfolioRet/i_portfolioStd)
    #Using 252 becuase of daily returns
    i_sharpeRatio = sqrt(252) *(i_portfolioRet/i_portfolioStd)    

    return i_portfolioStd, i_portfolioRet, i_sharpeRatio, i_cumPortReturn, df_prices


def getNormalizedTickerReturns(dt_start, dt_end, ls_symbols):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    c_dataobj = da.DataAccess('Yahoo')
    # Keys to be read from the Yahoo data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Handling missing values withing the time period
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values    
    # Normalizing the prices to start at 1 and hence see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Converting the normalized prize into a Pandas dataframe
    df_prices = pd.DataFrame(na_normalized_price, columns=ls_symbols)
    return df_prices      
    
def main():
    ''' Main Function'''

    startTime = dt.datetime.now()
    print(startTime.strftime('%H:%M:%S %m/%d/%Y') + " :: Starting Optimizer")
    
    # Start and End date of the charts, closing price data retrieved from Yahoo Finance
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)

    # List of Symbols/Ticker. Tried a maximum of 8 Symbols/Tickers. Takes ~3 mins
    ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']

    p1 = xrange(0,11)
    p2 = xrange(0,11)
    p3 = xrange(0,11)
    p4 = xrange(0,11)

    i_maxSharpe = 0.0
    for i, j, k , l  in itertools.product(p1, p2, p3, p4):
        i_allocationSum = i + j + k + l
        if i_allocationSum == 10:
            na_port = np.array([i,j,k,l])
            na_port = na_port/10
            ls_simPort = na_port.tolist()
            volatility, avg_daily_ret, sharpe, cum_ret, df_portFolio = simulate(dt_start, dt_end, ls_symbols, ls_simPort)
            
            if sharpe > i_maxSharpe:
                i_maxSharpe = sharpe
                ls_maxPort = ls_simPort

    # Calculating Optimal Portfolio Statistics
    volatility, avg_daily_ret, sharpe, cum_ret, df_portFolio = simulate(dt_start, dt_end, ls_symbols, ls_maxPort)
    
    print dt_start.strftime('\nStart Date: %B %d, %Y')
    print dt_end.strftime('End Date: %B %d, %Y')
    print("Portfolio Tickers: " + str(ls_symbols))
    print("Optimized Allocations: " +str (ls_maxPort))   
    print("Sharpe Ratio: %0.10f" % sharpe)    
    print("Volatility (StDev of daily returns): %0.10f" % volatility)
    print("Avg. Daily Return: %0.10f" % avg_daily_ret)
    print("Cumulative Return: %0.10f" % cum_ret)

    s_SPY = 'SPY'
    ls_symbols.append(s_SPY)
    
    df_symbNormalized = getNormalizedTickerReturns(dt_start, dt_end, ls_symbols)    
    concatPortfolio = pd.concat([df_symbNormalized, df_portFolio['Portfolio']], axis = 1)
    #concatPortfolio.drop('Port_Return',axis=1,inplace=True)
    concatPortfolio.plot().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('SPYvsPort.pdf',bbox_inches='tight')

    endTime = dt.datetime.now()
    runTime = endTime - startTime 
    print(endTime.strftime('\n%H:%M:%S %m/%d/%Y') + " :: Ending Optimizer")
    print("Optimzer Total Run Time " + str(runTime)[:7])

if __name__ == '__main__':
    main()
