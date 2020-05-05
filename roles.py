import globals as g


class Burger:
    team = "Burgers"
    night_step = None
    day_step = None
    death_step = None


class Herbergier(Burger):
    class night_step:
        priority = 1

        @staticmethod
        def send_page():
            pass

        @staticmethod
        def handle_message(msg):
            pass


class Hoer(Burger):
    def __init__(self):
        Burger.__init__(self)


class Oma(Burger):
    def __init__(self):
        Burger.__init__(self)


class Pimp(Burger):
    def __init__(self):
        Burger.__init__(self)


class Priester(Burger):
    def __init__(self):
        Burger.__init__(self)


class Scooterjeugd(Burger):
    def __init__(self):
        Burger.__init__(self)


class Nazi:
    team = "Nazi's"
    night_step = None
    day_step = None
    death_step = None


class Snor(Nazi):
    def __init__(self):
        Nazi.__init__(self)
