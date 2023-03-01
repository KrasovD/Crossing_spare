import scrapy
from scrapy.crawler import CrawlerProcess
import config

DATA = ''

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
            formdata={'login': config.forum_auto_login, 'password': config.forum_auto_password},
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
        if response.xpath('//div[@id="effect"]//tr') == []:
            yield {
                    'store': self.name,
                    'article': 'Отсутствует', 
                    'brend': '-', 
                    'name': '-',
                    'price': '-', 
                    'location': '-',
                    'count': '-'
                } 
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
            formdata={'LoginForm[username]': config.autoopt_login,
                      'LoginForm[password]': config.autoopt_password,
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
        if response.xpath('//div[@class="n-catalog-item relative grid-item n-catalog-item__product"]') == []:
            yield {
                    'store': self.name,
                    'article': 'Отсутствует', 
                    'brend': '-', 
                    'name': '-',
                    'price': '-', 
                    'location': '-',
                    'count': '-'
                } 
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
                    'location': '-',
                    'count': count
                }



if __name__ == '__main__':
    open("items.json","w").close()
    process = CrawlerProcess(
        settings={"FEEDS": {"items.json": {"format": "json"}}}
        )
    process.crawl(ForumSpider, spare='SRS 83SA40')
    process.start()