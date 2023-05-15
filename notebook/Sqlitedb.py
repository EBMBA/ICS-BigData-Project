import sqlite3
from pyspark.sql import SparkSession
import pandas as pd

class SQLiteDB:

    TABLE_NAME ='images'
    DB_NAME = './shared/taxon.db'
    def __init__(self):
        self.connection = sqlite3.connect(self.DB_NAME)
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
    
   

    def table_exist(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.TABLE_NAME,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

  
    
    def read_sqlite_table(self):
        # Créer une instance de la classe SQLiteDB
        sqlite_db = SQLiteDB()

        # Lire les données de la table et les convertir en Pandas DataFrame
        cursor = sqlite_db.connection.cursor()
        cursor.execute(f"SELECT * FROM {self.TABLE_NAME}")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])

        # Fermer la connexion à la base de données
        cursor.close()
        sqlite_db.close()

        return df

    