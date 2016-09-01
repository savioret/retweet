Use Retweet
==================
After the configuration of Retweet, just launch the following command::

    $ retweet /path/to/retweet.ini

Using the -l or --limit command line option, you can limit the retrieved statuses from Twitter::

    $ retweet -l 12 /path/to/retweet.ini

Using the --dry-run command line option allows not retweeting the tweets and not feed local SQLite database, for testing purpose::

    $ retweet --dry-run /path/to/retweet.ini
