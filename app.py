
from connexion import App
from flask_cors import CORS

from swagger_server.configuration import ons_env

if __name__ == '__main__':
    ons_env.activate()
    app = App(__name__, specification_dir='./swagger_server/swagger/')
    CORS(app.app)
    app.add_api('swagger.yaml', arguments={'title': 'ONS Microservice'})
    app.run(host='0.0.0.0', port=ons_env.port)
