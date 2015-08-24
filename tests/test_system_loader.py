import pytest

import amoco

def test_loader_001(samples):
    for f in samples:
        p = amoco.system.loader.load_program(f)

