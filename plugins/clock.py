def load(config):
    return ClockModule(config)

class ClockModule():

    def __init__(self, config):
        self.config = config

    def update(self):
        pass
