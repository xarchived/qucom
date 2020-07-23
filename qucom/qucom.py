from typing import Any, Iterator

import psycopg2.errors
from patabase import Postgres

from qucom.exceptions import *


def _error_handler(func):
    def wrapper(*args, **kwargs):
        assert isinstance(args[0], Qucom)

        if 'table' in kwargs:
            table = kwargs['table']
        else:
            table = args[1]

        if 'pk' in kwargs:
            pk = kwargs['id']
        elif len(args) > 2 and isinstance(args[2], int):
            pk = args[2]
        else:
            pk = -1

        try:
            return func(*args, **kwargs)
        except psycopg2.errors.UndefinedTable:
            raise UndefinedTable(f'Table not found (table={table})') from None
        except psycopg2.errors.UndefinedColumn:
            raise UndefinedColumn(f'Column not found ({str(kwargs)})') from None
        except psycopg2.errors.UniqueViolation:
            raise DuplicateRecord(f'Duplicate record ({str(kwargs)})') from None
        except psycopg2.errors.NotNullViolation:
            raise NotNull(f'Not NULL violation ({str(kwargs)})') from None
        except psycopg2.errors.RaiseException as e:
            if 'Nothing updated' in str(e):
                raise NothingUpdated(f'Record not found (id={pk})') from None
            if 'Nothing deleted' in str(e):
                raise NothingDeleted(f'Record not found (id={pk})') from None
            raise e

    return wrapper


class Qucom(object):
    def __init__(self, user: str, password: str, database: str, host: str = 'localhost', port=5432):
        self._db = Postgres(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)

    @_error_handler
    def add(self, table: str, **parameters: Any) -> int:
        if not parameters:
            raise RequiredArgument('Parameters can not be empty')

        placeholders = ['%s' for _ in parameters]

        sql = f'''
            insert into {table} ({', '.join(parameters)})
            values ({', '.join(placeholders)})
            returning id
        '''

        rows = self._db.select(sql, *parameters.values())
        row = next(rows)
        return row['id']

    @_error_handler
    def edit(self, table: str, pk: int, **parameters: Any) -> int:
        if not parameters:
            raise RequiredArgument('Parameters can not be empty')

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

        return self._db.perform(sql, *values, pk)

    @_error_handler
    def delete(self, table: str, pk: int) -> None:
        sql = f'''
            do $$
            begin
                if exists(select from {table} where id = %s) then
                    delete
                    from {table}
                    where id = %s;
                else
                    raise exception 'Nothing deleted';
                end if;
            end
            $$
        '''

        self._db.perform(sql, pk, pk)

    @_error_handler
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

    @_error_handler
    def get(self, table: str, pk: int, user_id: int = None) -> dict:
        sql = f'''
            select * 
            from {table}_facade
            where id = %s
        '''

        if user_id:
            sql += f' and {user_id} = any(user_ids)'

        return next(self._db.select(sql, pk), dict())

    @_error_handler
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

    @_error_handler
    def calendar(self, table: str) -> list:
        sql = f'''
            select *
            from {table}_calendar
        '''

        return list(self._db.select(sql))

    @_error_handler
    def columns(self, table: str):
        sql = f'''
            select column_name, is_nullable, data_type
            from information_schema.columns
            where table_schema = 'public'
              and table_name = %s
        '''

        return list(self._db.select(sql, table))

    @_error_handler
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
