import os
import json
import random
import pandas as pd
from Sqlitedb import SQLiteDB
from sklearn import tree
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class Analyse:
    #TODO: set the table names in env variables
    TABLE_IMAGE_NAME = 'images'
    TABLE_USER_NAME = 'users'
    TABLE_LIKED_NAME = 'liked'
    TABLE_DISLIKED_NAME = 'disliked'
    
    def __init__(self) -> None:
        self.db = SQLiteDB()
        self.df = self.db.read_table(self.TABLE_IMAGE_NAME)
        # print(self.df.show())
        self.df = self.df.toPandas()
        pass
    
    def clean_user_preferences(self, user_id=1):
        # get records from liked table with the same user_id
        liked_images = self.db.read_table(self.TABLE_LIKED_NAME).toPandas()
        liked_images = liked_images[liked_images["user_id"] == user_id]
        # delete records with the same user_id
        for record in liked_images.iterrows():
            self.db.delete_record_table(self.TABLE_LIKED_NAME, record[1]["id"])
        # get records from disliked table with the same user_id
        disliked_images = self.db.read_table(self.TABLE_DISLIKED_NAME).toPandas()
        disliked_images = disliked_images[disliked_images["user_id"] == user_id]
        # delete records with the same user_id
        for record in disliked_images.iterrows():
            self.db.delete_record_table(self.TABLE_DISLIKED_NAME, record[1]["id"])
        
    def clean_users_preferences(self):
        self.db.clean_table_users()

    def generate_all_users_preferences(self, number_of_images=10):
        # generate all users preferences and save them in the database
        users = self.db.read_table(self.TABLE_USER_NAME).toPandas()
        for user in users.iterrows():
            self.generate_user_preferences(int(user[1]["id"]), number_of_images=number_of_images)
    
    def generate_user_preferences(self, user_id=1, number_of_images=10):
        # clean the user preferences
        self.clean_user_preferences(user_id)
        # get random liked images
        liked_images = self.get_random_liked_image(number_of_images=number_of_images)
        print(liked_images)
        # insert liked images
        self.set_liked_images(user_id=user_id, images=liked_images)
        # get random disliked images
        disliked_images = self.get_random_disliked_image(number_of_images=number_of_images)
        self.set_disliked_images(user_id=user_id, images=disliked_images)
    
    def get_random_image(self):
        random_image = self.df.sample().iloc[0]
        # print(random_image)
        return random_image
    
    def validate_image_attributes(self, image):
        if not image["family"] or image["family"] == "None":
            return False
        if not image["location"] or image["location"] == "None":
            return False
        # TODO: uncomment this when the data is ready
        # if not image["dominated_colors_name"] or image["dominated_colors_name"] == "None":
        #     return False
        return True

    def get_random_liked_image(self, number_of_images=10):
        images_set = set()
        disliked_images = self.get_disliked_images()
        i = 0
        while i < number_of_images:
            random_image = self.get_random_image()
            # print("random image id : ", random_image["id"])
            # print("disliked images : ", disliked_images)
            if random_image["id"] not in images_set and self.validate_image_attributes(random_image) and random_image["id"] not in disliked_images:
                images_set.add(random_image["id"])
                i += 1
        return images_set
    
    def get_random_disliked_image(self, number_of_images=10):
        images_set = set()
        liked_images = self.get_liked_images()
        i = 0
        while i < number_of_images:
            random_image = self.get_random_image()
            if random_image["id"] not in images_set and self.validate_image_attributes(random_image) and random_image["id"] not in liked_images:
                images_set.add(random_image["id"])
                i += 1
        return images_set
    
    def set_liked_images(self, images, user_id=1):
        # get records from liked table with the same user_id
        liked_images = self.db.read_table(self.TABLE_LIKED_NAME).toPandas()
        liked_images = liked_images[liked_images["user_id"] == user_id]
        # delete records with the same user_id
        for record in liked_images.iterrows():
            self.db.delete_record_table(self.TABLE_LIKED_NAME, record[1]["id"])
        # insert new records
        for image in images:
            print("image id: ", image, " add to liked for user id: ", user_id)
            image_id = int(image)
            self.db.insert_record_table(self.TABLE_LIKED_NAME, user_id = user_id, image_id = image_id)
    
    def set_disliked_images(self, images, user_id=1):
        # get records from disliked table with the same user_id
        disliked_images = self.db.read_table(self.TABLE_DISLIKED_NAME).toPandas()
        disliked_images = disliked_images[disliked_images["user_id"] == user_id]
        # delete records with the same user_id
        for record in disliked_images.iterrows():
            self.db.delete_record_table(self.TABLE_DISLIKED_NAME, record[1]["id"])
        # insert new records
        for image in images:
            print("image id: ", image, " add to disliked for user id: ", user_id)
            image_id = int(image)
            self.db.insert_record_table(self.TABLE_DISLIKED_NAME, user_id = user_id, image_id = image_id)

    def get_liked_images(self, user_id=1):
        # check if the table exists and user_id exists in users table
        if self.db.table_exist(self.TABLE_LIKED_NAME) and self.db.table_exist(self.TABLE_USER_NAME) and user_id in self.db.read_table(self.TABLE_USER_NAME).toPandas()["id"].values.tolist():
            liked_images = self.db.read_table(self.TABLE_LIKED_NAME).toPandas()
            return set(liked_images[liked_images["user_id"] == user_id]["image_id"].values.tolist())
        return set()
    
    def get_disliked_images(self, user_id=1):
        if self.db.table_exist(self.TABLE_DISLIKED_NAME) and self.db.table_exist(self.TABLE_USER_NAME) and user_id in self.db.read_table(self.TABLE_USER_NAME).toPandas()["id"].values.tolist():
            disliked_images = self.db.read_table(self.TABLE_DISLIKED_NAME).toPandas()
            return set(disliked_images[disliked_images["user_id"] == user_id]["image_id"].values.tolist())
        return set()
    
    def get_image_name(self, image_id):
        if image_id not in self.df["id"].values.tolist():
            return None
        return  self.df[self.df["id"] == image_id]["image_name"].values[0]
    
    def generate_input_data(self, user_id=1):
        liked_images = self.get_liked_images(user_id)
        disliked_images = self.get_disliked_images(user_id)
        # print("liked images : ", liked_images)
        # print("disliked images : ", disliked_images)
        input_data = []
        for image_id in liked_images:
            location = self.df[self.df["id"] == image_id]["location"].values[0]
            family = self.df[self.df["id"] == image_id]["family"].values[0]
            input_data.append([family, location])
            # TODO: uncomment this when the data is ready
            # color = self.df[self.df["id"] == image_id]["dominated_colors_name"].values[0]
            # input_data.append([family, location, color])
        for image_id in disliked_images:
            location = self.df[self.df["id"] == image_id]["location"].values[0]
            family = self.df[self.df["id"] == image_id]["family"].values[0]
            input_data.append([family, location])
            # TODO: uncomment this when the data is ready
            # color = self.df[self.df["id"] == image_id]["dominated_colors_name"].values[0]
            # input_data.append([family, location, color])
        
        result = ["favorite"] * len(liked_images) + ["not favorite"] * len(disliked_images)
        return input_data, result
    
    def predict(self, imaged_id, user_id):
        data, result = self.generate_input_data(user_id)
        # print("data : ", data)

        families = set(x[0] for x in data)
        locations = set(x[1] for x in data)
        # colors = set(x[2] for x in data)

        image = self.df[self.df["id"] == imaged_id]
        family = image["family"].values[0]
        location = image["location"].values[0]
        # color = image["dominated_colors_name"].values[0]

        # if the user input have not been used in the dataset we get random values from 
        if family not in families:
            family = random.choice(list(families))
        if location not in locations:
            location = random.choice(list(locations))
        # if color not in colors:
        #     color = random.choice(list(colors))

        dataframe = pd.DataFrame(data, columns=["family", "location"])
        resultframe = pd.DataFrame(result, columns=["favorite"])

        # print("dataframe : ", dataframe)
        # print("resultframe : ", resultframe)

        # generating numerical labels for categorical data
        le1 = LabelEncoder()
        dataframe["family"] = le1.fit_transform(dataframe["family"])

        le2 = LabelEncoder()
        dataframe["location"] = le2.fit_transform(dataframe["location"])

        # le3 = LabelEncoder()
        # dataframe["color"] = le3.fit_transform(dataframe["color"])

        le4 = LabelEncoder()
        resultframe["favorite"] = le4.fit_transform(resultframe["favorite"])

        rfc = RandomForestClassifier(n_estimators=10, max_depth=2,
                      random_state=0)
        rfc = rfc.fit(dataframe, resultframe.values.ravel())

        # prediction = rfc.predict([[le1.transform([family])[0], le2.transform([location])[0]]], le3.transform([color])[0])
        prediction = rfc.predict([[le1.transform([family])[0], le2.transform([location])[0]]])

        return le4.inverse_transform(prediction)[0]



    
