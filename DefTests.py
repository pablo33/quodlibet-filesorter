#!/usr/bin/python2
# -*- coding: utf_8 -*-

import unittest
import quodlibet_filesorter
#import datetime
#import os



#####TESTS########

TM = quodlibet_filesorter

class Pathnormalizer_test (unittest.TestCase):
	""" Corrects erroneous paths.
		"""
	known_values = (
		('//home///pablo/Musica//folder/song.mp3','/home/pablo/Musica/folder/song.mp3'),
		)
	def test_CharChange (self):
		for example, validate in self.known_values:
			result = TM.Pathnormalizer (example)
			self.assertEqual (result, validate)


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

class Nextfilenumber_test (unittest.TestCase):
	""" test for Nextfilenumber function """
	known_values = (
		("file.jpg", "file(0).jpg"),
		("file1.jpg", "file1(0).jpg"),
		("file(0).jpg", "file(1).jpg"),
		("file(222).jpg", "file(223).jpg"),
		("file33", "file33(0)"),
		("file(33)", "file(34)"),
		("file(-1)", "file(-1)(0)"),
		("file.","file(0)."),
		("file(10).", "file(11)."),
		("file(X).jpg", "file(X)(0).jpg"),
		)
	def test_known_input (self):
		for inputfile, outputfile in self.known_values:
			result = TM.Nextfilenumber (inputfile)
			self.assertEqual (outputfile, result)
	def test_mad_values (self):
		self.assertRaises (TM.EmptyStringError, TM.Nextfilenumber, "")
		pass


if __name__ == '__main__':
	unittest.main()

