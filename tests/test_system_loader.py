import pytest

import amoco

def test_loader_001(samples):
    for f in samples:
        p = amoco.system.loader.load_program(f)

def test_loader_002(sc1):
    p = amoco.system.loader.load_program(sc1)
    assert p.bin.filename == '(sc-eb165e31...)'
