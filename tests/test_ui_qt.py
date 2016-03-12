import amoco
from amoco.ui.graphics.qt_.engine import *
amoco.ui.graphics.configure(graphics="qt")

p = amoco.system.loader.load_program('samples/x86/flow.elf')
z = amoco.lbackward(p)
z.getcfg()
f = z.G.C[2].sV[0].data.misc['func']

w = MainWindow(z)
w.createFuncGraph(f)
#gs = GraphScene(f.view.layout)
#gv = GraphView(gs)
#gs.Draw()
#gv.show()
w.show()
