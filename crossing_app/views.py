import crochet
from flask import render_template, request, redirect, url_for, send_from_directory
from sqlalchemy import func
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
from datetime import timedelta
import configparser
from crossing_app import app, db
from crossing_app.spiders import Autokontinent_spiders, formation, ForumSpider, AutoOptSpider
from crossing_app.model import *
from crossing_app.function import export_to_excel
import pandas
import csv

crochet.setup()
output_data = []
crawl_runner = CrawlerRunner()

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


@app.route('/', methods=['GET'])
def index():
    return render_template("home.html") 
        
@app.route('/search')
def search():
    search = request.args.get('search')
    def format_text(text):
        return text.replace('/','_').replace('-','_')
    similar_list = ''
    desired_list = db.session.query(Spare_parts, Available).join(Available, Spare_parts.id==Available.spare_parts_id).filter(Spare_parts.article_number.like('%{}%'.format(format_text(search)))).limit(50).all()
    if desired_list != []:
        db.session.add(Log(spare=search))
        db.session.commit()
    for spare, avail in desired_list:
        #db.session.execute('pg_trgm.similarity_threshold (0.7)')
        similar_list = db.session.query(Spare_parts, Available).join(Available, Spare_parts.id==Available.spare_parts_id).filter(Spare_parts.category == spare.category, func.similarity(Spare_parts.name, spare.name) > 0.5).limit(15).all()
    return render_template('result_search.html', 
                            spare = search,
                            desired_value=desired_list,
                            similar_value=similar_list
                            )


@app.route('/database')
def database():
    config = configparser.ConfigParser()
    config.read('crossing_app/files/details.cfg')
    date_parsing = config['Parsing']['date_parsing']

    if date_parsing == datetime.now().date().strftime('%d.%m'):
        return render_template(
            'database.html', 
            date_parsing=date_parsing,
            parsing=False
            )
    else:
        return render_template(
            'database.html', 
            parsing=True,
            date_parsing=date_parsing,
            autokontinent_category=autokontinent_category,
            autoopt_category=autoopt_category,
            forum_category=forum_category
            )

@app.route('/database/download/<format>', methods=['POST'])
def db_download(format):
    if request.method == 'POST':
        if format == 'csv':
            spare = db.session.query(Spare_parts).join(Available, Spare_parts.id==Available.spare_parts_id).all()
            with open('crossing_app/uploads/database.csv') as csv_db:
                csvwriter = csv.writer(csv_db, delimiter=';')
                csvwriter.writerow([])
                for element in spare:
                    csvwriter.writerow([])
            return send_from_directory('crossing_app/uploads', 'database.csv')
        if format == 'xls':
            spare = db.session.query(Spare_parts).join(Available, Spare_parts.id==Available.spare_parts_id).all()
            data_dict = dict()
            headers = ['Магазин', 'Артикул', 'Бренд', 'Название', 'Цена', 'Склад', 'Количество']
            for num in range(headers):
                data_dict[headers[num]] = list()
            for row in spare:
                data_dict['Магазин'].append(row['store'])
                data_dict['Артикль'].append(row['article'])
                data_dict['Бренд'].append(row['brend'])
                data_dict['Название'].append(row['name'])
                data_dict['Цена'].append(row['price'])
                data_dict['Склад'].append(row['location'])
                data_dict['Количество'].append(row['count'])

            df = pandas.DataFrame(data_dict)
            df.to_excel('crossing_app/uploads/database.xlsx')
            return send_from_directory('crossing_app/uploads', 'database.xlsx')


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
    month_ago = datetime.today() - timedelta(days=30)
    data = db.session.query(Log.spare, func.count(Log.spare)).filter(Log.datetime > month_ago).group_by(Log.spare).order_by(func.count(Log.spare).desc()).limit(int(count)).all()
    return render_template('requests.html', 
                           count=count, 
                           top_requests=data, 
                           name_table='Топ запросов (месяц)'
                           )

@app.route('/latest_requests/<count>')
def view_latest_requests(count):
    month_ago = datetime.today() - timedelta(days=30)
    data = db.session.query(Log.spare, func.to_char(Log.datetime, 'DD.mm.yy HH:MM:SS')).filter(Log.datetime > month_ago).order_by(Log.datetime.desc()).limit(int(count)).all()
    return render_template('requests.html', 
                           count=count, 
                           top_requests=data,
                           name_table='Последние запросы'
                           )

@app.route('/export_to_excel', methods=['GET']) 
def export_to_excel():
    try:
        if output_data:
            function.export_to_excel(output_data)
            return send_from_directory('crossinf_app/uploads', 'request_excel.xlsx')
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