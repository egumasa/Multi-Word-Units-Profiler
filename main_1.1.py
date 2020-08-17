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
INDEX = "index_0.3_current.html"

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


def dict_freq(example, mwu_dict, matched_list, header):

	for item in matched_list:
		#print(mwu_dict[item])
		if item not in example:
			example[item] ={}
			for col in header:
				holder[item][col] = mwu_dict[item][col]
			example[item]['Occurrence'] = 1
		else:
			example[item]['Occurrence'] += 1
	return example



def text_markup(input_text, matched):
	for key, item in matched.items():
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
		selected_list = request.form.get('mwu_list', '')

		if input_text:
			#temp = {} #can store all the information for text mark-up
			#preprocessing if any
			example = {}
			#tagging
			#doc = nlp(input_text)

			#n-gram tokenization + identification -> token no. corresponds to n-grams



			if selected_list == "AFL_all":
				header = AFL_head_s
				example = dict_freq(example, AFL_all, pattern_matching(AFL_all, input_text), header)
			elif selected_list == "PHRASAL":
				header = PHRASAL_head_s
				example = dict_freq(example, PHRASAL, pattern_matching(PHRASAL, input_text), header)

			elif selected_list == "Biber_2004":
				header = Biber_header_s
				example = dict_freq(example, Biber_2004, pattern_matching(Biber_2004, input_text), header)

			elif selected_list == "": #When no lists were selected.
				res['input_text'] = input_text
				res['list_select_error'] = "Please select a list for analysis."
				return render_template(INDEX, res=res)


			print(example)
			#text markup here
			output_text = text_markup(input_text, example)

			try:
				table_head = ['Multi-Word Expression']
				table_head.extend(list(example[list(example.keys())[0]].keys()))
			except IndexError:
				table_head = ["No expressions found."]

			res = {'input_text' : input_text,
					'output' : output_text,
					'output_text': output_text.split(r"\s"),
					'selected_list': resource[selected_list],
					'header': table_head,
					'example':example}

		return render_template(INDEX, res=res)


	return render_template(INDEX)




if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()

