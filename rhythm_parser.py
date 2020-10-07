'''
Authors: Chunyang Song, Christopher Harte
Institution: Centre for Digital Music, Queen Mary University of London
'''

# Parse the rhythm file and return a list of Bar objects
#Piece = []

from parameter_setter import timeSignatureBase
from music_objects import *

comment_sign = '#'

def discard_comments(line):
	if comment_sign in line:
		line = line[0:line.find(comment_sign)]
	return line

def discard_spaces(line):
	line = line.replace(" ", '').replace("\t", '')
	return line

def discard_linereturns(line):
	line = line.replace("\n","").replace("\r","")
	return line
	

# def extractInfo(line):
# 	try:
# 		if '{' not in line and '}' not in line:
# 			raise RhythmSyntaxError(line)
# 		else:
# 			return line[line.find('{')+1 : line.find('}')]
# 	except RhythmSyntaxError:
# 		print 'Rhythmic information needs to be enclosed by "{" and "}"'


def read_rhythm(fileName):
	fileContent = open(fileName)

	barList = BarList()

	tempo=None
	timeSignature=None
	ticksPerQuarter=None

	# for each line in the file, parse the line and add any 
	# new bars to the main bar list for the piece
	for line in fileContent:
		
		# ignore the line if it's only a comment
		if is_comment(line) or line=="\n":
			continue

		# if time signature has not yet been set then it should be the first 
		# thing we find in a file after the comments at the top
		if timeSignature==None:
			(field, line) = get_next_field(line)
			# if there is a valid field, it should be a time signature
			if field!=None:
				[fieldname,value] = field
				if fieldname.lower()=="t":
					timeSignature = TimeSignature(value)
				else:
					print('Error, first field in the file should set the time signature.')

		# parse the line
		(newbarlist, tempo, timeSignature, ticksPerQuarter) = parse_line(line, timeSignature,  tempo, ticksPerQuarter)
		
		# if we found some bars in this line then add them to the overall bar list
		if len(newbarlist)>0:
			barList.concat(newbarlist)

	return barList

def is_comment(line):
	if discard_spaces(line)[0]==comment_sign:
		return True
	else:
		return False

def parse_line(line,  timeSignature=None, tempo=None, ticksPerQuarter=None):
	
	#strip the line of line returns, spaces and comments
	line = discard_linereturns(discard_spaces(discard_comments(line)))
	
	bars = BarList()

	#work through each field in the line
	while len(line)>0:
		(field, line) = get_next_field(line)

		if field!=None:
			
			[fieldname, value] = field
			
			if fieldname.lower() == "v":
				#velocity sequence
				bar = Bar(VelocitySequence(value),timeSignature, ticksPerQuarter, tempo)	
				bars.append(bar)

			elif fieldname.lower() == "y":
				#note sequence	
				bar = Bar(NoteSequence(value), timeSignature, ticksPerQuarter, tempo)	
				bars.append(bar)

			elif fieldname.lower() == "t":
				#time signature
				timeSignature = TimeSignature(value)
			
			elif fieldname.lower() == "tpq":
				#ticks per quarter
				ticksPerQuarter = int(value)
			
			elif fieldname.lower() == "qpm":
				#tempo
				tempo = int(value)
			
			else:
				print('Unrecognised field type: "' + fieldname + '"')
	
	return bars, tempo, timeSignature, ticksPerQuarter

class RhythmSyntaxError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def get_next_field(line):
	index = line.find("}")
	field = None
	if index>=0:
		fieldtext = line[:index]
		line = line[index+1:]
		field = fieldtext.split("{")
	else:
		print('Error, incorrect syntax: "'+line+'"')
		raise RhythmSyntaxError(line)

	return field,line





