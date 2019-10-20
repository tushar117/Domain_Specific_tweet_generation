#for sumy package
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# from sumy.summarizers.lsa import LsaSummarizer
# from sumy.summarizers.luhn import LuhnSummarizer
# from sumy.summarizers.edmundson import EdmundsonSummarizer
# from sumy.summarizers.kl import KLSummarizer
#from sumy.summarizers.lex_rank import LexRankSummarizer 
# from sumy.summarizers.sum_basic import SumBasicSummarizer
# from sumy.summarizers.reduction import ReductionSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import os,sys,re
import pandas as pd
import pickle
import json

handles=['TheEconomist','ReutersBiz','CNBC']
LANGUAGE = "english"
# summarizers_name_list=['lex_rank','luhn','lsa','kl','text_rank','sum_basic','reduction']
# summarizers_list=[LsaSummarizer,LexRankSummarizer,LuhnSummarizer,KLSummarizer,TextRankSummarizer,SumBasicSummarizer,ReductionSummarizer]

summarizers_name_list=['text_rank']
summarizers_list=[TextRankSummarizer]
SENTENCES_COUNT = 1

for hnd in handles:
    data_path="../data-business/"+hnd+"/final_data_json_news/"
    files=os.listdir(data_path)
    for ffi,ff in enumerate(files):
        if ffi%1000 == 0:
        	print(ffi,ff,hnd)
        with open(data_path+ff,"r") as ft:
            news_text=json.load(ft)
        for ssi,ss in enumerate(summarizers_list):
            stemmer = Stemmer(LANGUAGE)
            summarizer=ss(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)

            parser=PlaintextParser.from_string(news_text['text'],Tokenizer(LANGUAGE))
            with open("../data-business/data_summaries_1_sen/"+hnd+"_"+ff+"_"+summarizers_name_list[ssi],"w",encoding='utf-8') as fs:
                for eid,sentence in enumerate(summarizer(parser.document, SENTENCES_COUNT)):
                    fs.writelines(sentence._text)