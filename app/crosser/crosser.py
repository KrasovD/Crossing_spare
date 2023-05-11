from flask import render_template, request, redirect, abort, send_from_directory, jsonify
from flask_login import login_required
from app.crosser import bp
from app import db
from sqlalchemy import func, select, update
from app.crosser.spiders import formation, ForumParsing, AutooptParsing
import time
from datetime import timedelta, datetime
from app.model import Spare_parts, Available, Log
import pandas
from threading import Thread

output_data = list()

def time_to_function(function):
    def wrapped(*args):
        start_time = time.perf_counter_ns()
        res = function(*args)
        print(time.perf_counter_ns() - start_time)
        return res
    return wrapped


@bp.route('/', methods=['GET'])
def index():
    return render_template("home.html")


@bp.route('/search')
@login_required
def search():
    search = request.args.get('search')

    def format_text(text):
        return text.replace('/', '_').replace('-', '_')
    similar_list = ''
    desired_list = db.session.query(Spare_parts, Available).join(Available, Spare_parts.id == Available.spare_parts_id).filter(
        Spare_parts.article_number.like('{}'.format(format_text(search)))).limit(50).all()
    if desired_list != []:
        db.session.add(Log(spare=search))
        db.session.commit()
    for spare, avail in desired_list:
        if spare.name == 'null':
            similar_list = db.session.query(Spare_parts, Available).join(Available, Spare_parts.id == Available.spare_parts_id).filter(
                Spare_parts.category == spare.category, func.similarity(Spare_parts.another_info, spare.another_info) > 0.5).limit(15).all()
        else:
            # db.session.execute('pg_trgm.similarity_threshold (0.7)')
            similar_list = db.session.query(Spare_parts, Available).join(Available, Spare_parts.id == Available.spare_parts_id).filter(
                Spare_parts.category == spare.category, func.similarity(Spare_parts.name, spare.name) > 0.5).limit(15).all()

        similar_article = [
            spare.article_number for spare, avail in similar_list]
        if spare.article_number in similar_article:
            similar_list.pop(similar_article.index(spare.article_number))
    output_data.extend(desired_list)
    output_data.extend(similar_list)
    return jsonify({
        'data': render_template('search_result.html',
                                spare=search,
                                desired_value=desired_list,
                                similar_value=similar_list
                                ),
        'spare': search
    })


@bp.route("/scrape", methods=['GET', 'POST'])
@login_required
def scrape():
    if request.method == 'POST':

        spare = request.json['search']
        output_data.clear()

        def parse_forum():
            forum = ForumParsing(spare)
            [output_data.append(el) for el in forum.parsing()]

        def parse_autoot():
            autoopt = AutooptParsing(spare)
            [output_data.append(el) for el in autoopt.parsing()]
        # thread1 = Thread(target=parse_forum)
        # thread2 = Thread(target=parse_autoot)
        start_time = time.perf_counter()
        parse_autoot()
        parse_forum()
        '''thread1.run()
        thread2.run()
        while True:
            if thread1.is_alive() == True and thread2.is_alive() == True:
                time.sleep(0.2)
            else:
                break'''
        time_request = time.perf_counter() - start_time

        desired_value, similar_value, avail = formation(
            data_spare=output_data, spare=spare)
        if avail:
            log = Log(
                spare=spare
            )
            db.session.add(log)
            db.session.commit()
        return jsonify({
            'data': render_template(
                'parsing_result.html',
                time_request=round(
                    time_request, 1),
                spare=spare,
                desired_value=desired_value,
                similar_value=similar_value)
        })
    if request.method == 'GET':
        return render_template('parsing_result.html')


@bp.errorhandler(500)
def server_error(e):
    return render_template('500.html')


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@bp.errorhandler(401)
def not_auth(e):
    return render_template('401.html')


@bp.route('/top_requests/<count>')
@login_required
def view_top_requests(count):
    month_ago = datetime.today() - timedelta(days=30)
    data = db.session.query(Log.spare, func.count(Log.spare)).filter(Log.datetime > month_ago).group_by(
        Log.spare).order_by(func.count(Log.spare).desc()).limit(int(count)).all()
    return render_template('requests.html',
                           count=count,
                           top_requests=data,
                           name_table='Топ запросов (месяц)'
                           )


@bp.route('/latest_requests/<count>')
@login_required
def view_latest_requests(count):
    month_ago = datetime.today() - timedelta(days=30)
    data = db.session.query(Log.spare, func.to_char(Log.datetime, 'DD.mm.yy HH24:MM:SS')).filter(
        Log.datetime > month_ago).order_by(Log.datetime.desc()).limit(int(count)).all()
    return render_template('requests.html',
                           count=count,
                           top_requests=data,
                           name_table='Последние запросы'
                           )


@bp.route('/export_to_excel', methods=['POST'])
@login_required
def export_to_excel():
    try:
        if output_data:
            try:
                df_spare = pandas.DataFrame(
                    data=[
                        (avail.store,
                         spare.article_number,
                         spare.brend,
                         spare.name,
                         avail.price,
                         avail.location,
                         avail.count) for spare, avail in output_data],
                    columns=('store', 'article', 'brend', 'name',
                             'price', 'location', 'count')
                )
            except:
                df_spare = pandas.DataFrame(
                    data=[
                        (spare['store'],
                         spare['article_number'],
                         spare['brend'],
                         spare['name'],
                         spare['price'],
                         spare['location'],
                         spare['count']) for spare in output_data],
                    columns=('store', 'article', 'brend', 'name',
                             'price', 'location', 'count')
                )
            df_spare.to_excel('app/uploads/request_excel.xlsx')
            return send_from_directory('uploads', 'request_excel.xlsx')
        else:
            return abort(500)
    except Exception as e:
        print(e)
        return abort(500)
