#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
# Copyright © 2015 Carl Chenet <chaica@backupcheckerproject.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Unit tests for Retweet
'''Unit tests for Retweet '''

import datetime
import sys
import unittest

from retweet.cliparse import CliParse
from retweet.confparse import ConfParse
from retweet.waitamoment import WaitAMoment

class TestRetweet(unittest.TestCase):
    '''TestRetweet class'''

    def test_getconfigfile(self):
        '''Test the CliParse class'''
        filepath = './tests.py'
        sys.argv[-1] = filepath
        clip = CliParse()
        self.assertEqual(clip.configfile, filepath)

    def test_getconfigvars(self):
        '''Test the ConfParse class'''
        confp = ConfParse('tests/getconfigvars/retweet.ini')
        self.assertEqual(confp.confvalues, {'user_to_retweet': 'journalduhacker',
                                            'consumer_key': '4s3nOBU7hUkPrTqeWzw6lxzC3',
                                            'consumer_secret': 'aoWjhD7UQcXfxipa2ufkypqiUle9cF0ZlaOngiOAiJyFb23Ftb',
                                            'access_token': '1370158707-m8eN2YcfVcKGfWmVLERDGMd1UPKHVPzAQHoP7qa',
                                            'access_token_secret': 'aB74LfWy551sRTU49buGE6YXIukY74TmBK6JLECeOA5ta',
                                            'retweets': 0,
                                            'waitminsecs': 2,
                                            'waitmaxsecs': 3,
                                            'sqlitepath': '/var/lib/retweet/retweet.db',
                                            'dontretweethashes': ['dnr']})
    def test_getconfigvarsnodnr(self):
        '''Test the ConfParse class'''
        confp = ConfParse('tests/getconfigvars/retweet-nodnr.ini')
        self.assertEqual(confp.confvalues, {'user_to_retweet': 'journalduhacker',
                                            'consumer_key': '4s3nOBU7hUkPrTqeWzw6lxzC3',
                                            'consumer_secret': 'aoWjhD7UQcXfxipa2ufkypqiUle9cF0ZlaOngiOAiJyFb23Ftb',
                                            'access_token': '1370158707-m8eN2YcfVcKGfWmVLERDGMd1UPKHVPzAQHoP7qa',
                                            'access_token_secret': 'aB74LfWy551sRTU49buGE6YXIukY74TmBK6JLECeOA5ta',
                                            'retweets': 0,
                                            'waitminsecs': 2,
                                            'waitmaxsecs': 3,
                                            'sqlitepath': '/var/lib/retweet/retweet.db',
                                            'dontretweethashes': []})
    def test_waitamoment(self):
        '''Test WaitAMoment class'''
        before = datetime.datetime.now()
        wam = WaitAMoment(1,2)
        after = datetime.datetime.now()
        res = after - before
        self.assertTrue(res.seconds >= 1)


#######################################################################################
#
# Testing the consistent given version of the software both in setup.py and cliparse.py
#
#######################################################################################

    def test_versionconsistency(self):
        '''test the consistency of the version of the software
           in both setup.py and README.MD
        '''
        with open('setup.py') as setuppy:
            setuppycode = setuppy.readlines()
        with open('README.md') as readme:
            readmecode = readme.readlines()
        for line in setuppycode:
            if 'version=' in line:
                setuppyversion = line.split("'")[1]
                break
        for line in readmecode:
            if 'retweet-' in line:
                readmeversion = line.split('retweet-')[1].split(".tar.gz")[0]
                break
        self.assertEqual(setuppyversion, readmeversion)

################################################################
#
# End of the unit tests
#
################################################################

if __name__ == '__main__':
    unittest.main()
