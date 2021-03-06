import inspect
import logging


LOG = logging.getLogger(__name__)


def _log_need_to_fix(name):
    def wrapped(*args, **kwargs):
        # pylint: disable=unused-argument
        stack = inspect.stack()
        caller = inspect.getframeinfo(stack[1][0])
        LOG.warning("NEED TO FIX: {}, {} called {}".format(
            caller.filename,
            caller.lineno,
            name
        ))
    return staticmethod(wrapped)
