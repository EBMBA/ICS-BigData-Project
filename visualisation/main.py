

import os
from flask import Flask, render_template, make_response
from Visualisation import Visualisation

app = Flask(__name__, static_folder='./visualisation_images')

@app.route('/visualisation')
def visualisation():
    # obtenir tous les noms de fichier dans le dossier image
    images = [f for f in os.listdir(app.static_folder) if os.path.isfile(os.path.join(app.static_folder, f))]
    return render_template('visualisation.html', images=images)

@app.route('/generate')
def generate():
    visualisation = Visualisation()
    visualisation.generate_images()
    return make_response('', 204)


if __name__ == '__main__':
    app.run()