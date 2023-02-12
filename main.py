# _*_ coding: utf-8 _*_
from flask import Flask, request, render_template, jsonify
import json
import stock
import backtesting
import twitter_scrap

app = Flask(__name__)

@app.route('/')
def root():
    stock_list = stock.stock_list()
    return render_template('stockList.html', stock_list = stock_list)

@app.route('/<code>/')
def stock_page(code):
    code_name = request.args.get('name')
    label = code
    xlabels = stock.stock_labels(code)
    high_price = stock.stock_high_prices(code)
    low_price = stock.stock_low_prices(code)
    open_price = stock.stock_open_prices(code)
    initial, final = backtesting.execute(code, 10000000)
    percent = float(final - initial) / float(initial) * 100.
    return render_template('chart.html', **locals())

    # parameter_dict = request.args.to_dict()
    # if len(parameter_dict) == 0:
    #     return 'No parameter'
    #
    # parameters = ''
    # for key in parameter_dict.keys():
    #     parameters += 'key: {}, value: {}\n'.format(key, request.args[key])
    # return parameters
@app.route('/<code>/backtesting/')
def backtesting_page(code):
    code_name = request.args.get('name')
    initial, final = backtesting.execute(code,10000000)
    percent = float(final - initial) / float(initial) * 100.
    print(percent)
    return render_template('backtesting.html', **locals())

@app.route('/twitter')
def twitter_page():
    labels, twitter_num, start_time, date_list_str = twitter_scrap.twitter_data()
    high_price, low_price, open_price, close_price = twitter_scrap.yfinance_data(start_time)
    data = twitter_scrap.make_data(high_price,low_price,close_price,labels,twitter_num)
    return render_template('twitter.html', **locals())

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)