# Qucom
When we want to delete a record from a table or insert a simple record despite table design queries are very similar.
Personally always copy-paste code of another table and just edit it a little bit. Wouldn't it be nice if there was a
query helper that do this tedious part for us? So, I created a package that do the exact job and now I am going to share
it with you.

I spot 6 type of queries:

- add: insert a new record into a table
- edit: edit a record of a table
- delete: delete a record from a table
- list: select all records of table  
- get: select only one record by primary key  
- query: select all records where a field is contains a certain word   


## Installation
Simply you can install it from PyPi by following command:

```bash
pip install -U qucom
```

or if you prefer the latest development version, you can install it from the source:

```bash
git clone https://github.com/xurvan/qucom.git
cd qucom
python setup.py install
```

## Quickstart
Usually, There is a foreign key in a table and we don't like to get an integer or whole record from another table, we
need only some fields of that table. Another scenario is when there are some metadata fields or some security related
fields those we dont like to show in our query. To solve these problems for each table we going to create a view then
customize fields as we like inside it. These views should have a "_facade" postfix so library can understand them. 

```python
from qucom import Qucom

db = Qucom(host='localhost', user='USERNAME', password='PASSWORD', database='DATABASE_NAME')

db.perform('''
    create table users
    (
        id          serial primary key not null,
        name        varchar            not null,
        username    varchar unique     not null,
        password    varchar            not null
    )
''')

db.perform('''
    create view users_facade as
    select id, name, username
    from users
''')

db.add(table='users', name='Edward Elric', username='edward', password='password')

rows = db.list('users')
for row in rows:
    print(row)

db.edit(table='users', pk=1, username='new_edward')

row = db.get(table='users', pk=1)
print(row)
```
