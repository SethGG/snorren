from .burger import Burger
from .herbergier import Herbergier
from .hoer import Hoer
from .nazi import Nazi
from .oma import Oma
from .pimp import Pimp
from .priester import Priester
from .scooterjeugd import Scooterjeugd
from .snor import Snor

roles = {
    Burger: (1, 5),
    Nazi: (1, 5),
    Snor: (0, 1),
    Herbergier: (0, 1),
    Priester: (0, 1),
    Hoer: (0, 1),
    Pimp: (0, 1),
    Scooterjeugd: (0, 1),
    Oma: (0, 1)}
