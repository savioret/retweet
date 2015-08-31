#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Launch Retweet
'''Launch Retweet'''

import sys
from retweet.main import Main


class Retweet(object):
    '''Retweet class'''
    def __init__(self):
        '''Constructor of the Retweet class'''
        self.main()

    def main(self):
        '''main of the Main class'''
        Main()

if __name__ == '__main__':
    Main()
    sys.exit(0)
