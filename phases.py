from flask_login import current_user, login_user
from cerberus import Validator
import globals as g


class DayNightBase:
    steps = None

    def handle_join(self, msg):
        def handle_player(name):
            if name in g.PLAYERS and not g.PLAYERS[name].is_active:
                g.PLAYERS[name].is_active = True
                login_user(g.PLAYERS[name])
                self.steps[0].send_page()

        def handle_game_master():
            if not g.GAME_MASTER.is_active:
                g.GAME_MASTER.is_active = True
                login_user(g.GAME_MASTER)
                self.steps[0].send_page()

        schema = {
            'type': {
                'type': 'string',
                'allowed': ['game master', 'player']
            },
            'name': {
                'type': 'string',
                'required': False,
                'dependencies': {'type': ['player']}
            }
        }
        v = Validator(schema)
        if v.validate(msg) and not current_user.is_authenticated:
            if msg['type'] == 'game master':
                handle_game_master()
            elif msg['type'] == 'player':
                handle_player(msg['name'])

    @staticmethod
    def handle_disconnect():
        current_user.is_active = False


class Night(DayNightBase):
    class NightStart:
        def send_page():
            pass

        def handle_message(msg):
            pass

    class NightEnd:
        def send_page():
            pass

        def handle_message(msg):
            pass

    def __init__(self, num):
        def get_prio(step):
            return step.priority

        for player in g.PLAYERS.values():
            print(player.name)
            print(player.info)

        self.num = num
        if not Night.steps:
            Night.steps = sorted({player.role.night_step for player in g.PLAYERS.values()
                                  if player.role.night_step}, key=get_prio)

    def start_next_step(self):
        del self.steps[0]
        if not self.steps:
            g.CURRENT_PHASE = Day(self.num)


class Day(DayNightBase):
    def __init__(self, num):
        def get_prio(step):
            return step.priority

        self.num = num
        if not Day.steps:
            Day.steps = sorted({player.role.day_step for player in g.PLAYERS.values()
                                if player.role.day_step}, key=get_prio)

    def start_next_step(self):
        del self.steps[0]
        if not self.steps:
            g.CURRENT_PHASE = Night(self.num + 1)
