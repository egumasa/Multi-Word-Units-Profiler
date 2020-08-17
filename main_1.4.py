#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 15:39:23 2020

@author: eguchimasaki

version 1.0: spacy process added
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 15:39:23 2020

@author: eguchimasaki
"""

#for main
import pickle
import re
import spacy
nlp = spacy.load("en_core_web_md", disable=["ner", "textcat"])
#for development test

DIR_ = '/Users/eguchimasaki/Dropbox/0_Projects/009_MWU_profiler'
#INDEX = "index_0.3.html"
INDEX = "index_0.4.html"

#from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, Markup
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


###.keys()
def pattern_matching(mwu_dict: dict, input_text: str) -> list:
	holder = []
	for mwu in mwu_dict.keys():
		match = re.findall(mwu, input_text.lower(), re.IGNORECASE)
		holder.extend(match)
	#print(holder)
	return holder


def dict_freq(example, mwu_dict, lst_name, matched_list, header):

	for item in matched_list:
		#print(mwu_dict[item])
		if item not in example[lst_name]:
			example[lst_name][item] = {}
			for col in header:
				example[lst_name][item][col] = mwu_dict[item][col]
			example[lst_name][item]['Occurrence'] = 1
		else:
			example[lst_name][item]['Occurrence'] += 1

def text_markup(input_text, matched):
	"""
	Parameters
	----------
	input_text : str
	matched : dictionary
		example = {"AFL_all": {}, "PHRASAL": {}, "Biber_2004": {}}

	Returns
	-------
	str
		html safe texts (markup).

	"""
	for lst in matched.keys(): #iterate the dictionary
		for key, item in matched[lst].items(): 
			#print(key)
			input_text = re.sub(r"\b{}\b".format(key) , " <span style='color:red'>" + " " + r"\g<0>" + " "  +"</span> ", input_text, flags = re.IGNORECASE)
	return Markup(input_text)


import spacy
nlp = spacy.load("en_core_web_md", disable=["ner", "textcat"])
#for development test

def token_dictor(token_dict, token):
	token_dict[token.i] = {'word': token.text, 
						'lemma': token.lemma_,
						'style': ['color:black']} #


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
			
			ngram_lemm = [w.lemma_ for w in doc[token.i : token.i+number]] #lemma ngrams
			ngram_lemm_string = connect.join(ngram_lemm)
			
			ngram_id = tuple(w.i for w in doc[token.i : token.i+number]) #store token ids for text mark-up
			
			if ngram_string not in ngram_dict: # create an entry in ngram dict
				ngram_dict[ngram_string] = {'type': ngram_string,
											'lemma': ngram_lemm_string,
											'loc': [ngram_id],}
			else:
				ngram_dict[ngram_string]['loc'].append(ngram_id) #for the second occurrence (and later) we only need the token id info
					
	return(ngram_dict) #add ngram_list to master list


def namestr(obj, namespace): #this will return the variable name
	return [name for name in namespace if namespace[name] is obj]


def mwu_search(matched_mwu: dict,text_mwu: dict, mwu_dict:dict) -> dict:
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
	
	for mwu in text_mwu: #iterate the text_mwu
		if mwu not in mwu_dict: #if it is not in the selected list, igore
			continue
		else: #if they are matched
			if mwu not in matched_mwu: #see if the matched_mwu alredy has an entry, if not create one
				matched_mwu[mwu] = {}
				matched_mwu[mwu].update(text_mwu[mwu])
				matched_mwu[mwu].update(dict.fromkeys(resource.keys(), dict())) #add empty keys
				
			matched_mwu[mwu][mwu_dict_name] = mwu_dict[mwu] #finally transfer info from resource.
	return(matched_mwu)


color_codes = {"rank": {1: "color:#FF003C",
						2: "color:#FF8A00",
						3: "color:#FABE28",
						4: "color:#88C100",
						5: "color:#00C176"},
	}

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

def overwrite_color(token_loc, color, token_info):
	for loc in token_loc:
		for token_id in loc:
			if token_info[token_id]['style'][0] == 'color:black':
				token_info[token_id]['style'][0] = color


def update_token_info(matched_mwus, token_info):
	for mwu, dict_mwu in matched_mwus.items():
		token_loc = dict_mwu["loc"]
		
		if len(dict_mwu['PHRASAL']) > 0: #check if the item occurs in the list
		
			color = color_phrasal(dict_mwu['PHRASAL']['Frequency Level'], color_codes)
			overwrite_color(token_loc, color, token_info)

		if len(dict_mwu['AFL_all']) > 0:
			color = color_AFL(dict_mwu['AFL_all']['Sub-list'], color_codes)
			overwrite_color(token_loc, color, token_info)
		
		else:
			continue
		#if len(dict_mwu['Biber_2004']) > 0:


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
			
			matched_mwus = {} #equivalent to example in the earlier versions
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
			
			print(ngram_holder)
			
			'''Pattern matching component'''
			#then match the results and store in a dict
			#n-gram tokenization + identification -> token no. corresponds to n-grams
			if "AFL_all" in selected_list:
				mwu_search(matched_mwus, ngram_holder, AFL_all) #alternative to the pattern matching
			elif "PHRASAL" in selected_list:
				mwu_search(matched_mwus, ngram_holder, PHRASAL)
			elif "Biber_2004" in selected_list:
				mwu_search(matched_mwus, ngram_holder, Biber_2004)


			update_token_info(matched_mwus, token_info)

			
			''' text mark-up '''
			output_text = token_mark_up(doc, token_info)
			print(output_text)
			
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




if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()




			


input_text = "One particularly interesting finding in Gardner and Davies’ study is that PVs are highly polysemous lexical items, with the PVs on their list having 5.6 meaning senses on average. This means that, in reality, the learning load of PVs is probably greater than most other words or word combinations in English. This 5.6 meaning sense average figure suggests that mastering the most frequent PVs in English does not entail knowing only 100 or 150 form–meaning links, but between 560 and 840. However, while PVs are undoubtedly highly polysemous, there are reasons to question Gardner and Davies’ exact polysemy figures. First, WordNet, the electronic database used by Gardner and Davies to recognize distinctions between different meaning senses of the same word forms, seems to yield redundant meaning senses (i.e. what constitutes a single meaning sense comes up as two different entries). A quick search using only one example given by Gardner and Davies, put out, is enough to illustrate this (the seventh and eighth meaning senses are the same baseball sporting term):"
input_text = "Other studies have also explored the nature of learner collocation problems. Nesselhauf (2003) explored the use of verb–noun collocations such as take a break and shake one’s head in essays written by advanced German-speaking learners of English. Borrowing from Howarth (1998), Nesselhauf (2003) distinguishes three major classes of collocations: free combinations, such as want a car (both the verb and the noun are used in an unrestricted sense; words can be freely combined); collocations, such as take a picture (the sense of the noun is unrestricted, but that of the verb is restricted; one can also say take a photograph); and idioms, for example, sweeten the pill (both the verb and the noun are used in a restricted sense; substitution is not possible, or is very limited). The learners made the greatest proportion of errors with collocations (79%), followed by free combinations (23%) and idioms (23%). However, Nesselhauf also found the highest rate of errors (33%) in collocations with a medium degree of restriction (e.g., exert influence, where a number of other nouns such as control, pressure, and power are also possible) and a much lower rate (18%) in collocations with ‘a lot of restriction’ (e.g., fail an exam/test, where fewer nouns are possible). These findings are congruent with those reported by Howarth.Granger (1998) also investigated native and non-native knowledge of collocations, focusing on -ly intensifier þ adjective collocations extracted from academic learner essays (L1 French) and essays written by native-English-speaking students. Granger distinguishes between two types of intensifiers: ‘maximizers’ (e.g., absolutely, totally) and ‘boosters’ (e.g., deeply, highly). She reports that the advanced learners’ usage of the former was not different from the native usage; the ‘boosters,’ however, seem to be used with lower frequencies in learner production than in that of NSs. Having further submitted a number of -ly intensifier þ adjective collocations to native and non-native (L1 French) informants, she reports that learners had a poorer sense of salience for collocations. Specifically, these learners were shown to be more accepting of combinations found unacceptable by the NSs. Overall, Granger concludes that although her learners did use collocations, they underused native-like expressions and tended to use atypical word combinations instead."

doc = nlp(input_text)
len(doc)


token_info = {}
for token in doc:
	token_dictor(token_info, token) 

# This will extract ngram list
ngram_holder = ngram(doc, 5, connect = " ")
ngram_holder.update(ngram(doc, 4, connect = " "))
ngram_holder.update(ngram(doc, 3, connect = " "))
ngram_holder.update(ngram(doc, 2, connect = " "))


### first 
#then match the results and store in a dict
matched_mwus = {} #equivalent to example in the earlier versions



mwu_search(matched_mwus, ngram_holder, AFL_all) #alternative to the pattern matching
mwu_search(matched_mwus, ngram_holder, PHRASAL)
mwu_search(matched_mwus, ngram_holder, Biber_2004)


#use the matched dictionary to update the token information
update_token_info(matched_mwus)
#iterate the matched dictionary
#update the style in token info according to the rules
#don't update if the style has been already changed (i.e., not "color:black")


#text markup updated here
def token_mark_up(doc, token_info):
	holder = []
	
	for token in doc:
		string = "<span style='{}'>".format(token_info[token.i]['style'][0]) + str(token.text) + "</span>"
		holder.append(string)
	return Markup(" ".join(holder))
		

token_mark_up(doc, token_info)
