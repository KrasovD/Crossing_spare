import scrapy
from scrapy.crawler import CrawlerProcess
from time import sleep
from app import db
from app.model import Spare_parts, Available
from sqlalchemy import update
from datetime import datetime
import requests
import configparser
from bs4 import BeautifulSoup
import traceback

from app.config import *


def add_to_bd(item):
    # поиск в бд по артикулу
    spare_id = db.session.query(Spare_parts.id).filter(
        item['article_number'] == Spare_parts.article_number).all()
    if spare_id:
        # если артикул найден, то поищем такую же позицию
        # в available по магазину и складу
        available = update(Available).where(
            Available.spare_parts_id == spare_id[0][0],
            Available.location == item['location'],
            Available.store == item['store']
        ).values(
            count=item['count'],
            price=item['price'],
            data_update=datetime.now()
        ).return_defaults(Available.id)
        r = db.session.execute(available)
        if r.returned_defaults == None:
            available = Available(
                spare_parts_id=spare_id[0][0],
                price=item['price'],
                count=item['count'],
                location=item['location'],
                store=item['store'],
                data_update=datetime.now()
            )
            db.session.add(available)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
    else:
        spare = Spare_parts(
            article_number=item['article_number'],
            brend=item['brend'],
            name=item['name'],
            category=item['category'],
            another_info=item['another_info'],
        )
        db.session.add(spare)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        spare_id = db.session.query(Spare_parts.id).filter(
            item['article_number'] == Spare_parts.article_number).all()[0]
        available = Available(
            spare_parts_id=spare_id[0],
            price=item['price'],
            count=item['count'],
            location=item['location'],
            store=item['store'],
            data_update=datetime.now()
        )
        db.session.add(available)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


def formation(data_spare, spare):
    desired_value = list()
    similar_value = list()
    avail = False
    store = ('Autoopt', 'Forum-auto')

    def raw_string(string):
        return (string.replace('_', '').replace(' ', '').replace('-', '').replace('/', '')).lower()

    for data in data_spare:
        try:
            if raw_string(spare) == raw_string(data['article_number']) or data['article_number'] == 'Отсутствует':
                desired_value.append(data)
            else:
                similar_value.append(data)
            add_to_bd(data)
        except:
            pass
    for data in desired_value:
        if data['article_number'] != 'Отсутствует':
            avail = True
    for st in store:
        if st not in [data['store'] for data in desired_value]:
            desired_value.append({
                'store': st,
                'article_number': 'Отсутствует',
                'brend': '',
                'name': '',
                'price': '',
                'location': '',
                'count': ''
            })
    return desired_value, similar_value, avail


class ForumParsing():

    def __init__(self, value) -> None:
        self.url = 'https://itrade.forum-auto.ru/shop/index.html'
        self.value = value

    def post(self, data):
        session = requests.Session()
        return session.post(self.url, cookies=self.set_cookies(), data=data, timeout=None)

    def set_cookies(self, cookies=True):
        config = configparser.ConfigParser()
        config.read('app/files/cookies.cfg')
        if cookies:
            return {'PHPSESSID': config['Forum']['phpsessid']}
        else:
            form_data = {
                'login': forum_auto_login,
                'password': forum_auto_password,
                'enter': r'%C2%EE%E9%F2%E8',
                'check': 'stopSpam'
            }
            sleep(1)
            session = requests.Session()
            session.post(self.url, data=form_data)
            config['Forum'] = session.cookies
            with open('app/files/cookies.cfg', 'w') as cfg:
                config.write(cfg)
            sleep(1)
            return session.cookies

    def parsing_elements(self, page):
        elements_list = page.select('.tr_r, .tr, .tr_sa', limit=None)
        data = list()
        for elements in elements_list:
            if elements['class'] == ['header']:
                continue
            if elements['class'] != ['tr_hr']:
                try:
                    article_number = elements.select(
                        '[class=td2]')[0].get_text()
                    brend = elements.select('[class=td3]')[0].get_text()
                    try:
                        name = elements.select('[class=td4]')[0].get_text(';').split(';')[
                            0].replace('\n', ' ').replace('\xa0', '')
                    except:
                        name = elements.select('[class=td4]')[0].get_text(
                            ';').replace('\n', ' ').replace('\xa0', '')
                    another_info = elements.select('[class=td5]')[
                        0].get_text(';')
                    price = elements.select('[class=td6]')[3].get_text('')
                    count_loc = elements.select('[class=td7]')[
                        0].get_text(';').split(';')
                    count = count_loc[0]
                    location = count_loc[1]

                    data.append(dict(
                        article_number=article_number,
                        brend=brend,
                        name=name,
                        store='Forum-auto',
                        another_info=another_info,
                        price=price,
                        count=count,
                        location=location
                    ))
                except Exception as e:
                    pass
        return data

    def parsing(self):
        response = self.post({
            'gr1': 999,
            'gr2': 0,
            'cat_num': self.value
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        login = soup.select('.leftside')
        if login != []:
            page = soup.find(attrs={'name': 'to_basket'})
            if page:
                return self.parsing_elements(page)
            else:
                return []
        else:
            self.set_cookies(False)
            return self.parsing()


class AutooptParsing():

    def __init__(self, value) -> None:
        self.cookies = self.set_cookies()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69'}
        self.value = value

    def get(self, value):
        session = requests.Session()
        url = 'https://www.autoopt.ru/search/index'
        return session.get(url, cookies=self.set_cookies(), params={'search': value}, timeout=None)

    def set_cookies(self, cookies=True):
        config = configparser.ConfigParser(interpolation=None)
        config.read('app/files/cookies.cfg')
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

    def page_parsing(self, soup):
        elements_list = soup.select('[class~=n-catalog-item__product]')
        data = list()
        for elements in elements_list:
            try:
                article_number = elements.select('[class~=n-catalog-item__article]')[0].select(
                    '[class~=n-catalog-item__click-copy]')[0].get_text(';')
                brend = elements.select('[class~=n-catalog-item__brand]')[0]
                if brend.select('a') != []:
                    brend = brend.select('a')[0].get_text()
                name = elements.select(
                    '[class~=n-catalog-item__name-link]')[0].get_text()
                price = elements.select(
                    '[class~=n-catalog-item__price-box]')[0].select('span')[1].get_text()
                count = elements.select('[class~=n-catalog-item__count-box]')[
                    0].select('[class~=fake]')[0].get_text(';').split(';')
                data.append(dict(
                    article_number=article_number,
                    brend=brend,
                    name=name.replace('\n', '').replace('  ', ''),
                    another_info='null',
                    store='Autoopt',
                    price=price,
                    count=count[0].replace('\n', '').replace('  ', ''),
                    location='null'
                ))
            except Exception as e:
                print(traceback.format_exc())
        return data

    def parsing(self):
        response = self.get(self.value)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select('[class~=username]') != []:
            return self.page_parsing(soup)
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
        config.read('app/files/cookies.cfg')
        cookie = response.headers.getlist(
            'Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")
        config['Autoopt'][cookie[0]] = cookie[1]
        with open('crossing_app/files/cookies.cfg', 'w') as cfg:
            config.write(cfg)
        return {cookie[0]: cookie[1]}


'''class AutokontinentParsing():

    def __init__(self, value) -> None:
        self.url = 'https://autokontinent.ru/'
        self.value = value

    def start(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
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
            driver.add_cookie({'name': 'ak_sid', 'value': config['Autokontinent']['ak_sid']})
            driver.add_cookie({'name': 'ak_user', 'value': config['Autokontinent']['ak_user']})
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
            for value in driver.get_cookies():
                config['Autokontinent'][value['name']] = value['value']
            with open('crossing_app/files/cookies.cfg', 'w') as cfg:
                    config.write(cfg)
            return driver

    def parsing(self):
        driver = self.login() 
        data = list()
        try: 
            driver.find_element('class name', 'h_login_state')
            print('True')
        except:
            print('False')
            driver = self.login(False)
        search = driver.find_element('id', 'h_seek_input')
        search.send_keys(self.value)
        sleep(1)
        search.send_keys(Keys.ENTER)
        sleep(1)
        all_elements = driver.find_elements('tag name', 'tr')
        for num, elements in enumerate(all_elements):
            if num == 0:
                continue
            position = elements.find_elements('tag name', 'td')
            try:
                name_brand = position[0].find_elements('tag name', 'div')
                name = name_brand[5].get_attribute('innerHTML')
                brend = name_brand[3].get_attribute('innerHTML')
                article = name_brand[2].get_attribute('innerHTML')
                count = position[2].get_attribute('innerHTML')
                location = position[4].get_attribute('innerHTML')
                if '<!--' in location:
                    location = location.split('<!--')[0]
                price = position[5].get_attribute('innerHTML')

            except:
                name_brand = all_elements[num-1].find_elements('tag name', 'div')
                name = name_brand[5].get_attribute('innerHTML')
                brend = name_brand[3].get_attribute('innerHTML')
                article = name_brand[2].get_attribute('innerHTML')
                count = position[1].get_attribute('innerHTML')
                location = position[3].get_attribute('innerHTML')
                if '<!--' in location:
                    location = location.split('<!--')[0]
                price = position[4].get_attribute('innerHTML')
            if count == '&gt;10 шт':
                count = '>10 шт.'
            data.append({
                'store': 'Autokontinent',
                'article_number': article,
                'brend': brend,
                'name': name,
                'price': price,
                'location': location,
                'count': count
                })
        return data

'''
if __name__ == '__main__':
    pass
