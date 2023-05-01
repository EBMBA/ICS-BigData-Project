import os
import json
import pandas as pd
import math
import matplotlib.pyplot as plot
from wordcloud import WordCloud
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession 
import pyarrow 


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

        self.df = pd.DataFrame(data)
        spark = SparkSession.builder.getOrCreate()
        self.dfspark = spark.createDataFrame(self.df)


    def get_years(self):

        year_counts = self.df.groupby('year').size()

        plot.bar(year_counts.index, year_counts.values)
        plot.xlabel('Année')
        plot.ylabel('Nombre de photos')
        plot.xticks(rotation=90)

        plot.savefig('./visualisation_images/years.png')
        plot.clf()

    def get_years_spark(self):

        year_counts = self.df.groupby('year').size()

        plot.bar(year_counts.index, year_counts.values)
        plot.xlabel('Année')
        plot.ylabel('Nombre de photos')
        plot.xticks(rotation=90)

        plot.savefig('./visualisation_images/years.png')
        plot.clf()


    def get_devices(self):
        grouped = self.df.groupby(['year', 'make']).size()

        grouped = grouped.reset_index(name='count')

        nr = math.ceil(grouped['make'].nunique() / 2)
        _, axes = plot.subplots(nrows=nr, ncols=2, figsize=(20, 25))

        for i, make in enumerate(grouped['make'].unique()):
            g = grouped[grouped['make'] == make]
            g.plot(
                x="year", y="count", kind="bar", title=make, ax=axes[math.floor(i / 2), i % 2]
            )

        plot.savefig('./visualisation_images/devices.png')
        plot.clf()

    def get_families(self):
        top_families = self.df.groupby('family').size().nlargest(20)
        total_photos = len(self.df)
        plot.pie(top_families.values, labels=top_families.index, autopct=lambda p: '{:.1f}%'.format(p * (sum(top_families.values)/total_photos)))
        plot.title('Répartition des photos par famille')

        plot.savefig('./visualisation_images/top_families_pie_chart.png')
        plot.clf()


    def get_top_families(self):
        top_families = self.df.groupby('family').size().nlargest(20)
        plot.title("Nombe des photos des 20 plus grandes familles")
        plot.bar(top_families.index, top_families.values)
        plot.xlabel('Familles')
        plot.xticks(rotation=90)
        plot.ylabel('Nombre de photos')
        #plot.show()

        plot.savefig('./visualisation_images/top_families_graph.png')
        plot.clf()

    
    def get_wordcloud_families(self):
        captions = ' '.join(self.df['family'].astype(str))

        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)

        plot.figure(figsize=(12, 6))
        plot.imshow(wordcloud, interpolation='bilinear')
        plot.axis('off')

        plot.savefig('./visualisation_images/worldcloud_families.png')
        plot.clf()


    def get_colors(self):
        colors = [color for list_color in self.df['dominated_colors_name'] if list_color is not None for color in list_color]

        color_counts = pd.DataFrame(colors, columns=['color'])

        colors_size = color_counts.groupby("color").size().nlargest(10)
        total_colors = len(color_counts)
        print(colors_size)
        print(total_colors)
        plot.pie(colors_size.values, labels=colors_size.index, autopct=lambda p: '{:.1f}%'.format(p * (sum(colors_size.values)/total_colors)))
        plot.title('Répartition des couleurs dominantes')

        plot.savefig('./visualisation_images/colors.png')
        plot.clf()

    def get_wordcloud_colors(self):

        colors = [color for list_color in self.df['dominated_colors_name'] if list_color is not None for color in list_color]
        color_counts = pd.DataFrame(colors, columns=['color'])
        captions = ' '.join(color_counts['color'].astype(str))

        wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(captions)

        plot.figure(figsize=(12, 6))
        plot.imshow(wordcloud, interpolation='bilinear')
        plot.axis('off')

        plot.savefig('./visualisation_images/wordcloud_colors.png')
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



