import time

# 5 minutes in nanoseconds
IDLE_LIMIT = 5 * 60 * 1e9


class Timer:
    def __init__(self):
        # initialize the active and idle time
        self.last_active_time = time.time_ns()

    def greater_than_idle_limit(self):
        """
        Return whether the idle time is greater than the idle limit.
        """
        return time.time_ns() - self.last_active_time > IDLE_LIMIT
