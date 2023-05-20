import time


class Timer:
    def __init__(self, idle_limit):
        # initialize the active and idle time
        self.last_active_time = time.time_ns()

        self.idle_limit = idle_limit

    def greater_than_idle_limit(self):
        """
        Return whether the idle time is greater than the idle limit.
        """
        return time.time_ns() - self.last_active_time > self.idle_limit
