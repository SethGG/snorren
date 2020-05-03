import globals as g


class Night:
    def __init__(self, num):
        self.night_num = num
        self.night_steps = {player.role.night_step for player in g.PLAYERS.values()
                            if player.role.night_step}
        print(self.night_steps)
