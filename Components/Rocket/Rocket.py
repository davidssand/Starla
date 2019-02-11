import sys

sys.path.append("/home/pi/Components")
from States.States import WaitingIgnition

class Rocket:
    """
    State machine of rocket
    """
    def __init__(self):
        # Starting with a default state.
        self.state = WaitingIgnition()

    '''def on_event(self, event):
        """
        Used for changing state of rocket
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)'''