class Decision:
    def __init__(self, action_type, card=None, target_player=None, target_organ=None):
        self.action = action_type
        self.card = card
        self.target_player = target_player
        self.target_organ = target_organ
