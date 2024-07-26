# -*- coding: utf-8 -*-

try:
    from blinker import Namespace
    signals_available = True

except ImportError:
    class Namespace(object):
        def signal(self, name, doc=None):
            return _FakeSignal(name, doc)

    class _FakeSignal(object):
        """If blinker is unavailable, create a fake class with the same
        interface that allows sending of signals but will fail with an
        error on anything else.  Instead of doing anything on send, it
        will just ignore the arguments and do nothing instead.
        """

        def __init__(self, name, doc=None):
            self.name = name
            self.__doc__ = doc

        def _fail(self, *args, **kwargs):
            raise RuntimeError('signalling support is unavailable '
                               'because the blinker library is '
                               'not installed.')
        send = lambda *a, **kw: None
        connect = disconnect = has_receivers_for = receivers_for = \
            temporarily_connected_to = connected_to = _fail
        del _fail

# The namespace for code signals.  If you are not Flask code, do
# not put signals in here.  Create your own namespace instead.
_signals = Namespace()


# Core signals.  For usage examples grep the source code or consult
# the API documentation in docs/api.rst as well as docs/signals.rst
after_template_rendered = _signals.signal('after-template-rendered')
before_render_template = _signals.signal('before-render-template')
report_started = _signals.signal('report-started')
report_finished = _signals.signal('report-finished')

