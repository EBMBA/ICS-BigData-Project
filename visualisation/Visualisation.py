import os
import json
import pandas as pd
import math
import matplotlib.pyplot as plot
from wordcloud import WordCloud
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark import sql
from pyspark.sql import SparkSession 
import pyarrow 
import matplotlib.pyplot as plt
from pyspark.sql.functions import collect_list, concat_ws, explode



class Visualisation:

    METADATA_PATH = '../metadata'

    def __init__(self) -> None:
        data = []

        for filename in os.listdir(self.METADATA_PATH):
            if filename.endswith(".json"):
                with open(os.path.join(self.METADATA_PATH, filename), "r") as f:
                    metadata = json.load(f)

                name = metadata.get("name")
                scientific_name = metadata.get("scientific_name")
                family = metadata.get("family")
                location = metadata.get("location")
                width = metadata.get("width")
                height = metadata.get("height")
                format = metadata.get("format")
                mode = metadata.get("mode")
                dominated_colors = metadata.get("dominated_colors")
                dominated_colors_name = metadata.get("dominated_colors_name")
                exif = metadata.get("exif", {})
                make = exif.get("Make")
                model = exif.get("Model")
                orientation = exif.get("Orientation")
                if "exif" in metadata and "DateTime" in metadata["exif"]:
                    date_time = metadata['exif']['DateTime'][:4]
                else:
                    date_time = None

                data.append({
                    "name": name,
                    "scientific_name": scientific_name,
                    "family": family,
                    "location": location,
                    "filename": filename,
                    "width": width,
                    "height": height,
                    "format": format,
                    "mode": mode,
                    "dominated_colors": dominated_colors,
                    "dominated_colors_name": dominated_colors_name,
                    "make": make,
                    "model": model,
                    "orientation": orientation,
                    "year": date_time
                })

        # self.df = pd.DataFrame(data)
        self.spark = SparkSession.builder.getOrCreate()
        self.dfspark = self.spark.createDataFrame(data)
        self.dfspark.createOrReplaceTempView("visualisation")



    def get_years(self):
        year_counts = self.spark.sql("SELECT Year, COUNT(YEAR) AS Number FROM  visualisation GROUP BY year ORDER by year")

        years = [str(row['Year']) for row in year_counts.collect() if row['Year'] != None and row['Year'] != "0000"]
        numbers = [row['Number'] for row in year_counts.collect() if row['Year'] != None and row['Year'] != "0000" ]

        plot.bar(years, numbers)
        plot.xlabel('Année')
        plot.ylabel('Nombre de photos')
        plot.xticks(rotation=90)

        plot.savefig('./visualisation_images/years.png')
        plot.clf()

    def get_devices(self):
        devices = self.dfspark.groupby(['year', 'make']).agg({"make": "count"}).withColumnRenamed("count(make)", "count")
        devices.createOrReplaceTempView("devices")
        
        makes = self.spark.sql("SELECT DISTINCT make FROM devices ORDER BY make").collect()

        nr = math.ceil(len(makes) / 2)
        fig, axes = plot.subplots(nrows=nr, ncols=2, figsize=(20, 70))

        for i, make in enumerate(makes):
            if make[0] == None :
                continue
            g = self.spark.sql(f"SELECT year, count FROM devices WHERE make = '{make[0]}' ORDER BY year")
            g = g.toPandas()
            g.plot(
                x="year", y="count", kind="bar", title=make[0], ax=axes[math.floor(i / 2), i % 2]
            )
        plot.savefig('./visualisation_images/devices.png')
        plot.clf()

    def get_families(self):
        top_families = self.spark.sql("""
                SELECT family, COUNT(*) AS count
                FROM visualisation
                GROUP BY family
                ORDER BY count DESC
                LIMIT 20
            """)
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
        top_families = self.spark.sql("""
                SELECT family, COUNT(*) AS count
                FROM visualisation
                GROUP BY family
                ORDER BY count DESC
                LIMIT 20
            """)
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

        plot.savefig('./visualisation_images/worldcloud_families.png')
        plot.clf()


    def get_colors(self):
        df_colors = self.dfspark.select(explode(self.dfspark.dominated_colors_name).alias('color'))
        color_counts = df_colors.groupBy('color').count().orderBy('count', ascending=False)
        color_size = color_counts.collect()[:10]
        color_labels = [row["color"] for row in color_size]
        color_values = [row["count"] for row in color_size]
        total_colors = color_counts.agg({"count": "sum"}).collect()[0][0]
        plot.pie(color_values, labels=color_labels, autopct=lambda p: '{:.1f}%'.format(p * (sum(color_values)/total_colors)))
        plot.title('Répartition des couleurs dominantes')

        plot.savefig('./visualisation_images/colors.png')
        plot.clf()

    def get_wordcloud_colors(self):
        df_colors = self.dfspark.select(explode(self.dfspark.dominated_colors_name).alias('color'))
        color_counts = df_colors.groupBy('color').count().orderBy('count', ascending=False)
        

        color_size = color_counts.collect()
        colors = [row["color"] for row in color_size]
        captions = ' '.join(colors)

        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)

        plot.figure(figsize=(12, 6))
        plot.imshow(wordcloud, interpolation='bilinear')
        plot.axis('off')

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



