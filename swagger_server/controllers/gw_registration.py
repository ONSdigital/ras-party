import asyncio
import time

import requests

from swagger_server.controllers.url_builder import build_url


def make_registration_func(app):

    config = app.config
    scheme, host, port = config['scheme'], config['host'], config['port']

    endpoints = set()
    for rule in app.url_map.iter_rules():
        endpoint = '/'.join(rule.rule.split('/')[0:4])
        endpoints.add(endpoint)
    registrations = [{'protocol': scheme, 'host': host, 'port': port, 'uri': ep}
                     for ep in endpoints if ep not in ['/static/<path:filename>']]

    def register():
        while True:
            for reg in registrations:
                gw_svc = app.config.dependency['api-gateway']
                ping_url = build_url('{}://{}:{}/api/1.0.0/ping/{}/None', gw_svc, app.config['name'])
                response = requests.get(ping_url)
                if response.status_code == '204':
                    reg_url = build_url('{}"//{}:{}/api/1.0.0/register', gw_svc)
                    requests.post(reg_url, json=reg)
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