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

def CharChange (string):
	""" Replaces character in a string with assigned values
		"""
	charset = {
				'/\a\b\f\r\v':'',
				'\n\t':' ',
				'|~':'-',
				}
	for a in charset:
		for i in a:
			string = string.replace (i,charset[a])

	return string

def filemove (origin, dest):
	if itemcheck (origin) != 'file':
		return None
	while itemcheck (dest) != "" :
		infomsg = "File already exists at destination, assigning a new name."
		dest = Nextfilenumber (dest)
		logging.info (infomsg + " >> " + dest)

	if not dummy:
		if itemcheck (os.path.dirname(dest)) == '':
			os.makedirs (os.path.dirname(dest))
		shutil.move (origin, dest)
	#print ("      > file has been moved. {}".format(dummymsg))
	logging.info ("\tfile has been moved. {}".format(dummymsg))
	return dest



userlibrary = os.path.join(os.getenv('HOME'),'.quodlibet/songs')  # Place where the quod-libet cPickle object is
userfilegrouppingtag = 'filegroupping'  # Tag name which defines the desired path structure for the file
dbpathandname = userfilegrouppingtag + '.sqlite3'  # Sqlite3 database archive for processing
dummy = False  # Dummy mode, True means that the software will check items, but will not perform file movements


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
	con.execute ("CREATE TABLE SongsTable \
		(id INT PRIMARY KEY 	NOT NULL, \
		mountpoint	TEXT 	NOT NULL, \
		filefolder	TEXT 	NOT NULL, \
		filename 	TEXT 	NOT NULL, \
		format		TEXT 	NOT NULL, \
		fullpathfilename	TEXT 	NOT NULL,\
		filegroupping TEXT 	NOT NULL, \
		targetpath	TEXT 	NOT NULL, \
		fileflag	TEXT 	NOT NULL)" )

	con.execute ('CREATE VIEW "SF" AS SELECT DISTINCT filefolder FROM songstable')
	con.execute ('CREATE TABLE Associatedfiles \
		(originfile	TEXT 	NOT NULL, \
		targetpath	TEXT 	NOT NULL, \
		fileflag	TEXT 	NOT NULL)')
	con.execute ('CREATE VIEW "filemovements" AS SELECT * FROM (\
				SELECT * FROM \
					associatedfiles UNION \
					SELECT fullpathfilename as originfile, targetpath, fileflag \
					FROM songstable) \
				WHERE originfile <> targetpath ORDER BY originfile')


	# Open quodlibet dumped database, process it.
	with open(userlibrary, 'r') as songsfile:
		songs = cPickle.load(songsfile)
		Id = 0
		processed_counter = 0
		# iterate over duped elements
		for element in songs:
			processed_counter += 1

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
						metavalue = CharChange (metavalue)  # clears some non allowed chars
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
				valuetuple = ( 	processed_counter,
								mountpoint,
								filefolder,
								filename,
								str.decode(str(element('~format')),							'utf8'),
								fullpathfilename,
								filegroupping,
								targetpath,
								'Qfile'
								)
				con.execute ("INSERT INTO SongsTable VALUES (?,?,?,?,?,?,?,?,?)", valuetuple)
				Id += 1
		con.commit()
	
	print '\t{} total songs processed at quod-libet database.'.format(processed_counter)
	print '\t{} songs with <{}> tag defined ({:.1%}).'.format(Id, userfilegrouppingtag, float(Id)/processed_counter)
	### 
	### Looking for Associated files and folders
	###
	logging.debug ('#'*43)
	logging.debug ('## Looking for Associated files and folders')
	logging.debug ('#'*43)
	print '\tLooking for associated files.'
	cursor = con.cursor ()
	cursor.execute ('SELECT * FROM sf')
	for contaninerfolder in cursor:
		originfolder = contaninerfolder[0]  # SELECT Query returns a tuple ([0],)
		itemlist = os.listdir (originfolder)

		ATargetdict = dict ()  # Associated target list, and number of leading coincidences.
		Aitemdict = dict ()  # Associated items dictionary
		leading_counter = 0  # Leading tracks counter on a folder.
		associated_counter = 0  # Associated files counter.
		afolder_counter = 0  # Associated folders counter.

		for item in itemlist:
			typeflag = None
			targetfile = None
			originfile = os.path.join(originfolder,item)
			logging.debug ('')
			logging.debug ('originfile = ' + originfile)
			if os.path.isfile (originfile):
				exist, a_targetfile_path = con.execute ('SELECT COUNT (fullpathfilename), targetpath \
								FROM songstable WHERE \
								fullpathfilename = ?', (originfile,)).fetchone()
				if exist:
					logging.debug('\t > file is a leading file.')
					a_targetfolder_path = os.path.dirname(a_targetfile_path)
					if a_targetfolder_path in ATargetdict:
						ATargetdict[a_targetfolder_path] += 1
					else:
						ATargetdict[a_targetfolder_path] = 1
					leading_counter += 1
					continue
				logging.debug('\t > file is going to be Associated')
				associated_counter += 1
				typeflag = 'Afile'
			elif os.path.isdir (originfile):
				exist = con.execute ('SELECT COUNT (filefolder) \
								FROM sf WHERE \
								filefolder LIKE ?', (originfile+'%',)).fetchone()[0]
				if exist:
					logging.debug ('\tFolder has some songs to be processed, I will not move this folder: {}'.format(originfile))
					continue
				logging.debug ('\t > folder is going to be associated: {}'.format(originfile))
				afolder_counter += 1
				typeflag = 'Afolder'
			else:
				logging.warning ('This may be a symbolic link. It will be discarded')
				continue
			Aitemdict [item] = typeflag
		## Selecting the most suitable destination
		winnerpath = ''
		points = 0
		for i in ATargetdict:
			if ATargetdict[i] > points:
				winnerpath, points = i, ATargetdict[i]
					
		## Inserting Associated files into DB
		for i in Aitemdict:
			valuetuple = (os.path.join(originfolder,i),   os.path.join(winnerpath,i),   Aitemdict[i])
			con.execute ('INSERT INTO associatedfiles VALUES (?,?,?)', valuetuple)
		logging.debug('\tleading processed files: {}'.format(leading_counter))
		logging.debug('\tassociated processed files: {}'.format(associated_counter))
		logging.debug('\tNumber of associated target Paths: {}'.format (len(ATargetdict)))
	con.commit ()

	### Moving files and folders (Filemovements)



				



		
	print 'Done!'
