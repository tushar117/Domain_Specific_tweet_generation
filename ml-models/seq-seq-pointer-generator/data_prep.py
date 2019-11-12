import json
import re

import os


def get_tweet_and_news(tweet_file_path,news_file_path):
    with open(tweet_file_path) as f:
        data = json.load(f)
    # Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
    tweet = data['full_text']
    tweet = tweet.rstrip('\r\n')
    tweet = re.sub('\W+',' ', tweet)
    #tweet = re.sub("\n|\r|\r\n", " ", tweet)
    if(os.path.exists(news_file_path)):
        with open(news_file_path) as f:
            data = json.load(f)
        # Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
        news = data['text']
        news = news.rstrip('\r\n')
        news = re.sub('\W+',' ', news)
        #news = re.sub("\n|\r|\r\n", " ", news)
        return tweet,news
    else:
        return None,None


tweet_directory_in_str = "tweets"
tweet_directory = os.fsencode(tweet_directory_in_str)

news_directory_in_str = "news"
news_directory = os.fsencode(news_directory_in_str)

final_tweets_file = "tweets.txt"
final_news_file = "news.txt"

out_file_tweets = open(final_tweets_file, "w")  # write mode
out_file_news = open(final_news_file, "w")  # write mode

for file in os.listdir(tweet_directory):
    tweet_filename = os.fsdecode(file)
    news_filename = tweet_filename.replace("tweet", "news")
    tweet_file_path = "tweets" + "/" + tweet_filename
    news_file_path = "news" + "/" + news_filename
    tweet,news = get_tweet_and_news(tweet_file_path,news_file_path)
    if((tweet is not None) and (news is not None) and len(news)>0 and len(tweet)>0):
        out_file_tweets.write(tweet + "\n")
        out_file_news.write(news + "\n")

out_file_tweets.close()
out_file_news.close()

# print(len(tweet_file_names))

# with open('tweets/politics_1146048975922798592_tweet') as f:
#   data = json.load(f)
# # Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
# text = data['full_text']
# text = text.rstrip('\r\n')
# text = re.sub("\n|\r|\r\n", " ", text)
# print(text)
