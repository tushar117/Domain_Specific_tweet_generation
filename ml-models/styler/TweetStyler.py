import os,sys,re
import numpy as np
import spacy as sc
import pandas as pd
import collections
import pickle
import dill
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import readability

class TweetStyler():
	def __init__(self):
		self.nlp = sc.load("en_core_web_md")
		self.analyzer = SentimentIntensityAnalyzer()
		self.spacy_stopwords = sc.lang.en.stop_words.STOP_WORDS
		self.pat_punct_remove=re.compile(r"[^\w' ]+")
		self.pat_extra_space=re.compile(r" {2,}")
		self.emojis_NRC={"anger":"X-(", "fear":"D:<", "anticipation":":^)", "trust":":|", "surprise":":-o", "sadness":":-(",
					"joy":":-D", "disgust":"D="}


	def clean_chunks(self,tt):
		tt=" ".join([tkn.lemma_ for tkn in tt])
		nn_punct=self.pat_extra_space.sub(r" ",self.pat_punct_remove.sub(r" ",tt).lower()).strip().split(" ")
		clean_tt=""
		for wrd in nn_punct:
			if wrd not in self.spacy_stopwords:
				clean_tt+=" "+wrd
		return clean_tt.strip()

	def get_hashtags(self,sp_text,frequent_n=5,num_hashtags=5):#spacy text
		hashtags_list=[]
		#remove punctuations and stopwords
		noun_words=[]
		noun_lemmas=[]

		for token in sp_text:
			if token.is_stop != True and token.is_punct != True and len(token.text.strip())>0 and token.pos_ == "NOUN":
				noun_words.append(token.text)
				noun_lemmas.append(token.lemma_)
		word_freq = collections.Counter(noun_words)
		lemma_freq= collections.Counter(noun_lemmas)
		total_words=sum(word_freq.values())
		total_lemma=sum(lemma_freq.values())

		frequent_lemma =[w[0] for w in lemma_freq.most_common(frequent_n)]
		candidate_np=collections.defaultdict(tuple)
		for chunk in sp_text.noun_chunks:
			chunk_lemma=" ".join([word.lemma_ for word in chunk])
			if any(word in chunk_lemma for word in frequent_lemma):
				cc=self.clean_chunks(chunk)
				ccs=cc.split(" ")
				if len(ccs)<=3:
					score=0.0
					for ww in ccs:
						score+=lemma_freq[ww]/total_lemma
					vs = styler.analyzer.polarity_scores(cc)
					candidate_np[cc]=(score/len(ccs),vs['pos'],vs['neg'],vs['compound'])
		hashtags_list=[("#"+re.sub(" ","",ht[0].title()),ht[1]) for ht in sorted(candidate_np.items(),key=lambda x:(x[1][3],x[1][0]),reverse=True)]
		#for hashtags consider one positive - top of the list , one negative - bottom of the list and one in the middle
		final_hashtags=[]
		top=0
		bottom=len(hashtags_list)-1
		flg_normal_pos=False
		flg_normal_neg=False
		for ii in range(num_hashtags):
			if ii%2==0 and flg_normal_pos==False:
				final_hashtags.append(hashtags_list[top])
				top+=1
				if hashtags_list[top][1][3]==0.0:
					flg_normal_pos=True
			elif (ii-1)%2==0 and flg_normal_neg==False:
				final_hashtags.append(hashtags_list[bottom])
				bottom-=1
				if hashtags_list[bottom][1][3]==0.0:
					flg_normal_neg=True
			else:
				final_hashtags.append(hashtags_list[top])
				top+=1
		return final_hashtags,candidate_np

	def get_url(self,candidates_nps,top_chunks=3,domain_name="business"):
		url_text=""
		top_nps=[re.sub(" ","_",tp[0]) for tp in sorted(candidates_nps.items(),key=lambda x:x[1][0],reverse=True)[:top_chunks]]
		url_text="http://www."+domain_name+".com/"+"_".join(top_nps)
		return url_text

	def read_NRC(self,ff):	
		NRCtext=pd.read_csv(ff,sep='\t',header=None)
		emotion_keys=np.unique(NRCtext[1])
		NRCd=collections.defaultdict(list)
		for idx,ll in NRCtext.iterrows():
			if ll[2] ==1:
				NRCd[ll[1]].append(ll[0])
		return NRCd

	def get_emojis(self,sp_text,NRCd,num_emotions=2):
		token_lemmas=collections.defaultdict(tuple)
		sent_list=['positive','negative']
		pos_score=[]
		neg_score=[]
		comp_score=[]
		emotions_count=collections.defaultdict(float)
		for token in sp_text:
			if token.is_stop != True and token.is_punct != True and len(token.text.strip())>0 and token.pos_ in ["NOUN","VERB"]:
				vs = styler.analyzer.polarity_scores(token.lemma_)
				token_lemmas[token.lemma_]=(vs['pos'],vs['neg'],vs['compound'])
				#pos_score.append(vs['pos'])
				#neg_score.append(vs['neg'])
				#comp_score.append(vs['compound'])
				for kk in NRCd.keys():
					if token.lemma_ in NRCd[kk] or token.text in NRCd[kk]:
						emotions_count[kk]+=1
		for kk in NRCd.keys():
			emotions_count[kk]/=len(token_lemmas)
		#pos_score_val=np.sum(pos_score)/len(np.where(np.array(pos_score)!=0.0)[0])
		#neg_score_val=np.sum(neg_score)/len(np.where(np.array(neg_score)!=0.0)[0])
		#comp_score_val=np.sum(comp_score)/len(np.where(np.array(comp_score)!=0.0)[0])
		return [em[0] for em in sorted(emotions_count.items(),key=lambda x:x[1],reverse=True) if em[0] not in sent_list][:num_emotions]


if ( __name__ == "__main__"):
	# flg_file=sys.argv[1]
	# if flg_file == "-f":
	#     input_file=sys.argv[2]
	#     with open(input_file,"r") as fin:
	#     	input_text=" ".join(fin.readlines()).strip()
	# else:
	# 	input_text=sys.argv[2]

	url_actual=False

	styler=TweetStyler()
	# input_text="Among other recommendations in the report, the ACCC the ACCC said the ACCC wanted privacy law updated to give people the right to erase personal data stored online, aligning Australia with some elements of the European Union’s General Data Protection Regulation."
	input_text='SYDNEY (Reuters) - Australia said it would establish the world’s first dedicated office to police Facebook Inc (FB.O) and Google (GOOGL.O) as part of reforms designed to rein in the U.S. technology giants, potentially setting a precedent for global lawmakers.\n \n The move tightens the regulatory screws on the online platforms, which have governments from the United States to Europe scrambling to address concerns ranging from anti-trust issues to the spread of “fake news” and hate speech.\n \n Australian Treasurer Josh Frydenberg said the $5 billion fine slapped on Facebook in the United States this month for privacy breaches showed regulators were now taking such issues extremely seriously.\n \n “These companies are among the most powerful and valuable in the world,” Frydenberg told reporters in Sydney after the release of a much-anticipated report on future regulation of the dominant digital platforms.\n \n “They need to be held to account and their activities need to be more transparent.”\n \n Canberra would form a special branch of the Australian Competition and Consumer Commission (ACCC), the antitrust watchdog, to scrutinize how the companies used algorithms to match advertisements with viewers, giving them a stronghold on the main income generator of media operators.\n \n The new office was one of 23 recommendations in the ACCC’s report, including strengthening privacy laws, protections for the news media and a code of conduct requiring regulatory approval to govern how internet giants profit from users’ content.\n \n Frydenberg said the government intended to “lift the veil” on the closely guarded algorithms the firms use to collect and monetize users’ data, and accepted the ACCC’s “overriding conclusion that there is a need for reform”.\n \n The proposals would be subject to a 12-week public consultation process before the government acts on the report, he added.\n \n Google and Facebook have opposed tighter regulation while traditional media owners, including Rupert Murdoch’s News Corp (NWSA.O), have backed reform.\n \n News Corp’s local executive chairman, Michael Miller, welcomed the “strength of the language and the identification of the problems”, and said the publisher would work with the government to ensure “real change”.\n \n Facebook and Google said they would engage with the government during the consultation process, but had no comment on the specific recommendations.\n \n FILE PHOTO: The Google logo is pictured at the entrance to the Google offices in London, Britain January 18, 2019. REUTERS/Hannah McKay/File Photo\n \n The firms have previously rejected the need for tighter regulation and said the ACCC had underestimated the level of competition for online advertising.\n \n FIVE INVESTIGATIONS ONGOING\n \n ACCC Chairman Rod Sims said the regulator had five investigations of the two companies under way, and “I believe more will follow”.\n \n He said he was shocked at the amount of personal data the firms collected, often without users’ knowledge.\n \n “There needs to be a lot more transparency and oversight of Google and Facebook and their operations and practices,” he said.\n \n Among other recommendations in the report, the ACCC said it wanted privacy law updated to give people the right to erase personal data stored online, aligning Australia with some elements of the European Union’s General Data Protection Regulation.\n \n “We cannot leave these issues to be dealt with by commercial entities with substantial reach and market power. It’s really up to government and regulators to get up to date and stay up to date in relation to all these issues,” Sims said.\n \n FILE PHOTO: Silhouettes of mobile users are seen next to a screen projection of the Facebook logo in this picture illustration taken March 28, 2018. REUTERS/Dado Ruvic/Illustration/File Photo\n \n While the regulator did not recommend breaking up the tech giants, Sims also did not rule it out.\n \n “If it turns out that ... divestiture is a better approach, then that can always be recommended down the track,” he said.'

	if isinstance(input_text, str):#if not spacy type then convert
		input_text=styler.nlp(input_text)

	with open("NRC_dict.pickle","rb") as fw:
		NRC_dict = dill.load(fw)

	hashtags,candidate_nounchunks=styler.get_hashtags(input_text)
	# print(hashtags)
	print("Hashtags:")
	for hh in hashtags:
		print(hh[0])
	    
	if url_actual==False:
		article_url=styler.get_url(candidate_nounchunks)
	else:
		article_url="https://t.co/MVHV69gKNr"
		print("provide actual article link")
	print("Article Url:")
	print(article_url)

	emotions_list=styler.get_emojis(input_text,NRC_dict)
	print("Emotions:")
	for em in emotions_list:
		print(em,styler.emojis_NRC[em])


	

	    
