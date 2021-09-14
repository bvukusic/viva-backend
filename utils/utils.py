import os
import json
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

with open(os.environ.get('VIVA_CONFIG')) as f:
    configuration = json.loads(f.read())


def get_env_var(setting, config=configuration):
    try:
        val = config[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        error_msg = f'ImproperlyConfigured: Set {setting} environment variable.'
        raise ImproperlyConfigured(error_msg)