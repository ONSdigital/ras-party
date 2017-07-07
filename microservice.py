from ons_ras_common.factories.ras_application import ConnexionFactory
from ons_ras_common.ras_config import ras_config
from ons_ras_common.ras_database.ras_database import RasDatabase
from ons_ras_common.ras_logger import ras_logger
from ons_ras_common.ras_registration.ras_registration import RasRegistration
from ons_ras_common.ras_swagger.ras_swagger import RasSwagger
from ons_ras_common.service.ras_service import RasMicroService


config = ras_config.from_yaml_file('test', './config.yaml')
logger = ras_logger.make(config)

PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
db = PartyDatabase('ras-party-db', config).activate()

swagger = RasSwagger(config, './swagger_server/swagger/swagger.yaml')
if config.feature('gateway-registration'):
    RasRegistration(config, swagger).activate()

service = RasMicroService(config, app_factory=ConnexionFactory(config, swagger))
