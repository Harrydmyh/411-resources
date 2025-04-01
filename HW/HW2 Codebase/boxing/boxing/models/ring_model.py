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
    A class to manage boxers in a ring fight.

    Attributes:
        ring (List[Boxer]): The list of boxers in the ring.
    """
    def __init__(self):
        """Initializes the RingModel with an empty list of boxers.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        if len(self.ring) < 2:
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
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

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
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

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
