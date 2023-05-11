from parsing import *
from app.model import Parsing
from app.config import password_db

session = Session(create_engine("postgresql+psycopg2://crossing_db:{}@localhost/crossing_db".format(password_db)))

def run_parsing(value, Parser: classmethod):
    try:
        element = session.query(Parsing).filter(Parsing.value==value).first()
        element.status = True
        session.commit()
        parse = Parser(value)
        parse.parsing()
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
    values = [value.split(':') for value in input().split(';')]
    while True:
        if datetime.now().hour > 18:
            for value in values:
                if value[0] == 'FORUM-AUTO':
                    run_parsing(value[1], ForumParsing)
                if value[1] == 'AUTOOPT':
                    run_parsing(value[1], AutooptParsing)
            break
        sleep(500)

