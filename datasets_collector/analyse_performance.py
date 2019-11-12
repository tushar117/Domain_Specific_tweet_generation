import os
import re
from tqdm import tqdm
from rouge import Rouge
from nltk import word_tokenize
from nltk.translate.bleu_score import corpus_bleu
import sys

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
    filters = set(['(', '{', '[', ']', '}', ')', '=', '|', '?', ',', '+', '\'', '\\', '*', ';', '!', '\"', '%', '\n', '\r', '-', '_', ':', '#', '@', '.'])
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

def get_content_from_file(file_path):
    tweet_list = []
    with open(file_path, 'r+', encoding='utf-8') as txt_file:
        for line in txt_file.readlines():
            tweet_list.append(filter_content(line))
    return tweet_list

def remove_empty_tweets(reference, hypothesis):
    new_reference, new_hypothesis = [], []
    for index in range(len(reference)):
        # if both are non-empty then consider it as a valid tweet
        if len(reference[index].strip()) != 0 and len(hypothesis[index].strip()):
            new_reference.append(reference[index])
            new_hypothesis.append(hypothesis[index])
    return new_reference, new_hypothesis 

def calculate_scores(reference_file_path, hypothesis_file_path):
    rouge = Rouge()
    reference = get_content_from_file(reference_file_path)
    hypothesis = get_content_from_file(hypothesis_file_path)
    if len(reference) != len(hypothesis):
        print("reference and hypothesis are of different length, reference : %d - hypothesis : %d" % (len(reference), len(hypothesis)))
        return [-1, -1, -1, -1, -1], {'rouge-1' : {'f' : -1}}
    print("content length : reference [%d]  hypothesis [%d]" % (len(reference), len(hypothesis)))
    reference, hypothesis =  remove_empty_tweets(reference, hypothesis)
    print("filtered content length : reference [%d]  hypothesis [%d]" % (len(reference), len(hypothesis)))
    ##bleu scores >>
    ref_token_list = [[word_tokenize(entry)] for entry in reference]
    hypo_token_list = [word_tokenize(entry) for entry in hypothesis]
    print("--"*32)
    print("- original tweets vs predicted tweets -")
    corpus_stats = [corpus_bleu(ref_token_list, hypo_token_list, weights=(1, 0, 0, 0)),
                    corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 1, 0, 0)),
                    corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 0, 1, 0)),
                    corpus_bleu(ref_token_list, hypo_token_list, weights=(0, 0, 0, 1)),
                    corpus_bleu(ref_token_list, hypo_token_list)
                    ]

    print("individual bleu with 1-gram: %.2f" % corpus_stats[0])
    print("individual bleu with 2-gram: %.2f" % corpus_stats[1])
    print("individual bleu with 3-gram: %.2f" % corpus_stats[2])
    print("individual bleu with 1-gram: %.2f" % corpus_stats[3])
    print(">> cummulative bleu score: %.2f" % corpus_stats[4])
    print("--"*32)
    rouge_scores = rouge.get_scores(hypothesis, reference, avg=True)
    print("rouge :", rouge_scores)
    print("--"*32)
    return corpus_stats, rouge_scores

def init():
    if len(sys.argv) != 3:
        print("error : invalid number of argument passed [1] arguments required [2], need path to 1 > reference file and 2 > hypothesis file")
        return -1
    reference_file_path = sys.argv[1]
    hypothesis_file_path = sys.argv[2]
    calculate_scores(os.path.abspath(reference_file_path), os.path.abspath(hypothesis_file_path))

if __name__ == "__main__":
    init()