from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()


# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

### Add
def test_create_boxer(mock_cursor):
    None
    
def test_create_boxer_duplicate(mock_cursor):
    None
    
def test_create_boxer_invalid_weight():
    None

def test_create_boxer_invalid_height():
    None
    
def test_create_boxer_invalid_reach():
    None
    
def test_create_boxer_invalid_age():
    None
    
### Delete
def test_delete_boxer(mock_cursor):
    None
    
def test_delete_boxer_bad_id(mock_cursor):
    None
    
######################################################
#
#    Get Leaderboard, Boxer, Weightclass
#
######################################################

### Leaderboard
def test_get_leaderboard(mock_cursor):
    None
    
def test_get_leaderboard_bad_sortby(mock_cursor):
    None
    
### Get Boxer by ID
def test_get_boxer_by_id(mock_cursor):
    None

def test_get_boxer_by_id_bad_id(mock_cursor):
    None

### Get Boxer by Name
def test_get_boxer_by_name(mock_cursor):
    None
    
def test_get_boxer_by_name_bad_name(mock_cursor):
    None
    
### get Weightclass
def test_get_weight_class(mock_cursor):
    None
    
def test_get_weight_class_bad_weight(mock_cursor):
    None


######################################################
#
#    Update stats
#
######################################################

def test_update_boxer_stats(mock_cursor):
    None

def test_update_boxer_stats_bad_name(mock_cursor):
    None 