import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import Column, VARCHAR, INTEGER, DATE, TEXT, ForeignKey
from sqlalchemy import create_engine
from time import sleep
from datetime import datetime
from crossing_app.config import *
import configparser
import requests

class Base(DeclarativeBase):
    pass

class Spare_parts(Base):
    __tablename__ = "spare_parts"

    id = Column(INTEGER, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(300), nullable=True)
    article_number = Column(VARCHAR(150), nullable=True)
    another_info = Column(TEXT, nullable=True)
    brend = Column(VARCHAR(300), nullable=True)
    category = Column(VARCHAR(200), nullable=True)

class Available(Base):
    __tablename__ = 'available'

    id = Column(INTEGER, unique=True, primary_key=True, autoincrement=True)
    spare_parts_id = Column(ForeignKey('spare_parts.id'))
    store = Column(VARCHAR(100), nullable=True)
    count = Column(VARCHAR(100), nullable=True)
    price = Column(VARCHAR(100), nullable=True)
    location = Column(VARCHAR(100), nullable=True)
    data_update = Column(DATE)

class ForumParsing():

    def __init__(self, value) -> None:
        self.url = 'https://itrade.forum-auto.ru/shop/index.html'
        self.value = value
        self.session = Session(create_engine("postgresql+psycopg2://crossing:{}@localhost/crossing_db".format(password_db)))
        self.category = 'all'
        self.count_elements = 0
        self.count_success = 0
    
    def post(self, data):
        session = requests.Session()
        return session.post(self.url, cookies=self.set_cookies(), data=data, timeout=None)
    
    
    def set_cookies(self, cookies = True):
        config = configparser.ConfigParser()
        config.read('crossing_app/files/cookies.cfg')
        if cookies:
            return {'PHPSESSID': config['Forum']['phpsessid']}
        else:   
            form_data = {
                    'login': forum_auto_login, 
                    'password': forum_auto_password,
                    'enter': r'%C2%EE%E9%F2%E8',
                    'check': 'stopSpam'
                }
            sleep(10)
            session = requests.Session()
            session.post(self.url, data=form_data)
            config['Forum'] = session.cookies
            with open('crossing_app/files/cookies.cfg', 'w') as cfg:
                    config.write(cfg)
            sleep(2)
            return session.cookies         

    def add_to_bd(self, item):
        try:
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
        except Exception as e:
            spare_id = False
        if spare_id:
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='Forum-auto',
                data_update=datetime.now()
            )
            self.session.add(available)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
        else:
            spare = Spare_parts(
                article_number = item['article_number'],
                brend = item['brend'],
                name = item['name'],
                category = item['category'],
                another_info = item['another_info']
            )
            self.session.add(spare)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='Forum-auto',
                data_update=datetime.now()
            )
            self.session.add(available)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
    

    def parsing_elements(self, page):
        elements_list = page.select('.tr_r, .tr, .tr_sa', limit=None)
        self.count_elements += len(elements_list)
        for elements in elements_list:
            if elements['class'] == ['header']:
                continue
            if elements['class'] != ['tr_hr']:
                try:
                    article_number = elements.select('[class=td2]')[0].get_text()
                    brend = elements.select('[class=td3]')[0].get_text()
                    try:
                        name = elements.select('[class=td4]')[0].get_text(';').split(';')[0].replace('\n', ' ').replace('\xa0', '')
                    except:
                        name = elements.select('[class=td4]')[0].get_text(';').replace('\n', ' ').replace('\xa0', '')
                    another_info = elements.select('[class=td5]')[0].get_text(';')
                    price = elements.select('[class=td6]')[3].get_text('')
                    count_loc = elements.select('[class=td7]')[0].get_text(';').split(';')
                    count = count_loc[0]
                    location = count_loc[1]              
                    self.count_success += 1
                    
                    self.add_to_bd(dict(
                        article_number = article_number,
                        brend = brend,
                        name = name,
                        another_info = another_info,
                        category = self.category,
                        price = price,
                        count = count,
                        location = location
                    ))
                except Exception as e:
                    pass
            
         
    def parsing(self):
        response = self.post({
            'gr1': 999,
            'gr2': self.value    
        })
        sleep(5)
        soup = BeautifulSoup(response.text, 'html.parser')
        login = soup.select('.leftside')
        if login != []:
            self.category = soup.select('#lr%s' % self.value)[0].get_text()
            page = soup.find(attrs={'name': 'to_basket'})
            if page:
                self.parsing_elements(page)
            else:
                try:
                    select_name = soup.find(attrs={'class': 'mas'})['name'] # тут случилась ошибка
                    selects = soup.find(attrs={'name': select_name}).findAll('option')
                    for select in selects:
                        if select['value'].encode('cp1251').isalnum() == False:
                            response = self.post({
                                'gr1': 999,
                                'gr2': self.value,
                                select_name: select['value'].encode('cp1251')
                            })
                        soup = BeautifulSoup(response.text, 'html.parser')
                        page = soup.find(attrs={'name': 'to_basket'})
                        if page:
                            self.parsing_elements(page)
                            sleep(5)
                        else:
                            sleep(5)
                            continue
                except Exception as e:
                    print(e)
                        
        else:  
            self.set_cookies(False)
            return self.parsing()

class AutooptParsing():

    def __init__(self, url) -> None:
        self.cookies = self.set_cookies()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69'}
        self.url = url
        self.session = Session(create_engine("postgresql+psycopg2://crossing:{}@localhost/crossing_db".format(password_db)))
        self.category = 'all'
        self.count_elements = 0
        self.count_success = 0
    
    def get(self, url, page = 1):
        session = requests.Session()
        params = {
                'pageSize': 100,
                'PAGEN_1': page
                        }
        return session.get(url, cookies=self.set_cookies(), params=params, timeout=None)
       
    def set_cookies(self, cookies = True):
        config = configparser.ConfigParser(interpolation=None)
        config.read('crossing_app/files/cookies.cfg')
        if cookies:
            return {'_identity': config['Autoopt']['_identity']}
        else:   
            import sys
            from twisted.internet import reactor
            from twisted.internet import default            
            del sys.modules['twisted.internet.reactor']
            default.install()   
            crawl_runner = CrawlerProcess()
            crawl_runner.crawl(AutoOptLogin)
            crawl_runner.start()
            return self.set_cookies()        

    def add_to_bd(self, item):
        try:
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
        except Exception as e:
            spare_id = False
        if spare_id:
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='Autoopt',
                data_update=datetime.now()
            )
            self.session.add(available)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
        else:
            spare = Spare_parts(
                article_number = item['article_number'],
                brend = item['brend'],
                name = item['name'],
                category = item['category'],
                another_info = item['another_info'],
            )
            self.session.add(spare)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='Autoopt',
                data_update=datetime.now()
            )
            self.session.add(available)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
    
    def page_parsing(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        elements_list = soup.select('[class~=n-catalog-item__product]')
        for elements in elements_list:
            try:
                article_number = elements.select('[class~=n-catalog-item__articles]')[0].get_text()
                brend = elements.select('[class~=n-catalog-item__brand]')[0].get_text(';')
                name = elements.select('[class~=n-catalog-item__name-link]')[0].get_text()
                price = elements.select('[class~=n-catalog-item__price-box]')[0].select('span')[1].get_text()
                count = elements.select('[class~=n-catalog-item__count-box]')[0].select('[class~=fake]')[0].get_text(';').split(';')
                self.add_to_bd(dict(
                    article_number = article_number,
                    brend = brend.split(';')[0].replace('\n', '').replace('  ', ''),
                    name = name.replace('\n', '').replace('  ', ''),
                    another_info = 'null',
                    category = self.category,
                    price = price,
                    count = count[0].replace('\n', '').replace('  ', ''),
                    location = 'null'
                ))
                self.count_success +=1
            except Exception as e:
                pass

    def parsing(self):
        sleep(3)
        response = self.get(self.url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select('[class~=username]') != []:
            self.category = soup.select('h1')[0].get_text()
            self.count_elements = int(soup.select('[class=bold]')[-1].get_text())
            count_page = int(soup.select('[class=bold]')[-1].get_text()) // 100
            for page in range(1, count_page + 1):
                sleep(3)
                self.page_parsing(self.get(self.url, page))       
        else:
            self.set_cookies(False)

class AutoOptLogin(scrapy.Spider):
    name = 'autoopt'
    start_urls = ['https://www.autoopt.ru/']
    

    def parse(self, response, **kwargs):
        token = response.xpath('//input[@name="_csrf"]/@value').get()
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form[@id="login-form"]',
            formdata={'LoginForm[username]': autoopt_login,
                      'LoginForm[password]': autoopt_password,
                      '_csrf': token,
                      },
            callback=self.set_cookies
        )
    def set_cookies(self, response):
        config = configparser.ConfigParser(interpolation=None)
        config.read('crossing_app/files/cookies.cfg')
        cookie = response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")
        config['Autoopt'][cookie[0]] = cookie[1]
        with open('crossing_app/files/cookies.cfg', 'w') as cfg:
            config.write(cfg)
        return {cookie[0]: cookie[1]}
              
        

class AutokontinentSpider():

    def __init__(self, url) -> None:
        self.url = 'https://autokontinent.ru/'
        self.urls = [url]
        self.session = Session(create_engine("postgresql+psycopg2://crossing:{}@localhost/crossing_db".format(password_db)))
        self.category = 'all'
        self.count_elements = 0
        self.count_success = 0
    

    def start(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        return webdriver.Chrome(chrome_options=options, executable_path='chromedriver')
        #return webdriver.Chrome() # не фоновый режим

    def login(self, cookies = True):
        config = configparser.ConfigParser()
        config.read('crossing_app/files/cookies.cfg')
        if cookies:
            try:
                driver = self.start()
            except:
                pass
            driver.get(self.url)
            for k, v in config['Autokontinent'].items():
                driver.add_cookie({'domain': 'autokontinent.ru', 'name': k, 'value': v})
            return driver
        else:
            try:
                driver = self.start()
            except:
                pass
            driver.get(self.url)
            click = driver.find_element('id', 'auth_link')
            click.click()
            login = driver.find_element('name', 'login')
            login.send_keys(autocontinent_login)
            password = driver.find_element('name', 'password')
            password.send_keys(autocontinent_password)
            button1 = driver.find_element('xpath', '//*[@id="ak_panel_1"]/form/input[3]')
            sleep(1)
            button1.click()
            sleep(1)
            button2 = driver.find_element('xpath', '//*[@id="login_state"]/form/div[2]/div[2]/input[1]')
            button2.click()
            sleep(1)
            driver.get_cookies()
            for value in driver.get_cookies():
                config['Autokontinent'][value['name']] = value['value']
            with open('crossing_app/files/cookies.cfg', 'w') as cfg:
                    config.write(cfg)
            return driver


    def add_to_bd(self, item):
        try:
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
        except Exception as e:
            spare_id = False
        if spare_id:
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='AutoKontinent',
                data_update=datetime.now()
            )
            self.session.add(available)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
        else:
            spare = Spare_parts(
                article_number = item['article_number'],
                brend = item['brend'],
                name = item['name'],
                category = item['category'],
                another_info = item['another_info']
            )
            self.session.add(spare)
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise
            spare_id = self.session.query(Spare_parts.id).filter(item['article_number'] == Spare_parts.article_number).all()[0]
            available = Available(
                spare_parts_id=spare_id[0], 
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store='Autokontinent',
                data_update=datetime.now()
            )
            self.session.add(available)
            self.session.commit()


    def page_v1(self, result):
        element_list =  result.select('tr')
        self.count_elements += len(element_list)
        name_position = [element.get_text() for element in element_list[0].select('th')]
        for elements in element_list[1:]:
            element = [element.get_text() for element in elements.select('td')]
            count = elements.select('td')[-1].find("div", {"onmouseover" : "oApp.core.tooltip.handler(event)"})['data-tooltip']
            data = dict()
            for num, el in enumerate(element):
                data[name_position[num]] = el
            try:
                data['Наименование']
            except:
                data['Наименование'] = 'null'
            another_info = dict()
            try:
                for info in name_position[3:len(name_position)-2]:
                    another_info[info] = data[info]
            except:
                another_info = 'null'
            try:
                self.add_to_bd(dict(
                    article_number = data['Артикул'],
                    brend = data['Бренд'],
                    name =  data['Наименование'],
                    another_info = another_info,
                    category = self.category,
                    price = 'null',
                    count = count,
                    location = 'null'
                        ))      
                
                self.count_success +=1
            except:
                pass

    def page_v2(self, result_list):
        self.count_elements += len(result_list)
        for elements in result_list:
            name = elements.select('h4')[0].get_text()
            article_number = name.split(' ')[-1]
            info_name = elements.select('div.part_info_column')[0].select('b')
            info_result = elements.select('div.part_info_column')[0].select('span')
            info = ['%s %s' % (info_name[key].get_text(), value.get_text()) for key, value in enumerate(info_result)]
            count = elements.find("div", {"onmouseover" : "oApp.core.tooltip.handler(event)"})['data-tooltip']
            try:
                self.add_to_bd(dict(
                    article_number = article_number,
                    brend = 'null',
                    name =  name,
                    another_info = info,
                    category = self.category,
                    price = 'null',
                    count = count,
                    location = 'null'
                        ))  
                
                self.count_success += 1
            except:
                pass
            

    def parsing(self):
        driver = self.login() 
        for url in self.urls:
            try:
                # Отключение 'в наличии'
                driver.get(url)
                driver.find_element('class name', 'available_item')
                driver.find_element('xpath', '//*[@id="available_item"]').click()
                sleep(3)
                # названия позиций
                soup = BeautifulSoup(driver.page_source, 'lxml')
                result = soup.select('#result')
                self.category = soup.select('.aside_caption')[0].get_text()
                if len(result) !=0:
                    self.page_v1(result[0])
                else:
                    self.page_v2(soup.select('div.part_block'))
            except:
                try:
                    [self.urls.append(url.get_attribute('href')) for url in driver.find_elements('class name', 'h1_url')]
                except:
                    print('Ошибка', url)


if __name__ == '__main__':
    
    pass