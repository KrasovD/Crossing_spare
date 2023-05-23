from app.parser import bp
from app import db 
from datetime import datetime
from flask import render_template, send_from_directory, request, redirect, url_for, jsonify
from flask_login import login_required
from sqlalchemy import select
import pandas, csv
from app.model import Available, Spare_parts, Parsing


@bp.route('/database', methods=['GET', 'POST'])
@login_required
def database():
    catalog = db.session.query(Parsing)
    if request.method == 'GET':
        try:
            last_update = catalog.filter(Parsing.date_update!=None).order_by(Parsing.date_update.desc()).first().date_update
        except:
            last_update = 'Обновлений не было'
        return render_template('database.html', catalog=catalog.all(), last_update=last_update)
    if request.method == 'POST':
        values = request.get_json()
        all_configuration = catalog.all()
        for configuration in all_configuration:
                if [configuration.store, configuration.value] not in values:
                    configuration.status = False 
                else:
                    configuration.status = True
        db.session.commit()
        return jsonify({'data':True})

@bp.route('/database/download/<format>', methods=['POST'])
def db_download(format):
        stmt = select(Spare_parts, Available).join(
                Available, 
                Spare_parts.id==Available.spare_parts_id
                ).execution_options(yield_per=10)  
        if format == 'csv':      
            with open('app/uploads/database.csv', 'w', encoding='utf-8') as csv_db:
                csvwriter = csv.writer(csv_db, delimiter=';')
                csvwriter.writerow(['store', 'article_number','brend', 'name', 'price', 'location', 'count'])
                for spare, avail in db.session.execute(stmt):
                    try:
                        csvwriter.writerow([avail.store, spare.article_number, spare.brend, spare.name, avail.price, avail.location, avail.count])
                    except Exception as e:
                        print(e)
            return send_from_directory('uploads','database.csv')
        if format == 'xls':
            df_spare = pandas.DataFrame(
                data=[
                    (avail.store, 
                    spare.article_number, 
                    spare.brend, 
                    spare.name, 
                    avail.price, 
                    avail.location, 
                    avail.count) for spare, avail in db.session.execute(stmt)],
                columns=('store', 'article', 'brend', 'name', 'price', 'location', 'count')
                )
            df_spare.to_excel('crossing_app/uploads/database.xlsx')
            return send_from_directory('uploads', 'database.xlsx')


@bp.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@bp.errorhandler(401)
def not_auth(e):
    return render_template('401.html')
