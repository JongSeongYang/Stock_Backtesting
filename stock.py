import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl
from datetime import datetime
from datetime import timedelta
import time

def stock_list():
    df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    list = []
    for i in range(len(df)):
        d = {}
        name = df.iloc[i, 0]
        code = str(df.iloc[i, 1])
        d["name"] = name
        add_length_code = 6 - len(code)
        for j in range(add_length_code):
            code = '0' + code
        d["code"] = code
        list.append(d)

    return list

def scrap_data(code, endtime, starttime, timeframe):
    if endtime == 'today':
        endtime = datetime.today().strftime('%Y%m%d')
    if starttime == 'default':
        date = datetime.strptime(endtime, '%Y%m%d') - timedelta(days=365*3)
        starttime = date.strftime('%Y%m%d')
    url = 'https://api.finance.naver.com/siseJson.naver?symbol=' + str(code) + '&requestType=1&startTime=' + str(
        starttime) + '&endTime=' + str(endtime) + '&timeframe=' + str(timeframe)
    res = urlopen(url, context=ssl.create_default_context())
    soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')
    data = str(soup).split('],')
    return data

def stock_labels(code='005930',starttime='default',endtime='today',timeframe='day'):
    data = scrap_data(code, endtime, starttime, timeframe)
    labels = []
    for i in range(1,len(data)):
        label = data[i].split(', ')[0].split('["')[1].split('"')[0]
        format = '%Y/%m/%d'
        new_label = label[0:4]+"/"+label[4:6]+"/"+label[-2:]
        date_time = datetime.strptime(new_label, format).date()
        labels.append(int(time.mktime(date_time.timetuple())) * 1000)
    return labels

def stock_high_prices(code='005930',starttime='default',endtime='today',timeframe='day'):
    data = scrap_data(code, endtime, starttime, timeframe)
    high_prices = []
    for i in range(1,len(data)):
        high_prices.append(int(data[i].split(', ')[2]))

    return high_prices

def stock_low_prices(code='005930',starttime='default',endtime='today',timeframe='day'):
    data = scrap_data(code, endtime, starttime, timeframe)
    low_prices = []
    for i in range(1,len(data)):
        low_prices.append(int(data[i].split(', ')[4]))
    return low_prices

def stock_open_prices(code='005930',starttime='default',endtime='today',timeframe='day'):
    data = scrap_data(code, endtime, starttime, timeframe)
    open_prices = []
    for i in range(1,len(data)):
        open_prices.append(int(data[i].split(', ')[1]))
    return open_prices