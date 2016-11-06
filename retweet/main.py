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

# Main class
'''Main class'''

# standard library imports
import configparser
import os.path
import sys
from operator import itemgetter

# external library imports
import tweepy

# retweet imports
from retweet.cliparse import CliParse
from retweet.confparse import ConfParse
from retweet.tweetwasposted import TweetWasPosted
from retweet.validate import Validate
from retweet.waitamoment import WaitAMoment


class Main(object):
    '''Main class'''
    def __init__(self):
        '''Constructor of the Main class'''
        # parse the command line
        rtargs = CliParse()
        self.args = rtargs.arguments
        # read the configuration file
        cfgparse = ConfParse(self.args.pathtoconf)
        self.cfgvalues = cfgparse.confvalues
        self.twp = TweetWasPosted(self.cfgvalues)

        # activate the twitter api
        self.auth = tweepy.OAuthHandler(self.cfgvalues['consumer_key'],
                                        self.cfgvalues['consumer_secret'])
        self.auth.secure = True
        self.auth.set_access_token(self.cfgvalues['access_token'],
                                    self.cfgvalues['access_token_secret'])
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.main()

    def update_cache_table(self, max_tweets=300):
        last_id = self.twp.get_last_cached_id()
        if not last_id:# is None or len(lasttweets) == 0:
            print("No cache, first lookup")
            # empty cache, look for a big amount of results
            lasttweets = self.api.search(self.cfgvalues['search_query'], count=100)
            count = len(lasttweets)
            self.twp.cache_tweets(lasttweets)
            while len(lasttweets) == 100 and count < max_tweets:
                WaitAMoment(1,1)
                #look for older than max_id
                max_id = lasttweets[len(lasttweets)-1].id - 1
                lasttweets = self.api.search(self.cfgvalues['search_query'], count=100, max_id=max_id)
                count += len(lasttweets)
                self.twp.cache_tweets(lasttweets)
        else:
            print("Updating table from ID %d", last_id)
            #look for newer than last_id
            lasttweets = self.api.search(self.cfgvalues['search_query'], count=100, since_id=last_id)
            count = len(lasttweets)
            self.twp.cache_tweets(lasttweets)
            while len(lasttweets) == 100 and count < max_tweets:
                WaitAMoment(1,1)
                #look for newer than last_id AND older than max_id
                max_id = lasttweets[len(lasttweets)-1].id - 1
                lasttweets = self.api.search(self.cfgvalues['search_query'], count=100, max_id=max_id, since_id=last_id)
                count += len(lasttweets)
                self.twp.cache_tweets(lasttweets)
        print("Added %d entries to cache table"%count)

    def fetch_oldest_unprocessed_tweets(self, max_tweets=100):
        ids = self.twp.get_oldest_unprocessed_ids(max_tweets)
        lasttweets = self.api.statuses_lookup(ids)

        #sorted(lasttweets, key=itemgetter('name', 'age'))
        lasttweets = sorted(lasttweets, key = lambda item: item.id)
        c = 0
        for id in ids:
            print("%s = %s"%(id, lasttweets[c].id))
            c+=1
        return lasttweets

    def main(self):
        '''Main of the Main class'''

        self.update_cache_table()

        last_processed = self.twp.get_last_processed(6)
        last_id=None
        if last_processed:
            # print("LASTPROC", last_processed)
            # last_id = last_processed[0]['id']
            # if last_id:
            #     print("Searching since ID", last_id)
            for tw in last_processed:
                self.cfgvalues['blacklist'].append(tw['name'])

        # get tweets based upon the cache table
        unprocessed = self.fetch_oldest_unprocessed_tweets()
        #lasttweets = self.api.search(self.cfgvalues['search_query'], count=100, since_id=last_id)

        for t in unprocessed:
            print(t.created_at)

        # extract the last tweet ids
        #lasttweetids = [tweet.id for tweet in lasttweets]
        #ordered_tweets = list(reversed(lasttweets))
        # see if the last tweet of twitter api was sent already
        #lasttweetid = ordered_tweets[0]
        print("Fetching %d tweets"%len(unprocessed))
        # if self.args.limit:
        #     # take the oldest N
        #     ordered_tweets = ordered_tweets[0:self.args.limit]
        #     print("Limiting to oldest %d tweets"%len(ordered_tweets))
        # tweetstosend = []

        # in_reply_to_user_id_str == None
        # in_reply_to_user_id_str
        # favorited = False
        # retweet_count
        # user.id

        posted_cnt = 0
        process_cnt = 0
        # test if the last tweets were posted
        for lasttweet in unprocessed:
            print("[%d/%d] Processing: "%(posted_cnt,process_cnt), lasttweet.id)
            v = Validate(self.cfgvalues, self.args, self.api, lasttweet)
            print(v.to_string()+"\n----------------------------------------")
            posted_cnt += 1 if v.was_posted() else 0
            process_cnt += 1
            if self.args.limit and posted_cnt >= self.args.limit:
                print("Reached posting limit of %d"%self.args.limit)
                break
        sys.exit(0)
