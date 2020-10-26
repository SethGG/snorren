from roles.burger import Burger
from roles.herbergier import Herbergier
from roles.hoer import Hoer
from roles.nazi import Nazi
from roles.oma import Oma
from roles.pimp import Pimp
from roles.priester import Priester
from roles.scooterjeugd import Scooterjeugd
from roles.snor import Snor
from lobby import Lobby
from flask_socketio import send
from random import shuffle

# ------------------------------------------------------------------------------------------------ #
# Global variables
# ------------------------------------------------------------------------------------------------ #


class Manager:
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

    def __init__(self):
        self.game_master = None
        self.players = []
        self.phase_stack = [Lobby]

        self.next_phase()

    def start_game(self, role_selection):
        pool = []
        for role, num in role_selection.items():
            obj = [x for x in self.roles if x.__name__ == role]
            pool.extend(obj * num)
        if len(pool) != len(self.players):
            send({'error': 'Opgegeven aantal rollen is ongelijk aan het aantal spelers.'})
        else:
            shuffle(pool)
            for idx, player in enumerate(self.players):
                player.role = pool[idx]()

    def next_phase(self):
        if self.phase_stack:
            self.current_phase = self.phase_stack.pop()(self)
    #    elif isinstance(self.current_phase, Lobby):

    def reset(self):
        self.__init__()
