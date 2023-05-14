import pandas as pd
import math
import matplotlib.pyplot as plot
from wordcloud import WordCloud
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark import sql
from pyspark.sql import SparkSession 
import matplotlib.pyplot as plt
from pyspark.sql.functions import collect_list, concat_ws, explode
from Sqlitedb import SQLiteDB
from pyspark.sql.functions import col, expr
import pyspark.sql.functions as F

class Visualisation:
    def __init__(self) -> None:
        self.db = SQLiteDB()
        self.dfspark = self.db.get_dataframe()
        self.dfspark.createOrReplaceTempView("visualisation")

    def get_years(self):
        year_counts = self.dfspark.groupby(['date']).agg({"date": "count"}).withColumnRenamed("count(date)", "Number").orderBy(col("date"))
        # Change date yyyy:mm:dd hh:mm:ss format to year yyyy
        year_counts = year_counts.withColumn("year", expr("substring(date, 1, 4)"))
        years = [str(row['year']) for row in year_counts.collect() if row['year'] != None and row['year'] != "0000" and row['year'] != "null"]
        numbers = [row['Number'] for row in year_counts.collect() if row['year'] != None and row['year'] != "0000" and row['year'] != "null"]

        plot.bar(years, numbers)
        plot.xlabel('Année')
        plot.ylabel('Nombre de photos')
        plot.xticks(rotation=90)
        plot.title('Nombre de photos par année')
        plot.savefig('./visualisation_images/years.png')
        plot.clf()

    def get_devices(self):
        devices = self.dfspark.groupby(['date', 'make']).agg({"make": "count"}).withColumnRenamed("count(make)", "count")
        devices.createOrReplaceTempView("devices")
        
        # Change date yyyy:mm:dd hh:mm:ss format to year yyyy
        devices = devices.withColumn("year", expr("substring(date, 1, 4)"))         
        print(devices.show())

        makes = devices.select("make").distinct().collect()

        nr = math.ceil(len(makes) / 2)
        fig, axes = plot.subplots(nrows=nr, ncols=2, figsize=(20, 70))

        for i, make in enumerate(makes):
            if make[0] == None or make[0] == "null" or make[0] == "None" or make[0] == "none":
                continue
            g = devices.filter(devices.make == make[0]).orderBy(col("year")).toPandas()
            g.plot(
                x="year", y="count", kind="bar", title=make[0], ax=axes[math.floor(i / 2), i % 2]
            )
        plot.title("Nombre de photos par appareil")
        plot.savefig('./visualisation_images/devices.png')
        plot.clf()

    def get_families(self):
        top_families = self.dfspark.groupby(['family']).agg({"family": "count"}).withColumnRenamed("count(family)", "count").orderBy(col("count").desc()).limit(4)
        total_photos = self.dfspark.count()
        top_families_list = top_families.collect()
        labels = [row['family'] for row in top_families_list]
        sizes = [row['count'] for row in top_families_list]
        percentages = [size / total_photos * 100 for size in sizes]

        fig, ax = plot.subplots()
        ax.pie(sizes, labels=labels, autopct=lambda p: '{:.1f}%'.format(p))
        plot.title('Répartition des photos par famille')
        plot.savefig('./visualisation_images/top_families_pie_chart.png')
        plot.clf()


    def get_top_families(self):
        top_families = self.dfspark.groupby(['family']).agg({"family": "count"}).withColumnRenamed("count(family)", "count")
        top_families_list = top_families.collect()[:20]
        labels = [row['family'] for row in top_families_list]
        sizes = [row['count'] for row in top_families_list]
        plot.title("Nombe des photos des 20 plus grandes familles")
        plot.bar(labels, sizes)
        plot.xlabel('Familles')
        plot.xticks(rotation=90)
        plot.ylabel('Nombre de photos')
        plot.savefig('./visualisation_images/top_families_graph.png')
        plot.clf()

    
    def get_wordcloud_families(self):
        captions = self.dfspark.select(collect_list('family').alias('family_list')) \
             .select(concat_ws(' ', 'family_list').alias('captions')) \
             .collect()[0]['captions']

        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)

        plot.figure(figsize=(12, 6))
        plot.imshow(wordcloud, interpolation='bilinear')
        plot.axis('off')
        plot.title('Nuage de mots des familles')
        plot.savefig('./visualisation_images/worldcloud_families.png')
        plot.clf()


    def get_colors(self):
        df_colors = self.dfspark.select(col("colors1_name").alias("color")).union(self.dfspark.select(col("colors2_name").alias("color")))
        df_colors = df_colors.filter(df_colors.color.isNotNull())
        color_counts = df_colors.groupBy("color").count().orderBy(F.desc("count"))
        #TODO: change limit to 10
        color_size = color_counts.limit(4).collect()
        color_labels = [row["color"] for row in color_size]
        color_values = [row["count"] for row in color_size]
        total_colors = color_counts.agg(F.sum("count")).collect()[0][0]
        print(total_colors)
        print(color_labels)
        print(color_values)
        plot.pie(color_values, labels=color_labels, autopct=lambda p: '{:.1f}%'.format(p * (sum(color_values)/total_colors)))
        plot.title('Répartition des couleurs dominantes')

        plot.savefig('./visualisation_images/colors.png')
        plot.clf()

    def get_wordcloud_colors(self):
        df_colors = self.dfspark.select(col("colors1_name").alias("color")).union(self.dfspark.select(col("colors2_name").alias("color")))
        df_colors = df_colors.filter(df_colors.color.isNotNull())
        color_counts = df_colors.groupBy("color").count().orderBy(F.desc("count"))
        

        color_size = color_counts.collect()
        colors = [row["color"] for row in color_size]
        captions = ' '.join(colors)

        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)

        plot.figure(figsize=(12, 6))
        plot.imshow(wordcloud, interpolation='bilinear')
        plot.axis('off')
        plot.title('Nuage de mots des couleurs dominantes')
        plot.savefig('./visualisation_images/wordcloud_colors.png')
        plot.clf()
    
    def get_region(self):
        region_size = self.dfspark.groupBy("location").count().withColumnRenamed("count", "size")
        total_region = region_size.agg({"size": "sum"}).collect()[0][0]
        region_size = region_size.collect()
        region_labels = [row["location"] for row in region_size]
        region_values = [row["size"] for row in region_size]
        plot.pie(region_values, labels=region_labels, autopct=lambda p: '{:.1f}%'.format(p * (sum(region_values)/total_region)))
        plot.title('Répartition des zones géographique des espèces')
        plot.savefig('./visualisation_images/region.png')
        plot.clf()
    
    def get_wordcloud_region(self):
        region_size = self.dfspark.groupBy("location").count().withColumnRenamed("count", "size")
        total_region = region_size.agg({"size": "sum"}).collect()[0][0]
        region_size = region_size.collect()
        region_labels = [row["location"] for row in region_size]
        captions = ' '.join(region_labels)
        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Nuage de mots des zones géographiques')
        plot.savefig('./visualisation_images/wordcloud_regions.png')
        plot.clf()

    def generate_images(self):
        self.get_colors()
        self.get_devices()
        self.get_colors()
        self.get_top_families()
        self.get_families()
        self.get_wordcloud_colors()
        self.get_wordcloud_families()
        self.get_years()
        self.get_region()
        self.get_wordcloud_region()