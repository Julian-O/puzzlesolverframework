class GameBoard(object):

    """Class that is responsible for maintaining all the Game-state"""

    # Not responsible for visualisation.
    # Not active.
    # Has friend GameBoardView

    def __init__(self, command_queue):
        self.command_queue = command_queue

    def is_solved(self):
        raise NotImplementedError()

    def solve(self, max_count=None, max_period=None):
        # maxPeriod is in seconds.
        self.command_queue.execute_many_commands(max_count, max_period)
