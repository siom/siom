#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from itertools import izip_longest

def usage():
	print sys.argv[0], '<input file>', '<output file>', '<solution file>'
	sys.exit(1)

def compare_files(contestant, solution):
	try:
		fc = open(contestant)
	except IOError:
		assert False, u'Nėra rezultatų failo'
	try:
		with open(solution) as fs:
			lineno = 1
			for cline, sline in izip_longest(fc, fs):
				assert cline is not None, u'Trūksta eilučių'
				assert sline is not None, u'Per daug eilučių'
				cline = cline.strip()
				sline = sline.strip()
				assert cline == sline, u'Neteisinga eilutė'
				lineno += 1
	finally:
		fc.close()

if __name__ == '__main__':
	if len(sys.argv) < 4:
		usage()
	try:
		compare_files(sys.argv[2], sys.argv[3])
		print 1
		print "ok"
	except AssertionError as e:
		print 0
		print e.args[0].encode('utf8')

