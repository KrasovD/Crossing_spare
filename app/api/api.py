from flask import jsonify
from app import db, app
from sqlalchemy import select
from app.model import Spare_parts, Available

def serialize_spare():
    spares_list = list()
    stmt = select(Spare_parts, Available).join(
                Available, 
                Spare_parts.id==Available.spare_parts_id
                ).execution_options(yield_per=10) 
    spares = db.session.execute(stmt)
    for spare, avail in spares:
        spare = dict(
            name = spare.name,
            article_number = spare.article_number,
            another_info = spare.another_info,
            brend = spare.brend,
            category = spare.category,
            count = avail.count,
            price = avail.price,
            location = avail.location,
            store = avail.store
        )
        spares_list.append(spare)
    return spares_list


@app.route('/api/all_spare', methods=['GET'])
def get_spare():
    return jsonify({'spares': serialize_spare()})