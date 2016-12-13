import tweepy
import ConfigParser
import argparse
import sqlite3

def get_config(cfg_file):
    config = ConfigParser.ConfigParser()
    options = config.read(cfg_file)
    if len(options) is 0:
        raise ValueError, "Oh no, you killed Kenny."
    return {
            "cKey": config.get("tweepy", "consumer_key"),
            "cSecret": config.get("tweepy", "consumer_secret"),
            "accToken": config.get("tweepy", "access_token"),
            "accTokenSecret": config.get("tweepy", "access_token_secret")
            }

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config-file", help="Config File",
            required=True)
    parser.add_argument("-u", "--user", help="@user", required=True)
    parser.add_argument("-db", "--database-file", help="Where is the DB file",
            required=True)
    parser.add_argument("-i", "--init-db", choices=("y", "n"), default="y",
            help="Create Database file. Default is y")
    return parser.parse_args()

def get_tweets(username, options):
    ''' Let us hope that options is truly a dict '''
    auth = tweepy.OAuthHandler(options["cKey"], options["cSecret"])
    auth.set_access_token(options["accToken"], options["accTokenSecret"])
    api =  tweepy.API(auth)
    user = api.get_user(username) #User object that we don't need
    tweets = []
    ''' Iteration AT ITS FINEST '''
    ''' At 250 you don't get temporarily banned. And this is nice '''
    cursoring_tweets = api.user_timeline(screen_name=username, count=250)
    tweets.extend(cursoring_tweets)
    last_id = tweets[-1].id - 1

    while len(cursoring_tweets) > 0:
        print "Latest ID is %s, and I'm fetching more" %(last_id)
        cursoring_tweets = api.user_timeline(
                screen_name=username,
                count=250,
                max_id=last_id
                )
        tweets.extend(cursoring_tweets)

        last_id = tweets[-1].id - 1

    return tweets

def query(query, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()

def create_db(db_name):
    try:
        print "Creating database %s" %(db_name)
        create_table = ''' CREATE TABLE tweets (id BIGINT, status TEXT)'''
        query(create_table, db_name)
    except sqlite3.OperationalError:
        print "Bro, seriously! Maybe check your cmd arguments?!"

def insert_tweets(tweets, db_name):
    print "Storing tweets"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for tweet in tweets:
        c.execute("INSERT INTO tweets (id, status) VALUES (?, ?)",
                (tweet.id, tweet.text))
        conn.commit()
    print "Done storing."
    conn.close()


if __name__ == "__main__":
    args = get_args()

    if args.init_db == 'y':
        create_db(args.database_file)
    config_opts = get_config(args.config_file)
    tweets = get_tweets(args.user, config_opts)
    insert_tweets(tweets, args.database_file)


