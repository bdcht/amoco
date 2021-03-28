from .term import engine as termengine

class Engine(object):
    """
    This class acts as the base class for all views
    and is just a placeholder that allows to define
    a common engine module available to all instances.
    """
    engine = termengine

from amoco.config import conf

def load_engine(engine=None):

    if isinstance(engine,str):
        conf.UI.graphics = engine
        engine=None

    if engine is None:
        if conf.UI.graphics == "gtk":
            from amoco.ui.graphics.gtk_ import engine as gtkengine

            engine = gtkengine

        elif conf.UI.graphics == "qt":
            from amoco.ui.graphics.qt_ import engine as qtengine

            engine = qtengine

        else:
            engine = termengine

    Engine.engine = engine
