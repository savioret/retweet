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
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Validate class
'''Validate class'''

# standard library imports
import datetime
import os.path
import sys

# external library imports
import tweepy

# retweet library imports
from retweet.tweetwasposted import TweetWasPosted
from retweet.waitamoment import WaitAMoment


class Validate(object):
    '''Validate class'''
    def __init__(self, cfgvalues, args, api, tweet):
        '''send the tweet'''
        self.api = api
        self.args = args
        self.cfgvalues = cfgvalues
        self.storeit = False
        self.tweet = tweet
        self.twp = TweetWasPosted(self.cfgvalues)
        self.main()

    def main(self):
        '''Main of the Validate class'''
        try:
            # test if it was retweeted enough to be retweeted by me
            if len(self.api.retweets(self.tweet.id)) >= self.cfgvalues['retweets']:
                # send the tweet if all checks are ok
                if not self.notretweethashes() and self.retweetonlyifhashtags() and self.retweetonlyifolderthan() and self.retweetonlyifoyoungerthan():
                    self.storeit = True
                    if self.args.dryrun:
                        print("tweet {} sent!".format(self.tweet.id))
                    else:
                        # at last retweet the tweet
                        self.api.retweet(self.tweet.id)
                        if self.cfgvalues['like']:
                            self.api.create_favorite(self.tweet.id)
                else:
                    self.storeit = False
        except (tweepy.error.TweepError) as err:
            print("{}".format(err))
            print("the tweet is probably retweeted already. Twitter does not allow to retweet 2 times")
        finally:
            # now store the tweet
            if not self.twp.wasposted(self.tweet.id) and self.storeit:
                if not self.args.dryrun:
                    self.twp.storetweet(self.tweet.id, self.tweet.user.id)
                WaitAMoment(self.cfgvalues['waitminsecs'], self.cfgvalues['waitmaxsecs'])

    def notretweethashes(self):
        '''check if the tweet has a hash for not retweeting'''
        found = False
        # check if the current tweet contains a do-not-retweet hash
        for i in self.cfgvalues['dontretweethashes']:
            if '#{}'.format(i) in self.api.get_status(self.tweet.id).text:
                found = True
        return found

    def retweetonlyifhashtags(self):
        '''retweet only if the tweet has the following hashtag'''
        found = False
        if self.cfgvalues['onlyifhashtags']:
            # check if the current tweet contains one of the hashtags to be retweeted
            for i in self.cfgvalues['onlyifhashtags']:
                if '#{}'.format(i) in self.api.get_status(self.tweet.id).text:
                    found = True
        else:
            found = True
        return found

    def retweetonlyifolderthan(self):
        '''retweet only if the tweet is older than a number of minutes'''
        send = False
        if self.cfgvalues['olderthan']:
            # check if the tweet is older than a number of minutes
            now = datetime.datetime.utcnow()
            tweetbirth = self.api.get_status(self.tweet.id).created_at
            lapse = now - tweetbirth
            print("Tweet older lapse seconds", lapse.seconds)
            try:
                if (lapse.seconds / 60) > self.cfgvalues['olderthan']:
                    send = True
                else:
                    send = False
            except ValueError:
                send = False
        else:
            send = True
        return send

    def retweetonlyifoyoungerthan(self):
        '''retweet only if the tweet is younger than a number of minutes'''
        send = False
        if self.cfgvalues['youngerthan']:
            # check if the tweet is younger than a number of minutes
            now = datetime.datetime.utcnow()
            tweetbirth = self.api.get_status(self.tweet.id).created_at
            lapse = now - tweetbirth
            print("Tweet younger lapse seconds", lapse.seconds)
            try:
                if (lapse.seconds / 60) < self.cfgvalues['youngerthan']:
                    send = True
                else:
                    send = False
            except ValueError:
                send = False
        else:
            send = True
        return send
