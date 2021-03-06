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
INDEX = "index_0.32.html"

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
PHRASAL = pickle.load(open("resource/PHRASAL.pickle","rb"))
Biber_2004 = pickle.load(open("resource/Biber_et_al_2004.pickle","rb"))



###.keys()
def pattern_matching(mwu_dict: dict, input_text: str) -> list:
	holder = []
	for mwu in mwu_dict.keys():
		match = re.findall(mwu, input_text.lower(), re.IGNORECASE)
		holder.extend(match)
	print(holder)
	return holder


def dict_freq(mwu_dict, matched_list):
	holder = {}
	for item in matched_list:
		#print(mwu_dict[item])
		if item not in holder:
			holder[item] = mwu_dict[item]
			holder[item]['occurrence'] = 1
		else:
			holder[item]['occurrence'] += 1
	return holder



def text_markup(input_text, matched):
	for key, item in matched.items():
		#print(key)
		input_text = re.sub(r"\b{}\b".format(key) , " <span style='color:red'>" + " " + r"\g<0>" + " "  +"</span> ", input_text, flags = re.IGNORECASE)
	return Markup(input_text)



@app.route('/', methods=['GET', 'POST'])
def output_():
	
	if request.method == 'POST': #when text input is given
		res = {'list_select_error': ""}
		input_text = request.form.get('input_text', '')
		selected_list = request.form.get('mwu_list', '')

		if input_text:
			if selected_list == "AFL_all":
				example = dict_freq(AFL_all, pattern_matching(AFL_all, input_text))
			elif selected_list == "PHRASAL":
				example = dict_freq(PHRASAL, pattern_matching(PHRASAL, input_text))
			
			elif selected_list == "Biber_2004": 
				example = dict_freq(Biber_2004, pattern_matching(Biber_2004, input_text))

			elif selected_list == "": #When no lists were selected.
				res['input_text'] = input_text
				res['list_select_error'] = "Please select a list for analysis."
				return render_template(INDEX, res=res)
			
			#print(example)
			output_text = text_markup(input_text, example)
			res = {'input_text' : input_text,
					'output' : output_text,
					'output_text': output_text.split(r"\s"),
					'selected_list': resource[selected_list]}
			
		return render_template(INDEX, res=res)
	
	
	return render_template(INDEX)



if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run()

