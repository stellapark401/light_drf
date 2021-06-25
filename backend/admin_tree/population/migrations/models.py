from admin_tree.common.models import CommonServices, Scrapper, DataTransferObject
import pandas as pd
import numpy as np
from sklearn import preprocessing
import folium
import platform
import matplotlib.pyplot as plt
import folium
import json
import warnings


class PopDTO(DataTransferObject):

    pop: object
    draw_korea: object


    @property
    def pop(self) -> object: return self._pop

    @pop.setter
    def pop(self, pop):
        self._pop = pop

    @property
    def draw_korea(self) -> object: return self._draw_korea

    @draw_korea.setter
    def draw_korea(self, draw_korea):
        self._draw_korea = draw_korea


class Service(CommonServices):
    BORDER_LINES = []

    def __init__(self):
        self.f = PopDTO()
        self.s = CommonServices()


    def xlsx(self, n) -> object:
        return pd.read_excel(self.new_file(), header=n, usecols=None)

    def modeling(self):
        this = self.new_model()
        this = self.area_risk_of_extinction(this)
        this = self.make_unique_id(this)
        this = self.make_map_with_cartogram(this)
        this = self.population_state(this)
        this = self.woman_ratio(this)
        this = self.save_folium_map(this)

    def new_model(self):
        f = self.f
        s = self.s

        path = "c:/Windows/Fonts/malgun.ttf"
        from matplotlib import font_manager, rc
        if platform.system() == 'Darwin':
            rc('font', family='AppleGothic')
        elif platform.system() == 'Windows':
            font_name = font_manager.FontProperties(fname=path).get_name()
            rc('font', family=font_name)
        else:
            print('Unknown system... sorry~~~~')

        plt.rcParams['axes.unicode_minus'] = False
        self.setting_context('../data/', '05. population_raw_data.xlsx')
        population = self.xlsx(1)
        population.fillna(method='pad', inplace=True)

        return population


    def area_risk_of_extinction(self, population):

        f = self.f

        population.rename(columns={'행정구역(동읍면)별(1)': '광역시도',
                                   '행정구역(동읍면)별(2)': '시도',
                                   '계': '인구수'}, inplace=True)

        population = population[(population['시도'] != '소계')]
        # 시구 컬럼이 소계 + 용산구 이런식으로 되어 있어서 소계는 제외한 시도를 뽑기 위한 코드

        population.is_copy = False

        population.rename(columns={'항목': '구분'}, inplace=True)

        population.loc[population['구분'] == '총인구수 (명)', '구분'] = '합계'
        population.loc[population['구분'] == '남자인구수 (명)', '구분'] = '남자'
        population.loc[population['구분'] == '여자인구수 (명)', '구분'] = '여자'

        population['20-39세'] = population['20 - 24세'] + population['25 - 29세'] + \
                               population['30 - 34세'] + population['35 - 39세']

        population['65세이상'] = population['65 - 69세'] + population['70 - 74세'] + \
                              population['75 - 79세'] + population['80 - 84세'] + \
                              population['85 - 89세'] + population['90 - 94세'] + \
                              population['95 - 99세'] + population['100+']

        pop = pd.pivot_table(population,
                             index=['광역시도', '시도'],
                             columns=['구분'],
                             values=['인구수', '20-39세', '65세이상'])

        print(pop.head())
        pop['소멸비율'] = pop['20-39세', '여자'] / (pop['65세이상', '합계'] / 2)
        pop['소멸위기지역'] = pop['소멸비율'] < 1.0
        print(pop.head())
        # .index.get_level_values(1) 멀티인덱스에서 특정 레벨(단계)의 레이블을 추출해야하는경우 = 벡터반환
        pop[pop['소멸위기지역'] == True].index.get_level_values(1)
        pop.reset_index(inplace=True) # 0,1,2 .. 를인덱스로 추가하고 기존인덱스는 1열이 된다

        tmp_columns = [pop.columns.get_level_values(0)[n] + \
                       pop.columns.get_level_values(1)[n]
                       for n in range(0, len(pop.columns.get_level_values(0)))
                       ]
        pop.columns = tmp_columns
        f.pop = pop
        return f

    ### 5.5 지도시각화를 위해 지역별 고유 ID 만들기
    def make_unique_id(self, this):
        f = self.f
        pop = this.pop
        pop['시도'].unique()

        si_name = [None] * len(pop)
        # 시도 칼럼에서 시 안에 포함된 구 가 값이 크기 떄문에 따로 빠져나온 경우로 인해서 아래와 같이 따로 만들어줌
        # 예를 들어 청주시의 경우 상당구 서원구가 시도 칼럼에 같이 존재 하기때문이다
        tmp_gu_dict = {'수원': ['장안구', '권선구', '팔달구', '영통구'],
                       '성남': ['수정구', '중원구', '분당구'],
                       '안양': ['만안구', '동안구'],
                       '안산': ['상록구', '단원구'],
                       '고양': ['덕양구', '일산동구', '일산서구'],
                       '용인': ['처인구', '기흥구', '수지구'],
                       '청주': ['상당구', '서원구', '흥덕구', '청원구'],
                       '천안': ['동남구', '서북구'],
                       '전주': ['완산구', '덕진구'],
                       '포항': ['남구', '북구'],
                       '창원': ['의창구', '성산구', '진해구', '마산합포구', '마산회원구'],
                       '부천': ['오정구', '원미구', '소사구']}
        for n in pop.index:
            # 광역시도 칼럼에서 광역시,특별시자치시를 제외한 경기도,전라남도 등 도를 뽑아라
            if pop['광역시도'][n][-3:] not in ['광역시', '특별시', '자치시']:
                # 만약 시도가 고성 = 강원도면 고성(강원)으로 출력하라
                if pop['시도'][n][:-1] == '고성' and pop['광역시도'][n] == '강원도':
                    si_name[n] = '고성(강원)'
                elif pop['시도'][n][:-1] == '고성' and pop['광역시도'][n] == '경상남도':
                    si_name[n] = '고성(경남)'
                # 위의 것과 다른 경우에의 일반적 시,도 에는 '안성시' '시' 를 빼고 '안성' 만 뽑아라
                else:
                    si_name[n] = pop['시도'][n][:-1]
                # tmp_gu_dict.items(): 이것들은 시에 포함되어 있는 구가 따로 존재 하니 딕셔너리로 만들어주고
                for keys, values in tmp_gu_dict.items():
                    if pop['시도'][n] in values:
                        if len(pop['시도'][n]) == 2:
                            si_name[n] = keys + ' ' + pop['시도'][n]
                            # 만약 '시도' 의 길이가 2이면 그대로 진행 (부산 - 남구)
                        elif pop['시도'][n] in ['마산합포구', '마산회원구']:
                            si_name[n] = keys + ' ' + pop['시도'][n][2:-1]
                            # 마지막 한글자 제외 출력 (tmp_gu_dict.items())
                        else:
                            si_name[n] = keys + ' ' + pop['시도'][n][:-1]
            # 세종 특별자치시는 한개 뿐
            elif pop['광역시도'][n] == '세종특별자치시':
                si_name[n] = '세종'
            # 나머지는 광역시, 특별시, 자치시 중에서
            else:
                # '시도'가 2글자인 경우 (광역시도의 앞 2글자 + '시도'
                if len(pop['시도'][n]) == 2:
                    si_name[n] = pop['광역시도'][n][:2] + ' ' + pop['시도'][n]
                else:
                    si_name[n] = pop['광역시도'][n][:2] + ' ' + pop['시도'][n][:-1]

        pop['ID'] = si_name
        del pop['20-39세남자']
        del pop['65세이상남자']
        del pop['65세이상여자']
        f.pop = pop
        return f

    ### 5.6 Cartogram으로 우리나라 지도 만들기
    def make_map_with_cartogram(self, this):
        f = self.f
        s = self.s
        self.setting_context('../data/', '05. draw_korea_raw.xlsx')
        pop = this.pop

        draw_korea_raw = self.xlsx(0)

        draw_korea_raw_stacked = pd.DataFrame(draw_korea_raw.stack())
        draw_korea_raw_stacked.reset_index(inplace=True)
        draw_korea_raw_stacked.rename(columns={'level_0': 'y', 'level_1': 'x', 0: 'ID'},
                                      inplace=True)

        draw_korea = draw_korea_raw_stacked


        self.BORDER_LINES = [
            [(5, 1), (5, 2), (7, 2), (7, 3), (11, 3), (11, 0)],  # 인천
            [(5, 4), (5, 5), (2, 5), (2, 7), (4, 7), (4, 9), (7, 9),
             (7, 7), (9, 7), (9, 5), (10, 5), (10, 4), (5, 4)],  # 서울
            [(1, 7), (1, 8), (3, 8), (3, 10), (10, 10), (10, 7),
             (12, 7), (12, 6), (11, 6), (11, 5), (12, 5), (12, 4),
             (11, 4), (11, 3)],  # 경기도
            [(8, 10), (8, 11), (6, 11), (6, 12)],  # 강원도
            [(12, 5), (13, 5), (13, 4), (14, 4), (14, 5), (15, 5),
             (15, 4), (16, 4), (16, 2)],  # 충청북도
            [(16, 4), (17, 4), (17, 5), (16, 5), (16, 6), (19, 6),
             (19, 5), (20, 5), (20, 4), (21, 4), (21, 3), (19, 3), (19, 1)],  # 전라북도
            [(13, 5), (13, 6), (16, 6)],  # 대전시
            [(13, 5), (14, 5)],  # 세종시
            [(21, 2), (21, 3), (22, 3), (22, 4), (24, 4), (24, 2), (21, 2)],  # 광주
            [(20, 5), (21, 5), (21, 6), (23, 6)],  # 전라남도
            [(10, 8), (12, 8), (12, 9), (14, 9), (14, 8), (16, 8), (16, 6)],  # 충청북도
            [(14, 9), (14, 11), (14, 12), (13, 12), (13, 13)],  # 경상북도
            [(15, 8), (17, 8), (17, 10), (16, 10), (16, 11), (14, 11)],  # 대구
            [(17, 9), (18, 9), (18, 8), (19, 8), (19, 9), (20, 9), (20, 10), (21, 10)],  # 부산
            [(16, 11), (16, 13)],  # 울산
            #     [(9,14), (9,15)],
            [(27, 5), (27, 6), (25, 6)],
        ]

        # 지역 이름 표시
        for idx, row in draw_korea.iterrows():
            # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다.
            # (중구, 서구)

            if len(row['ID'].split()) == 2:
                dispname = '{}\n{}'.format(row['ID'].split()[0], row['ID'].split()[1])
            elif row['ID'][:2] == '고성':
                dispname = '고성'
            else:
                dispname = row['ID']

            # 서대문구, 서귀포시 같이 이름이 3자 이상인 경우에 작은 글자로 표시한다.
            if len(dispname.splitlines()[-1]) >= 3:
                fontsize, linespacing = 9.5, 1.5
            else:
                fontsize, linespacing = 11, 1.2


            plt.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5), weight='bold',
                         fontsize=fontsize, ha='center', va='center',
                         linespacing=linespacing)

        # 시도 경계 그린다.
        for path in self.BORDER_LINES:
            ys, xs = zip(*path)
            plt.plot(xs, ys, c='black', lw=1.5)

        plt.gca().invert_yaxis()
        # plt.gca().set_aspect(1)

        plt.axis('off')

        plt.tight_layout()
        plt.show()

        set(draw_korea['ID'].unique()) - set(pop['ID'].unique())
        set(pop['ID'].unique()) - set(draw_korea['ID'].unique())

        tmp_list = list(set(pop['ID'].unique()) - set(draw_korea['ID'].unique()))

        for tmp in tmp_list:
            pop = pop.drop(pop[pop['ID'] == tmp].index)

        print(set(pop['ID'].unique()) - set(draw_korea['ID'].unique()))

        pop = pd.merge(pop, draw_korea, how='left', on=['ID'])

        mapdata = pop.pivot_table(index='y', columns='x', values='인구수합계')
        masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

        f.pop = pop
        f.draw_korea = draw_korea

        return f

    # 5.7 인구 현황 및 인구 소멸 지역 확인하기
    def population_state(self, this):
        f = self.f
        pop = this.pop
        self.drawKorea('인구수합계', pop, 'Blues')

        pop['소멸위기지역'] = [1 if con else 0 for con in pop['소멸위기지역']]
        self.drawKorea('소멸위기지역', pop, 'Reds')
        pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
        self.drawKorea('여성비', pop, 'RdBu')

        pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
        self.drawKorea('2030여성비', pop, 'RdBu')
        pop_folium = pop.set_index('ID')
        f.pop = pop
        return f

    #### 5-8. 인구 현황에서 여성 인구 비율 확인하기
    def woman_ratio(self, this):
        f = self.f
        pop = this.pop
        pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
        self.drawKorea_2('여성비', pop, 'RdBu')

        pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
        self.drawKorea_2('2030여성비', pop, 'RdBu')
        f.pop = pop
        return f

    def drawKorea(self, targetData, blockedMap, cmapname):
        gamma = 0.75

        whitelabelmin = (max(blockedMap[targetData]) -
                         min(blockedMap[targetData])) * 0.25 + \
                        min(blockedMap[targetData])

        datalabel = targetData

        vmin = min(blockedMap[targetData])
        vmax = max(blockedMap[targetData])

        mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
        masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

        plt.figure(figsize=(9, 11))
        plt.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname,
                   edgecolor='#aaaaaa', linewidth=0.5)

        # 지역 이름 표시
        for idx, row in blockedMap.iterrows():
            # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다.
            # (중구, 서구)
            if len(row['ID'].split()) == 2:
                dispname = '{}\n{}'.format(row['ID'].split()[0], row['ID'].split()[1])
            elif row['ID'][:2] == '고성':
                dispname = '고성'
            else:
                dispname = row['ID']

            # 서대문구, 서귀포시 같이 이름이 3자 이상인 경우에 작은 글자로 표시한다.
            if len(dispname.splitlines()[-1]) >= 3:
                fontsize, linespacing = 10.0, 1.1
            else:
                fontsize, linespacing = 11, 1.

            annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
            plt.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5), weight='bold',
                         fontsize=fontsize, ha='center', va='center', color=annocolor,
                         linespacing=linespacing)

        # 시도 경계 그린다.
        for path in self.BORDER_LINES:
            ys, xs = zip(*path)
            plt.plot(xs, ys, c='black', lw=2)

        plt.gca().invert_yaxis()

        plt.axis('off')

        cb = plt.colorbar(shrink=.1, aspect=10)
        cb.set_label(datalabel)

        plt.tight_layout()
        plt.show()

    #### 5-8. 인구 현황에서 여성 인구 비율 확인하기

    def drawKorea_2(self, targetData, blockedMap, cmapname):
        gamma = 0.75

        whitelabelmin = 20.

        datalabel = targetData

        tmp_max = max([np.abs(min(blockedMap[targetData])),
                       np.abs(max(blockedMap[targetData]))])
        vmin, vmax = -tmp_max, tmp_max

        mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
        masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

        plt.figure(figsize=(9, 11))
        plt.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname,
                   edgecolor='#aaaaaa', linewidth=0.5)

        # 지역 이름 표시
        for idx, row in blockedMap.iterrows():
            # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다.
            # (중구, 서구)
            if len(row['ID'].split()) == 2:
                dispname = '{}\n{}'.format(row['ID'].split()[0], row['ID'].split()[1])
            elif row['ID'][:2] == '고성':
                dispname = '고성'
            else:
                dispname = row['ID']

            # 서대문구, 서귀포시 같이 이름이 3자 이상인 경우에 작은 글자로 표시한다.
            if len(dispname.splitlines()[-1]) >= 3:
                fontsize, linespacing = 10.0, 1.1
            else:
                fontsize, linespacing = 11, 1.

            annocolor = 'white' if np.abs(row[targetData]) > whitelabelmin else 'black'
            plt.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5), weight='bold',
                         fontsize=fontsize, ha='center', va='center', color=annocolor,
                         linespacing=linespacing)

        # 시도 경계 그린다.
        for path in self.BORDER_LINES:
            ys, xs = zip(*path)
            plt.plot(xs, ys, c='black', lw=2)

        plt.gca().invert_yaxis()

        plt.axis('off')

        cb = plt.colorbar(shrink=.1, aspect=10)
        cb.set_label(datalabel)

        plt.tight_layout()
        plt.show()

    # 5-9. Folium에서 인구 소멸 위기 지역 표현하기
    def save_folium_map(self, this):

        f = self.f
        s = self.s
        pop = this.pop
        draw_korea = this.draw_korea

        pop_folium = pop.set_index('ID')
        pop_folium.head()

        warnings.simplefilter(action='ignore', category=FutureWarning)
        f.context = './data/'
        f.fname = '05. skorea_municipalities_geo_simple'
        # geo_path = './data/05. skorea_municipalities_geo_simple.json'
        geo_str = s.json(f)

        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        map.choropleth(geo_data=geo_str,
                       data=pop_folium['인구수합계'],
                       columns=[pop_folium.index, pop_folium['인구수합계']],
                       fill_color='YlGnBu',  # PuRd, YlGnBu
                       key_on='feature.id')

        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        map.choropleth(geo_data=geo_str,
                       data=pop_folium['소멸위기지역'],
                       columns=[pop_folium.index, pop_folium['소멸위기지역']],
                       fill_color='PuRd',  # PuRd, YlGnBu
                       key_on='feature.id')

        draw_korea.to_csv("./saved_data/05. draw_korea.csv", encoding='utf-8', sep=',')


if __name__ == '__main__':
    s = Service()
    s.modeling()
