from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    A class to manage the attibutes of a boxer.

    Attributes:
        id (int): The id of the boxer.
        name (string): The name of the boxer.
        weight (int): The weight of the boxer.
        heiight (int): The height of the boxer.
        reach (float): The reach of the boxer.
        age (int): The age of the boxer.
        weight_class (string): The weight class of the boxer.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Initializes the BoxersModel with a weight class based on the boxer's weight.

        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new instance in the database of a boxer if inputs pass validation.
    
    Args:
        name (str): name of the boxer to add to database. Must be unique to the database.
        weight (int): The boxer's weight.
        height (int): The boxer's height.
        reach (float): The boxer's reach.
        age (int): The boxer's age.
    
    Raises:
        ValueError:
            If Weight is less than or equal to 125 lbs.
            If either Height or Reach is less than or equal to 0.
            If age is less than 18 or greater than 40
            If name is not unique
        sqlite3.IntegrityError: If name of boxer is already in database.
        sqlite3.Error: If any other database error occurs.
    """
    logger.info(f"Received request to add boxer with name {name}, {weight} lbs, height of {height}, reach of {reach}, and age of {age}")
    
    # Raise error unless height is greater than 125 lbs, height and reach are greater than 0, and age is between 18 and 40
    if weight < 125:
        logger.warning(f"Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.warning(f"Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning(f"Invalid reach: {reach}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.warning(f"Invalid age: {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to add new boxer with name '{name}'")

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")
            
            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Boxer '{name}' has successfully been added to database")

    except sqlite3.IntegrityError:
        logger.error(f"IntegrityError: Boxer '{name}' already exists in database")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f'Database Error while creating boxer: {e}')
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Permanently deletes a boxer from the catalog.

        Args:
            boxer_id (int): The ID of the boxer to delete.

        Raises:
            ValueError: If the boxer with the given ID does not exist.
            sqlite3.Error: If any database error occurs.

        """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Attempted to delete non-existent boxer with ID {boxer_id}")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Successfully deleted song with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves and returns a leaderboard list, ranking boxers by either wins or win percentage.
    
    Args:
        sort_by (str):  
            If 'wins', list wins in descending order. 
            If 'win_pct',  list win percentage in descending order.
    
    Returns:
        List[dict[str, Any]]: A descending list of boxers based on sort_by arg.
    
    Raises:
        ValueError: If the sort_by input is invalid.
        sqlite3.Error: If database error occurs.
        
    """
    logger.debug("Executing leaderboard query.")
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.warning(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve leaderboard")
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)
        logger.info(f"Successfully retrieved leaderboard.")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error occured while retrieving leaderboard")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the catalog by its boxer ID.

        Args:
            boxer_id (int): The ID of the boxer to retrieve.

        Returns:
            Boxer: The Boxer object corresponding to the boxer_id.

        Raises:
            ValueError: If the boxer is not found.
            sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer with ID {boxer_id}")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with ID {boxer_id} found")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.info(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving song by ID {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves information for a boxer by name
    
    Args:
        boxer_name (str): the name of the boxer.
    
    Returns: 
        Boxer: The boxer instance corresponding to boxer_name 
    
    Raises:
        ValueError: If boxer cannot be found.
        sqlite3.Error: In case any error in the database happens.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer with name {boxer_name}")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Boxer with name {boxer_name} found")
                return boxer
            else:
                
                logger.info(f"Boxer {boxer_name} not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Data base error while retrieving boxer: '{boxer_name}'")
        raise e


def get_weight_class(weight: int) -> str:
    """Returns the weight class of the given weight.

        Args:
            weight (int): The weight of a given boxer.

        Returns:
            String: The corresponding weight class for the weight.

        Raises:
            ValueError: If the weight inputed is less than 125.

    """
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Weight must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
    
    logger.info(f"The weight class for {weight} pounds is {weight_class}.")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """ Updates the stats of the boxer, incrementing wins depending if result was a win or loss.
    Args:
        boxer_id (int): the ID of the boxer to be incremented.

    Raises:
        ValueError: If boxer cannot be found
        sqlite3.Error: If database errors occur.

    """
    
    if result not in {'win', 'loss'}:
        logger.warning(f"Invalid result: {result}. Expected 'win' or 'loss'")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to update record for boxer with ID: {boxer_id}")

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Cannot update boxer's stats: Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            
            logger.info(f"Boxer incremented for boxer with ID: {boxer_id} ")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating stants for boxer with ID: {boxer_id}")
        raise e
