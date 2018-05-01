import os
import logging
from flask import Flask
from flask_cors import CORS

from api import controllers


def load_conf():
    config_path = 'resources/config.ini'
    conf = {}
    if os.path.isfile(config_path):
        import configparser
        _config = configparser.ConfigParser()
        _config.read(config_path)
        conf['db_host'] = _config.get('db', 'host')
        conf['db_port'] = _config.get('db', 'port')
        conf['db_username'] = _config.get('db', 'username')
        conf['db_passwd'] = _config.get('db', 'passwd')
        conf['db_name'] = _config.get('db', 'name')
        conf['unittest'] = _config.get('app', 'unitest')
    else:
        conf['db_host'] = os.environ('DB_HOST')
        conf['db_port'] = os.environ('DB_PORT')
        conf['db_username'] = os.environ('DB_USERNAME')
        conf['db_passwd'] = os.environ('DB_PASSWD')
        conf['db_name'] = os.environ('DB_NAME')
        conf['unittest'] = os.environ('UNITTEST')

    return conf


def init_app():
    app = Flask(__name__)
    CORS(app)

    # set logging
    log_lv = logging.DEBUG if app.config['DEBUG'] else logging.INFO

    app.config['app.conf'] = load_conf()
    app.register_blueprint(controllers)


def init_config(app):
    is_mock = bool(app.config['UNIT_TEST'])
