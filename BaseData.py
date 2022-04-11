import sqlite3


import sqlite3

class BaseData:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.curson = self.connection.cursor()
    def sql(self, sql):
        with self.connection:
            return self.curson.execute(sql).fetchall()