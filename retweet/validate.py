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
from retweet.tweetcache import TweetCache
from retweet.waitamoment import WaitAMoment


class Validate(object):
    '''Validate class'''
    def __init__(self, cfgvalues, args, api, tweet):
        '''send the tweet'''
        self.api = api
        self.args = args
        self.cfgvalues = cfgvalues
        self.postit = False
        self.tweet = tweet
        self.twp = TweetCache(self.cfgvalues)
        self.main()

    def main(self):
        '''Main of the Validate class'''
        try:
            # test if it was retweeted enough to be retweeted by me
            if self.tweet.retweet_count >= self.cfgvalues['retweets']:
                print("IHT:", self.has_invalid_hashtags(), "VHT:", 
                    self.has_valid_hashtags(),"OLD:", self.is_old_enough(), 
                    "YNG:",self.is_young_enough(), "BL:", self.is_blacklisted())
                # send the tweet if all checks are ok
                invalid = self.tweet.retweeted or \
                    self.has_invalid_hashtags() or not self.has_valid_hashtags() \
                    or not self.is_old_enough() or not self.is_young_enough() \
                    or self.is_blacklisted()
                self.postit = not invalid

                if self.postit:
                    if not self.args.dryrun:
                        # at last retweet the tweet
                        self.api.retweet(self.tweet.id)
                        if self.cfgvalues['like']:
                            self.api.create_favorite(self.tweet.id)
                    print("tweet {} sent!".format(self.tweet.id))


        except (tweepy.error.TweepError) as err:
            print("{}".format(err))
            print("the tweet is probably retweeted already. Twitter does not allow to retweet 2 times")
        finally:
            # now set the tweet as processed
            if not self.args.dryrun:
                self.twp.process_tweet(self.tweet.id, self.postit)
            if self.postit:
                WaitAMoment(self.cfgvalues['waitminsecs'], self.cfgvalues['waitmaxsecs'])

    def to_string(self):
        return "%s\n %s by %s RT:%d RTC:%d"%(
            self.tweet.text, self.tweet.created_at, self.tweet.user.screen_name,
            self.tweet.retweeted, self.tweet.retweet_count)

    def was_posted(self):
        return self.postit

    def is_blacklisted(self):
        '''check if the tweet has a authors for not retweeting'''
        return self.tweet.user.screen_name in self.cfgvalues['blacklist']

    def has_invalid_hashtags(self):
        '''check if the tweet has a hash for not retweeting'''
        found = False
        # check if the current tweet contains a do-not-retweet hash
        for i in self.cfgvalues['dontretweethashes']:
            if '#{}'.format(i) in self.tweet.text:
                found = True
        return found

    def has_valid_hashtags(self):
        '''retweet only if the tweet has the following hashtag'''
        found = False
        if self.cfgvalues['onlyifhashtags']:
            # check if the current tweet contains one of the hashtags to be retweeted
            for i in self.cfgvalues['onlyifhashtags']:
                if '#{}'.format(i) in self.tweet.text:
                    found = True
        else:
            found = True
        return found

    def is_old_enough(self):
        '''retweet only if the tweet is older than a number of minutes'''
        old = False
        if self.cfgvalues['olderthan']:
            # check if the tweet is older than a number of minutes
            now = datetime.datetime.utcnow()
            lapse = now - self.tweet.created_at
            print("OLD LAPSE:", lapse.seconds/60, "|", now, "|", self.tweet.created_at)
            try:
                if (lapse.seconds / 60) > self.cfgvalues['olderthan']:
                    old = True
                else:
                    old = False
            except ValueError:
                old = False
        else:
            old = True
        return old

    def is_young_enough(self):
        '''retweet only if the tweet is younger than a number of minutes'''
        young = False
        if self.cfgvalues['youngerthan']:
            # check if the tweet is younger than a number of minutes
            now = datetime.datetime.utcnow()
            lapse = now - self.tweet.created_at
            try:
                if (lapse.seconds / 60) < self.cfgvalues['youngerthan']:
                    young = True
                else:
                    young = False
            except ValueError:
                young = False
        else:
            young = True
        return young
