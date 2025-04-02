from dataclasses import asdict

import pytest

from boxing.models.boxers_model import Boxer
from boxing.models.ring_model import RingModel

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_db_connection(mocker):
    """Mock the connection to the SQLite database."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()

    mocker.patch("sqlite3.connect", return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.__enter__.return_value = mock_cursor

    return mock_conn

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture()
def sample_boxer1():
    return Boxer(1, "Mike Tyson", 220, 178, 71.0, 30)
    
@pytest.fixture()
def sample_boxer2():
    return Boxer(2, "Muhammad Ali", 215, 191, 78.0, 30)

@pytest.fixture()
def sample_boxer3():
    return Boxer(3, "Canelo Álvarez", 168, 173, 70.5, 33)

@pytest.fixture()
def sample_boxers(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

##################################################
# Fight Test Cases
##################################################
def test_fight_with_one_boxer(ring_model, sample_boxer1):
    """Test a fight with only one boxer.

    """
    ring_model.ring.append(sample_boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_with_two_boxers(ring_model, sample_boxers,  mock_db_connection, mocker):
    """Test a fight between two boxers.

    """
    ring_model.ring.extend(sample_boxers)

    mocker.patch("boxing.models.ring_model.get_random", return_value=1.3)

    winner_name = ring_model.fight()
    assert winner_name == "Muhammad Ali", f"Expected winner: Muhammad Ali. Actual winner {winner_name}."

##################################################
# Add / Remove Ring Management Test Cases
##################################################

def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the RingList.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Mike Tyson'
    
def test_add_bad_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding a wrong boxer to the ringList.

    """
    with pytest.raises(TypeError, match=f"Invalid type: Expected 'Boxer', got 'dict'"):
        ring_model.enter_ring(asdict(sample_boxer1))

def test_add_too_many_boxer_to_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test adding more than two boxers to the RingList.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)
    
def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ringList.

    """
    ring_model.ring.append(sample_boxer1)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "RingList should be empty after clearing"
    
    
##################################################
# Boxer Retrieval Test Cases
##################################################

def test_get_all_boxers(ring_model, sample_boxers):
    """Test successfully retrieving all boxers from the ringList.

    """
    ring_model.ring.extend(sample_boxers)

    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[1].id == 2

def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test successfully calculating the fighting skill score for a boxer.

    """
    sample_skill = ring_model.get_fighting_skill(sample_boxer1)
    assert sample_skill == 2207.1, f"Expected score 2207.1, got score {sample_skill}"