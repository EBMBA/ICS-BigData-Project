from Analyse import Analyse
import os
from flask import Flask, render_template, make_response
from Sqlitedb import SQLiteDB

app = Flask(__name__, static_folder='images/')

@app.route('/analyse')
def analyse_all():
    analyse = Analyse()
    analyse.generate_all_users_preferences(number_of_images=2)
    return make_response("ok")

@app.route('/analyse/<user_id>')
def analyse(user_id):
    user_id = int(user_id)
    analyse = Analyse()
    analyse.generate_user_preferences(user_id=user_id, number_of_images=2)
    # analyse.clean_user_preferences(user_id=user_id)
    # analyse.set_disliked_images(analyse.get_random_disliked_image(number_of_images=2), user_id=user_id)
    # analyse.set_liked_images(analyse.get_random_liked_image(number_of_images=2), user_id=user_id)
    # print("liked images ",analyse.get_liked_images(user_id))
    # print("disliked images ",analyse.get_disliked_images(user_id))
    images_liked = [analyse.get_image_name(image_id) for image_id in analyse.get_liked_images(user_id)]
    images_disliked = [analyse.get_image_name(image_id) for image_id in analyse.get_disliked_images(user_id)]
    return render_template('analyse.html', images_liked=images_liked, images_disliked=images_disliked, user_id=user_id)

@app.route('/user/<user_id>/image/<image_id>')
def recommandation(image_id, user_id):
    analyse = Analyse()
    image_name = analyse.get_image_name(int(image_id))
    if image_name is None:
        return render_template('recommandation.html', image_status="no_image")
    
    prediction = analyse.predict(imaged_id=int(image_id), user_id=int(user_id))
    print("prediction : ", prediction)
    if prediction == "favorite":

        image_status=" Image would be liked by the user"
    else:
        image_status=" Image would be disliked by the user"
    
    return render_template('recommandation.html', image=image_name, image_status=image_status, user_id=int(user_id))

@app.route('/user/<user_id>/image/random')
def recommandation_random(user_id):
    analyse = Analyse()
    image_id = analyse.get_random_image()["id"]
    image_name = analyse.get_image_name(int(image_id))
    if image_name is None:
        return render_template('recommandation.html', image_status="no_image")
    
    prediction = analyse.predict(imaged_id=int(image_id), user_id=int(user_id))
    print("prediction : ", prediction)
    if prediction == "favorite":

        image_status=" Image would be liked by the user"
    else:
        image_status=" Image would be disliked by the user"
    
    return render_template('recommandation.html', image=image_name, image_status=image_status, user_id=int(user_id))

@app.route('/user/<user_id>/image/<image_id>/liked')
def like_image(image_id, user_id):
    analyse = Analyse()
    image_liked = analyse.get_liked_images(int(user_id))
    image_disliked = analyse.get_disliked_images(int(user_id))
    if int(image_id) in image_liked and int(image_id) not in image_disliked:
        return make_response("OK")
    if int(image_id) in image_disliked:
        image_disliked.remove(int(image_id))
        analyse.set_disliked_images(image_disliked, user_id=int(user_id))
    image_liked.add(int(image_id))
    analyse.set_liked_images(image_liked, user_id=int(user_id))
    return make_response("OK")

@app.route('/user/<user_id>/image/<image_id>/disliked')
def dislike_image(image_id, user_id):
    analyse = Analyse()
    image_liked = analyse.get_liked_images(int(user_id))
    image_disliked = analyse.get_disliked_images(int(user_id))
    if int(image_id) in image_disliked and int(image_id) not in image_liked:
        return make_response("OK")
    if int(image_id) in image_liked:
        image_liked.remove(int(image_id))
        analyse.set_liked_images(image_liked, user_id=int(user_id))
    image_disliked.add(int(image_id))
    analyse.set_disliked_images(image_disliked, user_id=int(user_id))
    return make_response("OK")

if __name__ == "__main__":
    app.run(port=8080, debug=True)
