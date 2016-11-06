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

'''Was this tweet posted before'''

# external library imports
import sqlite3 as lite
import time

class TweetWasPosted:
    '''Was this tweet posted before'''
    def __init__(self, cfgvalues):
        '''Constructor of the TweetWasPosted'''
        self.cfgvalues = cfgvalues
        # activate the sqlite db
        print("Opening database %s"%self.cfgvalues['sqlitepath'])
        self.con = lite.connect(self.cfgvalues['sqlitepath'])
        #self.cur = con.cursor()
        self.create_all()

    def __del__(self):
        print("Closing database connection")
        self.con.close()

    def create_all(self):
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='senttweets'")
        exists = cur.fetchone()

        if exists[0] == 0:
            cur = self.con.cursor()
            cur.execute("""CREATE TABLE senttweets
                (id INTEGER(8) PRIMARY KEY, name TEXT, posted INT, processed INT, timestamp INT)""")
            self.con.commit()
            print("Creating table")

    def last_processed_id(self):
        v = self.get_last_processed()
        if v and len(v):
            return v[0]['id']

    # ordered by ascending ID
    def get_oldest_unprocessed_ids(self, num):
        cur = self.con.cursor()
        cur.execute("""SELECT id
            FROM senttweets
            WHERE processed = 0
            ORDER BY id ASC LIMIT 0,?""", (num,))
        rows = cur.fetchall()
        ids = []
        for row in rows:
            ids.append(row[0])

        return ids

    def get_last_cached_id(self):
        #self.con.row_factory = lite.Row
        cur = self.con.cursor()
        cur.execute("SELECT MAX(id) FROM senttweets")
        res = cur.fetchone()
        if res:
            return res[0]

    def get_last_processed(self, num):
        #self.con.row_factory = lite.Row
        cur = self.con.cursor()
        cur.execute("""SELECT id, name, posted, timestamp 
            FROM senttweets 
            WHERE processed = 1
            ORDER BY id DESC LIMIT 0,?""", (num,))
        res = []
        for row in cur:
            res.append({
                'id':row[0], 
                'name':row[1], 
                'posted':row[2], 
                'timestamp':row[3]})
        return res
        #return cur.fetchall()

    def is_stored(self, tweet_id):
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM senttweets WHERE id=?", (tweet_id,))
        twinfo = cur.fetchone()
        '''Was this tweet posted already'''
        if twinfo[0]:
            return True
        else:
            return False

    def cache_tweets(self, tweets):
        for t in tweets:
            self.store_tweet(t.id, t.user.screen_name, 0, 0)

    def process_tweet(self, tweet_id, posted, processed=1):
        cur = self.con.cursor()
        cur.execute("UPDATE senttweets SET posted=?, processed=?, timestamp=?) WHERE id=?", 
            (posted, processed, int(time.time()), int(tweet_id)))
        self.con.commit()

    def store_tweet(self, tweet_id, name, posted, processed):
        cur = self.con.cursor()
        cur.execute("INSERT INTO senttweets(id, name, posted, processed, timestamp) VALUES (?,?,?,?,?)", 
            (int(tweet_id), name, posted, processed, int(time.time())))
        self.con.commit()

