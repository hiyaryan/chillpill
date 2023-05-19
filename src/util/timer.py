import time

import util.constants as constants


class Timer:
    def __init__(self):
        # initialize the active and idle time
        self.last_active_time = time.time_ns()

        self.idle_limit = constants.IDLE_LIMIT

    def greater_than_idle_limit(self):
        """
        Return whether the idle time is greater than the idle limit.
        """
        return time.time_ns() - self.last_active_time > self.idle_limit
