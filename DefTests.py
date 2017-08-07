#!/usr/bin/python2
import unittest
import quodlibet_filesorter
#import datetime
#import os



#####TESTS########

TM = quodlibet_filesorter

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

