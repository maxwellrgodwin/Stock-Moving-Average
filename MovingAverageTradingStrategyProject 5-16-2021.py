#!/usr/bin/env python
# coding: utf-8

# In[1]:


#I am running this in Jupyter Notebook and used !pip install the 3 packages below
#!pip install pandas_datareader
#!pip install yfinance
#!pip install yahoofinancials
import pandas as pd #Data Structures py package
import numpy as np #Data Structures and support for arrays
import datetime #Date and Time as of time running program
import matplotlib.pyplot as plt #Visualization This line is necessary for the plot to appear in Jupyter notebook
import scipy.stats as sc   
from sklearn.datasets import load_iris
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from pandas_datareader import data as pdr


# In[2]:


import yfinance as yf
from yahoofinancials import YahooFinancials
from datetime import date


# In[3]:


class MovingAverage:  
    def __init__(self):
       pass 

    def getd (self,symbol,start_date):
        today = date.today()
        tickerSymbol = symbol
        tickerData = yf.Ticker(tickerSymbol)
        start_date= start_date
        d = pdr.get_data_yahoo(symbol, start=start_date, end=today)
        return d
    
    def strategy_and_result(self,symbol,start_date):
        today = date.today()
        df=self.getd(symbol,start_date)
        stock=df['Close']
        win=50
        win2=200
        
        signals=pd.DataFrame(index=stock.index)
        signals['signal']=0.0
        signals['short_mavg']= stock.rolling(window=win,min_periods=1,center=False).mean()
        signals['long_mavg']= stock.rolling(window=win2,min_periods=1,center=False).mean()
        signals['signal'][win:]=np.where(signals['short_mavg'][win:]
                                                 > signals['long_mavg'][win:], 1.0, 0.0 )
        signals['positions']=signals['signal'].diff()

        initial_cap=float(300_000)
        positions=pd.DataFrame(index=signals.index).fillna(0.0)
        #but 1000 shares
        positions['Position']=1_000*(signals['positions'])
        #initialize the portfolio with shares owned
        portfolio=pd.DataFrame(index=signals.index).fillna(0.0)
        portfolio["shares"]=positions['Position'].cumsum(axis = 0)
        #add 'holding'
        portfolio["holdings"]=portfolio["shares"]*stock
        #store difference in shares owned 
        portfolio["pos_diff"]=portfolio["shares"].diff()
        #add 'cash'
        portfolio['cash']= initial_cap - (portfolio["pos_diff"]*stock).cumsum(axis = 0)
        #add 'total'
        portfolio['total']=portfolio['cash'] + portfolio['holdings']
        #add 'return'
        portfolio['return']=portfolio['total'].pct_change()
        
        fig = plt.figure(figsize=(20, 15))
        ax1 = fig.add_subplot(111,ylabel='Price in $')
        stock.plot(ax=ax1,color='black',lw=2.)
        signals[['short_mavg','long_mavg']].plot(ax=ax1,lw=2.0)
        #plot the buy signals 
        ax1.plot(signals.loc[signals.positions==1.0].index,
                signals.short_mavg[signals.positions == 1.0],
                '^',markersize=10,color='g')
        #plot the sell signals
        ax1.plot(signals.loc[signals.positions==-1.0].index,
                signals.short_mavg[signals.positions == -1.0],
                'v',markersize=10,color='r')
        plt.show()
        
        print("Portfolio total value as of {0}: ${1}".format(today,(round((portfolio['total'][-1]),2))))
        abs_return=((portfolio['total'][-1]/initial_cap)-float(1))*100
        print("Absolute return as of {0}: {1}%".format(today,round(abs_return,2)))
        
        print("")
        print("The 50 Day moving average as of {0} is {1}" .format(today,round(signals['short_mavg'].iloc[-1],4)))
        print("The 200 Day moving average as of {0} is {1}" .format(today,round(signals['long_mavg'].iloc[-1],4)))
        
        df_b= pd.DataFrame(signals.loc[signals.positions==1.0].index, columns=list(''))
        df_b["buy-price"]= signals.short_mavg[signals.positions == 1.0]
       
        df_s=pd.DataFrame(signals.loc[signals.positions==-1.0].index,columns=list(''))
        df_s["sell-price"]=signals.short_mavg[signals.positions == -1.0]
        print("")
        print("Buy indicators:")
        print(df_b)
        print("")
        print("Sell indicators:")
        print(df_s)
        


# In[ ]:


if __name__ == "__main__":
    i=input("Do you want to test a ticker? (yes to continue no to stop)").upper()
    while i != "NO":
        ticker=(input("Please input your stock ticker:")).upper()
        s_date=input("Please input the start date: Format (YYYY-MM-DD)")
        MA=MovingAverage()
        strategy=MA.strategy_and_result
        strategy(ticker,s_date)
        i = input("Do you want to test a ticker? (yes to continue no to stop)").upper()


# In[ ]:




