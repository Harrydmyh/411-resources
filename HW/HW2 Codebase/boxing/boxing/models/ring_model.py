import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring of boxers.

    Attributes:
        ring (List[Boxer]): A list of boxer's in the ring

    """
    def __init__(self):
        """ Initializes the RingModel with an empty list of boxers.
        
        """
        self.ring: List[Boxer] = []
        

    def fight(self) -> str:
        """Returns the outcome of a simulation of two boxers fighting based off randomness and fighting skill, and updates their stats.
        
        Returns:
            str: The name of the winner of the fight.
        
        Raises:
            ValueError: If the number of boxers in the ring is less than 2.

        """
        if len(self.ring) < 2:
            logger.warning("There must be two boxers to start a fight.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        logger.info(f"Updated stats for winner: {winner.name} (ID: {winner.id})")
        update_boxer_stats(loser.id, 'loss')
        logger.info(f"Updated stats for loser: {loser.name} (ID: {loser.id})")

        self.clear_ring()
        logger.info(f"Successfully simulated winner of fight between boxers: {winner.name} and {loser.name}")
        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ringList.

        If the ringList is already empty, logs a warning.
        """
        logger.info("Received request to clear the ringList")
        if not self.ring:
            logger.warning("Clearing an empty playlist")
            return
        self.ring.clear()
        logger.info("Successfully cleared the ringList")

    def enter_ring(self, boxer: Boxer):
        """ Adds a boxer into the ring.

        Args:
            boxer (Boxer): The boxer observation.
        
        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If the ring is already full.

        """
        logger.info("Received request to add boxer to ring")
        
        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance.")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error("Ring is full, cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Successfully added boxer: {boxer.name} to the ring.")

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of all boxers in the ringList.

        Returns:
            List[Boxer]: A list of all boxers in the ringList.
        """
        logger.info("Retrieving all boxers in the ringList")
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Gets the fighting skill for a boxer.

        Args:
            boxer (Boxer): The boxer to calculate fighting skill score.

        Returns:
            float: A score to indicate the fighting skill of the boxer.
        """
        # Arbitrary calculations
        logger.info(f"Calculating fighting skill for boxer with ID {boxer.boxer_id}")
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
