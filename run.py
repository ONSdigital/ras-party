from json import loads

from flask import jsonify
from flask_cors import CORS
from ras_common_utils.ras_config import ras_config
from ras_common_utils.ras_config.flask_extended import Flask
from ras_common_utils.ras_database.ras_database import RasDatabase
from ras_common_utils.ras_error.ras_error import RasError
from ras_common_utils.ras_logger.ras_logger import configure_logger


def create_app(config):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_ras_config(config)

    @app.errorhandler(Exception)
    def handle_error(error):
        if isinstance(error, RasError):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
        else:
            response = jsonify({'errors': [str(error)]})
            response.status_code = 500
        return response

    # register view blueprints
    from ras_party.views.party_view import party_view
    from ras_party.views.info_view import info_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')
    app.register_blueprint(info_view)

    CORS(app)
    return app


def initialise_db(app):
    # Initialise the database with the specified SQLAlchemy model
    party_database = RasDatabase.make(model_paths=['ras_party.models.models'])
    db = party_database('ras-party-db', app.config)
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = db


if __name__ == '__main__':
    config_path = 'config/config.yaml'

    config = ras_config.from_yaml_file(config_path)
    configure_logger(config.service)

    app = create_app(config)
    with open(app.config['PARTY_SCHEMA']) as io:
        app.config['PARTY_SCHEMA'] = loads(io.read())

    initialise_db(app)

    scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])

    app.run(debug=app.config['DEBUG'], host=host, port=port)
