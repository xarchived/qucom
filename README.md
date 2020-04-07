# Qedgal
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
pip install -U qedgal
```

or if you prefer the latest development version, you can install it from the source:

```bash
git clone https://github.com/xurvan/qedgal.git
cd qedgal
python setup.py install
```

## Quickstart
We have to create a view for each table with a postfix "_facade" 

```python
from qedgal import Qedgal

db = Qedgal(host='localhost', user='USERNAME', password='PASSWORD', database='DATABASE_NAME')

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
