import warnings
import snscrape.modules.twitter as sntwitter
import datetime
import yfinance as yf

warnings.filterwarnings(action='ignore')

def yfinance_data(starttime):
    data = yf.download('TSLA',start = '2020-01-01')
    data.drop('Adj Close', axis = 1,inplace=True)
    data = data.sort_index(ascending=True)
    high_price = data['High'].tolist()
    low_price = data['Low'].tolist()
    open_price = data['Open'].tolist()
    close_price = data['Close'].tolist()
    return high_price, low_price, open_price, close_price

def twitter_data():
    query = "elonmusk"
    num_list = []
    date_list = []
    date_list_str = []
    duration = 50
    today_datetime = datetime.date.today()
    start_datetime = today_datetime-datetime.timedelta(days=duration)
    print(today_datetime, start_datetime)
    for i in range(duration):
        date_list.append(today_datetime)
        date_list_str.append(today_datetime.strftime("%Y-%m-%d"))
        num_list.append(0)
        today_datetime = today_datetime-datetime.timedelta(days=1)
    index = 0
    for tweet in sntwitter.TwitterUserScraper(query).get_items():
        for j in range(index,duration):
            if tweet.date.date() == date_list[j]:
                num_list[j] = num_list[j]+1
                index = j
                break;
        if index == duration-1:
            break;
    date_list.reverse()
    num_list.reverse()
    date_list_str.reverse()
    return date_list, num_list, start_datetime, date_list_str

def make_data(high_price, low_price, close_price, date_list, num_list):
    list = []
    for i in range(1, len(date_list)):
        dic = {}
        # 변동성 구하기
        v = abs(high_price[i]-low_price[i])/close_price[i-1]*100
        dic['volatility'] = v
        # 날짜 넣기
        dic['date'] = date_list[i].strftime("%Y-%m-%d")
        # 트위터 개수 넣기
        dic['twitter_count'] = int(num_list[i])
        list.append(dic)
    return list

if __name__ == '__main__':
    labels, twitter_num, start_time = twitter_data()
    print(labels)
    high_price, low_price, open_price, close_price = yfinance_data(start_time)
    result = make_data(high_price,low_price,close_price,labels,twitter_num)
    print(result)