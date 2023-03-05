import crochet
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask import Flask , render_template, request, redirect, url_for, send_from_directory
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time

import spiders
import function

app = Flask(__name__)

bootstrap = Bootstrap5(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///log.db"
db.init_app(app)

import model

crochet.setup()
output_data = []
crawl_runner = CrawlerRunner()

@app.route('/')
def index():
	return render_template("home.html") 

@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.form['url'] 
        global SPARE
        SPARE = s
        output_data.clear()


        return redirect(url_for('scrape'))


@app.route("/scrape")
def scrape():
    try:
        parser = spiders.Autokontinent(spare=SPARE)
        [output_data.append(el) for el in parser.parse()]
        scrape_with_crochet(spare=SPARE)
        time.sleep(5)
        desired_value, similar_value, avail = spiders.formation(data_spare=output_data, spare=SPARE)
        if avail:
            spare = model.Log(
                spare=SPARE
            )
            db.session.add(spare)
            db.session.commit()
        return render_template('table.html', 
                            spare = SPARE,
                            desired_value=desired_value, 
                            similar_value=similar_value
                            )
    except Exception as e:
        print(e)
        redirect(url_for(''))

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
            function.export_to_excel(output_data, SPARE)
            return send_from_directory('uploads', 'request_excel.xlsx')
    except Exception as e:
        print(e)
        return redirect(url_for(''))



@crochet.run_in_reactor
def scrape_with_crochet(spare):
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual_forum = crawl_runner.crawl(spiders.ForumSpider, spare = spare)
    eventual_autoopt = crawl_runner.crawl(spiders.AutoOptSpider, spare = spare)
    return eventual_forum, eventual_autoopt

def _crawler_result(item, response, spider):
    output_data.append(dict(item))


if __name__== "__main__":
    app.run()