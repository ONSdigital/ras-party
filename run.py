from flask import Flask
from ons_ras_common.factories.ras_application import ConnexionFactory
from ons_ras_common.ras_config import ras_config
from ons_ras_common.ras_database.ras_database import RasDatabase
from ons_ras_common.ras_logger import ras_logger
from ons_ras_common.ras_registration.ras_registration import RasRegistration
from ons_ras_common.ras_swagger.ras_swagger import RasSwagger
from ons_ras_common.service.ras_service import RasMicroService


# TODO: this wrapper is a bodge to workaround ras-common issues, and will likely simplify with use of vanilla Flask
class PartyService:

    CONFIG_PATH = './config.yaml'
    SWAGGER_PATH = './swagger_server/swagger/swagger.yaml'

    service = None

    @staticmethod
    def get():
        if not PartyService.service:
            config = ras_config.from_yaml_file('test', PartyService.CONFIG_PATH)
            # TODO: this should just configure the standard logger, check that it works:
            logger = ras_logger.make(config)

            PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
            db = PartyDatabase('ras-party-db', config).activate()

            swagger = RasSwagger(config, PartyService.SWAGGER_PATH)
            if config.feature('gateway-registration'):
                RasRegistration(config, swagger).activate()

            PartyService.service = RasMicroService(config, app_factory=ConnexionFactory(config, swagger), db=db)

        return PartyService.service


def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)

    config = ras_config.from_yaml_file('test', PartyService.CONFIG_PATH)
    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', config).activate()
    app.db = db
    # TODO: investigate a way to unify the environment/config with Flask config, or at least a neater approach!
    app.environment = config

    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')

    return app


if __name__ == '__main__':
    app = create_app('ras_party.settings.default_settings')
    app.run(debug=app.config['DEBUG'], port=8080)
