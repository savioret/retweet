# -*- coding: utf-8 -*-
# Copyright © 2015 Carl Chenet <carl.chenet@ohmytux.com>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# Setup for Retweet
'''Setup for Retweet'''

# standard library imports
import os.path

# external library imports
from setuptools import setup

CLASSIFIERS = [
    'Intended Audience :: End Users/Desktop',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4'
]

setup(
    name='retweet',
    version='0.9',
    license='GNU GPL v3',
    description='twitter bot to retweet all tweets from a user based on Carl Chenet implentation',
    long_description='twitter bot to retweet all tweets from a user',
    classifiers=CLASSIFIERS,
    author='Miguel Martinez',
    author_email='rodilla@gmail.com',
    url='https://github.com/savioret/retweet',
    download_url='https://github.com/chaica/retweet',
    packages=['retweet'],
    scripts=['scripts/retweet'],
    install_requires=['tweepy>=3.5.0'],
    test_suite = 'tests',
)
