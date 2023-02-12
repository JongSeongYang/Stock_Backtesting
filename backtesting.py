import backtrader as bt
from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib as mlt
mlt.use('Agg')
import mpld3

class SmaCross(bt.Strategy):  # bt.Strategy를 상속한 class로 생성해야 함.
    params = (
        ("period", 17),
        ("devfactor", 2),
        ("debug", False)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor, plot=True)

    def next(self):
        global size
        if not self.position:  # not in the market
            if self.data.low[0] < self.boll.lines.bot[0]:
                bottom = self.boll.lines.bot[0]
                size = int(self.broker.getcash() / bottom)  # 최대 구매 가능 개수
                self.buy(price=bottom, size=size)  # 매수 size = 구매 개수 설정
        else:
            if self.data.high[0] > self.boll.lines.mid[0]:
                self.sell(price=self.boll.lines.mid[0], size=size)  # 매도

def stock_data(code='005930',starttime='default',endtime='today',timeframe='day'):
    if endtime == 'today':
        endtime = datetime.today().strftime('%Y%m%d')
    if starttime == 'default':
        date = datetime.strptime(endtime,'%Y%m%d')-timedelta(days=365)
        starttime = date.strftime('%Y%m%d')
    url = 'https://api.finance.naver.com/siseJson.naver?symbol='+str(code)+'&requestType=1&startTime='+str(starttime)+'&endTime='+str(endtime)+'&timeframe='+str(timeframe)
    res = urlopen(url, context=ssl.create_default_context())
    soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='utf-8')
    data = str(soup).split('],')
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    for i in range(1,len(data)):
        date = data[i].split(', ')[0].split('["')[1].split('"')[0]
        open = data[i].split(', ')[1]
        high = data[i].split(', ')[2]
        close = data[i].split(', ')[3]
        low = data[i].split(', ')[4]
        volume = data[i].split(', ')[5]
        list = [date, open, high, low, close, volume]
        df = df.append(pd.Series(list, index=df.columns), ignore_index=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df = df.astype({'Open':'int','High':'int','Low':'int','Close':'int','Volume':'int'})
    df = df.sort_index(ascending=True)
    return df

def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
              width=16, height=9, dpi=300, tight=True, use=None, file_path='', **kwargs):
    from backtrader import plot
    if cerebro.p.oldsync:
        plotter = plot.Plot_OldSync(**kwargs)
    else:
        plotter = plot.Plot(**kwargs)

    figs = []
    for stratlist in cerebro.runstrats:
        for si, strat in enumerate(stratlist):
            rfig = plotter.plot(strat, figid=si * 100,
                                numfigs=numfigs, iplot=iplot,
                                start=start, end=end, use=use, style="candle", barup="red", bardown="blue")
            figs.append(rfig)

    for fig in figs:
        for f in fig:
            f.savefig(file_path, bbox_inches='tight')
    return figs

def execute(stock_code, init_cash):
    cerebro = bt.Cerebro()
    # cerebro.addstrategy(MyStrategy)
    cerebro.addstrategy(SmaCross)
    df = stock_data(stock_code)  # 국내
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.broker.setcash(init_cash)
    cerebro.run()
    final_cash = cerebro.broker.getvalue()
    # cerebro.plot(style='candle', barup='red', bardown='blue')
    # saveplots(cerebro, file_path='templates\savefig.png')
    # result = mpld3.fig_to_html(cerebro.plot(style='candle', barup='red', bardown='blue'))
    # print(result)
    return init_cash, int(final_cash)

if __name__ == "__main__":
    execute(stock_code="005930", init_cash=100000)