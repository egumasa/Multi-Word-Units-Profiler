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
					holder[items[0].lower()] = {}
				else:
					holder[items[0].lower()][header[col]] = item
			
	return holder
		

AFL_core_dict = list_pickle(AFL_all_file)

def save_pickle(file, dict_):
	with open(file.replace(".txt", '.pickle'), 'wb') as outf:
		pickle.dump(dict_, outf)
	

def main(file):
	dict_ = list_pickle(file)
	print(dict_)
	save_pickle(file, dict_)


main('resource/AFL_all.txt')
main('unit_lists/PHRASAL.txt')

