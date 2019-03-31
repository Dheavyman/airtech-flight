from enum import Enum


class StatusChoices(Enum):
    """Choices for flight status

    Arguments:
        Enum {enum} -- Enum class
    """
    B = 'Booked'
    R = 'Reserved'
    C = 'Cancelled'
