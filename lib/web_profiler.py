from functools import wraps

from cloudscheduler.lib.csv2_config import Config
config = Config('web_frontend')

if config.enable_profiling:
    from silk.profiling.profiler import silk_profile
else:
    def silk_profile(name=None):
        def s_profile(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                r = f(*args, **kwargs)
                return r
            return wrapped
        return s_profile

