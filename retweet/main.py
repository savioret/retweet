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

import time
from datetime import datetime

# external library imports
import tweepy

# retweet imports
from retweet.cliparse import CliParse
from retweet.confparse import ConfParse
from retweet.tweetcache import TweetCache
from retweet.validate import Validate
from retweet.waitamoment import WaitAMoment

def show_pretty_table(data):
    col_width = max(len(str(word)) for row in data for word in row) + 2  # padding
    for row in data:
        print("".join(str(word).ljust(col_width) for word in row))

def show_sqlite_table(rows):
    tuples = []
    titles = []
    n = 0
    for r in rows:
        t = []
        for k,v in r.items():
            if n == 0:
                titles.append(k)
            if k == 'timestamp':
                v = datetime.fromtimestamp(int(v)).strftime('%Y/%m/%d %H:%M')
            t.append(v)
        if n == 0:
            tuples.append(titles)
        tuples.append(t)
        n += 1
    show_pretty_table(tuples)

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
        self.twp = TweetCache(self.cfgvalues)

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
        if not last_id:
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

    def fetch_oldest_unprocessed_tweets(self, max_tweets=100, exclude_users=[]):
        ids = self.twp.get_oldest_unprocessed_ids(max_tweets, exclude_users)
        lasttweets = []
        if len(ids):
            lasttweets = self.api.statuses_lookup(ids)
            lasttweets = sorted(lasttweets, key = lambda item: item.id)

        return lasttweets

    def cleanup_unexisting_tweets(self, max_tweets=100):
        ids = self.twp.get_oldest_unprocessed_ids(max_tweets)
        statuses = None
        remove = lasttweets = []
        if len(ids):
            lasttweets = self.api.statuses_lookup(ids)
            if lasttweets:
                statuses = [x.id for x in lasttweets]

        if statuses is not None:
            remove = set(ids) - set(statuses)

        if not self.args.dryrun:
            for tid in remove:
                self.twp.process_tweet(tid, 0)

        return remove

    def process_all(self):
        # users not to process (handled different to blacklisted users)
        exclude_users = []
        if self.cfgvalues['author_frequency']:
            last_posted = self.twp.get_last_posted(self.cfgvalues['author_frequency'])
            last_id=None
            if last_posted:
                for tw in last_posted:
                    exclude_users.append(tw['name'])
                print("Excluding from process: ", exclude_users)

        if self.args.tweet_id:
                unprocessed = self.api.statuses_lookup([self.args.tweet_id])
        else:
                # get API tweets based upon the cache table
                unprocessed = self.fetch_oldest_unprocessed_tweets(100, exclude_users)

        # for t in unprocessed:
        #     print(t.created_at)

        # extract the last tweet ids
        print("Fetching %d tweets"%len(unprocessed))

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

    def show_processed_tweets(self):
        num = self.args.limit if self.args.limit else 1000
        rows = self.twp.get_last_processed(num)
        show_sqlite_table(rows)

    def show_posted_tweets(self):
        num = self.args.limit if self.args.limit else 1000
        rows = self.twp.get_last_posted(num)
        show_sqlite_table(rows)

    def show_pending_tweets(self):
        num = self.args.limit if self.args.limit else 1000
        rows = self.twp.get_oldest_pending(num)
        show_sqlite_table(rows)


    def must_process_all(self):
        return self.args.purge is None \
            and self.args.throttle is None \
            and not self.args.list_processed \
            and not self.args.list_pending \
            and not self.args.list_posted

    def main(self):
        '''Main of the Main class'''

        print("\n----", time.strftime('%x %X'))

        if self.args.purge is not None:
            num =self.args.purge or 100
            removed = self.cleanup_unexisting_tweets(num)
            print("Removed %d unexisting tweets"%len(removed), removed)

        if self.args.throttle is not None:
            num = self.args.throttle or self.cfgvalues['author_frequency']
            removed = self.twp.remove_throttling_tweets(num, dryrun = self.args.dryrun)
            print("Removed %d throttling user tweets"%len(removed), removed)

        if self.args.list_pending:
            self.show_pending_tweets()

        if self.args.list_processed:
            self.show_processed_tweets()

        if self.args.list_posted:
            self.show_posted_tweets()

        if self.must_process_all():
            self.update_cache_table()
            self.process_all()

        sys.exit(0)
