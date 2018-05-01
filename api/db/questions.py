
from sqlalchemy import JSON, Column, INT, TEXT, TIMESTAMP
from sqlalchemy import Table
from sqlalchemy.sql.expression import select
from api.db import BaseModel


class Questions(BaseModel):

    def __init__(self, engine, metadata, role='reader'):
        table = Table(
            'questions',
            metadata,
            Column('id', INT, primary_key=True, autoincrement=True),
            Column('type_id', INT),
            Column('content', TEXT),
            Column('choices', JSON),
            Column('answers', JSON),
            Column('created_at', TIMESTAMP),
            Column('updated_at', TIMESTAMP)
        )
        super().__init__(engine, metadata, table, role)

    def get_question_by_question_id(self, question_id):
        table = self.table
        stmt = select([table.c.content, table.c.choices]).where(table.c.id == question_id)
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        return {'question_id': question_id, 'content': row.content, 'choices': row.choices}

    def get_answer_by_question_id(self, question_id):
        table = self.table
        stmt = select([table.c.answers]).where(table.c.id == question_id)
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        return {'question_id': question_id, 'content': row.content, 'choices': row.choices}

    def get_question_by_type(self, type_id):
        table = self.table
        stmt = select([table.c.content, table.c.choices]) \
            .where(table.c.type_id == type_id) \
            .order_by(table.c.question_id)
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            yield {
                'question_id': row.question_id,
                'content': row.content,
                'choices': row.choices
            }
