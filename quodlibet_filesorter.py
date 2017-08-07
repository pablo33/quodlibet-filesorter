#!/usr/bin/python2

import quodlibet, cPickle, sqlite3


__version__ = 1.0


#=====================================
# Function  myfunction
#=====================================
def Getchunklist (fgstring, delimitters):
	'''Getchunklist

	It splits into chunks a string expression due to delimiters
	delimieters must be a string of two characters
	it returns a list of aplitted texts

	example:
	Getchunklist ('~/Genre/<artist>/<album>/[<cd> -][<track> -]<title>.<ext>', '[]')
	Generated list is:
	['~/Genre/<artist>/<album>/',
	'[<cd> -]',
	'[<track> -]',
	'<title>.<ext>'
	]
	'''
	chunklist = []
	if fgstring == '' or fgstring == None:
		return []
	from_pos, to_pos, switch = 0,0,0
	for char in fgstring:
		if char == delimitters[0] and switch == 0:
			if from_pos != to_pos:
				chunklist.append (fgstring[from_pos:to_pos])
			switch = 1
			from_pos = to_pos
		elif char == delimitters[1] and switch == 1:
			chunklist.append (fgstring[from_pos:to_pos + 1])
			switch = 0
			from_pos = to_pos + 1
		to_pos += 1
	if from_pos < to_pos:
		chunklist.append (fgstring[from_pos:to_pos])
	return chunklist



if __name__ == '__main__':
	print ('Running, have a good time')