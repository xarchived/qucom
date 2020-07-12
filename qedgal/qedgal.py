from typing import Any, Iterator

import psycopg2.errors
from patabase import Postgres

from qedgal.exceptions import *


class Qedgal(object):
    def __init__(self, user: str, password: str, database: str, host: str = 'localhost', port=5432):
        self._db = Postgres(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)

    def add(self, table: str, **parameters: Any) -> int:
        placeholders = ['%s' for _ in parameters]

        sql = f'''
            insert into {table} ({', '.join(parameters)})
            values ({', '.join(placeholders)})
            returning id
        '''

        rows = self._db.select(sql, *parameters.values())
        row = next(rows)
        return row['id']

    def edit(self, table: str, pk: int, **parameters: Any) -> int:
        fields = [f'{key} = %s' for key in parameters if parameters[key]]
        values = [parameters[key] for key in parameters if parameters[key]]

        sql = f'''
            do $$
            begin
                update {table}
                set {', '.join(fields)}
                where id = %s;

                if not found then
                    raise exception 'Nothing updated';
                end if;
            end
            $$
        '''

        try:
            return self._db.perform(sql, *values, pk)
        except psycopg2.errors.RaiseException as e:
            if 'Nothing updated' in str(e):
                raise NothingUpdated(f'There is no row such as "id = {pk}"') from None
            raise e

    def delete(self, table: str, pk: int) -> None:
        sql = f'''
            do $$
            begin
                if exists(select from students where id = %s) then
                    delete
                    from {table}
                    where id = %s;
                else
                    raise exception 'Nothing deleted';
                end if;
            end
            $$
        '''

        try:
            self._db.perform(sql, pk, pk)
        except psycopg2.errors.RaiseException as e:
            if 'Nothing deleted' in str(e):
                raise NothingDeleted(f'There is no row such as "id = {pk}"') from None
            raise e

    def list(self, table: str, user_id: int = None, limit: int = 10, offset: int = 0) -> list:
        sql = f'''
            select * 
            from {table}_facade
        '''

        if user_id:
            sql += f' where {user_id} = any(user_ids)'

        sql += f' limit {limit}'
        sql += f' offset {offset}'

        return list(self._db.select(sql))

    def get(self, table: str, pk: int, user_id: int = None) -> dict:
        sql = f'''
            select * 
            from {table}_facade
            where id = %s
        '''

        if user_id:
            sql += f' and {user_id} = any(user_ids)'

        return next(self._db.select(sql, pk), dict())

    def query(self, table: str, q: str, fields: list, user_id: int = None, limit: int = 10, offset: int = 0) -> list:
        filters = [f'{key}::varchar like %s' for key in fields]
        values = [f'%{q}%' for _ in fields]

        sql = f'''
            select *
            from {table}_facade
            where {' or '.join(filters)}
        '''

        if user_id:
            sql += f' and {user_id} = any(user_ids)'

        sql += f' limit {limit}'
        sql += f' offset {offset}'

        return list(self._db.select(sql, *values))

    def count(self, table: str) -> int:
        sql = f'''
            select count(*)
            from {table}_facade
        '''

        rows = self._db.select(sql)
        row = next(rows)
        return row['count']

    def perform(self, sql: str, *args: Any) -> int:
        return self._db.perform(sql, *args)

    def select(self, sql: str, *args: Any) -> Iterator[dict]:
        return self._db.select(sql, *args)

    def procedure(self, func_name: str, **parameters: Any) -> int:
        return self._db.procedure(func_name, **parameters)

    def function(self, func_name: str, **parameters: Any) -> Iterator[dict]:
        return self._db.function(func_name, **parameters)
