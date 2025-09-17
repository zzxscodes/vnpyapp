import warnings
from functools import wraps


def suppress_warnings(warning_types=(DeprecationWarning, FutureWarning)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with warnings.catch_warnings():
                for warning_type in warning_types:
                    warnings.filterwarnings("ignore", category=warning_type)
                return func(*args, **kwargs)

        return wrapper

    return decorator
