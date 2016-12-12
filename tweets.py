import tweepy
import ConfigParser
import argparse

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
    parser.add_argument("-f", "--config_file", help="Config File")
    parser.add_argument("-u", "--user", help="@user")
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

if __name__ == "__main__":
    args = get_args()
    config_opts = get_config(args.config_file)
    print args.user
    get_tweets(args.user, config_opts)

