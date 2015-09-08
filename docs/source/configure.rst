Configure Retweet
=================

As a prerequisite to use Retweet, you need a Twitter app. Log in Twitter, go to https://apps.twitter.com, create an app and generate the access token.

In order to configure Retweet, you need to create a retweet.ini file (or any name you prefer, finishing with the extension .ini) with the following parameters::

    [main]
    screen_name_of_the_user_to_retweet=journalduhacker
    consumer_key=ml9jaiBnf3pmU9uIrKNIxAr3v
    consumer_secret=8Cmljklzerkhfer4hlj3ljl2hfvc123rezrfsdctpokaelzerp
    access_token=213416590-jgJnrJG5gz132nzerl5zerwi0ahmnwkfJFN9nr3j
    access_token_secret=3janlPMqDKlunJ4Hnr90k2bnfk3jfnwkFjeriFZERj32Z
    retweets = 0
    last_sent_tweet_id_file=lastsenttweet

- screen_name_of_the_user_to_retweet: the screen_name of the user to retweet (in @carl_chenet, it's carl_chenet)
- consumer_key: the Twitter consumer key (see your apps.twitter.com webpage)
- consumer_secret: the Twitter consumer secret key (see your apps.twitter.com webpage)
- access_token: the Twitter access token key (see your apps.twitter.com webpage)
- access_token_secret: the Twitter access token secret key (see your apps.twitter.com webpage)
- retweets: the minimal number of retweets the tweet needs to have in order we also retweet it
- waitminsecs: the minimal number of seconds to wait after processing a tweet
- waitmaxsecs: the maximal number of seconds to wait after processing a tweet
- last_sent_tweet_id_file: the file having the last sent tweet id in it (e.g /tmp/lastsenttweet)
