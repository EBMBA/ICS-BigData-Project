import os
from flask import Flask, render_template, make_response
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful import Api
from Visualisation import Visualisation

app = Flask(__name__, static_folder='./visualisation_images')
api = Api(app)

@app.route('/visualisation')
def visualisation():
    images = [f for f in os.listdir(app.static_folder) if os.path.isfile(os.path.join(app.static_folder, f))]
    return render_template('visualisation.html', images=images)

@app.route('/generate')
def generate():
    visualisation = Visualisation()
    visualisation.generate_images()
    return make_response('', 204)

@app.route('/swagger')
def swagger_ui():
    swag = swagger(app, prefix='/api')
    swag['info']['title'] = 'Container visualisation'
    swag['info']['version'] = '1.0'
    swag['info']['description'] = 'Documentation de la visualisation'
    swag['paths']['/generate'] = {
        'get': {
            'summary': 'Générer des images',
            'description': 'Génère des images à partir des données de Visualisation',
            'responses': {
                '204': {
                    'description': 'Succès'
                }
            }
        }
    }

    swag['paths']['/visualisation'] = {
        'get': {
            'summary': 'Afficher les images',
            'description': "Renvoi une page web permettant d'afficher les images générerées par la visualisation",
            'responses': {
                '200': {
                    'description': 'Succès'
                }
            }
        }
    }
    return swag


if __name__ == '__main__':
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
    app.run(debug=True, threaded=True, host='0.0.0.0', port=3002)