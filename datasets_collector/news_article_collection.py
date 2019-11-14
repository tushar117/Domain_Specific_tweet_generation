from newspaper import Article, Config
import json
from datetime import datetime
from tqdm import tqdm
import os


def load_error_tweet_ids(topic_name, error_file_path, debug=False):
    error_file_names = []
    try:
        if os.path.isfile(error_file_path):
            with open(error_file_path, 'r', encoding='utf-8') as error_file:
                tweet_ids = error_file.readlines()
                error_file_names = ["{}_{}_{}".format(topic_name, str(tweet_id).strip(), 'news') for tweet_id in tweet_ids] 
    except Exception as e:
        if debug:
            print('[error] : while reading tweet error file : %s' % (str(e)))
    return error_file_names

def write_to_error_file(error_file_path, tweet_ids, debug=False):
    if len(tweet_ids)==0:
        return
    try:
        with open(error_file_path, 'a+', encoding='utf-8') as error_file:
            for tweet_id in tweet_ids:
                error_file.write("%d\n" % (tweet_id))
    except Exception as e:
        if debug:
            print('[error] : while writing tweet_id to error file : %s' % (str(e)))

def news_extraction(topic_name, exception_file_name, root_location, tweets_location, dataset_location, retry_error=False):
    #formally used for multiprocessing if tweet count is large
    process_id = 0
    exception_file = exception_file_name+'-'+str(process_id)+'.txt'
    file_list = os.listdir(os.path.abspath(tweets_location))
    news_file_list = os.listdir(os.path.abspath(dataset_location))
    print('[INFO] working on the news article extraction for topic -- %s -- with total tweet count %d' % (topic_name, len(file_list)))
    # print('sorting the files...')
    sorted(file_list)

    error_cases = 0
    empty_cases = 0
    already_extracted = 0
    success = 0
    error_tweet_ids = []

    #configuration for the newspaper module
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    config = Config()
    # uncomment below line when 403 status code is returned
    config.browser_user_agent = user_agent
    config.fetch_images = False
    config.request_timeout = 15

    offset = len(file_list)
    start = process_id*offset
    end = start+offset
    total_file_count = (end - start) #len(file_list)
    # print('start : %d, end : %d' % (start, end))
    error_file_path = os.path.join(os.path.abspath(root_location), 'error_tweets.txt')
    error_file_names = load_error_tweet_ids(topic_name, error_file_path)
    pbar = tqdm(total=total_file_count)
    for the_file in file_list[start:end]:
        tweet_id = 0
        tweet_urls = []

        pbar.update(1)
        pbar.set_description('Success(%d) | Error(%d) | Empty(%d) | Already_done(%s)' % (success, error_cases, empty_cases, already_extracted))
        pbar.refresh()
        
        with open(os.path.join(os.path.abspath(tweets_location), the_file), 'r', encoding='utf-8') as tweet_file:
            tweet_info = json.load(tweet_file)
            tweet_id = tweet_info['id']
            tweet_urls = tweet_info['urls']
        
        file_name = "{}_{}_{}".format(topic_name, str(tweet_id), 'news')

        if tweet_id==0 or len(tweet_urls)==0:
            empty_cases +=1
            continue
    
        if file_name in news_file_list:
            #already extracted the article from news site
            already_extracted+=1
            continue
        if not retry_error and file_name in error_file_names:
            #already error occured
            error_cases += 1
            continue
        try:
            news_article = Article(tweet_urls[0], config=config)
            news_article.download()
            news_article.parse()
            news_content = news_article.text
            if len(str(news_content).strip()) == 0:
                empty_cases += 1
                continue 
            #write to the file
            with open(os.path.join(os.path.abspath(dataset_location), file_name), 'w', encoding='utf-8') as news_file:
                data = {
                    'title' : news_article.title,
                    'text': news_article.text,
                    'news_url' : tweet_urls[0],
                }
                json.dump(data, news_file)
            success += 1
        except Exception as e:
            error_cases +=1
            if file_name not in error_file_names:
                #new errors add to error list
                error_tweet_ids.append(tweet_id)
            with open(os.path.join(os.path.abspath(root_location), exception_file), 'a+', encoding='utf-8') as error_file:
                error_file.write("%s %s %s \n" % (tweet_urls[0], str(tweet_id), str(e)))
            continue
    write_to_error_file(error_file_path, error_tweet_ids)
    pbar.close()
    print('already extracted : %d, error cases : %d, empty cases : %d, success cases : %d' % (already_extracted, error_cases, empty_cases, (total_file_count - error_cases - empty_cases - already_extracted)))

def check_and_create_directory(dir_path):
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
            print('[Success] directory create : %s' % (dir_path))
        except Exception as e:
            print('[Abort] unable to create directory : %s' % (str(e)))
            return False
    else:
        print('directory %s already present, starting the news articles extraction.' % dir_path) 
    return True

def initialize():
    topic_names = ['sports', 'space-science']
    root_location = './Domain_Specific_tweet_generation/data/' 
    error_log_file_name = 'article_scrape_issue'

    for topic in topic_names:
        root_topic_location = root_location + topic
        tweets_location = root_topic_location + '/tweets'
        dataset_location = root_topic_location +'/news'
        if not os.path.isdir(os.path.abspath(tweets_location)):
            print('[ABORT] unable to find the tweets location for topic : %s at %s' % (topic, tweets_location))
            continue
        if check_and_create_directory(os.path.abspath(dataset_location)):
            news_extraction(topic, error_log_file_name, root_topic_location, tweets_location, dataset_location)

if __name__ == "__main__":
    initialize()