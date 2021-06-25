from django.db import models
from admin_tree.common.models import CommonServices, Scrapper
from glob import glob
import pandas as pd

class Service(CommonServices, Scrapper):

    def __init__(self):
        self.svc = CommonServices()
        self.scp = Scrapper()

    def get_url(self):
        svc = self.svc
        scp = self.scp

        # scp.url = 'https://www.opinet.co.kr/searRgSelect.do'
        scp.url = 'https://www.naver.com'
        driver = scp.chrome_driver()
        driver.get(scp.url)

    def price_info_by_gas_station(self):
        svc = self.svc
        scp = self.scp
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        temp_raw = []
        for name in glob('data/지역_위치별*xls'):
            svc.setting_context('./', name)
            temp_raw.append(svc.xls())
        station_raw = pd.concat(temp_raw, ignore_index=True)

        stations = pd.DataFrame({'Oil_store': station_raw['상호'],
                                 '주소': station_raw['주소'],
                                 '가격': station_raw['휘발유'],
                                 '셀프': station_raw['셀프여부'],
                                 '상표': station_raw['상표']})
        stations['구'] = [i.split()[1] for i in stations['주소']]
        # stations.reset_index(drop=True)
        # idx = stations.index
        # print(idx.get_level_values(0))
        print(stations)
        # stations['구'].unique()
        '''
        for i, district in enumerate(stations['구']):
            if district[-1] != '구':
                print(f'{i+1}번째 "구"는 {district}')
        139번째 "구"는 서울특별시
        482번째 "구"는 특별시
        '''
        stations = stations.drop([stations.index[138], stations.index[481]])
        '''
        for i, price in enumerate(stations['가격']):
            if str(price).isnumeric():
                pass
            else:
                print(f'{i+1}번째 가격은 {price}')
        17번째 가격은 -
        239번째 가격은 -
        251번째 가격은 -
        '''
        stations = stations.drop([stations.index[16], stations.index[238], stations.index[250]])
        svc.dframe(stations)