#!/usr/bin/python2
# -*- coding: utf_8 -*-

import quodlibet, cPickle
import sqlite3, re, os, logging
from datetime import datetime


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
userfilegrouppingtag = 'filegroupping'
dbpathandname = userfilegrouppingtag + '.sqlite3'



if __name__ == '__main__':
	print ('Running, have a good time.')

	loginlevel = 'DEBUG'  # INFO ,DEBUG
	logpath = './'
	logging_file = os.path.join(logpath, userfilegrouppingtag+'.log')


	# Getting current date and time
	now = datetime.now()
	today = "/".join([str(now.day), str(now.month), str(now.year)])
	tohour = ":".join([str(now.hour), str(now.minute)])

	print '\tLoginlevel: {}'.format(loginlevel)
	logging.basicConfig(
		level = loginlevel,
		format = '%(asctime)s : %(levelname)s : %(message)s',
		filename = logging_file,
		filemode = 'w'  # a = add
	)
	print '\tLogging to: {}'.format(logging_file)
	


	#initializing DB
	if os.path.isfile(dbpathandname):
		os.remove (dbpathandname)
	con = sqlite3.connect (dbpathandname)
	con.execute ('CREATE TABLE SongsTable \
		(id INT PRIMARY KEY 	NOT NULL, \
		mountpoint	TEXT 	NOT NULL, \
		filefolder	TEXT 	NOT NULL, \
		filename 	TEXT 	NOT NULL, \
		format		TEXT 	NOT NULL, \
		fullpathfilename	TEXT 	NOT NULL,\
		filegroupping TEXT 	NOT NULL, \
		targetpath	TEXT 	NOT NULL)')
	con.execute ('CREATE VIEW "SF" AS SELECT DISTINCT filefolder FROM songstable')
	con.execute ('CREATE TABLE Associatedfiles \
		(originfile	TEXT 	NOT NULL, \
		targetfile	TEXT 	NOT NULL, \
		fileflag	TEXT 			)')

	# Open quodlibet dumped database 
	with open(userlibrary, 'r') as songsfile:
		songs = cPickle.load(songsfile)
		Id = 0	
		# iterate over duped elements
		for element in songs:

			if element(userfilegrouppingtag) != '':
				fullpathfilename = str.decode(str(element('~filename')),'utf8')
				mountpoint = str.decode(str(element('~mountpoint')),'utf8')
				filefolder = os.path.dirname(fullpathfilename)
				filename = os.path.basename(fullpathfilename)
				extension = os.path.splitext (fullpathfilename)[1]
				filegroupping = str.decode(str(element(userfilegrouppingtag)),'utf8')

				if filegroupping.endswith ('.<ext>'):
					addfilenameflag = False
					tmpfilegroupping = filegroupping [:-6]
				else:
					addfilenameflag = True
				#Splicing filegrouppingtag in chunks
				chunklist = Getchunklist (tmpfilegroupping,'[]')
				
				logging.debug ('>>>>')
				logging.debug ('Chunklist = {}'.format(chunklist))
				targetpath = ''
				for chunk in chunklist:
					# Checking and flagging an optional chunk
					optionalflag = False
					if chunk.startswith ('[') and chunk.endswith (']'):
						optionalflag = True
					# We start with the chunk, and later perform tag substitutions
					formedchunk = chunk
					taglist = re.findall ('<\w*>',chunk)
					logging.debug ('\tchunk  = {}'.format(chunk))
					logging.debug ('\ttaglist= {}'.format(taglist))
					for tag in taglist:
						metaname = tag[1:-1]
						logging.debug ('\t\tmetaname = {}'.format(metaname))
						metavalue = element(metaname)
						# we trim the slash and total tracks if any
						if metaname == 'tracknumber':
							slashpos = metavalue.find('/')
							if slashpos != -1:
								metavalue = metavalue [:slashpos]
							if metavalue.isnumeric():
								metavalue = '{:0>2}'.format (metavalue)
						metavalue = metavalue.replace('/','¬')
						metavalue = metavalue.replace('\n',' ')
						metavalue = metavalue.replace('\t',' ')
						metavalue = metavalue.replace('|','-')
						metavalue = metavalue.replace('~','-')
						formedchunk = formedchunk.replace('<'+ metaname + '>',metavalue)
						# Break and return an empty chunk if any tag is not present
						if metaname not in element.keys() and optionalflag:
							formedchunk = ''
							break
					if optionalflag and formedchunk != '':
						formedchunk = formedchunk [1:-1]
					targetpath = targetpath + formedchunk
				# Adding a mountpoint lead if necessary
				if targetpath.startswith ('~/'):
					targetpath = mountpoint + targetpath [1:]
				# Adding original filename if necessary
				if addfilenameflag:
					targetpath = targetpath + os.path.basename(fullpathfilename)
				else:
					targetpath = targetpath + extension
				targetpath = os.path.normpath (targetpath)
				logging.debug ('\ttargetpath = {}'.format(targetpath))
				valuetuple = ( 	Id,
								mountpoint,
								filefolder,
								filename,
								str.decode(str(element('~format')),							'utf8'),
								fullpathfilename,
								filegroupping,
								targetpath
								)
				con.execute ("INSERT INTO SongsTable VALUES (?,?,?,?,?,?,?,?)", valuetuple)
				Id += 1
		con.commit()
	
	print '\t{} songs processed.'.format(Id)
	## Looking for Associated files and folders
	logging.debug ('#'*43)
	logging.debug ('## Looking for Associated files and folders')
	logging.debug ('#'*43)
	cursor = con.cursor ()
	cursor.execute ('SELECT * FROM sf')
	for contaninerfolder in cursor:
		originfolder = contaninerfolder[0]
		itemlist = os.listdir (originfolder)

		Associatedlistdir = set ()
		associatedpathscounter = 0

		for item in itemlist:
			typeflag = None
			originfile = os.path.join(originfolder,item)
			logging.debug ('originfile = ' + originfile)
			targetfile = None
			if os.path.isfile (originfile):
				exist, associatedtargetfilepath = con.execute ('SELECT COUNT (fullpathfilename), targetpath \
								FROM songstable WHERE \
								fullpathfilename = ?', (originfile,)).fetchone()
				#logging.debug ('\t existflag = ' + str(existflag[0]))
				if exist:
					logging.debug('\t > is already a processed file.')
					Associatedlistdir.add (os.path.dirname(associatedtargetfilepath))
					associatedpathscounter += 1
					continue
				logging.debug('\t > is going to be Associated')
				typeflag = 'file'
		print '\n supported processed files: {}'.format(associatedpathscounter)
		print ' Number of associated target Paths: {}'.format (len(Associatedlistdir))
		for i in Associatedlistdir:
			print i


		
	print 'Done!'
