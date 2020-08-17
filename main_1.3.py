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


def token_dictor(token):
	return {'word': token.text, 
			'lemma': token.lemma_,
			'style': ['color:black']} #

color_codes = {"rank": {1: "#FF003C",
						2: "#FF8A00",
						3: "#FABE28",
						4: "88C100",
						5: "#00C176"},
			   
	}}

def ngrammer(tokenized,number,connect = "__"):
	ngram_list = [] #empty list for ngrams
	last_index = len(tokenized) - 1 #this will let us know what the last index number is
	for i , token in enumerate(tokenized): #enumerate allows us to get the index number for each iteration (this is i) and the item
		if i + number > last_index: #if the next index doesn't exist (because it is larger than the last index)
			continue
		else:
			ngram = tokenized[i:i+number] #the ngram will start at the current word, and continue until the nth word
			ngram_string = connect.join(ngram) #turn list of words into an n-gram string
			ngram_list.append(ngram_string) #add string to ngram_list
	
	return(ngram_list) #add ngram_list to master list



@app.route('/', methods=['GET', 'POST'])
def output_():

	if request.method == 'POST': #when text input is given
		res = {'list_select_error': ""}
		input_text = request.form.get('input_text', '')
		#selected_list = request.form.get('mwu_list', '')
		selected_list = request.form.getlist("mwu_list")
		#print(selected_list)

		if input_text:
			''' holders '''
			token_holder = {} #can store all the information for text mark-up
			example = {"AFL_all": {}, "PHRASAL": {}, "Biber_2004": {}} #This will store MWEs 
			

			#preprocessing if any
			
			''' Tagging '''
			doc = nlp(input_text)

			for token in doc:
				token_holder.update(token.i, token_dictor(token))
			
			

			#n-gram tokenization + identification -> token no. corresponds to n-grams

			'''Pattern matching component'''
			
			if "AFL_all" in selected_list:
				header = headers['table']['AFL_all']
				#example = {"AFL_all": {}}
				dict_freq(example, AFL_all, 'AFL_all', pattern_matching(AFL_all, input_text), header)
			if "PHRASAL" in selected_list:
				header = headers['table']["PHRASAL"]
				#example = {"PHRASAL": {}}
				dict_freq(example, PHRASAL, "PHRASAL",pattern_matching(PHRASAL, input_text), header)

			if "Biber_2004" in selected_list:
				header = headers['table']["Biber_2004"]
				#example = {"Biber_2004": {}}
				dict_freq(example, Biber_2004, 'Biber_2004',pattern_matching(Biber_2004, input_text), header)

			elif len(selected_list) == 0: #When no lists were selected.
				res['input_text'] = input_text
				res['list_select_error'] = "Please select a list for analysis."
				return render_template(INDEX, res=res)

			#print(example)
			
			''' text mark-up '''
			output_text = text_markup(input_text, example)
			
			
			''' Compile response data '''
			res = {'input_text' : input_text,
					'output' : output_text,
					'output_text': output_text.split(r"\s"),
					'resource': resource,
					'selected_list': [key for key in selected_list],
					'table_headers': headers['table'],
					'example': example}
			
			return render_template(INDEX, res=res)
		
		
	return render_template(INDEX)




if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()




input_text = "One particularly interesting finding in Gardner and Davies’ study is that PVs are highly polysemous lexical items, with the PVs on their list having 5.6 meaning senses on average. This means that, in reality, the learning load of PVs is probably greater than most other words or word combinations in English. This 5.6 meaning sense average figure suggests that mastering the most frequent PVs in English does not entail knowing only 100 or 150 form–meaning links, but between 560 and 840. However, while PVs are undoubtedly highly polysemous, there are reasons to question Gardner and Davies’ exact polysemy figures. First, WordNet, the electronic database used by Gardner and Davies to recognize distinctions between different meaning senses of the same word forms, seems to yield redundant meaning senses (i.e. what constitutes a single meaning sense comes up as two different entries). A quick search using only one example given by Gardner and Davies, put out, is enough to illustrate this (the seventh and eighth meaning senses are the same baseball sporting term):"
doc = nlp(input_text)



for token in doc:
	print(token.text, token.lemma_, token.i, token.pos_)
	
	token_holder.update(token.i, token_dictor(token))

