import pytest
import amoco
#from amoco.ui.graphics import load_engine
#load_engine()
#from amoco.ui.graphics.qt_.engine import app
#from amoco.ui.graphics.qt_.mainwin import MainWindow
#amoco.conf.UI.graphics = 'qt'

@pytest.mark.skipif(True,reason="work-in-progress")
def test_graph():
    p = amoco.loader.load_program('samples/x86/flow.elf')
    z = amoco.lbackward(p)
    z.getcfg()
    f = z.functions[2]
    w = MainWindow(z)
    w.createFuncGraph(f)
    w.show()
