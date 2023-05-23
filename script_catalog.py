insert_autoopt = '''insert into parsing (category, value, store)
values 
('AUTOOPT', 'Отечественные грузовики', 'https://www.autoopt.ru/catalog/otechestvennye_gruzoviki/'),
        ('AUTOOPT', 'Европейские грузовики', 'https://www.autoopt.ru/catalog/evropeyskie_gruzoviki/'),
        ('AUTOOPT', 'Корейские грузовики', 'https://www.autoopt.ru/catalog/koreyskie_gruzoviki/'),
        ('AUTOOPT', 'Полуприцепы и оси', 'https://www.autoopt.ru/catalog/polupritsepy_i_osi/'),
        ('AUTOOPT', 'Коммерческий транспорт', 'https://www.autoopt.ru/catalog/kommercheskiy_transport/'),
        ('AUTOOPT', 'Легковые автомобили', 'https://www.autoopt.ru/catalog/legkovye_avtomobili/'),
        ('AUTOOPT', 'Автобусы', 'https://www.autoopt.ru/catalog/avtobusy/'),
        ('AUTOOPT', 'Тракторы и спецтехника', 'https://www.autoopt.ru/catalog/traktory_i_spetstekhnika/'),
        ('AUTOOPT', 'Коммунальная техника', 'https://www.autoopt.ru/catalog/kommunalnaya_tekhnika/'),
        ('AUTOOPT', 'Двигатели', 'https://www.autoopt.ru/catalog/dvigateli/'),
        ('AUTOOPT', 'Кабины, кузова и рамы', 'https://www.autoopt.ru/catalog/kabiny_kuzova_i_ramy/');
'''

insert_forum = '''insert into parsing (category, value, store)
values 
        ('FORUM-AUTO', 'Аккумуляторы', '81'),
        ('FORUM-AUTO', 'Аксессуары', '83'),
        ('FORUM-AUTO', 'Антифриз', '106'),
        ('FORUM-AUTO', 'Домкраты', '108'),
        ('FORUM-AUTO', 'Доп.оборудование', '84'),
        ('FORUM-AUTO', 'Инструмент', '85'),
        ('FORUM-AUTO', 'Коврики салона', '80'),
        ('FORUM-AUTO', 'Крыло', '86'),
        ('FORUM-AUTO', 'Лампы', '87'),
        ('FORUM-AUTO', 'Масло', '88'),
        ('FORUM-AUTO', 'Мочевина', '107'),
        ('FORUM-AUTO', 'Отопители автономные', '89'),
        ('FORUM-AUTO', 'Фитинги', '75'),
        ('FORUM-AUTO', 'Химия', '91'),
        ('FORUM-AUTO', 'Щетки стеклоочистителей ', '92'),
        ('FORUM-AUTO', 'Электроника', '112'),
        ('FORUM-AUTO', 'Незамерзайка', '110'),
        ('FORUM-AUTO', 'Средства по уходу за авто', '115');
'''

from sqlalchemy import insert, select, create_engine, text
from app.config import password_db
engine = create_engine("postgresql+psycopg2://crossing_db:{}@localhost/crossing_db".format(password_db))

with engine.connect() as conn:
    item = text(insert_autoopt)
    item2 = text(insert_forum)
    conn.execute(item)
    conn.execute(item2) 


