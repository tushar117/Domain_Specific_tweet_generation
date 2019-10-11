from newspaper import Article, Config
import json
from datetime import datetime
from tqdm import tqdm
import os


def news_extraction(topic_name, exception_file_name, root_location, tweets_location, dataset_location):
    #formally used for multiprocessing if tweet count is large
    process_id = 0
    exception_file = exception_file_name+'-'+str(process_id)+'.txt'
    file_list = os.listdir(os.path.abspath(tweets_location))
    print('[INFO] working on the news article extraction for topic -- %s -- with total tweet count %d' % (topic_name, len(file_list)))
    # print('sorting the files...')
    sorted(file_list)

    error_cases = 0
    empty_cases = 0

    #configuration for the newspaper module
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    config = Config()
    # uncomment below line when 403 status code is returned
    # config.browser_user_agent = user_agent
    config.fetch_images = False
    config.request_timeout = 15

    offset = len(file_list)
    start = process_id*offset
    end = start+offset
    total_file_count = (end - start) #len(file_list)
    # print('start : %d, end : %d' % (start, end))

    pbar = tqdm(total=total_file_count)
    for the_file in file_list[start:end]:
        tweet_id = 0
        tweet_urls = []

        pbar.update(1)
        pbar.set_description('Error(%d) | Empty(%d)' % (error_cases, empty_cases))
        pbar.refresh()
        
        with open(os.path.join(os.path.abspath(tweets_location), the_file), 'r', encoding='utf-8') as tweet_file:
            tweet_info = json.load(tweet_file)
            tweet_id = tweet_info['id']
            tweet_urls = tweet_info['urls']
        if tweet_id==0 or len(tweet_urls)==0:
            empty_cases +=1
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
            file_name = "{}_{}_{}".format(topic_name, str(tweet_id), 'news')
            with open(os.path.join(os.path.abspath(dataset_location), file_name), 'w', encoding='utf-8') as news_file:
                data = {
                    'title' : news_article.title,
                    'text': news_article.text,
                    'news_url' : tweet_urls[0],
                }
                json.dump(data, news_file)
        except Exception as e:
            error_cases +=1
            with open(os.path.join(os.path.abspath(root_location), exception_file), 'a+', encoding='utf-8') as error_file:
                error_file.write("%s %s %s \n" % (tweet_urls[0], str(tweet_id), str(e)))
            continue
    pbar.close()
    print('error cases : %d, empty cases : %d, success cases : %d' % (error_cases, empty_cases, (total_file_count - error_cases - empty_cases)))

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