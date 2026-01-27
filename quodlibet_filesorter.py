#!/usr/bin/python3
# -*- coding: utf_8 -*-

import sqlite3
import shutil, re, os, logging
from datetime import datetime
from glob import glob
from sys import stdout, argv
from readtag import get_id3Tag		# local library

__version__ = "2.1.0"

#=====================================
# Custom Error Classes
#=====================================
class NotStringError(ValueError):
	pass
class MalformedPathError(ValueError):
	pass
class EmptyStringError(ValueError):
	pass

#=====================================
# Functions
#=====================================
def NoTAlloChReplace (myfilename):
	''' This function gets a string and replace a set of characters by a underscore.
	It is intended to clean filenames and add compatibility with Windows and OSx file systems
		'''
	chars = r'\:*?"<>|'
	for i in chars:
		myfilename = myfilename.replace(i, '_')
	return myfilename

def trimto (texto, widht):
	textout = texto
	if len (texto) > widht:
		textout = "..." + texto [-47:]
	return textout

def Getchunklist (fgstring, delimitters):
	'''Getchunklist

	It splits into chunks a string expression due to delimiters
	delimieters must be a string of two characters
	it returns a list of aplitted texts

	example:
	Getchunklist ('~/Genre/<artist>/<album>/[<cd> -][<track> -]<title>.<ext>', '[]')
	Generated list is:
	[
		'~/Genre/<artist>/<album>/',
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
				'|~%':'-',
				}
	for a in charset:
		for i in a:
			string = string.replace (i,charset[a])

	return string

def itemcheck(pointer):
	''' returns what kind of a pointer is '''
	if not (type(pointer) is str):
		raise NotStringError ('Bad input, it must be a string')
	if pointer.find("//") != -1 :
		raise MalformedPathError ('Malformed Path, it has double slashes')
	try:
		if os.path.isfile(pointer):
			return 'file'
	except ValueError:
		print ('ValueError: embedded null byte')
		print ('file:', pointer)
		exit()

	if os.path.isdir(pointer):
		return 'folder'
	if os.path.islink(pointer):
		return 'link'
	return ""

def Nextfilenumber (dest):
	''' Returns the next filename counter as filename(nnn).ext
	input: /path/to/filename.ext
	output: /path/to/filename(n).ext
		'''
	if dest == "":
		raise EmptyStringError ('empty strings as input are not allowed')
	filename = os.path.basename (dest)
	extension = os.path.splitext (dest)[1]
	# extract secuence
	expr = r'\(\d{1,}\)' + extension
	mo = re.search (expr, filename)
	try:
		grupo = mo.group()
	except:
		#  print ("No final counter expression was found in %s. Counter is set to 0" % dest)
		counter = 0
		cut = len (extension)
	else:
		#  print ("Filename has a final counter expression.  (n).extension ")
		cut = len (mo.group())
		countergroup = (re.search (r'\d{1,}', grupo))
		counter = int (countergroup.group()) + 1
	if cut == 0 :
		newfilename = os.path.join( os.path.dirname(dest), filename + "(" + str(counter) + ")" + extension)
	else:
		newfilename = os.path.join( os.path.dirname(dest), filename [0:-cut] + "(" + str(counter) + ")" + extension)
	return newfilename

def Nextplaylistname (dest):
	""" It checks and gives a new name to the playlist.
		Adds a 0 to the end.
		If newer file exists, the adds another 0 and so on
		"""
	newname = dest+"0"
	while itemcheck(newname) != "":
		newname = newname+"0"
	return newname

def Filemove (origin, dest):
	""" Moves files or folders,
	it makes necessary directories,
	moves folders and subfolders,
	it gives a next secuencial number in case of an existing archive
	it returns the moved path.

	please do not use with symliks.
	
	___dependencies__:
		itemcheck (pointer)
		Nextfilenumber (dest)
		dummy variable
		"""

	origin_is = itemcheck (origin)
	if origin_is not in ('file','folder'):
		logging.warning ('!! This should not be here, is a link !!')
		return None
	while itemcheck (dest) != "":
		dest = Nextfilenumber (dest)
		logging.info ("\tObject-file already exists at destination, assigning recursively a new name. >> {}".format(dest))
		if dest == origin:
			logging.info ("\tFound itself while iterating a new name. The file remains.>> {}".format(dest))
			return dest

	if not dummy:
		renameflag = False
		if origin.lower() == dest.lower():
			renameflag = True
			dest = dest + "_"
		if origin_is == 'file':
			if itemcheck (os.path.dirname(dest)) == '':
				os.makedirs (os.path.dirname(dest))
		shutil.move (origin, dest)
		if renameflag:
			shutil.move (dest, dest[:-1])
			dest=dest.removesuffix("_")
	logging.debug ("\t{} has been moved. {}".format(origin_is,dummymsg))
	return dest

def Pathnormalizer (path):
	normpath = path
	normpath = re.sub ('/+', '/', normpath)
	return normpath

class Progresspercent:
	''' Show the progression of an activity in percentage
	it is swhon on the same line'''
	def __init__ (self, maxValue, title = '', showpartial=True):
		if title != '':
			self.title = f" {title} "  # Name of the 
		else:
			self.title = " "
		self.maxValue = maxValue
		self.partial = showpartial

	def showprogress (self, p, valuetext = ""):
		'''
		Shows the progress in percentage vía stdout, and returns its value again.
		'''
		progresspercent = '{:.2%}'.format(float(p) / self.maxValue)
		if self.partial == True:
			progresspartial = '({:6}/{:<6})'.format(p,self.maxValue)
		else:
			progresspartial = ''
		progresstext = f"{self.title}{valuetext}{progresspartial}{progresspercent}"
		stdout.write (progresstext + chr(8)*len(progresstext))
		if p == self.maxValue:
			stdout.write('\n')
		stdout.flush()
		return progresspercent

def fetchtagline (textfile,tag,sep):
	'''Opens a textfile and fetch a value when the tag and sep is encountered

		'''
	with open (textfile,'r') as f:
		for line in f:
			if line.startswith(tag):
				pos = line.find(sep)
				if pos > 0:
					value = line[pos+1:].strip()
					break
	return value

def getmetasep (scanline,sep):
	#scanline = scanline
	chunklist = list()
	chunk = ''
	rpos = 0
	while rpos < len (scanline):
		esc = False
		if scanline [rpos] == '\\':
			if rpos+1 < len (scanline):
				rpos += 1
				esc = True
		addchar = scanline [rpos]
		chunk = chunk + addchar
		if not esc and addchar == sep:
			chunklist.append(chunk[:-1])
			chunk = ''
		if rpos+1 == len(scanline):
			chunklist.append(chunk)
		rpos += 1
	return chunklist

def addchilddirectory(directorio):
	""" Returns a list of child directories

	Usage: addchilddirectory(directory with absolute path)"""
	addeddirs = []
	ficheros = os.listdir(directorio)
	for a in ficheros:
		item = os.path.join(directorio, a)
		if os.path.isdir(item):
			addeddirs.append(item)
	return addeddirs

def lsdirectorytree( directory = os.getenv( 'HOME')):
	""" Returns a list of a directory and its child directories

	usage:
	lsdirectorytree ("start directory")
	By default, user's home directory

	Own start directory is also returned as result
	"""
	#init list to start, own start directory is included
	dirlist = [directory]
	#setting the first scan
	moredirectories = dirlist
	while len (moredirectories) != 0:
		newdirectories = moredirectories
		moredirectories = list ()
		for element in newdirectories:
			toadd = addchilddirectory(element)
			moredirectories += toadd
		dirlist += moredirectories
	return dirlist

def getqluserfolder ():
	folderlist = [
		os.path.join (os.getenv('HOME') ,'.config/quodlibet'),
		os.path.join (os.getenv('HOME')	,'.quodlibet'),
	]
	for f in folderlist:
		if itemcheck(f) == 'folder':
			return f
	else:
		print ('no quodlibet config folder was found,\nEnsure that Quodlibet is intalled')
		exit()

#=====================================
# User config 
#=====================================
userfilegrouppingtag = 'filegroupping'  # Tag name which defines the desired path structure for the file

qluserfolder  =  getqluserfolder()
qlcfgfile     = os.path.join (qluserfolder		,'config')
dbpathandname = f'{userfilegrouppingtag}.sqlite3'  # Sqlite3 database archive for processing
#filepaths = [os.path.join(os.getenv('HOME'),'Music'), ]		# List of initial paths to search.

dummy = False  # Dummy mode, True means that the software will check items, but will not perform file movements
dummymsg = ''


#========== Command line options ==========
# for now just one parameter --dummy
try:
	if argv[1] == '--dummy':
		dummy = True
except:
	pass

#========== Dummy message ==========
if dummy:
	dummymsg = '(dummy mode)'
	print ('** (Running in Dummy mode) **')

#========== Fetch library paths ==========
scanline = fetchtagline (qlcfgfile,'scan','=')
librarypaths = getmetasep (scanline,':')
print (f'libraries to read:{librarypaths}')


#=====================================
# Main
#=====================================
if __name__ == '__main__':
	print (f'Running, this could take a while. {dummymsg}')

	loginlevel = 'INFO'  # INFO ,DEBUG
	logpath = './'
	logging_file = os.path.join(logpath, f'{userfilegrouppingtag}.log')


	# Getting current date and time
	now = datetime.now()
	today = "/".join([str(now.day), str(now.month), str(now.year)])
	tohour = ":".join([str(now.hour), str(now.minute)])

	print (f'\tLoginlevel: {loginlevel}')
	logging.basicConfig(
		level = loginlevel,
		format = '%(asctime)s : %(levelname)s : %(message)s',
		filename = logging_file,
		filemode = 'w'  # a = add
		)
	print (f'\tLogging to: {logging_file}')

	logging.info (f'Quodlibet config folder fount at {qluserfolder}')
	#initializing DB
	
	maxmtime = None
	if os.path.isfile(dbpathandname):
		con = sqlite3.connect (dbpathandname)
		maxmtime = con.execute ('SELECT MAX (modif) FROM SongsTable').fetchone()[0]
		logging.info("Found old database file, I will use it to retrieve the last modified time of the last processed file.")
		if maxmtime:
			print ('Using last modified time to exclude unmodified files')
		os.remove (dbpathandname)
	con = sqlite3.connect (dbpathandname)
	
	con.execute ("CREATE TABLE SongsTable \
		(id INT PRIMARY KEY 	NOT NULL, \
		mountpoint	TEXT 	NOT NULL, \
		filefolder	TEXT 	NOT NULL, \
		filename 	TEXT 	NOT NULL, \
		modif		REAL 	NOT NULL, \
		format		TEXT 	NOT NULL, \
		fullpathfilename	TEXT 	NOT NULL,\
		filegroupping TEXT 	NOT NULL, \
		targetpath	TEXT 	NOT NULL, \
		fileflag	TEXT 	NOT NULL)" )

	con.execute ('CREATE VIEW "ScannedFolders" AS SELECT DISTINCT filefolder FROM songstable WHERE fullpathfilename <> targetpath')
	con.execute ('CREATE VIEW "Allfolders" AS SELECT DISTINCT filefolder FROM songstable')

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
	
	print ('\tScanning librarypaths for mp3 folders.')
	# Iterating over scanned paths

	for scanpath in librarypaths:
		folders_counter, processed_counter = 0, 0
		### iterate over mp3 files. addressing Database
		listree = lsdirectorytree (scanpath)
		progressindicator = Progresspercent (len(listree), title = '\tScanning files in directories', showpartial=True)
		for d in listree:
			if "/.Trash" in d:	#is a trash folder, ignoring
				continue
			itemlist = list()
			itemlist += glob(os.path.join(d,'*.mp3'))
			itemlist += glob(os.path.join(d,'*.MP3'))
			itemlist += glob(os.path.join(d,'*.Mp3'))
			if len (itemlist) > 0:
				for f in itemlist:
					logging.debug ('>>>>')
					logging.debug (f'Working on file: {f}')
					fullpathfilename = os.path.join (d,f)
					modif = os.path.getmtime(fullpathfilename)
					#Discards old modified files
					if maxmtime:
						if modif <= maxmtime:
							print (f'\tSkipping {fullpathfilename} as it is older than the last processed file.')
							continue
					audiofile = get_id3Tag (fullpathfilename)
					if audiofile == None:
						continue
					tagvalue = audiofile.readtag (userfilegrouppingtag)
					logging.debug (f'\tFilegroupping value:{tagvalue}')
					if not (tagvalue == None or tagvalue == ''):
						processed_counter += 1
						mountpoint = scanpath
						filefolder = d
						filename = f
						extension = os.path.splitext (fullpathfilename)[1]
						filegroupping:str = tagvalue
						if filegroupping.endswith ('.<ext>'):
							addfilenameflag = False
							tmpfilegroupping = filegroupping [:-6] # Deletes '.<ext>' trailing
						else:
							addfilenameflag = True
							tmpfilegroupping = filegroupping
						#Splicing filegrouppingtag in chunks
						chunklist = Getchunklist (tmpfilegroupping,'[]')
						logging.debug ('Chunklist = {}'.format(chunklist))
						targetpath = ''
						for chunk in chunklist:
							# Checking and flagging an optional chunk
							optionalflag = False
							if chunk.startswith ('[') and chunk.endswith (']'):
								optionalflag = True
							# We start with the chunk, and later perform tag substitutions
							formedchunk:str = chunk
							taglist = re.findall (r'<\w*>',chunk)
							logging.debug (f'\tchunk  = {chunk}')
							logging.debug (f'\ttaglist= {taglist}')
							for tag in taglist:
								metaname = tag[1:-1] # Eliminates < >
								# Break and return an empty chunk if the tag is not present				
								if metaname not in audiofile.keys() and optionalflag: 
									formedchunk = ''
									break
								metavalue:str = audiofile.readtag (metaname)
								# we trim the slash and total tracks if any
								if metaname in ('tracknumber','discnumber') :
									slashpos = metavalue.find('/')
									if slashpos != -1:
										metavalue = metavalue [:slashpos]
									if metavalue.isdigit():
										metavalue = '{:0>2}'.format (metavalue)
								#if metavalue.endswith('[Unknown]'):
								if metavalue == None:
									metavalue = f'[no <{metaname}>]'
								logging.debug (f'\t\tmetaname = {metaname}\tmetavalue = {metavalue}')
								metavalue = CharChange (metavalue)  # clears some non allowed chars
								formedchunk = formedchunk.replace('<'+ metaname + '>',metavalue)
							if optionalflag and formedchunk != '':
								formedchunk = formedchunk [1:-1]
							targetpath = targetpath + formedchunk
						# Adding a mountpoint lead if necessary
						if targetpath.startswith ('~/'):
							targetpath = mountpoint + targetpath [1:]
						# Relative paths are mounted on current song's mount-point
						elif not targetpath.startswith ('/'):
							targetpath = os.path.join(mountpoint,targetpath)
						# Preserving original filename if could not constructo a valid one.
						if targetpath.endswith('/') and not addfilenameflag:
							#targetpath = targetpath[:-1]
							addfilenameflag = True
							logging.warning ('It was not possible construct a valid filename, I will preserve original filename.')
						# Adding original filename if necessary
						if addfilenameflag:
							targetpath = targetpath + os.path.basename(fullpathfilename)
						else:
							targetpath = targetpath + extension
						targetpath = os.path.normpath (targetpath)
						targetpath = NoTAlloChReplace (targetpath)
						logging.debug ('\ttargetpath = {targetpath}')
						valuetuple = ( 	processed_counter,
										mountpoint,
										filefolder,
										filename,
										modif,
										extension[1:],
										fullpathfilename,
										filegroupping,
										targetpath,
										'Qfile'
										)
						con.execute ("INSERT INTO SongsTable VALUES (?,?,?,?,?,?,?,?,?,?)", valuetuple)
			progressindicator.showprogress (folders_counter); folders_counter += 1
		con.commit()
	
	print ('\t{} total songs fetched from librarypaths.'.format(processed_counter))
	if processed_counter > 0:
		print ('\t{} songs with <{}> tag defined ({:.1%}).'.format(processed_counter, userfilegrouppingtag, float(processed_counter)/processed_counter))
	### 
	### Looking for Associated files and folders
	###
	logging.debug ('#'*43)
	logging.debug ('## Looking for Associated files and folders')
	logging.debug ('#'*43)
	print ('\tLooking for associated files.')
	cursor = con.cursor ()
	cursor.execute ('SELECT * FROM ScannedFolders')
	for contaninerfolder in cursor:
		originfolder = contaninerfolder[0]  # SELECT Query returns a tuple ([0],)
		if itemcheck (originfolder) != 'folder':
			logging.warning('Folder is not present, Skipping!: {}'.format(originfolder))
			continue

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
								FROM SongsTable WHERE \
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
				if "/.Trash" in originfile:
					logging.debug ('\t > folder is a Trash folder, skipping: {}'.format(originfile))
					continue
				exist = con.execute ('SELECT COUNT (filefolder) \
								FROM Allfolders \
								WHERE filefolder LIKE ?', (originfile+'%',)).fetchone()[0]
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
	con.commit()

	## Lowering associated file names and extension simplification.
	# Lower filenames in targetpath field.
	# On SAMBA systems, upper and lowercase is the same file/path
	cursor = con.cursor ()
	cursor2 = con.cursor ()
	cursor.execute ('SELECT * FROM Associatedfiles WHERE fileflag = "Afile" ')
	for originfile, targetpath, fileflag in cursor:
		#print (originfile, targetpath, fileflag)
		Tpath, Tfile = os.path.split(targetpath)
		Tfilename, Tfileext = os.path.splitext(Tfile)
		Tfilename, Tfileext = Tfilename.lower(), Tfileext.lower()
		if Tfileext == ".jpeg":
			Tfileext = ".jpg"
		newtargetpath = os.path.join(Tpath,Tfilename+Tfileext)
		if targetpath != newtargetpath:
			cursor2.execute("UPDATE Associatedfiles SET targetpath=? WHERE originfile=?", (newtargetpath, originfile))
	con.commit()

	# Reporting
	T_associated_files = con.execute("SELECT COUNT () FROM filemovements WHERE fileflag = 'Afile'").fetchone()[0]
	T_afolder_counter = con.execute("SELECT COUNT () FROM filemovements WHERE fileflag = 'Afolder'").fetchone()[0]
	pluralfi, pluralfo = 's','s'
	if T_associated_files == 1: pluralfi = ''
	if T_afolder_counter == 1: pluralfo = ''
	print (f'\t\t{T_associated_files} associated file{pluralfi} found.')
	print (f'\t\t{T_afolder_counter} associated folder{pluralfo} found.')

	###
	### File operations
	###
	total = cursor.execute ("SELECT COUNT () FROM filemovements where originfile not like '%/.Trash-%'").fetchone()[0]
	progressindicator = Progresspercent (total, title = '\tMoving files', showpartial=True)
	counter = 1
	cursor.execute ("SELECT * FROM filemovements WHERE originfile NOT LIKE '%/.Trash-%'")
	print ('\tPerforming file operations.')
	for origin, dest, fileflag in cursor:
		progressindicator.showprogress (counter); counter += 1
		logging.debug (f'\t {fileflag}	from: {origin}')
		if itemcheck (origin) == '':
			loggingmsg = f'** Warning, {fileflag} at {trimto(origin,20)} does not exist. Skipping'
			print (loggingmsg)
			logging.warning (loggingmsg)
			continue
		movedto = Filemove (origin, dest)
		logging.debug (f'\t file moved: {dest}')
		logging.debug ('')
	###
	### fixing playlists
	###
	"""
	print ('\tChecking Playlists')
	
	# Create playlist DataBase and View
	con.execute ("CREATE TABLE Playlists \
		(id INT PRIMARY KEY 	NOT NULL, \
		playlistfile	TEXT 	NOT NULL, \
		position		INT 	NOT NULL, \
		originfile		TEXT 	NOT NULL)" )
	con.execute ("CREATE VIEW Playlists_new AS SELECT p.*, s.targetpath FROM Playlists as p LEFT JOIN SongsTable AS s ON p.originfile=s.fullpathfilename ORDER BY id")
	
	# Populate DB with playlists
	playlistfolder = os.path.join(qluserfolder,"playlists")
	playfiles = glob (os.path.join(playlistfolder,"*"))
	processed_counter = 0
	for f in playfiles:
		linecounter = 0
		print (f)
		with open (f, 'r') as txt:
			for line in txt:
				linecounter += 1
				processed_counter += 1
				valuetuple = ( 	processed_counter,
								f,
								linecounter,
								line[:-1]
							)
				con.execute ("INSERT INTO Playlists VALUES (?,?,?,?)", valuetuple)
		con.commit ()
	
	# Writting changes
	AfectedPlaylists = con.execute ('SELECT playlistfile from Playlists_new where originfile <> targetpath GROUP BY playlistfile')
	cursor = con.cursor ()
	for Playlist in AfectedPlaylists:
		cursor.execute ('SELECT originfile, targetpath FROM Playlists_new WHERE playlistfile=? ORDER BY id', Playlist)
		if not dummy:
			with open (Playlist[0], 'w') as txt:
				for entry in cursor:
					towrite = entry[1]
					if towrite == None:
						towrite = entry [0]
					txt.write (towrite+"\n")
			# renaming playlists
			shutil.move(Playlist[0],Nextplaylistname(Playlist[0]))
	"""
	# 
	###
	### Removing empty folders
	###
	print ('\tRemoving empty folders.')
	logging.info ('### Checking empty folders to delete them')
	cursor = con.execute ('SELECT * FROM ScannedFolders')
	for i in cursor:
		dir_item = i[0]
		logging.info (f'checking: {dir_item}')
		if itemcheck(dir_item) != 'folder':
			logging.warning ('\tDoes not exists or is not a folder. Skipping')
			continue
		while dir_item not in librarypaths :
			if len (os.listdir (dir_item)) == 0:
				if not dummy:
					shutil.rmtree (dir_item)
					logging.info ('\tDeleted (was empty)')
				print (f"\t\tempty folder removed: {trimto (dir_item,40)} {dummymsg}")
				logging.info (f'Empty folder removed: {dir_item}')
			else:
				break
			dir_item = os.path.dirname (dir_item)
	con.close ()
	print ('Done!', 'Visit https://github.com/pablo33/quodlibet-filesorter for updates')