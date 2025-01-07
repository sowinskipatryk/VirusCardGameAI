from players import BasePlayer


class HumanPlayer(BasePlayer):
    def decide_action(self):
        raise NotImplementedError
