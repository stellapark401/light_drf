from django.db import models
from dataclasses import dataclass
import json
import pandas as pd
import googlemaps
from selenium import webdriver
from abc import *
from icecream import ic

@dataclass
class DataTransferObject(object):
    context: str
    f_name: str
    dframe: object

    @property
    def context(self) -> str: return self._context

    @context.setter
    def context(self, context): self._context = context

    @property
    def f_name(self) -> str: return self._f_name

    @f_name.setter
    def f_name(self, f_name): self._f_name = f_name

    @property
    def dframe(self) -> object: return self._dframe

    @dframe.setter
    def dframe(self, dframe): self._dframe = dframe


class PrinterBase(metaclass=ABCMeta):
    @abstractmethod
    def dframe(self):
        pass


class ReaderBase(metaclass=ABCMeta):
    @abstractmethod
    def new_file(self):
        pass

    @abstractmethod
    def setting_context(self):
        pass

    @abstractmethod
    def csv(self):
        pass

    @abstractmethod
    def xls(self):
        pass

    @abstractmethod
    def json(self):
        pass

    @abstractmethod
    def gmaps(self):
        pass


class ScrapperBase(metaclass=ABCMeta):

    @abstractmethod
    def chrome_driver(self):
        pass


class CommonServices(PrinterBase, ReaderBase):
    dto = DataTransferObject()

    def dframe(self, df):
        print('*' * 50)
        print(f'Data type: {type(df)}이다.')
        print(f'Data column\n|->{df.columns}이다.')
        print(f"Data 상위 5개\n {df.head()}")
        print(f'Data null 갯수\n{df.isnull().sum()}개')
        print('*' * 50)

    def csv(self) -> object:
        return pd.read_csv(self.new_file(), encoding='UTF-8', thousands=',')

    def xls(self) -> object:
        return pd.read_excel(self.new_file(), header=2, usecols=None)

    def json(self) -> object:
        return json.load(open(self.new_file(), encoding='UTF-8'))

    def gmaps(self):
        return googlemaps.Client(key='AIzaSyBvIDK8Cn0nhO3N7TuSE4TlvWiNOViPqOs')

    def setting_context(self, payload1, payload2):
        self.dto.context = payload1
        self.f_name = payload2

    def new_file(self) -> str:
        return self.context + self.f_name


class Scrapper(ScrapperBase):

    def __init__(self):
        self.url = ''

    def chrome_driver(self) -> object:
        '''
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_argument('lang=ko_KR')
        '''
        return webdriver.Chrome('../common/chromedriver')
