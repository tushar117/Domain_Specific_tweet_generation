import os
import json
import re
from nltk import word_tokenize
from nltk.translate.bleu_score import corpus_bleu
from tqdm import tqdm
from rouge import Rouge

def remove_urls(content):
    url_re = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    www_re = "www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    regex = re.compile(url_re)
    content = re.sub(regex, ' ', content)
    regex = re.compile(www_re)   
    content = re.sub(regex, ' ', content)
    return content

def remove_user_mention_and_hastag(content):
    regex = re.compile("[@#][a-zA-Z0-9]+")
    content = re.sub(regex, ' ', content)
    return content

def filter_content(content):
    #filter to remove irrelevant tokens
    filters = set(['(', '{', '[', ']', '}', ')', '=', '|', '?', ',', '+', '\'', '\\', '*', ';', '!', '\"', '%', '\n', '\r', '-', '_', ':', '#', '@'])
    content = content.strip()
    if len(content) == 0:
        return content
    #remove urls
    content = remove_urls(content)
    #reomve hashtags and user mentions
    content = remove_user_mention_and_hastag(content)
    
    if len(set(content).intersection(filters)) == 0:
        return content
    for elem in filters:
        content = content.replace(elem, ' ')
    return content

def get_tweet_info(root_data_location, file_name):
    tweet_info = {}
    file_name_token = file_name.split('_')
    tweet_file_name = "{}_{}_{}".format(file_name_token[0], file_name_token[1], 'tweet')
    tweet_folder = os.path.join(os.path.join(root_data_location, file_name_token[0]), 'tweets')
    with open(os.path.join(tweet_folder, tweet_file_name), 'r', encoding='utf-8') as tweet_file:
        tweet_info = json.load(tweet_file)
    return tweet_info

def analyse_news_article(root_data_location):
    rouge = Rouge()
    for topic_folder in os.listdir(root_location):
        # for calculating the similarity between tweets and article title
        reference = []
        hypothesis = []

        empty_title_count = 0
        empty_news_count = 0
        empty_article_average_length = 0
        empty_headline_average_length = 0

        average_article_length = 0
        average_headline_length = 0
        average_tweet_length = 0

        total_count = 0
        #check if its directory
        if not os.path.isdir(os.path.join(root_data_location, topic_folder)):
            # print(os.path.join(root_data_location, topic_folder))
            continue
        news_folder = os.path.join(os.path.join(root_data_location, topic_folder), 'news')
        print(">> working on topic : %s" % (topic_folder))
        news_collection = os.listdir(news_folder)
        total_count = len(news_collection)
        pbar = tqdm(total=total_count)
        for news_article in news_collection:
            news_file = os.path.join(news_folder, news_article)
            pbar.update(1)
            with open(news_file, 'r', encoding='utf-8') as txt_file:
                json_data = json.load(txt_file)
                title_data = filter_content(json_data['title'].strip())
                article_data = filter_content(json_data['text'].strip())
                #tweet information
                tweet_info = get_tweet_info(root_data_location, news_article)
                actual_tweet = tweet_info['full_text']
                processed_tweet = filter_content(actual_tweet)
                average_tweet_length += len(processed_tweet.split())
                if len(title_data.split()) == 0 or len(title_data) == 0:
                    empty_title_count += 1
                    # empty_article_average_length += len(article_data.split())
                elif len(article_data.split()) < 500:
                    empty_news_count += 1
                    empty_headline_average_length += len(title_data.split())
                    empty_article_average_length += len(article_data.split())
                else:
                    average_article_length += len(article_data.split())
                    average_headline_length += len(title_data.split())
                    reference.append(processed_tweet)
                    hypothesis.append(title_data)
                pbar.set_description('empty title: %d | empty article: %d' % (empty_title_count, empty_news_count))
                pbar.refresh()
        pbar.close()
        average_article_length = average_article_length/float(total_count - empty_title_count - empty_news_count)
        average_headline_length = average_headline_length/float(total_count - empty_title_count - empty_news_count)
        average_tweet_length = average_tweet_length/float(total_count)
        empty_article_average_length = empty_article_average_length/float(empty_news_count)
        empty_headline_average_length = empty_headline_average_length/float(empty_news_count)
        
        print("--"*32)
        print("total count : %d, empty title count : %d and empty news article count : %d" % (total_count, empty_title_count, empty_news_count))
        print("effective data : %d" % (total_count - empty_news_count - empty_title_count))
        print("average tweet length : %.2f" % (average_tweet_length))
        print("average headline length : %.2f, average article length : %.2f" % (average_headline_length, average_article_length))
        print("empty headline average length : %.2f, empty article average length : %.2f" % (empty_headline_average_length, empty_article_average_length))
        ##bleu scores >>
        ref_token_list = [[word_tokenize(entry)] for entry in reference]
        hypo_token_list = [word_tokenize(entry) for entry in hypothesis]
        print("--"*32)
        print("individual bleu with 1-gram: %.2f" % corpus_bleu(ref_token_list, hypo_token_list, weights=(1, 0, 0, 0)))
        print("individual bleu with 2-gram: %.2f" % corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 1, 0, 0)))
        print("individual bleu with 3-gram: %.2f" % corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 0, 1, 0)))
        print("individual bleu with 1-gram: %.2f" % corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 0, 0, 1)))
        print(">> cummulative bleu score: %.2f" % corpus_bleu(ref_token_list, hypo_token_list))
        print("--"*32)
        rouge_scores = rouge.get_scores(hypothesis, reference, avg=True)
        print("rouge :", rouge_scores)
        print("=="*32)

if __name__ == "__main__":
    root_location = os.path.abspath('./Domain_Specific_tweet_generation/data')
    analyse_news_article(root_location)