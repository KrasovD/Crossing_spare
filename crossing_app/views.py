import crochet
from flask import render_template, request, redirect, url_for, send_from_directory
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import configparser
from crossing_app import app, db
from crossing_app.spiders import Autokontinent_spiders, formation, ForumSpider, AutoOptSpider
from crossing_app.model import *
from crossing_app.function import export_to_excel

crochet.setup()
output_data = []
crawl_runner = CrawlerRunner()

@app.route('/', methods=['GET'])
def index():
    return render_template("home.html") 
        
@app.route('/search')
def search():
    search = request.args.get('search')
    def format_text(text):
        return text.replace('/','_').replace('-','_')
    data_list = list()
    for item in Autokontinent.query.filter(Autokontinent.article_number.like('%{}%'.format(format_text(search)))).limit(50).all():
        data_list.append(item)
        item.store = 'Autokontinent'
    for item in Autoopt.query.filter(Autoopt.article_number.like('%{}%'.format(format_text(search)))).limit(50).all():
        data_list.append(item)
        item.store = 'Autoopt'
    for item in Forum.query.filter(Forum.article_number.like('%{}%'.format(format_text(search)))).limit(50).all():
        data_list.append(item)
        item.store = 'Forum-auto'
    return render_template('table.html', 
                            spare = search,
                            desired_value=data_list
                            )


@app.route('/database')
def database():
    autokontinent_category = [
        {'name': 'Замки мотоцепей', 'url': 'https://autokontinent.ru/catalog_lock.php'},
        {'name': 'Инструменты', 'url': 'https://autokontinent.ru/catalog_tools.php'},
        {'name': 'Автохимия', 'url': 'https://autokontinent.ru/catalog_chemical.php'},
        {'name': 'Аккумуляторы', 'url': 'https://autokontinent.ru/catalog_battery.php'},
        {'name': 'Аксессуары', 'url': 'https://autokontinent.ru/catalog_accessories.php'},
        {'name': 'Багажники', 'url': 'https://autokontinent.ru/catalog_rack.php'},
        {'name': 'Лампы', 'url': 'https://autokontinent.ru/catalog_lamp.php'},
        {'name': 'Моторные масла', 'url': 'https://autokontinent.ru/catalog_oil.php'},
        {'name': 'Мотоцепи', 'url': 'https://autokontinent.ru/catalog_chain.php'},
        {'name': 'Омывающие жидкости', 'url': 'https://autokontinent.ru/catalog_washer.php'},
        {'name': 'Охлаждающие жидкости', 'url': 'https://autokontinent.ru/catalog_antifreeze.php'},
        {'name': 'Тормозные жидкости', 'url': 'https://autokontinent.ru/catalog_dot.php'},
        {'name': 'Фаркопы', 'url': 'https://autokontinent.ru/catalog_towbar.php'},
        {'name': 'Хомуты металлические', 'url': 'https://autokontinent.ru/catalog_mclamp.php'},
        {'name': 'Хомуты пластиковые', 'url': 'https://autokontinent.ru/catalog_pclamp.php'},
        {'name': 'Щетки стеклоочистителя', 'url': 'https://autokontinent.ru/catalog_wiper.php'},
        {'name': 'Эксплуатационные масла и жидкости', 'url': 'https://autokontinent.ru/catalog_liquid.php'},
    ]

    autoopt_category = [
        {'name': 'Отечественные грузовики', 'url': 'https://www.autoopt.ru/catalog/otechestvennye_gruzoviki/'},
        {'name': 'Европейские грузовики', 'url': 'https://www.autoopt.ru/catalog/evropeyskie_gruzoviki/'},
        {'name': 'Корейские грузовики', 'url': 'https://www.autoopt.ru/catalog/koreyskie_gruzoviki/'},
        {'name': 'Полуприцепы и оси', 'url': 'https://www.autoopt.ru/catalog/polupritsepy_i_osi/'},
        {'name': 'Коммерческий транспорт', 'url': 'https://www.autoopt.ru/catalog/kommercheskiy_transport/'},
        {'name': 'Легковые автомобили', 'url': 'https://www.autoopt.ru/catalog/legkovye_avtomobili/'},
        {'name': 'Автобусы', 'url': 'https://www.autoopt.ru/catalog/avtobusy/'},
        {'name': 'Тракторы и спецтехника', 'url': 'https://www.autoopt.ru/catalog/traktory_i_spetstekhnika/'},
        {'name': 'Коммунальная техника', 'url': 'https://www.autoopt.ru/catalog/kommunalnaya_tekhnika/'},
        {'name': 'Двигатели', 'url': 'https://www.autoopt.ru/catalog/dvigateli/'},
        {'name': 'Кабины, кузова и рамы', 'url': 'https://www.autoopt.ru/catalog/kabiny_kuzova_i_ramy/'},
    ]

    forum_category = [
        {'name': 'Аккумуляторы', 'value': '81'},
        {'name': 'Аксессуары', 'value': '83'},
        {'name': 'Антифриз', 'value': '106'},
        {'name': 'Домкраты', 'value': '108'},
        {'name': 'Доп.оборудование', 'value': '84'},
        {'name': 'Инструмент', 'value': '85'},
        {'name': 'Коврики салона', 'value': '80'},
        {'name': 'Крыло', 'value': '86'},
        {'name': 'Лампы', 'value': '87'},
        {'name': 'Масло', 'value': '88'},
        {'name': 'Мочевина', 'value': '107'},
        {'name': 'Отопители автономные', 'value': '89'},
        {'name': 'Фитинги', 'value': '75'},
        {'name': 'Химия', 'value': '91'},
        {'name': 'Щетки стеклоочистителей ', 'value': '92'},
        {'name': 'Электроника', 'value': '112'},
        {'name': 'Незамерзайка', 'value': '110'},
        {'name': 'Средства по уходу за авто', 'value': '115'},
    ]
    
    return render_template(
        'database.html', 
        autokontinent_category=autokontinent_category,
        autoopt_category=autoopt_category,
        forum_category=forum_category
        )


@app.route('/configuration', methods = ['POST'])
def configuration():
    if request.method == 'POST':
        autokontinent_values = request.form.getlist("autokontinent")
        autoopt_values = request.form.getlist("autoopt")
        forum_values = request.form.getlist("forum")
        config = configparser.ConfigParser()
        config['Autokontinent'] = {'url': str(autokontinent_values)}
        config['Autoopt'] = {'url': str(autoopt_values)}
        config['Forum'] = {'value': str(forum_values)}
        with open('crossing_app/files/configuration.cfg', 'w') as cfg:
            config.write(cfg)
        
        return redirect(url_for('database'))


@app.route("/scrape", methods = ['GET', 'POST'])
def scrape():
    if request.method == 'POST':
        spare = request.form['scrape']
        output_data.clear()
        scrape_with_crochet(spare=spare)
        time.sleep(12)
        desired_value, similar_value, avail = formation(data_spare=output_data, spare=spare)
        if avail:
            log = Log(
                spare=spare
            )
            db.session.add(log)
            db.session.commit()
        return render_template('table.html', 
                                spare = spare,
                                desired_value=desired_value, 
                                similar_value=similar_value
                                )
    if request.method == 'GET':
        return render_template('table.html')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')  

@app.route('/top_requests/<count>')
def view_top_requests(count):
    request = function.top_requests(db.session, count)
    return render_template('requests.html', 
                           count=count, 
                           top_requests=request, 
                           name_table='Топ запросов (месяц)'
                           )

@app.route('/latest_requests/<count>')
def view_latest_requests(count):
    request = function.latest_requests(db.session, count)
    return render_template('requests.html', 
                           count=count, 
                           top_requests=request,
                           name_table='Последние запросы'
                           )

@app.route('/export_to_excel', methods=['GET']) 
def export_to_excel():
    try:
        if output_data:
            function.export_to_excel(output_data)
            return send_from_directory('uploads', 'request_excel.xlsx')
    except Exception as e:
        print(e)
        return redirect(url_for(''))



@crochet.run_in_reactor
def scrape_with_crochet(spare):
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual_forum = crawl_runner.crawl(ForumSpider, spare = spare)
    eventual_autoopt = crawl_runner.crawl(AutoOptSpider, spare = spare)
    parser = Autokontinent_spiders(spare=spare)
    [output_data.append(el) for el in parser.parse()]
    return eventual_forum, eventual_autoopt

def _crawler_result(item, response, spider):
    output_data.append(dict(item))


if __name__== "__main__":
    app.run()