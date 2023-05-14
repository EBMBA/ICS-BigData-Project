import sqlite3
from pyspark.sql import SparkSession

class SQLiteDB:

    TABLE_IMAGE_NAME = 'images'
    TABLE_USER_NAME = 'users'
    TABLE_LIKED_NAME = 'liked'
    TABLE_DISLIKED_NAME = 'disliked'
    DB_NAME = './shared/taxon.db'
    def __init__(self):
        self.connection = sqlite3.connect(self.DB_NAME)
        self.spark = SparkSession.builder.appName("SQLiteDB").getOrCreate()
        for table_name in [self.TABLE_IMAGE_NAME, self.TABLE_USER_NAME, self.TABLE_LIKED_NAME, self.TABLE_DISLIKED_NAME]:
            if not self.table_exist(table_name):
                self.create_table(table_name)

    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def create_table(self, table_name):
        cursor = self.connection.cursor()
        if table_name == self.TABLE_IMAGE_NAME:
            cursor.execute(f'CREATE TABLE {self.TABLE_IMAGE_NAME} (id INTEGER PRIMARY KEY, image_name TEXT, name TEXT, age INTEGER, scientific_name TEXT, family TEXT, location TEXT, colors1_hex, colors2_hex TEXT, colors1_name TEXT, colors2_name TEXT, date_original TEXT, date_digitalized TEXT, date TEXT, orientation TEXT, model TEXT, copyright TEXT, make TEXT)')
        if table_name == self.TABLE_USER_NAME:
            cursor.execute(f'CREATE TABLE {self.TABLE_USER_NAME} (id INTEGER PRIMARY KEY)')
        if table_name == self.TABLE_LIKED_NAME:
            cursor.execute(f'CREATE TABLE {self.TABLE_LIKED_NAME} (id INTEGER PRIMARY KEY, user_id INTEGER, image_id INTEGER)')
        if table_name == self.TABLE_DISLIKED_NAME:
            cursor.execute(f'CREATE TABLE {self.TABLE_DISLIKED_NAME} (id INTEGER PRIMARY KEY, user_id INTEGER, image_id INTEGER)')
        self.connection.commit()
        cursor.close()
    
    def read_table(self, table_name):
        df = self.spark.read.format("jdbc").option("url", f"jdbc:sqlite:{self.DB_NAME}").option("dbtable", table_name).load()
        return df
    
    # def read_table(self, table_name):
    #     jdbc_url = f"jdbc:sqlite:{self.DB_NAME}"
    #     connection_properties = {
    #         "driver": "org.sqlite.JDBC",
    #         "url": jdbc_url,
    #         "dbtable": table_name
    #     }
    #     df = self.spark.read.format("jdbc").options(**connection_properties).load()
    #     return df

    def table_exist(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    def insert_record(self, **kwargs):
        cursor = self.connection.cursor()
        columns = ', '.join(kwargs.keys())
        values = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {self.TABLE_IMAGE_NAME} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(kwargs.values()))
        self.connection.commit()
        cursor.close()
    
    def update_record(self, id, **kwargs):
        cursor = self.connection.cursor()
        set_values = ', '.join([f"{column} = ?" for column in kwargs.keys()])
        query = f"UPDATE {self.TABLE_IMAGE_NAME} SET {set_values} WHERE id = ?"
        cursor.execute(query, tuple(kwargs.values()) + (id,))
        self.connection.commit()
        cursor.close()

    def delete_table(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE {table_name}")
        self.connection.commit()
        cursor.close()

    def insert_record_table(self, table_name, **kwargs):
        cursor = self.connection.cursor()
        columns = ', '.join(kwargs.keys())
        values = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(kwargs.values()))
        self.connection.commit()
        cursor.close()

    def delete_record_table(self, table_name, id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = {id}")
        self.connection.commit()
        cursor.close()

    def clean_table_users(self):
        for table_name in [self.TABLE_USER_NAME, self.TABLE_LIKED_NAME, self.TABLE_DISLIKED_NAME]:
            self.delete_table(table_name)
            self.create_table(table_name)
        for i in range(10):
            self.insert_record_table(self.TABLE_USER_NAME, id=i)