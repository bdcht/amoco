from .term import engine as termengine

class Engine(object):
    engine = termengine

from amoco.config import conf_proxy
conf = conf_proxy('ui')

def load_engine(engine=None):
    if engine is None:
        if conf['graphics'] == 'gtk':
            from amoco.ui.graphics.gtk_ import engine as gtkengine
            engine = gtkengine
        elif conf['graphics'] == "qt":
            from amoco.ui.graphics.qt_ import engine as qtengine
            engine = qtengine
    Engine.engine = engine
