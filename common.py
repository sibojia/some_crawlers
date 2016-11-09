# coding=utf8
import sys

class ProgressPrinter(object):
    """simple logger"""
    def __init__(self, interval = 1000, prefix = '', target = 0):
        super(ProgressPrinter, self).__init__()
        self.prefix = prefix
        self.interval = interval
        self.counter = 0
        self.target = target

    def start(self, target = 0, interval = 0):
        self.counter = 0
        if target != 0: self.target = target
        if interval != 0: self.interval = interval
    def finish(self):
        sys.stderr.write(' done.\n')
        self.counter = 0
    def tick(self):
        self.counter += 1
        if self.counter % self.interval == 0:
            if self.target != 0:
                sys.stderr.write('\r' + str(self.prefix) + ' %d/%d ...'%(self.counter, self.target))
            else:
                sys.stderr.write('\r' + str(self.prefix) + ' %d ...'%self.counter)
    def set_interval(self, interval):
        self.interval = int(interval)
