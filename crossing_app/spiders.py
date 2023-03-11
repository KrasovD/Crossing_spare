import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep

from crossing_app.config import *

def formation(data_spare, spare):
    desired_value = list()
    similar_value = list()
    avail = False
    store = ('Autoopt', 'AutoKontinent', 'Forum-auto')
    def raw_string(string):
        return (string.replace('_', '').replace(' ', '').replace('-', '').replace('/', '')).lower()

    for data in data_spare:
        if raw_string(spare) == raw_string(data['article']) or data['article'] == 'Отсутствует': 
            desired_value.append(data)
        else:
            similar_value.append(data)
    for data in desired_value:
        if data['article'] != 'Отсутствует':
            avail = True
    for st in store:
        if st not in [data['store'] for data in desired_value]:
                desired_value.append({
                    'store': st,
                    'article': 'Отсутствует',
                    'brend': '',
                    'name': '',
                    'price': '',
                    'location': '',
                    'count': ''
                })
    return desired_value, similar_value, avail
    
            
    
class ForumSpider(scrapy.Spider):
    name = 'Forum-auto'
    start_urls = ['https://itrade.forum-auto.ru/shop/index']

    def __init__(self, spare='', **kwargs): # The category variable will have the input URL.
        self.spare = spare
        super().__init__(**kwargs)

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formname='enter',
            formdata={'login': forum_auto_login, 'password': forum_auto_password},
            callback=self.after_login
        )


    def after_login(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formname='search',
            formdata={'cat_num': self.spare},
            callback=self.parsing
            )
        
    def parsing(self, response):
        for res in response.xpath('//div[@id="effect"]//tr'):
            data = res.get()
            article = scrapy.Selector(text=data).xpath('//td[@class="td2"]/text()').get()
            brend = scrapy.Selector(text=data).xpath('//td[@class="td3"]/text()').get()
            name = scrapy.Selector(text=data).xpath('//td[@class="td4"]/text()').get()
            use = scrapy.Selector(text=data).xpath('//td[@class="td5"]/text()').get()
            price = scrapy.Selector(text=data).xpath('//td[@class="td6"]//nobr/text()').getall()
            try:
                price = price[1]
            except:
                pass
            count = scrapy.Selector(text=data).xpath('//td[@class="td7"]//b/text()').get()
            location = scrapy.Selector(text=data).xpath('//td[@class="td7"]/text()').get()
            if article != None:
                yield {
                    'store': self.name,
                    'article': article,
                    'brend': brend,
                    'name': name,
                    'price': price,
                    'location': location,
                    'count': count
                    }
                        

class AutoOptSpider(scrapy.Spider):
    name = 'Autoopt'
    start_urls = ['https://www.autoopt.ru/']

    def __init__(self, spare='', **kwargs):
        self.spare = spare
        super().__init__(**kwargs)


    def parse(self, response, **kwargs):
        token = response.xpath('//input[@name="_csrf"]/@value').get()
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form[@id="login-form"]',
            formdata={'LoginForm[username]': autoopt_login,
                      'LoginForm[password]': autoopt_password,
                      '_csrf': token,
                      },
            callback=self.search
        )

    def search(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form',
            formdata={
                'search': self.spare
            },
            callback=self.parsing
        )

    def parsing(self, response):
        for res in response.xpath('//div[@class="n-catalog-item relative grid-item n-catalog-item__product"]'):
            data = res.get()
            code = scrapy.Selector(text=data).xpath('//span[@class="string bold n-catalog-item__click-copy"]/text()').get()
            get_brend = scrapy.Selector(text=data).xpath('//div[@class="n-catalog-item__brand d-none d-md-table-cell"]/text()').get()
            article= scrapy.Selector(text=data).xpath('//span[@class="string bold nowrap n-catalog-item__click-copy"]/text()').get()
            get_name = scrapy.Selector(text=data).xpath('//a[@class="n-catalog-item__name-link actions name-popover"]/text()').getall()
            get_price = scrapy.Selector(text=data).xpath('//div[@class="n-catalog-item__price-box col-12 col-md pr-0 mb-2"]/product-list-prices').get()
            get_count = scrapy.Selector(text=data).xpath('//a[@class="js-popover-wrapper popover-warehouses"]/span/span/text()').get()
            try:
                brend = (get_brend.replace('  ', '')).replace('\n', '')
                if brend == '':
                    get_brend = scrapy.Selector(text=data).xpath('//a[@class="actions brand-popover"]/text()').get()
                    brend = (get_brend.replace('  ', '')).replace('\n', '')
            except:
                brend = '-'
            name = (' '.join(get_name[1:3])).replace('  ', '')
            prices = get_price.split(',')
            price = (prices[4].split(':')[1] + ','+prices[5]).replace('"', '')
            try:
                count = (get_count.replace('  ', '')).replace('\n', '')
            except:
                count = scrapy.Selector(text=data).xpath('//a[@class="js-popover-wrapper popover-warehouses"]/span/text()').get()
            
            if article != None:
                yield {
                    'store': self.name,
                    'article': article, 
                    'brend': brend, 
                    'name': name,
                    'price': price, 
                    'location': '',
                    'count': count
                }


class Autokontinent_spiders():
    url = 'https://autokontinent.ru'
    name = 'AutoKontinent'
    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        return webdriver.Chrome(chrome_options=options, executable_path='chromedriver')

    def __init__(self, spare):
        self.spare = spare

    def parse(self):
        try:
            driver = self.run()
        except:
            pass
        try:
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
            print('Залогинился')
        except:
            print('Ошибка авторизации')
        try:     
            search = driver.find_element('id', 'h_seek_input')
            search.send_keys(self.spare)
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
                yield {
                        'store': self.name,
                        'article': article,
                        'brend': brend,
                        'name': name,
                        'price': price,
                        'location': location,
                        'count': count
                        }
        except:
            pass



if __name__ == '__main__':
    open("items.json","w").close()
    process = CrawlerProcess(
        settings={"FEEDS": {"items.json": {"format": "json"}}}
        )
    process.crawl(ForumSpider, spare='SRS 83SA40')
    process.start()