from parsing import *
from app.model import Parsing
from app.config import password_db

session = Session(create_engine("postgresql+psycopg2://crossing_db:{}@localhost/crossing_db".format(password_db)))

def run_parsing(value, Parser):
    try:
        parse = Parser(value)
        parse.parsing()
        element = session.query(Parsing).filter(Parsing.value==value).first()
        element.date_update = datetime.now().date()
        element.count_all = parse.count_elements
        element.count_success = parse.count_success
        element.status = False
        session.commit()
    except:
        element = session.query(Parsing).filter(Parsing.value==value).first()
        element.status = False
        session.commit()
    
if __name__ == '__main__':
    while True:
        if datetime.now().hour > 19:
            values = session.query(Parsing).filter(Parsing.status==True).all()
            for value in values:
                if value.store == 'FORUM-AUTO':
                    run_parsing(value.value, ForumParsing)
                if value.store == 'AUTOOPT':
                    run_parsing(value.value, AutooptParsing)
        sleep(500)

