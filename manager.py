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
from night import NightStart, NightEnd
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
        self.current_phase = Lobby(self)
        self.phase_stack = []
        self.night_cycle = [NightStart, NightEnd]
        self.day_cycle = []

    def start_game(self):
        pass

    def new_night(self, previous_day):
        pass

    def new_day(self, previous_night):
        pass

    def next_phase(self):
        if not self.phase_stack:
            if isinstance(self.current_phase, self.night_cycle[-1]):
                new_cycle = self.day_cycle
            else:
                new_cycle = self.night_cycle
            for phase in new_cycle:
                self.phase_stack.insert(0, phase(self))

        if self.phase_stack:
            self.current_phase = self.phase_stack.pop()
            for player in [p for p in self.players + [self.game_master] if p]:
                self.current_phase.send_page(player)
    #    elif isinstance(self.current_phase, Lobby):

    def reset(self):
        self.__init__()
