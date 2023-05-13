from Collecte import Collecte
import requests

if __name__ == '__main__':
    collecte = Collecte()
    collecte.download_and_insert_data()
    url = 'http://annotation:3001/annotation'

    response = requests.get(url)
    