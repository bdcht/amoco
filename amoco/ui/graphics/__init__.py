from .term import engine as termengine

class Engine(object):
    engine = termengine

def configure(**kargs):
    from amoco.config import get_module_conf
    conf = get_module_conf('ui')
    conf.update(kargs)
    g = conf['graphics']
    if g is 'gtk':
        from amoco.ui.graphics.gtk_ import engine
        Engine.engine = engine
    elif g is 'qt':
        from amoco.ui.graphics.qt_ import engine
        Engine.engine = engine

configure()
