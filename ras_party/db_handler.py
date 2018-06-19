import logging

import structlog


logger = structlog.wrap_logger(logging.getLogger(__name__))


async def db_handler(app, handler):
    async def middleware(request):
        logger.info("Acquiring database session.",
                    pool_size=app.db.engine.pool.size(),
                    connections_in_pool=app.db.engine.pool.checkedin(),
                    connections_checked_out=app.db.engine.pool.checkedout(),
                    current_overflow=app.db.engine.pool.overflow())

        request.db = app.db
        response = await handler(request)
        return response
    return middleware
