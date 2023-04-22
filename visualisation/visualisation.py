import os
import json
import pandas as pd
data = []

class Visualisation:
    def __prepare_dataframe():
        for filename in os.listdir("metadata"):
            if filename.endswith(".json"):
                with open(os.path.join("metadata", filename), "r") as f:
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

        return pd.DataFrame(data)