'''autokontinent_category = [
        ('Замки мотоцепей', 'https://autokontinent.ru/catalog_lock.php'),
        ('Инструменты', 'https://autokontinent.ru/catalog_tools.php'),
        ('Автохимия', 'https://autokontinent.ru/catalog_chemical.php'),
        ('Аккумуляторы', 'https://autokontinent.ru/catalog_battery.php'),
        ('Аксессуары', 'https://autokontinent.ru/catalog_accessories.php'),
        ('Багажники', 'https://autokontinent.ru/catalog_rack.php'),
        ('Лампы', 'https://autokontinent.ru/catalog_lamp.php'),
        ('Моторные масла', 'https://autokontinent.ru/catalog_oil.php'),
        ('Мотоцепи', 'https://autokontinent.ru/catalog_chain.php'),
        ('Омывающие жидкости', 'https://autokontinent.ru/catalog_washer.php'),
        ('Охлаждающие жидкости', 'https://autokontinent.ru/catalog_antifreeze.php'),
        ('Тормозные жидкости', 'https://autokontinent.ru/catalog_dot.php'),
        ('Фаркопы', 'https://autokontinent.ru/catalog_towbar.php'),
        ('Хомуты металлические', 'https://autokontinent.ru/catalog_mclamp.php'),
        ('Хомуты пластиковые', 'https://autokontinent.ru/catalog_pclamp.php'),
        ('Щетки стеклоочистителя', 'https://autokontinent.ru/catalog_wiper.php'),
        ('Эксплуатационные масла и жидкости', 'https://autokontinent.ru/catalog_liquid.php'),
    ]
'''

insert into parsing (category, value, store)
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
        ('AUTOOPT', 'Кабины, кузова и рамы', 'https://www.autoopt.ru/catalog/kabiny_kuzova_i_ramy/')


forum_category = [
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
        ('FORUM-AUTO', 'Средства по уходу за авто', '115'),
    ]

import app.model as model
from sqlalchemy import insert
