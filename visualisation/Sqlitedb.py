import sqlite3
from pyspark.sql import SparkSession

class SQLiteDB:

    TABLE_NAME ='images'
    DB_NAME = './shared/taxon.db'
    def __init__(self):
        self.connection = sqlite3.connect(self.DB_NAME)
        self.spark = SparkSession.builder.appName("SQLiteDB").getOrCreate()
        if not self.table_exist():
            self.create_table()

    def close(self):
        if self.connection:
            self.connection.close()
    
    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f'CREATE TABLE {self.TABLE_NAME} (id INTEGER PRIMARY KEY, image_name TEXT, name TEXT, age INTEGER, scientific_name TEXT, family TEXT, location TEXT, colors1_hex, colors2_hex TEXT, colors1_name TEXT, colors2_name TEXT, date_original TEXT, date_digitalized TEXT, date TEXT, orientation TEXT, model TEXT, copyright TEXT, make TEXT)')
        self.connection.commit()
        cursor.close()
    
    def read_table(self, table_name):
        df = self.spark.read.format("jdbc").option("url", f"jdbc:sqlite:{self.DB_NAME}").option("dbtable", table_name).load()
        return df.collect()
    
    def get_dataframe(self):
        df = self.spark.read.format("jdbc").option("url", f"jdbc:sqlite:{self.DB_NAME}").option("dbtable", self.TABLE_NAME).load()
        return df

    def table_exist(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.TABLE_NAME,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    def insert_record(self, **kwargs):
        cursor = self.connection.cursor()
        columns = ', '.join(kwargs.keys())
        values = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(kwargs.values()))
        self.connection.commit()
        cursor.close()

    def update_record(self, id, **kwargs):
        cursor = self.connection.cursor()
        set_values = ', '.join([f"{column} = ?" for column in kwargs.keys()])
        query = f"UPDATE {self.TABLE_NAME} SET {set_values} WHERE id = ?"
        cursor.execute(query, tuple(kwargs.values()) + (id,))
        self.connection.commit()
        cursor.close()

    