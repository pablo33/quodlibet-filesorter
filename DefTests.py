#!/usr/bin/python2
# -*- coding: utf_8 -*-

import unittest
import quodlibet_filesorter
#import datetime
#import os



#####TESTS########

TM = quodlibet_filesorter

class CharChange_test (unittest.TestCase):
	"""Replaces character in a string with assigned values
		"""
	known_values = (
		('a string to\nreplace','a string to replace'),
		('a string\tto replace','a string to replace'),
		('a string\nto\treplace~again','a string to replace-again'),
		('a string to\nreplace','a string to replace'),
		('the same/again and\tagain','the sameagain and again')
		)
	def test_CharChange (self):
		for example, validate in self.known_values:
			result = TM.CharChange (example)
			self.assertEqual (result, validate)

class Getchunklist_test (unittest.TestCase):
	'''testing Getchunklist function'''
	known_values = (
		(
			('~/Genre/<artist>/<album>/[<cd> -][<track> -]<title>.<ext>', '[]'),
			[	'~/Genre/<artist>/<album>/',
				'[<cd> -]',
				'[<track> -]',
				'<title>.<ext>']
			),
		(
			('~/albumes/<autor>/<album>/[<cd> - ][<track> - ]<title>.<ext>', '[]'),
			[	'~/albumes/<autor>/<album>/',
				'[<cd> - ]',
				'[<track> - ]',
				'<title>.<ext>']
			),
		(
			('/albumes/<autor>/<album>', '[]'),
			[	'/albumes/<autor>/<album>',
				]
			),

		(
			('[optional1][optional2][optional3]', '[]'),
			[	'[optional1]',
				'[optional2]',
				'[optional3]',]
			),
		(		
			('chunk0[optional1][optional2][optional3]', '[]'),
			[	'chunk0',
				'[optional1]',
				'[optional2]',
				'[optional3]',]
			),
		(		
			('chunk0[optional1][optional2][optional3]LastChunk', '[]'),
			[	'chunk0',
				'[optional1]',
				'[optional2]',
				'[optional3]',
				'LastChunk',]
			),
		(		
			('chunk0[optional1][optional2]middle[optional3]LastChunk', '[]'),
			[	'chunk0',
				'[optional1]',
				'[optional2]',
				'middle',
				'[optional3]',
				'LastChunk',]
			),


		)

	def test_Getchunklist (self):
		''' an empty string returns another empty string'''
		for example, validate in self.known_values:
			result = TM.Getchunklist (example[0],example[1])
			self.assertEqual (result, validate)



if __name__ == '__main__':
	unittest.main()

