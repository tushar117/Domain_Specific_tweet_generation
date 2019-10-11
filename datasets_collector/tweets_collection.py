import tweepy
import json
from datetime import datetime
from tqdm import tqdm
import os


def tweets_extraction(tweet_api, twitter_accounts_list, topic_name,  dataset_location, page_size=200, max_threshold=3000):
    user_required_fields_with_default = {
        'created_at': str(datetime.utcnow()),
        'id' : 0,
        'screen_name' : '',
        'name': '',
        'verified': False,
        'followers_count': 0,
        'friends_count': 0,
        'favourites_count': 0,
        'statuses_count': 0,
    }

    tweets_required_fields_with_default = {
        'created_at' : str(datetime.utcnow()),
        'id' : 0,
        'full_text': '',
        'retweet_count': 0, 
        'favorite_count': 0, 
        'lang': 'en', 
    }

    #url from tweets and hashtag are implicit part of the data collection
    for account_name in twitter_accounts_list:
        #initialize the internal variables
        total_tweets = 0
        empty_tweets = 0
        min_tweet_id = 1<<64
        first_pass = True
        
        #verify the account
        try:
            user_account_object = tweet_api.get_user(screen_name=account_name)
        except Exception as e:
            print('An error encountered with account %s : error : %s' % (account_name, str(e)))
            continue
        
        user_account_json = json.loads(json.dumps(user_account_object._json))
        user_data = {}
        for field in user_required_fields_with_default.keys():
            user_data[field] = user_account_json.get(field, user_required_fields_with_default[field])
        if user_data['statuses_count'] < max_threshold:
            print('[warning] %s has only %d tweets and current threshold is %d' % (account_name, user_data['statuses_count'], max_threshold))

        pbar = tqdm(total=min(max_threshold, user_data['statuses_count']))
        #extracting the tweets
        while (total_tweets < user_data['statuses_count']) and (total_tweets - empty_tweets) != max_threshold:
            if first_pass:
                user_tweets = tweet_api.user_timeline(screen_name=account_name, tweet_mode='extended', count=page_size)
                first_pass = False
            else:
                user_tweets = tweet_api.user_timeline(screen_name=account_name, tweet_mode='extended', count=page_size, max_id=min_tweet_id)

            if len(user_tweets) == 0:
                #no more tweets found
                break
            for tweet_object in user_tweets:
                total_tweets += 1
                extracted_data = {}
                tweet_json = json.loads(json.dumps(tweet_object._json))
                for field in tweets_required_fields_with_default.keys():
                    val = tweet_json.get(field, tweets_required_fields_with_default[field])
                    extracted_data[field] = val
                min_tweet_id = min(min_tweet_id, extracted_data['id'] - 1)
                #extracting the hashtags
                hashtags_text = []
                for hashtag_data in tweet_json['entities']['hashtags']:
                    hashtags_text.append(hashtag_data['text'])
                expanded_urls = []
                for url_data in tweet_json['entities']['urls']:
                    expanded_urls.append(url_data['expanded_url'])
                if len(expanded_urls) == 0:
                    #don't process further as it doesn't contain any link news article
                    empty_tweets +=1
                    # print('[', total_tweets, '] got an empty tweet > ', extracted_data['full_text'])
                    continue
                extracted_data['urls'] = expanded_urls
                extracted_data['hashtags'] = hashtags_text
                extracted_data['user'] = user_data
                # print('[', total_tweets, ']', extracted_data['full_text'])
                pbar.update(1)
                pbar.set_description("Progress [%s]" % (account_name))
                pbar.refresh()

                file_name = "{}_{}_{}".format(topic_name, str(extracted_data['id']), 'tweet')
                #writing to the file
                with open(os.path.join(os.path.abspath(dataset_location), file_name), 'w', encoding='utf-8') as txt_file:
                    json.dump(extracted_data, txt_file)

                if (total_tweets - empty_tweets) == max_threshold:
                    #sufficient number of tweets extracted
                    break
        pbar.close()
        print("[%s] total tweets explored : %d, tweets without url : %d, threshold_count : %d" % (account_name, total_tweets, empty_tweets, max_threshold))

def check_and_create_directory(dir_path):
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
            print('[Success] directory create : %s' % (dir_path))
        except Exception as e:
            print('[Abort] unable to create directory : %s' % (str(e)))
            return False
    else:
        print('directory %s already present, starting the tweets extraction.') 
    return True

def initialize():
    #Add dev credentials below
    twitter_keys = {
            'consumer_key':        '',
            'consumer_secret':     '',
            'access_token_key':    '',
            'access_token_secret': ''
    }
    #Setup access to API
    auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
    auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
    tweet_api = tweepy.API(auth)

    #configuration setting
    max_tweets = 3000    #max number of tweets to extract
    payload_size = 200     #number of tweets to extract in each request (max = 200)
    
    #domain and tweets handler mapping
    twitter_handles = {
        "sports" : ['toisports', 'TheHinduSports', 'IExpressSports', 'FirstpostSports'],
        "space-science" : ['SPACEdotcom', 'LiveScience', 'universetoday', 'SkyandTelescope'],
    }

    for topic_name, account_list in twitter_handles.items():
        dataset_location = './Domain_Specific_tweet_generation/data/'+ topic_name +'/tweets' 
        if check_and_create_directory(os.path.abspath(dataset_location)):
            tweets_extraction(tweet_api, account_list, topic_name, dataset_location, page_size=payload_size, max_threshold=max_tweets)

if __name__ == "__main__":
    initialize()