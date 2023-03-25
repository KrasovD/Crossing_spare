import configparser
import ast

from crossing_app.parser import *

def run_parsing(values, name: str, parser):
    config = configparser.ConfigParser()
    config.read('crossing_app/files/log_parsing.cfg')
    for value in values:
        try:
            parse = parser(value)
            parse.parsing()
            config[name] = {value : '%d in %d, date: %s'% (
                parse.count_success,
                parse.count_success,
                datetime.now().strftime('%d.%m'))
                }
            with open('crossing_app/files/log_parsing.cfg', 'w') as cfg:
                config.write(cfg)
        except Exception as e:
            config[name] = {'url': value,
                                 'Ошибка': e}
            with open('crossing_app/files/log_parsing.cfg', 'w') as cfg:
                config.write(cfg)

    
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('crossing_app/files/configuration.cfg')
    forum = ast.literal_eval(config.get('Forum', 'value'))
    autoopt = ast.literal_eval(config.get('Autoopt', 'url')) 
    kontinent =  ast.literal_eval(config.get('Autokontinent', 'url'))
    run_parsing(forum, 'Forum', ForumParsing)
    #run_parsing(kontinent, 'Autokontinent', AutokontinentSpider)
    #run_parsing(autoopt, 'AutoOpt', AutooptParsing)
