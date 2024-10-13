#!/usr/bin/python3
# -*- coding: utf_8 -*-

import logging
import eyed3, re

framedict = {
"""
Declared ID3v2 frames
https://id3.org/id3v2.4.0-frames
"""

"AENC" : "Audio encryption",
"APIC" : "Attached picture",
"ASPI" : "Audio seek point index",
"COMM" : "Comments",
"COMR" : "Commercial frame",
"ENCR" : "Encryption method registration",
"EQU2" : "Equalisation (2)",
"ETCO" : "Event timing codes",
"GEOB" : "General encapsulated object",
"GRID" : "Group identification registration",
"LINK" : "Linked information",
"MCDI" : "Music CD identifier",
"MLLT" : "MPEG location lookup table",
"OWNE" : "Ownership frame",
"PRIV" : "Private frame",
"PCNT" : "Play counter",
"POPM" : "Popularimeter",
"POSS" : "Position synchronisation frame",
"RBUF" : "Recommended buffer size",
"RVA2" : "Relative volume adjustment (2)",
"RVRB" : "Reverb",
"SEEK" : "Seek frame",
"SIGN" : "Signature frame",
"SYLT" : "Synchronised lyric",		#"Synchronised lyric/text"
"SYTC" : "Synchronised tempo codes",
"TALB" : "album",					#"Album/Movie/Show title"
"TBPM" : "bpm", 					#"BPM (beats per minute)",
"TCOM" : "composer",				#"Composer"
"TCON" : "genre",					#"Content type"
"TCOP" : "Copyright message",
"TDEN" : "Encoding time",
"TDLY" : "Playlist delay",
"TDOR" : "Original release time",
"TDRC" : "date", 					#"Recording time",
"TDRL" : "Release time",
"TDTG" : "Tagging time",
"TENC" : "Encoded by",
"TEXT" : "lyricist",				#Lyricist/Text writer
"TFLT" : "File type",
"TIPL" : "Involved people list",
"TIT1" : "Content group description",
"TIT2" : "title",  					#"Title/songname/content description"
"TIT3" : "subtitle",				#"Subtitle/Description refinement"
"TKEY" : "Initial key",
"TLAN" : "Language",				#"Language(s)"
"TLEN" : "Length",
"TMCL" : "Musician credits list",
"TMED" : "Media type",
"TMOO" : "Mood",
"TOAL" : "original album",			#"Original album/movie/show title"
"TOFN" : "original filename",		#"Original filename"
"TOLY" : "original lyricist",		#"Original lyricist(s)/text writer(s)",
"TOPE" : "original atist",			#"Original artist(s)/performer(s)"
"TOWN" : "file owner",				#"File owner/licensee"
"TPE1" : "artist",					#"Lead performer(s)/Soloist(s)",
"TPE2" : "performer",					#"Band/orchestra/accompaniment",
"TPE3" : "band", 					#"Conductor/performer refinement",
"TPE4" : "Interpreted, remixed, or otherwise modified by",
"TPOS" : "discnumber",				#"Part of a set",
"TPRO" : "Produced notice",
"TPUB" : "Publisher",
"TRCK" : "tracknumber", 			#"Track number/Position in set",
"TRSN" : "Internet radio station name",
"TRSO" : "Internet radio station owner",
"TSOA" : "Album sort order",
"TSOP" : "Performer sort order",
"TSOT" : "Title sort order",
"TSRC" : "ISRC (international standard recording code)",
"TSSE" : "Software/Hardware and settings used for encoding",
"TSST" : "discsubtitle",			#"Set subtitle",
"TXXX" : "User defined text information frame",
"UFID" : "Unique file identifier",
"USER" : "Terms of use",
"USLT" : "lyric",					#"Unsynchronised lyric/text transcription",
"WCOM" : "Commercial information",
"WCOP" : "Copyright",				#"Copyright/Legal information",
"WOAF" : "Official audio file webpage",
"WOAR" : "Official artist webpage", #"Official artist/performer webpage",
"WOAS" : "Official audio source webpage",
"WORS" : "Official Internet radio station homepage",
"WPAY" : "Payment",
"WPUB" : "Publishers official webpage",
"WXXX" : "User defined URL link frame",
# """ Extras  """
"TCMP" : "compilation",
"XRVA" : "Relative volume adjustment",
"NCON" : "NCON",
"RGAD" : "RGAD",
}


notusable = [
'USLT',
'APIC',
'POPM',
'COMM',
'RVA2',
'XRVA',
'PRIV',
'WXXX',
'GEOB',
'MCDI',
'PCNT',
'UFID',
'WOAF',
'WCOP',
'USER',

'NCON',
'RGAD',

	]

class get_id3Tag:
	def __init__ (self, filemp3):
		self.mp3audio = eyed3.load (filemp3)
		if self.mp3audio != None:
			self.keysdict = dict()
			self.framelist = list()
			if self.mp3audio.tag != None:
				for a in self.mp3audio.tag.frameiter():
					keyframe = a.id.decode()
					self.framelist.append (keyframe)
					try:
						rawtext  = a.data
					except KeyError:
						rawtext = ''
					key 	 = framedict.get (keyframe)
					value	 = ''
				
					if keyframe == 'TXXX':
						key = a.description [11:] # Removes 'Quodlibet::' leading text
						value = a.text
					elif keyframe == 'APIC':
						value = 'Has picture'
					elif keyframe in notusable:
						value = 'unavailable'
					else:
						try:
							value = self.mp3audio.tag.getTextFrame(keyframe)
						except:
							try:
								value = a.data[1:-1].decode()
								print ('extra raw method', keyframe)
							except AssertionError:
								print (f'AssertionError while fetching frame {keyframe} separator.')
								value = 'AssertionError'
							except UnicodeDecodeError:
								print ('UnicodeDecodeError while decoding:', a.data)
								print ('Song:', filemp3)
								print ('Frame', keyframe)
								value = 'UnicodeDecodeError'
							except:
								value = 'unavailable'
						value = value.replace ('\x00', ', ')	# For frames with multiple texts in data
			
					value = value.strip()
					self.keysdict [key] = value
			else:
				logging.warning (f'No id3 info was found:{filemp3}')
		else:
			logging.critical (f'Not a valid mp3 file:{filemp3}')
			return None
			
	def readtag (self, key):
		"""
		Given a key, returns its text value. None in case of no key found.
			"""
		return self.keysdict.get(key)
	
	def keys (self):
		"""
		Returns a list of usable keys
			"""
		keyslist = []
		for item in self.keysdict:
			keyslist.append (item)
		return keyslist

	def frames (self):
		"""
		Returns a list of frames in order
			"""
		return self.framelist