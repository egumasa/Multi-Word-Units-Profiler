#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 18:42:23 2020

@author: eguchimasaki
"""

#for main 
import pickle
import re
import spacy
import flask
from jinja2 import Template
#for development test
import glob


from flask import Flask
app = Flask(__name__)


## html template setting
html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
	<title>Output</title>
	<style>
	span {color: red;}
	h1   {color: blue;}
	p    {color: red;}
	</style>
</head>
<body>
	<h1>Original:</h1>
    <div>
	{{ input_text }}
	</div>
	</br>
	<h1>Highlighted:</h1>
    <div>
    {{ output }}
	</div>

</body>
</html>
'''
template = Template(html)

### These were for testing of html formatting
#html_test_data = {
#  'input_text' : 'This is a simple test.',
#  'output' : 'This is <span style="color:blue;">a simple</span> test.'
#}
#
#with open("sample.html", "w") as html_file:
#	html_file.write(template.render(html_test_data))


## loading lists
AFL_all = pickle.load(open("resource/AFL_all.pickle","rb"))



TARGET_TEXTS = glob.glob("example/*.txt")

input_text = open(TARGET_TEXTS[-1]).read()


###.keys()
def pattern_matching(pickled_dict: dict, input_text: str) -> list:
	holder = []
	for mwu in pickled_dict.keys():
		match = re.findall(mwu, input_text.lower(), re.IGNORECASE)
		holder.extend(match)
	return holder

def pattern_matching2(pickled_dict: dict, input_text: str) -> list:
	holder = []
	mwus = pickled_dict.keys()
	
	match = re.findall(r"\w" + '|'.join(mwus) + r"\w" ,input_text.lower(), re.IGNORECASE)
	holder.extend(match)
	return holder



matched_afl  = pattern_matching(AFL_all, input_text)
matched_afl2  = pattern_matching2(AFL_all, input_text)

len(matched_afl)
len(matched_afl2)

###frequency

def dict_freq(matched_list):
	holder = {}
	for item in matched_list:
		if item not in holder:
			holder[item] = AFL_all[item]
			holder[item]['occurrence'] = 1
		else:
			holder[item]['occurrence'] += 1
	return holder

example = dict_freq(matched_afl)
example2 = dict_freq(matched_afl2)


def text_markup(input_text, matched):
	for key, item in matched.items():
		print(key)
		input_text = re.sub(" " + key + " " , " <span>" + " " + key + " "  +"</span> ", input_text, re.IGNORECASE)
	return input_text

def text_markup2(input_text, matched):
	for key, item in matched.items():
		print(key)
		p = re.compile(r"\w" + key + r"\w")
		input_text = p.sub("<span>" + key +"</span> ", input_text, re.IGNORECASE)
	return input_text

output = text_markup(input_text, example)
output = text_markup2(input_text, example2)


html_sample = {
  'input_text' : input_text,
  'output' : output
}

with open("sample2.html", "w", encoding = "utf-8") as html_file:
	html_file.write(template.render(html_sample))
	

