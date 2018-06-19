import logging

from aiohttp import web
import structlog
from requests import RequestException

from ras_party.exceptions import RasError

logger = structlog.wrap_logger(logging.getLogger(__name__))


async def error_handler(app, handler):
    async def middleware(request):
        try:
            response = await handler(request)
            return response
        except RasError as error:
            error_message = error.to_dict()
            logger.exception('Uncaught exception', errors=error.to_dict(), status=error.status_code)
            return web.json_response(data=error_message, status=error.status_code)
        except RequestException as ex:
            errors = {'errors': {'method': ex.request.method, 'url': ex.request.url, }}
            if ex.response is not None:
                status_code = ex.response.status_code
            else:
                status_code = 500
            logger.exception('Uncaught exception', errors=errors, status=status_code)
            return web.json_response(data=errors, status=status_code)
        except Exception:
            logger.exception('Uncaught exception', status=500)
            return web.json_response(data={}, status=500)
    return middleware
