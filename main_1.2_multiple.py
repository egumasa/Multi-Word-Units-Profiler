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
from jinja2 import Template
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

## list of headers to be used
AFL_head = ["Sub-list", "#rank", "Spoken_Raw freq", "Spoken Frequency <br>(per million words)", \
			"Written_Raw freq", "Written Frequency <br>(per million words)",	"FTW"]
AFL_head_s = ["Sub-list", "Spoken Frequency <br>(per million words)", "Written Frequency <br>(per million words)"]
PHRASAL_head = ["Frequency Level", "rank", "Frequency <br> (per million words)","Spoken general", "Written general", "Written academic", "Example sentence"]
PHRASAL_head_s = ["Frequency Level", "Frequency <br> (per million words)","Spoken general", "Written general", "Written academic", "Example sentence"]
Biber_header = ["Lexical bundle", "Category", "Function", "Sub-function", "Dimension", "Frequency in Classroom teaching", "Frequency in Textbooks", "Frequency in Conversation", "Frequency in Academic prose"]
Biber_header_s = ["Category", "Function", "Sub-function", "Frequency in Classroom teaching", "Frequency in Textbooks", "Frequency in Conversation", "Frequency in Academic prose"]


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
			'style': ['']}


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
			#temp = {} #can store all the information for text mark-up
			example = {"AFL_all": {}, "PHRASAL": {}, "Biber_2004": {}} #This will store MWEs 
			
			table_headers = {"AFL_all": AFL_head_s, 
							"PHRASAL": PHRASAL_head_s, 
							"Biber_2004": Biber_header_s}


			#preprocessing if any
			
			''' Tagging '''
			#doc = nlp(input_text)

			#n-gram tokenization + identification -> token no. corresponds to n-grams

			'''Pattern matching component'''
			
			if "AFL_all" in selected_list:
				header = AFL_head_s
				#example = {"AFL_all": {}}
				dict_freq(example, AFL_all, 'AFL_all', pattern_matching(AFL_all, input_text), header)
			if "PHRASAL" in selected_list:
				header = PHRASAL_head_s
				#example = {"PHRASAL": {}}
				dict_freq(example, PHRASAL, "PHRASAL",pattern_matching(PHRASAL, input_text), header)

			if "Biber_2004" in selected_list:
				header = Biber_header_s
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
					'table_headers': table_headers,
					'example': example}
			
			return render_template(INDEX, res=res)
		
		
	return render_template(INDEX)




if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()


