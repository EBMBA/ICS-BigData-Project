import os
import json
from PIL import Image, ImageColor
from PIL.ExifTags import TAGS
import numpy as np
from sklearn.cluster import KMeans
import webcolors
import math

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

    PATH = '../images'

    def getDominatedColors(self, imgfile):
        # Parcourir les fichiers dans le répertoire d'images
        print(imgfile)
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
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - rgb_triplet[0]) ** 2
            gd = (g_c - rgb_triplet[1]) ** 2
            bd = (b_c - rgb_triplet[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    def run(self):

        metadata = []
        print('run')
        # Parcourir les fichiers dans le répertoire d'images
        for filename in os.listdir('../images'):
            print(filename)
            if filename.endswith('.jpg') or filename.endswith('.JPG') or filename.endswith('.jpeg') or filename.endswith('.png'):
                with Image.open(os.path.join(self.PATH, filename)) as img:
                    json_path = os.path.join("../metadata", filename.replace(".jpg", ".json").replace(".JPG", ".json").replace(".jpeg", ".json").replace(".png", ".json"))
                    if os.path.exists(json_path):
                        with open(json_path, 'r') as f:
                            existing_metadata = json.load(f)
                    # else:
                    #     existing_metadata = []

                    if 'dominated_colors_name' in existing_metadata.keys() :
                        print("Already treated")
                        pass

                    exif_data = img.getexif()
                    exif = {}
                    if exif_data:
                        for tag, value in exif_data.items():
                            decoded_tag = TAGS.get(tag, tag)
                            if decoded_tag in self.exif_data_interested:
                                exif[decoded_tag] = value

                    colors_dominated = self.getDominatedColors(img)
                    colors_dominated_name = []

                    print(colors_dominated)

                    for color in colors_dominated:
                        colors_dominated_name.append(self.get_closest_color(ImageColor.getcolor(color, "RGB")))



                    # Add the new metadata to the list
                    # print(existing_metadata)

                    existing_metadata['filename']= filename
                    existing_metadata['width']= img.width
                    existing_metadata['height']= img.height
                    existing_metadata['format']= img.format
                    existing_metadata['mode']= img.mode
                    existing_metadata['dominated_colors']= colors_dominated
                    existing_metadata['dominated_colors_name']= colors_dominated_name
                    existing_metadata['exif']= exif


                    # Save the metadata to a JSON file
                    with open(json_path, 'w') as f:
                        json.dump(existing_metadata, f, cls=CustomEncoder)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8', 'ignore')
        return super().default(obj)




