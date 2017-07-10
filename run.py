from flask_extended import Flask
from flask_cors import CORS
from ons_ras_common.ras_config import ras_config
#from flask_extended import from_yaml
from ons_ras_common.ras_database.ras_database import RasDatabase
import os

def create_app(config_file):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_yaml(os.path.join(app.root_path, config_file))

    # Initialise the database with the specified SQLAlchemy model
    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', app.config)
    # TODO: this isn't entirely safe, use a get_db() lazy initialized instead...s
    app.db = db

    # register view blueprints
    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')

    CORS(app)
    return app


if __name__ == '__main__':
    app = create_app('config/config.yaml')
    # TODO: reintroduce gw registration, which is just a case of iterating endpoints and posting to gw
    # If 5-sec iterative reg is required, then use asyncio

    scheme, host, port = app.config['scheme'], app.config['host'], app.config['port']
    # for rule in app.url_map.iter_rules():
    #     # TODO: how does the gw recognise parameterised endpoints? (perhaps just first part of endpoint?)
    #     reg = {'protocol': scheme, 'host': host, 'port': port, 'uri': rule.rule}
    #     print(reg)
    app.run(debug=app.config.get('debug'), port=port)
