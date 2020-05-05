from roles import Burger, Nazi, Snor, Herbergier, Priester, Hoer, Pimp, Scooterjeugd, Oma

# ------------------------------------------------------------------------------------------------ #
# Global variables
# ------------------------------------------------------------------------------------------------ #

CURRENT_PHASE = None
GAME_MASTER = None
PLAYERS = {}
ROLES = {
    Burger: (1, 5),
    Nazi: (1, 5),
    Snor: (0, 1),
    Herbergier: (0, 1),
    Priester: (0, 1),
    Hoer: (0, 1),
    Pimp: (0, 1),
    Scooterjeugd: (0, 1),
    Oma: (0, 1)}
