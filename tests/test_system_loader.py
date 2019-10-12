import pytest

import amoco

def test_loader_001(samples):
    for f in samples:
        p = amoco.system.core.read_program(f)

def test_loader_002(samples):
    for f in samples:
        p = amoco.system.load_program(f)

def test_loader_003(sc1):
    p = amoco.system.load_program(sc1)
    assert p.bin.f.getvalue() == sc1
    assert p.bin.filename == '(sc-eb165e31...)'
