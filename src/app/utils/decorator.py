import datetime
import traceback
from functools import wraps

import requests


def error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.HTTPError:
            error_info = traceback.format_exc()
            print(f"HTTPError at {datetime.datetime.now()} in {error_info}")
        except Exception:
            error_info = traceback.format_exc()
            print(f"Error at {datetime.datetime.now()} in {error_info}")
        return None

    return wrapper
