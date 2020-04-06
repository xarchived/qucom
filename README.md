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
