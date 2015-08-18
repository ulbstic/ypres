#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 
# Babelfy
#
# http://babelfy.org/
# http://babelfy.org/guide
# 

import urllib, urllib2, json
from urllib import unquote_plus as up
import re
import time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

# set paramaters
delay = 1 # delay between API calls
filetype = sys.argv[1] if len(sys.argv) > 1 else 'raw'
if filetype not in ['raw', 'corr']:
	print("usage: {0} raw or corr".format(sys.argv[0]))
	sys.exit()
if filetype == 'raw':
	inFilename = "../gsc3.txt"
	outFilename = "raw-Babelfy-ent.mapped"
else:
	inFilename = "../corr/gsc3.new.txt"
	outFilename = "corr-Babelfy-ent.mapped"

# extract places entities from Babelfy service
def get_entities(text,offset):
	global places
	url = "https://babelfy.io/v1/disambiguate"
	values = {
		'key': '54125585-30da-4baf-a44e-82f849f1f7f6',
		'lang': 'AGNOSTIC',
		'annType': 'NAMED_ENTITIES',
		'annRes': 'WIKI',
		'text' : text
	}
	data = urllib.urlencode(values)
	headers = {'Accept': 'application/json'}
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req)
	page = response.read()
	j = json.loads(page)
	s = set()
	for e in j:
		c = e # only 1 candidate
		start = c['charFragment']['start']
		stop = c['charFragment']['end']
		a = text[start:stop+1 ]
		if len(e['DBpediaURL']) > 0: # DBpedia uri
			uri = c['DBpediaURL'].replace("http://dbpedia.org/resource/", "dbr:")
			if uri in places:
				s.add((offset+start,offset+stop,up(str(uri[4:])))) # dbr:...
	for m in sorted(s):
		a,z,e = m
		print("{0}\t{1}\t{2}\t{3}".format(inFilename, a, z, e))
	return s

# load DBpedia places
places = set()
with open("../../dbpedia/dbpedia-places.lst") as locs:
	for uri in locs:
		places.add(uri.strip())

# collect results
offset = 0
results = set()
with open(inFilename) as inFile:
	for line in inFile:
		text = line.decode('utf-8')
		results = results.union(get_entities(text,offset))
		offset += len(text)
		time.sleep(delay)

# write results
with open(outFilename, 'w') as outFile:
	for item in sorted(results):
		(start, stop, label) = item
		outFile.write("{0}\t{1}\t{2}\t{3}\n".format(inFilename, start, stop, label))
