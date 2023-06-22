import requests as rq
import pandas as pd
import numpy as np
from datetime import datetime
import time

#Graping Nifty50 Company List
def NiftyList():
    X = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
    X = pd.read_csv(X)
    X = X.iloc[:,2]
    X = X.to_numpy()
    return X

#Graping Urls from yahoo finance for all 50 Nifty50 companis
def URLs():   
    today = datetime.now().date()
    now = datetime.now()
    today = time.mktime(today.timetuple())
    now = time.mktime(now.timetuple())
    t = int(now - today)
    start_time = int(time.mktime(datetime(2020,10,1).timetuple()))
    start_time = str(start_time + t)
    now = str(int(now))
    name = NiftyList()
    n = name.shape[0]
    url = []
    for i in range(0,n):
        X = 'https://query1.finance.yahoo.com/v7/finance/download/' + name[i] + '.NS?period1=' + start_time + '&period2=' + now +'&interval=1d&events=history&includeAdjustedClose=true'
        url = url + [X]
    url = np.array(url)
    return name, url

#Graping Clossing Prise
def ClosingTable(url):
    df = pd.read_csv(url)
    df = df.iloc[:,4] #Closing Prise Table
    return df

#Date table
def DateColumn(url):
    df = pd.read_csv(url)
    df = df.iloc[:,0]
    return df

#Equaty table for all stocks
def NetEquaty():
    name, url = URLs()
    url0 = url[0]
    date = DateColumn(url0)
    df = ClosingTable(url0)
    for i in range(1,50):
        df = pd.concat([df,ClosingTable(url[i])],axis=1)
    name = np.insert(name, 0, 'DATE')
    df.insert(0, 'DATE', date)
    df.columns = name
    return df

def NiftyURL():
    today = datetime.now().date()
    now = datetime.now()
    today = time.mktime(today.timetuple())
    now = time.mktime(now.timetuple())
    t = int(now - today)
    start_time = int(time.mktime(datetime(2020,10,1).timetuple()))
    start_time = str(start_time + t)
    now = str(int(now))
    url = 'https://query1.finance.yahoo.com/v7/finance/download/%5ENSEI?period1='+ start_time + '&period2=' + now + '&interval=1d&events=history&includeAdjustedClose=true'
    df = pd.read_csv(url)
    df = df['Close']
    df.columns = 'Close'
    return df

#Update Data
def UpdateData():
    df1 = NetEquaty()
    df2 = NiftyURL()
    df1.to_csv('Nifty.csv',  index=False)
    df2.to_csv('NiftyIndex.csv',  index=False)
    return df1, df2
