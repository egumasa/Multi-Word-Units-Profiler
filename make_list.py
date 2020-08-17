#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 19:23:38 2020

@author: eguchimasaki
"""


'''
This creates a pickled list for each list of use

Generic list structure

{"in terms of": {band: 1,
				freq_per_mil: ,
				},
 "rather than": {band: 1,
				freq_per_mil: ,},
 }


For AFL it makes sense to use normed frequency, not 

PHRASE list: integrated list Rank, Normed Freq, Spoken general,  
written general and Written academic


'''

import pickle

AFL_core_file = open('unit_lists/AFL_core.txt').read()
AFL_all_file = 'unit_lists/AFL_all.txt'
PHRASAL = 'unit_lists/PHRASAL_list.txt'
biber_2004 = "unit_lists/Biber_et_al_2004.txt"

def list_pickle(file):
	"""
	Parameters
	----------
	file : string
		This a string read from a file.

	Returns
	-------
	holder : Dictionary of chunks with frequencies.
	"""
	file = open(file).read()
	header = []
	holder = {}
	for no, line in enumerate(file.strip().split("\n")):
		#print(line, no)
		if no == 0:
			header.extend(line.strip().split("\t"))
		else:
			items = line.strip().split("\t")
			for col, item in enumerate(items):
				if col == 0:
					holder[items[0].lower().strip()] = {}
				else:
					holder[items[0].lower().strip()][header[col]] = item.strip()
			
	return holder
		

AFL_core_dict = list_pickle(AFL_all_file)

biber_2004_dict = list_pickle(biber_2004)
PHRASAL = list_pickle('unit_lists/PHRASAL_list.txt')


def save_pickle(file, dict_):
	with open(file.replace(".txt", '.pickle'), 'wb') as outf:
		pickle.dump(dict_, outf)
	

def main(file):
	dict_ = list_pickle(file)
	print(dict_)
	save_pickle(file, dict_)


main('unit_lists/AFL_all.txt')
main('unit_lists/PHRASAL_list.txt')

main(biber_2004)




# =============================================================================
# headers
# =============================================================================

## list of headers to be used
AFL_header = ["Sub-list", "#rank", "Spoken_Raw freq", "Spoken Frequency <br>(per million words)", \
			"Written_Raw freq", "Written Frequency <br>(per million words)",	"FTW"]
AFL_header_s = ["Occurrence", "Sub-list", "Spoken Frequency <br>(per million words)", "Written Frequency <br>(per million words)"]
PHRASAL_header = ["Frequency Level", "rank", "Frequency <br> (per million words)","Spoken general", "Written general", "Written academic", "Example sentence"]
PHRASAL_header_s = ["Occurrence", "Frequency Level", "Frequency <br> (per million words)","Spoken general", "Written general", "Written academic", "Example sentence"]
Biber_header = ["Lexical bundle", "Category", "Function", "Sub-function", "Dimension", "Frequency in Classroom teaching", "Frequency in Textbooks", "Frequency in Conversation", "Frequency in Academic prose"]
Biber_header_s = ["Occurrence", "Category", "Function", "Sub-function", "Frequency in Classroom teaching", "Frequency in Textbooks", "Frequency in Conversation", "Frequency in Academic prose"]

full_headers = {"AFL_all": AFL_header, 
				"PHRASAL": PHRASAL_header, 
				"Biber_2004": Biber_header}

table_headers = {"AFL_all": AFL_header_s, 
				"PHRASAL": PHRASAL_header_s, 
				"Biber_2004": Biber_header_s}


headers = {'full': full_headers,
		   'table': table_headers}

with open("resource/header_0.4.pickle", 'wb') as outf:
	pickle.dump(headers, outf)
