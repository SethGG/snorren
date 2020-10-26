class Night:

    name = 'Nacht'
    steps = []

    class NightStart(BasePhase):

        name = 'NachtStart'

        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page',
                 render_template('game/night_start.html', num=self.parent.num, player=player),
                 room=player.sid)

    class NightEnd(BasePhase):

        name = 'NachtEinde'

        def __init__(self, parent):
            super().__init__(parent)

        def send_page(self, player=current_user):
            emit('update_page',
                 render_template('game/night_end.html', num=self.parent.num, player=player),
                 room=player.sid)

    def __init__(self, num):
        def get_prio(step):
            return step.priority

        self.num = num
        self.protected = {}
        self.target = None

        if not Night.steps:
            Night.steps = sorted({player.role.night_step for player in g.PLAYERS.values()
                                  if player.role.night_step}, key=get_prio)
            Night.steps = [self.NightStart] + Night.steps + [self.NightEnd]

        g.CURRENT_PHASE = self.steps[0](self)

    def start_next_phase(self):
        del self.steps[0]
        g.CURRENT_PHASE = self.steps[0](self)
