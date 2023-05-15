from Analyse import Analyse
import os
from flask import Flask, render_template, make_response
from Sqlitedb import SQLiteDB
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful import Api

app = Flask(__name__, static_folder='./shared/images/')
api = Api(app)

@app.route('/analyse')
def analyse_all():
    print('analyse running')
    analyse = Analyse()
    analyse.clean_users_preferences()
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


@app.route('/swagger')
def swagger_ui():
    swag = swagger(app, prefix='/api')
    swag['info']['title'] = 'Container visualisation'
    swag['info']['version'] = '1.0'
    swag['info']['description'] = 'Documentation de la visualisation'
    swag['paths']['/analyse'] = {
        'get': {
            'summary': 'Générer des préférences',
            'description': "Génère des utilisateurs et des préférences d'images associées",
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }

    swag['paths']['/analyse/<user_id>'] = {
        'get': {
            'summary': 'Afficher les préférences utilisateurs',
            'description': "Affiche une page avec les photos likées et dislikées par l'utilisateur",
            'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'description': 'ID de l\'utilisateur',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            }
        ],
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }
    swag['paths']['/user/<user_id>/image/<image_id>'] = {
        'get': {
            'summary': 'Afficher une image et sa recommandation',
            'description': "Afficher une image et si ou non elle serait recommandée ens a basant sur les préférences de l'utilisateur ",
            'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'description': 'ID de l\'utilisateur',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            },
                        {
                'name': 'image_id',
                'in': 'path',
                'description': 'ID de l\'image',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            }
        ],
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }

    swag['paths']['/user/<user_id>/image/random'] = {
        'get': {
            'summary': 'Afficher une image random et sa recommandation',
            'description': "Afficher une image random et si ou non elle serait recommandée ens a basant sur les préférences de l'utilisateur ",
            'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'description': 'ID de l\'utilisateur',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            }],
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }

    swag['paths']['/user/<user_id>/image/<image_id>/liked'] = {
        'get': {
            'summary': 'Défini la photo comme likée',
            'description': "Défini la photo comme likée par l'utilisateur",
                        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'description': 'ID de l\'utilisateur',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            },
                        {
                'name': 'image_id',
                'in': 'path',
                'description': 'ID de l\'image',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            }
        ],
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }

    swag['paths']['/user/<user_id>/image/<image_id>/disliked'] = {
        'get': {
            'summary': 'Défini la photo comme likée',
            'description': "Défini la photo comme likée par l'utilisateur",
                        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'description': 'ID de l\'utilisateur',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            },
                        {
                'name': 'image_id',
                'in': 'path',
                'description': 'ID de l\'image',
                'required': True,
                'schema': {
                    'type': 'integer'
                }
            }
        ],
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }


    return swag

if __name__ == "__main__":
    SWAGGER_URL = '/swagger-ui'
    API_URL = '/swagger'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Container visualisation"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.run(host='0.0.0.0', port=8080, debug=True)
