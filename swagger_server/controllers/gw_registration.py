import asyncio
import time


def make_registration_func(app):

    gw_config = app.config.dependency['api-gateway']
    scheme, host, port = gw_config['scheme'], gw_config['host'], gw_config['port']

    endpoints = set()
    for rule in app.url_map.iter_rules():
        endpoint = '/'.join(rule.rule.split('/')[0:4])
        endpoints.add(endpoint)
    registrations = [{'protocol': scheme, 'host': host, 'port': port, 'uri': ep}
                     for ep in endpoints if ep not in ['/static/<path:filename>']]

    def register():
        while True:
            for reg in registrations:
                print(reg)
            time.sleep(5)
    return register


def call_in_background(target, *, loop=None, executor=None):
    """Schedules and starts target callable as a background task

    If not given, *loop* defaults to the current thread's event loop
    If not given, *executor* defaults to the loop's default executor

    Returns the scheduled task.
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    if callable(target):
        return loop.run_in_executor(executor, target)
    raise TypeError("target must be a callable, "
                    "not {!r}".format(type(target)))