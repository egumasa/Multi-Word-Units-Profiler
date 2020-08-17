#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 15:39:23 2020

@author: eguchimasaki

version 1.52: 
	- spacy process added
	- Color codes
	- External link to LexTutor Concordancer using url_for() in Flask

"""


#for main
import pickle
import re
import spacy
nlp = spacy.load("en_core_web_md", disable=["ner", "textcat"])
#for development test

DIR_ = '/Users/eguchimasaki/Dropbox/0_Projects/009_MWU_profiler'
#INDEX = "index_0.3.html"
INDEX = "index_0.4_conc_spin.html"

#from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, Markup, redirect
app = Flask(__name__)
#bootstrap = Bootstrap(app)

## html template setting
#html = open("templates/index_flask_boot.html").read()
#template = Template(html)


## loading lists
resource = {"AFL_all": "An Academic Formulas list (Simpson-vlach & Ellis, 2010)",
			"PHRASAL": "A Phrasal Expressions List (Martinez & Schmitt, 2012)",
			"Biber_2004": "Lexical Bundles in University language (Biber et al., 2004)"}

AFL_all = pickle.load(open("resource/AFL_all.pickle","rb"))
PHRASAL = pickle.load(open("resource/PHRASAL_list.pickle","rb"))
Biber_2004 = pickle.load(open("resource/Biber_et_al_2004.pickle","rb"))


headers = pickle.load(open("resource/header_0.3.pickle","rb"))

color_codes = {"rank": {1: "color:#FF003C",
						2: "color:#FF8A00",
						3: "color:#FABE28",
						4: "color:#88C100",
						5: "color:#00C176"},
	}


def token_dictor(token_dict, token):
	token_dict[token.i] = {'word': token.text, 
						'lemma': token.lemma_,
						'style': ['color:black'],
						"pos": token.pos_,
						"tag": token.tag_,
						"dep": token.dep_,
						"head": token.head.i,
						} #


def ngram(doc, number, connect = "__"):
	#if you want to examine the contexts in which the ngram occurs, store POS of the head.
	
	ngram_dict = {} 
	last_index = len(doc) - 1 #this will let us know what the last index number is
	
	for token in doc: #iterate the tokenized text (i.e., Spacy doc obj)
	
		if token.i + number > last_index: #if the next index doesn't exist (because it is larger than the last index)
			continue
		else:
			ngram = [w.text for w in doc[token.i : token.i+number]] #the ngram will start at the current word, and continue until the nth word
			ngram_string = connect.join(ngram) #turn list of words into an n-gram string

			ngram_id = tuple(w.i for w in doc[token.i : token.i+number]) #store token ids for text mark-up

			#storing lemma
			ngram_lemm = []
			for w in doc[token.i : token.i+number]:
				if w.lemma_ == "-PRON-":
					ngram_lemm.append(w.text)
				#if w.lemma_ == "be":
					#ngram_lemm.append(w.text)
				else:
					ngram_lemm.append(w.lemma_)

			ngram_lemm_string = connect.join(ngram_lemm)
			
			'''Change this into type'''
			if ngram_string not in ngram_dict: # create an entry in ngram dict
				ngram_dict[ngram_string.lower()] = {'type': ngram_string,
											'lemma': ngram_lemm_string,
											'loc': [ngram_id],}
			else:
				ngram_dict[ngram_string.lower()]['loc'].append(ngram_id) #for the second occurrence (and later) we only need the token id info
	#print(ngram_dict)
	return(ngram_dict) #add ngram_list to master list


def namestr(obj, namespace): #this will return the variable name
	return [name for name in namespace if namespace[name] is obj]



def mwu_search2(matched_mwu: dict,text_mwu: dict, mwu_dict:dict) -> dict:
	'''
	
	Parameters
	----------
	matched_mwu: dict
		this is where we store the matched mwu information
		
	text_mwu : dict
		 contains extracted n-gram (or collocations) 
		
	mwu_dict : dict
		Resource that we use for mwu identifications.

	Returns
	-------
	matched_mwu
		updated dictionary
	'''
	mwu_dict_name = namestr(mwu_dict, globals())[0] #return mwu_dict name
	
	for mwu, mwu_info in text_mwu.items(): #iterate the text_mwu
		mwu_key = mwu
		mwu_lemma = mwu_info['lemma'].lower() #
		if (mwu.lower() not in mwu_dict):
			if (mwu_lemma not in mwu_dict):
				continue
			else:
				mwu = mwu_lemma
		if mwu not in matched_mwu[mwu_dict_name]: #see if the mwu is identified using other resources
			matched_mwu[mwu_dict_name][mwu] = {} #if this was the first one, create an entry
			matched_mwu[mwu_dict_name][mwu].update(text_mwu[mwu_key]) 
			
		matched_mwu[mwu_dict_name][mwu].update(mwu_dict[mwu]) #finally transfer info from resource.
	#print(matched_mwu)
	return(matched_mwu)



def color_AFL(freq_level, colo_code):
	if freq_level == "Core":
		return color_codes['rank'][1]
	if freq_level == "Spoken":
		return color_codes['rank'][3]
	if freq_level == "Written":
		return color_codes['rank'][3]

def color_phrasal(freq_level, colo_code):
	if freq_level == "1-K":
		return color_codes['rank'][1]
	if freq_level == "2-K":
		return color_codes['rank'][2]
	if freq_level == "3-K":
		return color_codes['rank'][3]
	if freq_level == "4-K":
		return color_codes['rank'][4]
	if freq_level == "5-K":
		return color_codes['rank'][5]

def color_biber(freq_level, colo_code):
	if freq_level == "Over 100":
		return color_codes['rank'][1]
	if freq_level == "40–99":
		return color_codes['rank'][2]
	if freq_level == "20–39":
		return color_codes['rank'][3]
	if freq_level == "10–19":
		return color_codes['rank'][4]
	if freq_level == "–":
		return color_codes['rank'][5]


def overwrite_color(token_loc, color, token_info):
	for loc in token_loc:
		for token_id in loc:
			if token_info[token_id]['style'][0] == 'color:black':
				token_info[token_id]['style'][0] = color



def update_token_info2(matched_mwus, token_info):
	
	if len(matched_mwus['PHRASAL']) > 0:
	
		for mwu, item_info in matched_mwus['PHRASAL'].items():
			token_loc = item_info["loc"]
			rank = item_info['Frequency Level']
			color = color_phrasal(rank, color_codes)
			overwrite_color(token_loc, color, token_info)
			matched_mwus['PHRASAL'][mwu]['Frequency Level'] = Markup(re.sub(r'{}'.format(rank), r"<span style='{}'>".format(color) + rank + "</span>", rank))
			
	if len(matched_mwus['AFL_all']) > 0:
		for mwu, item_info in matched_mwus['AFL_all'].items():
			token_loc = item_info["loc"]
			rank = item_info['Sub-list']
			color = color_AFL(rank, color_codes)
			overwrite_color(token_loc, color, token_info)
			matched_mwus['AFL_all'][mwu]['Sub-list'] = Markup(re.sub(r'{}'.format(rank), r"<span style='{}'>".format(color) + rank + "</span>", rank))
			
	if len(matched_mwus['Biber_2004']) > 0:
		for mwu, item_info in matched_mwus['Biber_2004'].items():
			token_loc = item_info["loc"]
			rank = item_info['Frequency in Conversation']
			color = color_biber(rank, color_codes)
			overwrite_color(token_loc, color, token_info)
			matched_mwus['Biber_2004'][mwu]['Frequency in Conversation'] = Markup(re.sub(r'{}'.format(rank), r"<span style='{}'>".format(color) + rank + "</span>", rank))


#text markup updated here
def token_mark_up(doc, token_info):
	holder = []

	for token in doc:
		string = "<span style='{}'>".format(token_info[token.i]['style'][0]) + str(token.text) + "</span>"
		holder.append(string)
	return Markup(" ".join(holder))
		



@app.route('/', methods=['GET', 'POST'])
def output_():

	if request.method == 'POST': #when text input is given
		res = {'list_select_error': ""}
		input_text = request.form.get('input_text', '')
		#selected_list = request.form.get('mwu_list', '')
		selected_list = request.form.getlist("mwu_list")
		#print(selected_list)

		if input_text:
			
			if len(selected_list) == 0: #When no lists were selected.
				res['input_text'] = input_text
				res['list_select_error'] = "Please select a list for analysis."
				return render_template(INDEX, res=res)

			''' holders '''
			token_info = {}
			#example = {"AFL_all": {}, "PHRASAL": {}, "Biber_2004": {}} #This will store MWEs 
			
			matched_mwus = {"PHRASAL": {}, "AFL_all": {}, "Biber_2004": {}} #equivalent to example in the earlier versions
			#preprocessing if any
			
			''' Tagging '''
			doc = nlp(input_text)

			for token in doc:
				token_dictor(token_info, token) 
			
			# This will extract ngram list
			ngram_holder = ngram(doc, 5, connect = " ")
			ngram_holder.update(ngram(doc, 4, connect = " "))
			ngram_holder.update(ngram(doc, 3, connect = " "))
			ngram_holder.update(ngram(doc, 2, connect = " "))
			
			#print(ngram_holder)
			
			'''Pattern matching component'''
			#then match the results and store in a dict
			#n-gram tokenization + identification -> token no. corresponds to n-grams
			if "AFL_all" in selected_list:
				mwu_search2(matched_mwus, ngram_holder, AFL_all) #alternative to the pattern matching
			if "PHRASAL" in selected_list:
				mwu_search2(matched_mwus, ngram_holder, PHRASAL)
			if "Biber_2004" in selected_list:
				mwu_search2(matched_mwus, ngram_holder, Biber_2004)


			update_token_info2(matched_mwus, token_info)


			
			''' text mark-up '''
			output_text = token_mark_up(doc, token_info)
			#print(output_text)
			
			''' Compile response data '''
			res = {'input_text' : input_text,
					'output' : output_text,
					'output_text': output_text.split(r"\s"),
					'resource': resource,
					'selected_list': [key for key in selected_list],
					'table_headers': headers['table'],
					'example': matched_mwus}
			
			return render_template(INDEX, res=res)
		
		
	return render_template(INDEX)

@app.route('/conc', methods=['GET', 'POST'])
def conc():
	search_str = request.args.get('search_str')
	#search_str = "+".join(search_str.split(" "))
	url = "https://www.lextutor.ca/cgi-bin/conc/wwwassocwords.pl?lingo=English&unframed=true&SearchType=equals&SearchStr={}&remLen_1=17&Corpus=coca_sampler&AssocWord=&Sinclair=4&AssocSide=either&blockers=&ColloSize=1&SortType=right&KeySort=&LineWidth=100&Maximum=499&Gaps=no_gaps&ScanWidth=5&ScanFreq=4".format(search_str)
	return redirect(url)


if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()



