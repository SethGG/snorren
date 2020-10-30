from roles.burger import Burger


class Oma(Burger):
    name = "Oma"

    def __init__(self):
        Burger.__init__(self)
