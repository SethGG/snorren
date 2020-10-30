day_loop = [1, 3, 5, 7, 9]
night_loop = [2, 4, 6, 8, 0]
phase_stack = []


def game_loop():
    counter = 0
    while True:
        counter += 1
        if not phase_stack:
            phase_stack.extend(day_loop)
        while phase_stack:
            yield phase_stack.pop()
        phase_stack.extend(night_loop)
        while phase_stack:
            yield phase_stack.pop()
