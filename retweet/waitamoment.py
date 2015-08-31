'''Wait a moment before going on'''
import time
from random import randint

class WaitAMoment:
    '''Wait a moment before going on'''
    def __init__(self):
        '''Constructor of the WaitAMoment class'''
        self.min = 60
        self.max = 600
        self.main()

    def main(self):
        '''main of the WaitAMoment class'''
        waitsec = randint(self.min, self.max)
        time.sleep(waitsec)
