import pytest
import numpy as np
from psychopy import visual
from panda.generator import PANDA


@pytest.fixture(scope="session")
def psychopy_window():
    win = visual.Window(
        size=[1200, 1200],
        color="white",
        units="pix",
    )
    yield win
    win.close()


@pytest.fixture
def panda_instance(psychopy_window):
    return PANDA(
        psychopy_window,
        n_anchor=3,
        base_ta=30000.0,
        base_cha=120000.0,
        color="black",
        seed=42,
    )