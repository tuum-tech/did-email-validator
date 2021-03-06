import falcon
import threading

from app import log, config, redisBroker
from app.constants import CRED_GEN
from app.api.common import base
from app.middleware import AuthMiddleware
from app.api.v1 import validation
from app.model import emailValidationTx
from app.errors import AppError
from mongoengine import connect

LOG = log.get_logger()


class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info("API Server is starting")

        # Simple endpoint for base
        self.add_route("/", base.BaseResource())

        # Receive callback from elastOS
        self.add_route("/v1/validation/callback", validation.EmailConfirmation())

        self.add_error_handler(AppError, AppError.handle)


# Connect to mongodb
LOG.info("Connecting to mongodb...")
if config.PRODUCTION:
    connect(
        config.MONGO['DATABASE'],
        host="mongodb+srv://" + config.MONGO['USERNAME'] + ":" + config.MONGO['PASSWORD'] + "@" +
             config.MONGO['HOST'] + "/?retryWrites=true&w=majority"
    )
else:
    connect(
        config.MONGO['DATABASE'],
        host="mongodb://" + config.MONGO['USERNAME'] + ":" + config.MONGO['PASSWORD'] + "@" +
             config.MONGO['HOST'] + ":" + str(config.MONGO['PORT']) + "/?authSource=admin"
    )

did = CRED_GEN.did
if did:
    LOG.info(f"Using '{did.decode('utf-8')}' for issuing credentials...")
    LOG.info("Initializing the Falcon REST API service...")
    application = App(middleware=[
        AuthMiddleware(),
    ])

    th = threading.Thread(target=redisBroker.monitor_redis)
    th.setDaemon(True)
    th.start()
