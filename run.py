from flask_extended import Flask
from flask_cors import CORS
from ons_ras_common.ras_config import ras_config
from ons_ras_common.ras_database.ras_database import RasDatabase


def create_app(settings_class):
    app = Flask(__name__)
    # app.config.from_object(settings_class)

    # config = ras_config.from_yaml_file(app.config['CONFIG_PATH'])

    app.config.from_yaml('config.yaml')

    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', app.config)
    app.db = db
    # TODO: investigate a way to unify the environment/config with Flask config, or at least a neater approach!
    # app.environment = config

    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')
    CORS(app)
    return app


if __name__ == '__main__':
    app = create_app('ras_party.settings.default_settings.Config')
    # TODO: reintroduce gw registration, which is just a case of iterating endpoints and posting to gw
    # If 5-sec iterative reg is required, then use asyncio

    scheme, host, port = app.config['scheme'], app.config['host'], app.config['port']
    # for rule in app.url_map.iter_rules():
    #     # TODO: how does the gw recognise parameterised endpoints? (perhaps just first part of endpoint?)
    #     reg = {'protocol': scheme, 'host': host, 'port': port, 'uri': rule.rule}
    #     print(reg)
    app.run(debug=app.config['DEBUG'], port=8080)
