class Drone:
    def __init__(self, id: int):
        self.id = id
        self.hub_index = 0
        self.waiting = False
        self.finished = False
        self.drone_graphics = None
