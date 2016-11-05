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
        print("exists", type(exists), exists)
        if exists[0] == 0:
            cur = self.con.cursor()
            cur.execute("CREATE TABLE senttweets(id INTEGER(8) PRIMARY KEY, user_id INTEGER(8), addded INT, timestamp INT)")
            self.con.commit()
            print("Creating table")

    def last_processed_id(self):
        cur = self.con.cursor()
        cur.execute("SELECT id FROM senttweets ORDER BY timestamp DESC LIMIT 1")
        twinfo = cur.fetchone()
        if twinfo is not None:
            return twinfo[0]

    def wasposted(self, tweet_id):
        print("TYPE",type(tweet_id), str(tweet_id))
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM senttweets WHERE id=?", (tweet_id,))
        twinfo = cur.fetchone()
        '''Was this tweet posted already'''
        if twinfo[0]:
            return True
        else:
            return False

    def storetweet(self, tweet_id, user_id, added):
        cur = self.con.cursor()
        cur.execute("INSERT INTO senttweets(id, user_id, timestamp) VALUES (?,?,?,?)", 
            (int(tweet_id), int(user_id), added, int(time.time())))
        self.con.commit()

