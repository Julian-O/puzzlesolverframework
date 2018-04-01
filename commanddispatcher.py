from collections import defaultdict
import time


class CommandDispatcher(object):

    """
       Allows calls to slow functions to be queued up in prioritised order
       for execution more systematically than a simple recursive call.
       """

    def __init__(self):
        # priority -> set (callback, cookie)
        self.queue_dictionary = defaultdict(lambda: set())

        # Count how many commands have been executed for debug purposes.
        self.debug_command_count = 0

    def __len__(self):
        return sum(len(value) for value in self.queue_dictionary.values())

    def push(self, callback, cookie, priority):
        item = (callback, cookie)
        self.queue_dictionary[priority].add(item)

    def execute_one_command(self):
        if not len(self):
            return

        top_priority = max(self.queue_dictionary.keys())
        (callback, cookie) = self.queue_dictionary[top_priority].pop()

        if not self.queue_dictionary[top_priority]:
            # No more items at this priority.
            del self.queue_dictionary[top_priority]

        self.debug_command_count += 1

        callback(cookie)

    def execute_many_commands(self, max_count=None, max_period=None):
        # max_count is the most number of Commands to run.
        # max_count is (floating point) max number of seconds.
        #   Commands won't start after that point. May overrun though.
        
        if not len(self):
            return

        count = 0
        if max_period is not None:
            target_end_time = (time.clock() + max_period)
#            print "finishing at ", target_end_time, time.clock()

        finished = False

        while not finished:
            self.execute_one_command()
            count = count + 1

            solved = len(self) == 0
            hit_max_count = (
                max_count is not None and count >= max_count)
            hit_time_limit = (
                max_period is not None and time.time() > target_end_time)
            
            #print "Completed step. Solved? %s. Max Steps? %s Max Time? %s" % (
            #    solved, hit_max_count, hit_time_limit
            #)
            finished = solved or hit_max_count or hit_time_limit

    def __str__(self):
        return "%s(Num Of Priorities=%d, Num Executed=%d)" % (
            self.__class__.__name__,
            len(self),
            self.debug_command_count,
        )
