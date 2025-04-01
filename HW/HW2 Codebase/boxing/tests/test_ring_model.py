from dataclasses import asdict

import pytest

from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

@pytest.fixture()
def boxers_model():
    None
    
@pytest.fixture()
def mock_update_stats(mocker):
    None

@pytest.fixture()
def sample_boxer1():
    None
    
@pytest.fixture()
def sample_boxer2():
    None

@pytest.fixture()
def sample_ring(sample_boxer1, sample_boxer2):
    None

def test_fight_bad_number_boxers(ring_model):
    None

##################################################
# Add / Remove Ring Management Test Cases
##################################################

def test_add_boxer_to_ring(ring_model, sample_boxer1):
    None

def test_add_duplicate_boxer_to_ring(ring_model, sample_boxer1):
    None
    
def test_add_bad_boxer_to_ring(ring_model, sample_boxer1):
    None
    
def test_remove_boxer_from_ring_by_boxer_id(ring_model, sample_ring):
    None
    
def test_remove_boxer_from_ring_by_ring_position(ring_model, sample_ring):
    #IDK, do we need this?
    None
    
def test_clear_ring(ring_model, sample_boxer1):
    None
    
    
### Still adding more.