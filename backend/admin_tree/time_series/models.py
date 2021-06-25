from django.db import models
from monaco.common.models import FileDTO, Printer, Reader
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from fbprophet import Prophet
from datetime import datetime
from pandas_datareader import data
import yfinance as yf
yf.pdr_override()
path = "c:/Windows/Fonts/malgun.ttf"
import platform
from matplotlib import font_manager, rc

if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~')
plt.rcParams['axes.unicode_minus'] = False

'''
시계열 데이터 
: 일련의 순차적으로 정해진 데이터 셋의 집합
: 시간에 관해 순서가 매겨져 있다는 점과, 연속한 관측치는 서로 상관관계를 갖고 있다

회귀분석
: 관찰된 연속형 변수들에 대해 두 변수 사이의 모형을 구한뒤 적합도를 측정해 내는 분석 방법

'''



# class Entity(FileDTO, Printer, Reader, Scraper):
#     pass

class DataService(Reader):

    def __init__(self):
        self.file = FileDTO()
        self.reader = Reader()
        self.printer = Printer()

    # RMSE(Root Mean Square Error, 표준편차)을 계산해주는 error() 함수를 생성
    # f(x)는 예측값, y는 실제값
    # sqrt-> 제곱근 함수. 루트 역할
    def error(self,f, x, y):
        return np.sqrt(np.mean((f(x) - y) ** 2))

    def regression(self):
        file = self.file
        reader = self.reader

        file.context = './data/'
        file.fname = '08. PinkWink Web Traffic'

        df = reader.csv_header(file,header=None) # common.models.py 수정필요!
        df.columns = ['date','hit']
        df = df[df['hit'].notnull()]
        print(df.head())

        #  df 시각화
        df['hit'].plot(figsize=(12,4), grid=True)

        # 주기성 확인위한 작업

        # len은 매개변수의 요소의 개수
        # pinkwink_web index 값으로 이루어진 array 생성
        time =np.arange(0, len(df))

        # 웹 트래픽의 자료를 traffic 변수에 저장
        traffic = df['hit'].values

        # linespace()함수는 두 수 사이를 50개의 균일한 간격의 수를 배열로 만들어준다.
        fx = np.linspace(0, time[-1], 1000)

        '''
        polyfit(x, y, 함수의 차수)
        -> x와  y로 이루어진 그래프에서 함수의 차수의 계수를 찾아 본래 데이터의 기울기와 절편의 값과 
        유사하게 만들어 직선의 그래프로 만들어준다. 
        
        '''

        #  1차원 다항식
        fp1 = np.polyfit(time, traffic, 1) # 1차원 다항식으로 생성 후 계수 도출
        f1 = np.poly1d(fp1) # 도출한 계수로 다시 다항식 생성 후 계수 도출

        #  2차원 다항식
        f2p = np.polyfit(time, traffic, 2)
        f2 = np.poly1d(f2p)

        # 3차원 다항식
        f3p = np.polyfit(time, traffic, 3)
        f3 = np.poly1d(f3p)

        # 15차원 다항식
        f15p = np.polyfit(time, traffic, 15)
        f15 = np.poly1d(f15p)

        # error 함수를 통해 오차의 표준편차 즉, 잔차 제곱합을 구한다.
        # 데이터와 추정 모델 간의 불일치를 측정
        print(f' 1차원 다항식의 불일치 정도: {self.error(f1,time,traffic)}')
        print(f' 2차원 다항식의 불일치 정도: {self.error(f2,time,traffic)}')
        print(f' 3차원 다항식의 불일치 정도: {self.error(f3,time,traffic)}')
        print(f' 15차원 다항식의 불일치 정도: {self.error(f15,time,traffic)}')

        # 각 차원의 다항식 시각화
        plt.figure(figsize=(10, 6))
        plt.scatter(time, traffic, s=10) # scatter 함수를 통해 그래프 상에 점 찍기
        plt.plot(fx, f1(fx), lw=4, label='f1')  # plot 함수를 통해 그래프 생성
        plt.plot(fx, f2(fx), lw=4, label='f2')
        plt.plot(fx, f3(fx), lw=4, label='f3')
        plt.plot(fx, f15(fx), lw=4, label='f15')
        plt.grid(True, linestyle='-', color='0.75') # 그래프 상에 격자무늬 표현
        plt.legend(loc=2)
        # 이 그래프가 무엇을 의미하는지 알기 위해, label, scatter 을 plot안에 사용해야하며,
        # 그리고 plt.legend()를 실행해야 한다.
        plt.show()
        return df

    def forecast(self, df):
        df = df.rename(columns={"date":"ds", "hit":"y"} )
        df.reset_index(inplace=True)
        df['ds'] = pd.to_datetime(df['ds'], format="%y. %m. %d.")

        # 모델 생성
        m = Prophet(yearly_seasonality=True, daily_seasonality=True)
        # 주기성이 연단위(yearly_seasonality) 및 일단위(daily_seasonality)로 있다고 알려준다

        # 모델 학습
        m.fit(df);
        print(m)

        # make_future_dataframe()로 지정된 날짜 수만큼 예측할 것
        future = m.make_future_dataframe(periods=60)
        future.tail()

        # 예측
        forecast = m.predict(future)
        forecast.head()

        # 확인하고 싶은 변수들만 뽑아내서 확인
        forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

        # 시각화
        m.plot(forecast);
        m.plot_components(forecast);
        # forecast component 시각화 -> Trend, Holidays, Weakly, Yearly, Daily

    def seasonal(self):

        # 사용하고자 하는 데이터 기간 설정
        start_date = '1990-1-1'
        end_date = '2017-6-30'
        KIA = data.get_data_yahoo('000270.KS', start_date, end_date)  # 기아자동차 주식

        # KIA.head()

        # 종가를 기준으로 시각화
        KIA['Close'].plot(figsize=(12, 6), grid=True);

        # 일부 데이터를 잘라서 먼저 forecast
        KIA_trunc = KIA[:'2016-12-31']
        print(KIA)
        print(KIA_trunc)
        df = pd.DataFrame({'ds': KIA_trunc.index, 'y': KIA_trunc['Close']})
        df.reset_index(inplace=True)
        del df['Date']
        df.head()


        m = Prophet(daily_seasonality=True)
        m.fit(df);


        future = m.make_future_dataframe(periods=365)
        future.tail()
        forecast = m.predict(future)
        forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
        m.plot(forecast);

        # 계절성 성분 별로 분해해서 분석.
        m.plot_components(forecast);

        # 받아오는 데이터 날짜 변경
        start_date = '2014-1-1'
        end_date = '2017-7-31'
        KIA = data.get_data_yahoo('000270.KS', start_date, end_date)
        KIA['Close'].plot(figsize=(12, 6), grid=True);

        # 예측용으로 사용할 데이터
        KIA_trunc = KIA[:'2017-05-31']
        KIA_trunc['Close'].plot(figsize=(12, 6), grid=True);
        df = pd.DataFrame({'ds': KIA_trunc.index, 'y': KIA_trunc['Close']})
        df.reset_index(inplace=True)
        del df['Date']

        # 주기성 일단위
        m = Prophet(daily_seasonality=True)
        m.fit(df);
        future = m.make_future_dataframe(periods=61)
        future.tail()
        forecast = m.predict(future)

        m.plot(forecast);
        plt.figure(figsize=(12, 6))
        plt.plot(KIA.index, KIA['Close'], label='real')
        plt.plot(forecast['ds'], forecast['yhat'], label='forecast')
        plt.grid()
        plt.legend()
        plt.show()

    def growth_model(self):
        file = self.file
        reader = self.reader

        file.context = './data/'
        file.fname = '08. example_wp_R'

        df = reader.csv_header(file, header=0)
        df['y'] = np.log(df['y'])  # 로그 변환
        df['cap'] = 8.5  # 예측 값의 상한을 8.5로 설정
        df.head()

        # 예측값의 상한, 하한을 설정하기 위해서는 growth 파라미터를 설정해주어야 한다.
        # 주어진 데이터를 그래프로 그려보면 '로지스틱 함수'의 형태와 유사함을 알 수 있으므로, growth = 'logistic' 이라고 설정
        m = Prophet(growth='logistic', daily_seasonality=True)
        m.fit(df)
        future = m.make_future_dataframe(periods=1826)
        future['cap'] = 8.5 # 예측값의 상한 설정
        fcst = m.predict(future)
        m.plot(fcst);

        forecast = m.predict(future)
        m.plot_components(forecast);
        plt.show()

    def holiday_forecast(self):
        file = self.file
        reader = self.reader

        file.context = './data/'
        file.fname = '08. example_wp_peyton_manning'
        df = reader.csv_header(file, header=0)

        df['y'] = np.log(df['y'])  # 로그 변환
        m = Prophet(daily_seasonality=True)
        m.fit(df)

        future = m.make_future_dataframe(periods=366)
        df.y.plot(figsize=(12, 6), grid=True)
        playoffs = pd.DataFrame({
            'holiday': 'playoff',
            'ds': pd.to_datetime(['2008-01-13', '2009-01-03', '2010-01-16',
                                  '2010-01-24', '2010-02-07', '2011-01-08',
                                  '2013-01-12', '2014-01-12', '2014-01-19',
                                  '2014-02-02', '2015-01-11', '2016-01-17',
                                  '2016-01-24', '2016-02-07']),
            'lower_window': 0,
            'upper_window': 1,
        })
        superbowls = pd.DataFrame({
            'holiday': 'superbowl',
            'ds': pd.to_datetime(['2010-02-07', '2014-02-02', '2016-02-07']),
            'lower_window': 0,
            'upper_window': 1,
        })
        holidays = pd.concat((playoffs, superbowls))
        holidays.head()

        # 휴일과 같이 모델에 반영하고 싶은 이벤트가 있다면 새로 DataFrame을 생성하여 반영할 수 있다.
        # 모델 생성시, holidays 파라미터 사용
        m = Prophet(holidays=holidays, daily_seasonality=True)
        forecast = m.fit(df).predict(future)
        forecast[(forecast['playoff'] + forecast['superbowl']).abs() > 0][
            ['ds', 'playoff', 'superbowl']][-10:]
        m.plot(forecast)
        m.plot_components(forecast)
        plt.show()


if __name__ == '__main__':
    service = DataService()
    # df = service.regression()
    # service.forecast(df=df)
    # service.seasonal()
    # service.growth_model()
    # service.holiday_forecast()