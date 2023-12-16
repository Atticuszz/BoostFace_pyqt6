import datetime
import traceback
from functools import wraps

import requests

from src.app.config import qt_logger


def error_handler(f):
    """ decorator to catch error and print error info"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """ wrapper to catch error and print error info"""
        try:
            return f(*args, **kwargs)
        except requests.HTTPError:
            error_info = traceback.format_exc()
            qt_logger.error(f"HTTPError at {f.__name___}  with {error_info}")
        except Exception:
            error_info = traceback.format_exc()
            qt_logger.error(f"Error at {f.__name___} with {error_info}")
        return None

    return wrapper
