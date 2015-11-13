import pytest

from amoco.ui.render import *

@pytest.mark.skipif(not has_pygments,reason="no pygments")
def test_vltable():
    T = vltable()
    T.addrow([(Token.Literal,'abcd'),(Token.Register,'eax'),(Token.Column,'<-'),(Token.Constant,'0x23')])
    T.addrow([(Token.Literal,'abcd'),(Token.Register,'ebx'),(Token.Column,'<-'),(Token.Mnemonic,'mov')])
    T.addrow([(Token.Literal,'abcdxxxxxxx'),(Token.Register,'eflags'),(Token.Column,'<-'),(Token.Memory,'M32(eax+1)')])
    assert T.nrows == 3
    assert T.ncols == 2
    assert T.colsize[0] == 17
    assert T.getcolsize(0) == 17
    T.hiderow(2)
    assert T.getcolsize(0) == 7
    T.showrow(2)
    T.grep('eax',invert=True)
    assert T.hidden_r.issuperset((0,2))
    c0 = T.getcolsize(0)
    assert c0 == 7
    T.setcolsize(0,c0)
    T.squash_r = True
    T.squash_c = True
    s = str(T)


