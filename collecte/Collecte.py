import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import os
import requests
import shutil
from Sqlitedb import SQLiteDB

class Collecte:
    ENDPOINT_URL = "https://query.wikidata.org/sparql"
    LIMIT = 10
    QUERY = f"""SELECT DISTINCT ?taxon ?name ?image ?sciName ?familyLabel ?locationLabel
            WHERE {{
                ?taxon wdt:P31 wd:Q16521;
                        rdfs:label ?name;
                        wdt:P18 ?image;
                        wdt:P225 ?sciName;
                        wdt:P171 ?family;
                        wdt:P9714 ?location.
                FILTER(lang(?name) = "en")
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            LIMIT {LIMIT}"""
    

    def __init__(self) -> None:
        self.db = SQLiteDB()
        

    def get_results(self, endpoint_url, query):
        user_agent = "WDQS-example Python/%s.%s" % (
            sys.version_info[0],
            sys.version_info[1],
        )
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()
    
        
    def create_dataframe(self):
        array = []
        results = self.get_results(self.ENDPOINT_URL, self.QUERY)

        for result in results["results"]["bindings"]:
            array.append(
                (
                    result["name"]["value"],
                    result["image"]["value"],
                    result["sciName"]["value"],
                    result["familyLabel"]["value"],
                    result["locationLabel"]["value"],
                )
            )   
        dataframe = pd.DataFrame(array, columns=["name", "image", "scientific_name","family", "location"])

        dataframe = dataframe.astype(
            dtype={"name" : "<U200", "image" : "<U200", "scientific_name" : "<U200","family" : "<U200", "location" : "<U200"}   
        )
        return dataframe

    def download_and_insert_data(self):

        dataframe = self.create_dataframe()
        if not os.path.exists("metadata"):
            os.mkdir("metadata")
        for index, row in dataframe.iterrows():
            image_url = row["image"]
            response_code = self.download_image(image_url)
            if response_code == 200:
                image_filename = os.path.basename(image_url)
                if len(image_filename) > 50:
                    continue
                print(image_filename)
                self.db.insert_record(name = row["name"], scientific_name = row["scientific_name"], family = row["family"], location = row["location"], image_name = image_filename)

    def download_image(self, url):
        if not os.path.exists("./shared/images"):
            os.mkdir("./shared/images")
        headers = {"User-Agent": "Mozilla/5.0"}
        request = requests.get(url, allow_redirects=True, headers=headers, stream=True)
        if request.status_code == 200:
            filename = os.path.join("./shared/images", os.path.basename(url))            
            if len(filename) > 50:
                return
            with open(filename, "wb") as image:
                request.raw.decode_content = True
                shutil.copyfileobj(request.raw, image)
        return request.status_code
        