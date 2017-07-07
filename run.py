from flask import Flask
from ons_ras_common.ras_config import ras_config
from ons_ras_common.ras_database.ras_database import RasDatabase


def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)

    config = ras_config.from_yaml_file(app.config['ENVIRONMENT_NAME'], app.config['CONFIG_PATH'])
    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', config).activate()
    app.db = db
    # TODO: investigate a way to unify the environment/config with Flask config, or at least a neater approach!
    app.environment = config

    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')

    return app


if __name__ == '__main__':
    app = create_app('ras_party.settings.default_settings.Config')
    app.run(debug=app.config['DEBUG'], port=8080)
