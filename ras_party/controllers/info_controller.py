from json import loads
from pathlib import Path

from flask import current_app

from ras_party.controllers.error_decorator import translate_exceptions


_health_check = {}

if Path('git_info').exists():
    with open('git_info') as io:
        _health_check = loads(io.read())


@translate_exceptions
def get_info():
    info = {
        "name": current_app.config['NAME'],
        "version": current_app.config['VERSION'],
    }
    info = dict(_health_check, **info)

    if current_app.config.feature.report_dependencies:
        info["dependencies"] = [{'name': name} for name in current_app.config.dependency.keys()]

    return info
