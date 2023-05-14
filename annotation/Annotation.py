import os
import json
from PIL import Image, ImageColor
from PIL.ExifTags import TAGS
import numpy as np
from sklearn.cluster import KMeans
import webcolors
import math
from Sqlitedb import SQLiteDB
import pandas as pd

from pyspark.sql.functions import col

class Annotation:

    EXIF_DATA  = [
    "DateTimeOriginal",
    "Make",
    "Model",
    "Orientation",
    "Copyright",
    "DateTime",
    "DateTimeDigitized"
    ]

    SQL_EXIF_COLUMN = {
        'DateTimeOriginal' : 'date_original',
        'DateTimeDigitized' : 'date_digitalized',
        'DateTime' : 'date',
        'Orientation' : 'orientation',
        'Model' : 'model',
        'Copyright' : 'copyright',
        'Make' : 'make'
    }

    PATH = './shared/images'


    def __init__(self) -> None:
        self.db = SQLiteDB()

    def map_exif_to_sql_column(self, exif):
        exif_sql = {}
        for key, value in exif.items():
            exif_sql[self.SQL_EXIF_COLUMN[key]] = value
        return exif_sql

    def getDominatedColors(self, imgfile):
        # Parcourir les fichiers dans le répertoire d'images
        numarray = np.array(imgfile.getdata(), np.uint8)
        colors = []
        if len(numarray.shape) == 2:
            clusters = KMeans(n_clusters=2, n_init=2)
            clusters.fit(numarray)
            for i in range(len(clusters.cluster_centers_)):
                colors.append(
                    "#%02x%02x%02x"
                    % (
                        math.ceil(clusters.cluster_centers_[i][0]),
                        math.ceil(clusters.cluster_centers_[i][1]),
                        math.ceil(clusters.cluster_centers_[i][2]),
                    )
                )
        return colors

    # https://stackoverflow.com/questions/70967119/webcolors-has-no-attribute-css3-hex-to-names
    def get_closest_color(self, rgb_triplet):
        min_colours = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - rgb_triplet[0]) ** 2
            gd = (g_c - rgb_triplet[1]) ** 2
            bd = (b_c - rgb_triplet[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]


    def run(self):

        print('annotation_running')
        df = self.db.read_table('images').toPandas()
        for row in df.itertuples():
            print(f'annotation for {row.name}')
            # Accéder à la valeur par sa clé
            if row.image_name.endswith('.jpg') or row.image_name.endswith('.JPG') or row.image_name.endswith('.jpeg') or row.image_name.endswith('.png'):
                
                with Image.open(os.path.join(self.PATH, row.image_name)) as img:

                    colors_dominated = self.getDominatedColors(img)
                    exif_data = img.getexif()
                    exif = {}
                    if exif_data:
                        for tag, value in exif_data.items():
                            decoded_tag = TAGS.get(tag, tag)
                            if decoded_tag in self.EXIF_DATA:
                                exif[decoded_tag] = value
                exif_to_insert = self.map_exif_to_sql_column(exif)
                for column, value in exif_to_insert.items():
                    self.db.update_record(row.id, **{column: value})



                colors_dominated_name = []
                for color in colors_dominated:
                    colors_dominated_name.append(self.get_closest_color(ImageColor.getcolor(color, "RGB")))


                self.db.update_record(row.id, colors1_name = colors_dominated_name[0])
                self.db.update_record(row.id,  colors2_name = colors_dominated_name[1])
                








