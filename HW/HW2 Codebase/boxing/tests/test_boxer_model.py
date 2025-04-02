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
    """ Test creating a new boxer in the database.
    
    """
    create_boxer(name="Boxer Name", weight=150, height=70, reach=10, age=25)
    
    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 150, 70, 10, 25)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
    
def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error).
    
    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name' already exists"):
        create_boxer(name="Boxer Name", weight=150, height=70, reach=10, age=25)

    
def test_create_boxer_invalid_weight(mock_cursor):
    """Test error when trying to create a boxer with an invalid weight (e.g., less than or equal to 125)

    """
    with pytest.raises(ValueError, match=r"Invalid weight: 120. Must be at least 125."):
        create_boxer(name="Boxer Name", weight=120, height=70, reach=10, age=25)

    with pytest.raises(ValueError, match=r"Invalid weight: -10. Must be at least 125."):
        create_boxer(name="Boxer Name", weight= -10, height=70, reach=10, age=25)


def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with an invalid height (e.g., negative or 0)

    """
    with pytest.raises(ValueError, match=r"Invalid height: 0. Must be greater than 0."):
        create_boxer(name="Boxer Name", weight=150, height=0, reach=10, age=25)

    with pytest.raises(ValueError, match=r"Invalid height: -10. Must be greater than 0."):
        create_boxer(name="Boxer Name", weight=150, height= -10, reach=10, age=25)

    
def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with an invalid reach (e.g., negative or 0)

    """
    with pytest.raises(ValueError, match=r"Invalid reach: 0. Must be greater than 0."):
        create_boxer(name="Boxer Name", weight=150, height=70, reach=0, age=25)

    with pytest.raises(ValueError, match=r"Invalid reach: -10. Must be greater than 0."):
        create_boxer(name="Boxer Name", weight=150, height=70, reach= -10, age=25)

    
def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with an invalid age (e.g., less than 18 or greater than 40)

    """
    with pytest.raises(ValueError, match=r"Invalid age: 17. Must be between 18 and 40."):
        create_boxer(name="Boxer Name", weight=150, height=70, reach=10, age=17)

    with pytest.raises(ValueError, match=r"Invalid age: 41. Must be between 18 and 40."):
        create_boxer(name="Boxer Name", weight=150, height=70, reach=10, age=41)

    
### Delete
def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the database by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)
    
    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)
    
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]
    
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."
    
def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent boxer.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)
    
######################################################
#
#    Get Leaderboard, Boxer, Weightclass
#
######################################################

### Leaderboard - come back to this
def test_get_leaderboard_sorted_by_wins(mock_cursor):
    """ Test getting the leaderboard sorted by wins.
    
    """
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 200, 70, 10, 25, 10, 5, .5),
        (2, "Boxer B", 210, 65, 12, 30, 4, 3, .75),
        (3, "Boxer C", 220, 75, 14, 35, 8, 2, .25)
    ]
    
    leaderboard = get_leaderboard('wins')
    
    expected_result = [
        {"id": 1, "name": "Boxer A", "weight": 200, "height": 70, "reach": 10, "age": 25, "weight_class": "MIDDLEWEIGHT", "fights": 10, "wins": 5, "win_pct": 50.0},
        {"id": 2, "name": "Boxer B", "weight": 210, "height": 65, "reach": 12, "age": 30, "weight_class": "HEAVYWEIGHT", "fights": 4, "wins": 3, "win_pct": 75.0},
        {"id": 3, "name": "Boxer C", "weight": 220, "height": 75, "reach": 14, "age": 35, "weight_class": "HEAVYWEIGHT", "fights": 8, "wins": 2, "win_pct": 25.0},
    ]
    
    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_sorted_by_win_pct(mock_cursor):
    """ Test getting the leaderboard sorted by win_pct.
    
    """
    mock_cursor.fetchall.return_value = [
        (2, "Boxer B", 210, 65, 12, 30, 4, 3, .75),
        (1, "Boxer A", 200, 70, 10, 25, 10, 5, .5),
        (3, "Boxer C", 220, 75, 14, 35, 8, 2, .25)
    ]
    
    leaderboard = get_leaderboard('win_pct')
    
    expected_result = [
        {"id": 2, "name": "Boxer B", "weight": 210, "height": 65, "reach": 12, "age": 30, "weight_class": "HEAVYWEIGHT", "fights": 4, "wins": 3, "win_pct": 75.0},
        {"id": 1, "name": "Boxer A", "weight": 200, "height": 70, "reach": 10, "age": 25, "weight_class": "MIDDLEWEIGHT", "fights": 10, "wins": 5, "win_pct": 50.0},
        {"id": 3, "name": "Boxer C", "weight": 220, "height": 75, "reach": 14, "age": 35, "weight_class": "HEAVYWEIGHT", "fights": 8, "wins": 2, "win_pct": 25.0},
    ]
    
    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY win_pct DESC
    """)
    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    
def test_get_leaderboard_bad_sortby(mock_cursor):
    """ Test getting the leaderboard sorted by an invalid parameter. (should cause error)
    
    """
    with pytest.raises(ValueError, match="Invalid sort_by parameter: losses"):
        get_leaderboard("losses")
    
### Get Boxer by ID
def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 150, 70, 10, 25)
    
    result = get_boxer_by_id(1)
    
    expected_result = Boxer(1, "Boxer Name", 150, 70, 10, 25)
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    

def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent song.

    """
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

### Get Boxer by Name
def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 150, 70, 10, 25)

    result = get_boxer_by_name("Boxer Name")
    
    expected_result = Boxer(1, "Boxer Name", 150, 70, 10, 25)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name",)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

    
def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent song.

    """
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer 'Boxer Name' not found."):
        get_boxer_by_name("Boxer Name")

    
### get Weightclass
def test_get_weight_class_heavyweight():
    assert get_weight_class(210) == "HEAVYWEIGHT"

def test_get_weight_class_middleweight():
    assert get_weight_class(170) == "MIDDLEWEIGHT"

def test_get_weight_class_lightweight():
    assert get_weight_class(150) == "LIGHTWEIGHT"

def test_get_weight_class_featherweight():
    assert get_weight_class(130) == "FEATHERWEIGHT"
        
def test_get_weight_class_invalid():
    with pytest.raises(ValueError, match="Invalid weight: 120. Weight must be at least 125."):
        get_weight_class(120)


######################################################
#
#    Update stats
#
######################################################

def test_update_boxer_stats_win(mock_cursor):
    """Test updating the record of boxer when result is a win.

    """
    mock_cursor.fetchone.return_value = True
    boxer_id = 1
    update_boxer_stats(boxer_id, "win")
    
    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_boxer_stats_loss(mock_cursor):
    """Test updating the record of boxer when result is a loss.

    """
    mock_cursor.fetchone.return_value = True
    boxer_id = 1
    update_boxer_stats(boxer_id, "loss")
    
    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_boxer_stats_invalid_result(mock_cursor):
    """Test updating the record of boxer when result is invalid.

    """
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'"):
        update_boxer_stats(1, "draw")
    

def test_update_boxer_stats_bad_name(mock_cursor):
    """Test updating the record of boxer when result is invalid.

    """
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
        update_boxer_stats(1, "win")
    