from lobby import Lobby

# ------------------------------------------------------------------------------------------------ #
# Global variables
# ------------------------------------------------------------------------------------------------ #


class Manager:
    def __init__(self):
        self.game_master = None
        self.players = []
        self.current_phase = Lobby(self)
        self.phase_stack = []
        self.night_cycle = []
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
