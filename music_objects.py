
from .basic_functions import ceiling, string_to_sequence, calculate_bar_ticks, velocity_sequence_to_min_timespan
from . import parameter_setter 
from . import rhythm_parser 

class Note():
	def __init__(self, firstarg = None, duration = None, velocity = None):
		self.startTime = 0
		self.duration = 0
		self.velocity = 0

		if firstarg != None:
			if isinstance(firstarg,str):
				intlist = string_to_sequence(firstarg,int)
				self.startTime = intlist[0]
				self.duration = intlist[1]
				self.velocity = intlist[2]
			elif isinstance(firstarg,int):
				self.startTime = firstarg

		if duration != None:
			self.duration = duration
		if velocity != None:
			self.velocity = velocity


	def to_string(self):
		return "(%d,%d,%f)" %(self.startTime, self.duration, self.velocity)


# NoteSequence is a list of Note
class NoteSequence(list):
	def __init__(self, noteSequenceString = None):
		if noteSequenceString != None:
			self.string_to_note_sequence(noteSequenceString)

	def string_to_note_sequence(self, noteSequenceString):
		noteSequenceString = rhythm_parser.discard_spaces(noteSequenceString)
		# try:
			# Turning "(1,2,3),(4,5,6),(7,8,9)" into ["1,2,3","4,5,6,","7,8,9"]
		listStrings = noteSequenceString[1:-1].split("),(")
		for localString in listStrings:
			self.append(Note(localString))

	def to_string(self):
		noteSequenceString = ""
		for note in self:
			noteSequenceString += note.to_string() + ","
		return noteSequenceString[:-1]


class NormalisedVelocityValueOutOfRange(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# VelocitySequence is a list of float numbers
class VelocitySequence(list):
	def __init__(self, velocitySequence = None):
		if velocitySequence != None:
			if isinstance(velocitySequence,str):
				self.string_to_velocity_sequence(velocitySequence)
			elif isinstance(velocitySequence, list):
				self+=velocitySequence

	def string_to_velocity_sequence(self,inputString):
		
		def convert_velocity_value(argstring):
			value = float(argstring)
			if value>=0 and value<=1:
				return value
			else:
				raise NormalisedVelocityValueOutOfRange("Value: "+argstring+" in " + inputString)

		self.extend(string_to_sequence(inputString,convert_velocity_value))


	def to_string(self):
		return str(velocity_sequence_to_min_timespan(self))[1:-1].replace(" ","")


def velocity_sequence_to_note_sequence(velocitySequence, nextbarVelocitySequence = None):
	
	noteSequence = NoteSequence()

	for index in range(len(velocitySequence)):
		if (velocitySequence[index]!= 0): # onset detected
			startTime = index			
			velocity = velocitySequence[index]

			# if there are previous notes added
			if( len(noteSequence) > 0):
				previousNote = noteSequence[-1]
				previousNote.duration = startTime - previousNote.startTime

			# add the current note into note sequence
			noteSequence.append( Note(startTime, 0, velocity) )

	# to set the duration for the last note
	if( len(noteSequence) > 0):
		lastNote = noteSequence[-1]
		
		if nextbarVelocitySequence == None:
			lastNote.duration = len(velocitySequence) - lastNote.startTime
		else:
			nextNoteStartTime = next((index for index, v in enumerate(nextbarVelocitySequence) if v), None)
			lastNote.duration = len(velocitySequence) + nextNoteStartTime-lastNote.startTime


	return noteSequence


def note_sequence_to_velocity_sequence(noteSequence, timespanTicks = None):

	velocitySequence = VelocitySequence()
	
	previousNoteStartTime = -1

	for note in noteSequence:
		
		interOnsetInterval = note.startTime - previousNoteStartTime	
		#ignore note if it is part of a chord...
		if interOnsetInterval!=0:
			velocitySequence += [0]*(interOnsetInterval-1)	
			velocitySequence += [note.velocity]

		previousNoteStartTime = note.startTime

	if timespanTicks!=None:
		velocitySequence += [0]*(timespanTicks - len(velocitySequence))
	else:
		velocitySequence += [0]*(noteSequence[-1].duration-1)

	# normalising velocity sequence between 0-1
	if max(velocitySequence)>0:
		velocitySequence = VelocitySequence([float(v)/max(velocitySequence) for v in velocitySequence])

	return velocitySequence


class BarList(list):
	def append(self,bar):
		if(len(self)>0):
			bar.set_previous_bar(self[-1])
			self[-1].set_next_bar(bar)
		super(BarList, self).append(bar)

	def concat(self, barList):
		while(len(barList)!=0):
			localbar = barList[0]
			self.append(localbar)
			barList.remove(localbar)

	def to_string(self, sequenceType="y"):
		
		output = ""

		for bar in self:
			prev = bar.get_previous_bar()

			params = "t"+sequenceType

			if prev!=None and prev.get_time_signature()==bar.get_time_signature():
				params = "-"+params	
			
			output += " " + bar.to_string(params)

		return output

class Bar:
	def __init__(self, rhythmSequence, timeSignature, ticksPerQuarter=None, qpmTempo=None, nextBar=None, prevBar=None):
		if isinstance(rhythmSequence, NoteSequence):
			self.noteSequence = rhythmSequence
			self.velocitySequence = None 
		elif isinstance(rhythmSequence, VelocitySequence):
			self.velocitySequence = rhythmSequence
			self.noteSequence = None 

		if isinstance(timeSignature, str):
			self.timeSignature = TimeSignature(timeSignature)
		else:
			self.timeSignature = timeSignature
		
		if ticksPerQuarter==None:
			self.tpq = len(self.get_velocity_sequence())*self.timeSignature.get_denominator()/(4*self.timeSignature.get_numerator())
		else:
			self.tpq = ticksPerQuarter
		
		self.qpm = qpmTempo
		


		self.nextBar = nextBar
		self.prevBar = prevBar

	def get_note_sequence(self):
		if self.noteSequence == None:
			nextbarVelocitySequence = None
			if self.nextBar != None:
				nextbarVelocitySequence = self.nextBar.get_velocity_sequence()
			self.noteSequence = velocity_sequence_to_note_sequence(self.velocitySequence, nextbarVelocitySequence)
		return self.noteSequence

	def get_velocity_sequence(self):
		if self.velocitySequence == None:
			self.velocitySequence = note_sequence_to_velocity_sequence(self.noteSequence, self.get_bar_ticks())
		return self.velocitySequence

	def get_binary_sequence(self):
		return ceiling(self.get_velocity_sequence())

	def get_next_bar(self):
		return self.nextBar

	def get_previous_bar(self):
		return self.prevBar

	def set_next_bar(self, bar):
		self.nextBar = bar

	def set_previous_bar(self, bar):
		self.prevBar = bar		

	def get_subdivision_sequence(self):
		return self.timeSignature.get_subdivision_sequence()

	def get_beat_level(self):
		return self.timeSignature.get_beat_level()

	def get_time_signature(self):
		return self.timeSignature

	# return the length of a bar in time units (ticks)
	def get_bar_ticks(self):
		return calculate_bar_ticks(self.timeSignature.get_numerator(),self.timeSignature.get_denominator(), self.tpq)

	def is_empty(self):
		if max(self.get_velocity_sequence())>0:
			return False
		else:
			return True

	def to_string(self, sequenceType="ty"):
		
		# prev = self.get_previous_bar()
		# if prev!=None:
		# 	if prev.get_time_signature()==self.get_time_signature():
		# 		output=""
		output = ""

		if "-t" not in sequenceType:
			output = "t{"+self.timeSignature.to_string()+"}"

		if "v" in sequenceType:
			output += "v{"+self.get_velocity_sequence().to_string()+"}"
		else:
			output += "y{"+self.get_note_sequence().to_string()+"}"

		return output


class TimeSignature():
	def __init__(self, inputString):
		if inputString in parameter_setter.read_time_signature():
			self.tsString = inputString
		else:
			print("Error: undefined time-signature: ", inputString)
			raise NullTimeSignatureError

	def get_subdivision_sequence(self):
		return parameter_setter.timeSignatureBase[self.tsString][0]
	
	def get_beat_level(self):
		return parameter_setter.timeSignatureBase[self.tsString][1]

	def get_numerator(self):
		return int(self.tsString.split('/')[0])
			
	def get_denominator(self):
		return int(self.tsString.split('/')[1])

	def to_string(self):
		return self.tsString


