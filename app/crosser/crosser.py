from flask import render_template, request, abort, send_from_directory, jsonify
from flask_login import login_required
from app.crosser import bp
from app import db
from sqlalchemy import func
from app.crosser.spiders import formation, ForumParsing, AutooptParsing
import time
from datetime import timedelta, datetime
from app.model import Spare_parts, Available, Log, Crossing
import pandas

output_data = list()


def time_to_function(function):
    def wrapped(*args):
        start_time = time.perf_counter_ns()
        res = function(*args)
        return res
    return wrapped


@bp.route('/', methods=['GET'])
def index():
    return render_template("home.html")



@bp.route("/scrape", methods=['GET', 'POST'])
@login_required
def scrape():
    if request.method == 'POST':
        search = request.json['search']
        db_search = db.session.query(Spare_parts, Crossing).join(Crossing, Spare_parts.id == Crossing.id_spare).filter(
            Spare_parts.article_number == search).all()
        if db_search:
            similar_value = []
            start_time = time.perf_counter()
            desired_value = db.session.query(
                Spare_parts.brend,
                Spare_parts.name,
                Spare_parts.article_number,
                Available.count,
                Available.location,
                Available.price,
                Available.store,
                Available.data_update).join(Available, Spare_parts.id == Available.spare_parts_id).filter(
                Spare_parts.article_number == search).order_by(Available.price).all()
            desired_check = [value.store for value in desired_value]
            if 'Forum-auto' not in desired_check:
                desired_value.append({'store': 'Forum-auto', 'article_number':'Отсутствует'})
            if 'Autoopt' not in desired_check:
                desired_value.append({'store': 'Autoopt', 'article_number':'Отсутствует'})
            for spare, cross in db_search:
                similar_value.extend(db.session.query(
                    Spare_parts.brend,
                    Spare_parts.name,
                    Spare_parts.article_number,
                    Available.count,
                    Available.location,
                    Available.price,
                    Available.store,
                    Available.data_update).join(Available, Spare_parts.id == Available.spare_parts_id).filter(
                    Spare_parts.id == cross.id_cross).order_by(Available.price).all())
            time_request = time.perf_counter() - start_time
            if desired_value:
                log = Log(
                    spare=search
                )
                db.session.add(log)
                db.session.commit()

        else:
            output_data.clear()
            forum = ForumParsing(search)
            autoopt = AutooptParsing(search)
            start_time = time.perf_counter()
            [output_data.append(el) for el in forum.parsing()]
            [output_data.append(el) for el in autoopt.parsing()]

            time_request = time.perf_counter() - start_time

            desired_value, similar_value, avail = formation(
                data_spare=output_data, spare=search)
            if avail:
                log = Log(
                    spare=search
                )
                db.session.add(log)
                db.session.commit()
        return jsonify({
            'data': render_template(
                'parsing_result.html',
                time_request=round(
                    time_request, 1),
                spare=search,
                db_search = db_search,
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
