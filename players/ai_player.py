from players import BasePlayer


class AIPlayer(BasePlayer):
    def decide_action(self):
        raise NotImplementedError
