import pandas
import model
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

def export_to_excel(data, spare):

    data_dict = {
        'Магазин': [],
        'Артикль': [], 
        'Бренд': [], 
        'Название': [], 
        'Цена': [], 
        'Склад': [], 
        'Количество': []
    }
    for row in data:
        data_dict['Магазин'].append(row['store'])
        data_dict['Артикль'].append(row['article'])
        data_dict['Бренд'].append(row['brend'])
        data_dict['Название'].append(row['name'])
        data_dict['Цена'].append(row['price'])
        data_dict['Склад'].append(row['location'])
        data_dict['Количество'].append(row['count'])

    df = pandas.DataFrame(data_dict)
    return df.to_excel('uploads/request_excel.xlsx')


def top_requests(session, count):
    month_ago = datetime.today() - timedelta(days=30)
    data = select(model.Log.spare, func.count(model.Log.spare)).filter(model.Log.datetime > month_ago).group_by(model.Log.spare).order_by(func.count(model.Log.spare).desc()).limit(int(count))
    return session.execute(data).all()
def latest_requests(session, count):
    data = select(model.Log.spare).order_by(model.Log.datetime.desc()).limit(int(count))
    return session.execute(data).all()

if __name__ == '__main__':
    engine = create_engine("sqlite:///instance/log.db", echo=True)
    session = Session(engine)
    print(top_requests(session, 1))
