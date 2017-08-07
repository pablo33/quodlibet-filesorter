#!/usr/bin/python2

import quodlibet, cPickle, sqlite3, re, os


__version__ = 0.0


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


userlibrary = os.path.join(os.getenv('HOME'),'.quodlibet/songs')


if __name__ == '__main__':
	print ('Running, have a good time')
	# Open quodlibet database dumped
	with open(userlibrary, 'r') as songsfile:
		songs = cPickle.load(songsfile)
	
		# iterate over duped elements
		for element in songs:
			
			fullpathfilename = str(element('~filename'))
			extension = os.path.splitext (fullpathfilename)[1]

			if 'filegroupping' in element.keys():
				filegroupping = element('filegroupping')
				if filegroupping.endswith ('.<ext>'):
					addfilenameflag = False
					filegroupping = filegroupping [:-6]
				else:
					addfilenameflag = True
				chunklist = Getchunklist (filegroupping,'[]')
				
				print '\n','Chunklist = ', chunklist
				targetpath = ''
				for chunk in chunklist:
					optionalflag = False
					if chunk.startswith ('[') and chunk.endswith (']'):
						optionalflag = True
					formedchunk = chunk
					taglist = re.findall ('<\w*>',chunk)
					print 'chunk =', chunk
					print 'taglist= ', taglist
					for tag in taglist:
						metaname = tag[1:-1]
						print 'metaname=', metaname
						if metaname in element.keys():
							formedchunk = formedchunk.replace('<'+ metaname + '>',element(metaname))
						elif not optionalflag:
							formedchunk = ''
							break
					targetpath = targetpath + formedchunk
				if targetpath.startswith ('~/'):
					targetpath = element('~mountpoint') + targetpath [1:]
				if addfilenameflag:
					targetpath = targetpath + os.path.basename(element('~filename'))
				else:
					targetpath = targetpath + extension
				print element('~filename'), "\n", targetpath, "\n"