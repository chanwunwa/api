import time

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import delete, insert, update


class BaseModel:
    def __init__(self, engine, metadata, table, role='reader'):
        self.engine = engine
        self.metadata = metadata
        self.table = table
        self.role = role

    def execute(self, stmt):
        return self.engine.execute(stmt)

    def raw_insert(self, row):
        assert 'writer' == self.role
        row['updated_ts'] = int(time.time())
        stmt = insert(self.table, row)
        return self.execute(stmt)

    def raw_update(self, where, row):
        assert 'writer' == self.role
        row['updated_ts'] = int(time.time())
        stmt = update(self.table). \
            where(where). \
            values(row)
        return self.execute(stmt)

    def raw_upsert(self, row):
        assert 'writer' == self.role
        row['updated_ts'] = int(time.time())
        stmt = Upsert(self.table, row)
        return self.execute(stmt)

    def raw_delete(self, where):
        assert 'writer' == self.role
        stmt = delete(self.table). \
            where(where)
        return self.execute(stmt)


def new_engine_and_metadata(db_conf, db_settings=None):
    settings = {
        'max_overflow': -1,
        'pool_size': 8,
        'pool_recycle': 1024,
        'pool_timeout': 300,
    }

    if db_settings is not None:
        settings.update(db_settings)

    db_port = 3306
    if 'localhost' == db_conf['host'] or '127.0.0.1' == db_conf['host']:
        db_port = 13306

    if 'port' in db_conf:
        db_port = db_conf['port']

    db_connection_str = 'mysql://{}:{}@{}:{}/{}?binary_prefix=True'.format(
        db_conf['user'],
        db_conf['password'],
        db_conf['host'],
        db_port,
        db_conf['db_name']
    )

    engine = sqlalchemy.create_engine(db_connection_str, **settings)
    metadata = MetaData(bind=engine)

    return engine, metadata


class Upsert(sqlalchemy.sql.expression.Insert):
    pass


@compiles(Upsert, "mysql")
def mysql_compile_upsert(insert_stmt, compiler, **kwargs):
    preparer = compiler.preparer
    keys = insert_stmt.parameters.keys()

    insert = compiler.visit_insert(insert_stmt, **kwargs)

    ondup = 'ON DUPLICATE KEY UPDATE'

    updates = ', '.join(
        '{} = VALUES({})'.format(preparer.format_column(c), preparer.format_column(c))
        for c in insert_stmt.table.columns
        if c.name in keys
    )
    upsert = ' '.join((insert, ondup, updates))
    return upsert


@compiles(Upsert, "sqlite")
def sqlite_compile_upsert(insert_stmt, compiler, **kwargs):
    insert = compiler.visit_insert(insert_stmt, **kwargs)
    insert_or_replace = insert.replace("INSERT INTO", "INSERT OR REPLACE INTO", 1)

    return insert_or_replace
