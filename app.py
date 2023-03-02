import crochet
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask import Flask , render_template, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time

import spiders

app = Flask(__name__)

bootstrap = Bootstrap5(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///log.db"
db.init_app(app)
#SQLAlchemy(app)
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
    parser = spiders.Autokontinent(spare=SPARE)
    [output_data.append(el) for el in parser.parse()]
    scrape_with_crochet(spare=SPARE)
    time.sleep(5) 
    desired_value = list()
    similar_value = list()
    avail = False
    for data in output_data:
        if SPARE in data['article'] or data['article'] == 'Отсутствует': 
            desired_value.append(data)
        else:
            similar_value.append(data)
    for data in desired_value:
        if data['article'] != 'Отсутствует':
            avail = True
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