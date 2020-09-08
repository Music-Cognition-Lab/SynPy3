# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 22:19:52 2015

@author: christopherh
"""

from midiparser import MidiFile, MidiTrack, DeltaTime, MidiEvent
#from RhythmParser import Bar

from music_objects import *
from basic_functions import *




def read_midi_file(filename):
	""" open and read a MIDI file, return a MidiFile object """

	#create a midifile object, open and read a midi file
	midiFile = MidiFile()
	midiFile.open(filename, 'rb')
	midiFile.read()
	midiFile.close()

	return midiFile

# def get_bars(midiFile, trackindex=1):
# 	""" returns a list of bar objects from a MidiFile object """

# 	# select a track to extract (default = 1, ignoring dummy track 0)
# 	track = midiFile.tracks[trackindex] 
# 	eventIndex = 0
# 	numNotes = 0

# 	noteonlist = []
# 	noteOnFound==True

# 	while noteOnFound==True:
# 		(noteOnIndex, noteOnDelta, noteOnFound) = self.find_event(track, eventIndex, lambda e: e.type == 'NOTE_ON')
# 		noteEvent = track.events[noteOnIndex]
# 		eventIndex = noteOnIndex + 1
            	

#find_event(x.tracks[0], 0, lambda e: (e.type == 'NOTE_ON') | (e.type == 'KEY_SIGNATURE') | (e.type == "TIME_SIGNATURE"))

'''
	#read midiFile
	
	

	run through selected track getting notes out to build bars

'''
	


def get_bars_from_midi(midiFile):

	# couple of inner functions to tidy up getting the initial values of
	# tempo and time signature
	def get_initial_tempo(timeList):

		tempo = None
		i=0
		# Find the initial time and tempo:
		while(tempo == None and i<len(timeList)):
			event = timeList[i]
			i = i + 1
			if event.type=="SET_TEMPO":
		 		if tempo==None:
					tempo = midi_event_to_qpm_tempo(event)

		if tempo==None:
			tempo = 120

		return tempo

	def get_initial_time_signature(timeList):

		timesig = None
		i=0
		# Find the initial time and tempo:
		while(timesig == None and i<len(timeList)):
			event = timeList[i]
			i = i + 1
			if event.type=="TIME_SIGNATURE":
				if timesig==None:
					timesig = midi_event_to_time_signature(event)

		if timesig==None:
			timesig = TimeSignature("4/4")
			
		return timesig


	def get_time_signature(timeList,barStartTime, barLength, ticksPerQuarter, currentTimeSignature = None):
		
		timesig = None
		i=0
		
		while(i<len(timeList)):
			# run through list until we find the most recent time signature
			# before the end of the current bar
			event = timeList[i]
			i = i + 1
			if event.time>=barStartTime+barLength:
				break

			if event.type=="TIME_SIGNATURE" and event.time>=barStartTime:
				timesig = midi_event_to_time_signature(event)
				event.type = "USED_TIME_SIGNATURE"
				barLength = calculate_bar_ticks(timesig.get_numerator(), 
												timesig.get_denominator(), 
												ticksPerQuarter)
	
		if timesig==None:
			if currentTimeSignature==None:
				timesig = TimeSignature("4/4")
			else:
				timesig = currentTimeSignature

		return timesig,barLength	

	def get_tempo(timeList,barStartTime, barEndTime, currentTempo = None):
		
		tempo = None
		i=0
		# get first event:
		while(i<len(timeList)):
			# run through list until we find the most recent time signature
			# before the end of the current bar
			event = timeList[i]
			i = i + 1
			if event.time>=barEndTime:
				break

			# run through list until we find the most recent tempo
			# before the end of the current bar
			if event.type=="SET_TEMPO" and event.time>=barStartTime:
				tempo = midi_event_to_qpm_tempo(event)
				event.type = "USED_TEMPO"

		if tempo==None:
			if currentTempo==None:
				tempo = 120
			else:
				tempo = currentTempo

		return tempo



	# get initial time sig and tempo or use defaults
	timeList = get_time_events(midiFile)

	# get notes from the midi file (absolute start times from start of file)
	notesList = get_notes_from_event_list(get_note_events(midiFile))
	

	# get initial tempo and time signature from time list
	timesig = get_initial_time_signature(timeList)
	tempo = get_initial_tempo(timeList)




	# ticks per quarter note:
	ticksPerQuarter = midiFile.ticksPerQuarterNote
	#calculate the initial length of a bar in ticks
	barlength = calculate_bar_ticks(timesig.get_numerator(), timesig.get_denominator(), ticksPerQuarter)
	# initialise time for start and end of current bar
	barStartTime = 0
	barEndTime = 0# barlength
	

	# initialise bars list
	bars = BarList()
	noteIndex = 0

	note = notesList[0]
	# run through the notes list, chopping it into bars
	while noteIndex<len(notesList):
		#create a local note sequence to build a bar
		currentNotes = NoteSequence()

		[timesig,barlength] = get_time_signature(timeList,barStartTime, barlength, ticksPerQuarter, timesig)
		
		barEndTime = barEndTime + barlength

		tempo = get_tempo(timeList,barStartTime, barEndTime, tempo)
		

		#find all the notes in the current bar
		while(note.startTime<barEndTime):
			#make note start time relative to current bar
			note.startTime = note.startTime - barStartTime
			#add note to current bar note sequence
			currentNotes.append(note)
			noteIndex = noteIndex + 1
			if noteIndex<len(notesList):
				note = notesList[noteIndex]
			else:
				break

		# create a new bar from the current notes and add it to the list of bars
		bars.append(Bar(currentNotes, timesig, ticksPerQuarter, tempo))

		barStartTime = barEndTime

	return bars

		
#get note objects from a list of note midi events
def get_notes_from_event_list(noteEventList):
	noteslist = NoteSequence()

	index = 0
	
	#while not at the end of the list of note events
	while index<len(noteEventList):
		#get next event from list
		event = noteEventList[index]
		index = index + 1
		#if we've found the start of a note, search for the corresponding end event
		if event.type=="NOTE_ON" and event.velocity!=0:
			localindex = index
			
			#find corresponding end event
			while localindex<len(noteEventList):
				endEvent = noteEventList[localindex]
				#if its the same note and it's an end event
				if endEvent.pitch==event.pitch and (endEvent.type=="NOTE_OFF" or (endEvent.type=="NOTE_ON" and endEvent.velocity==0)):
					#make a note
					note = Note(event.time,endEvent.time-event.time,event.velocity)
					#alter the type of this end event so it can't be linked to another note on
					endEvent.type = "DUMMY"
					
					#if this note starts at the same time as the previous one
					# replace the previous one if this has longer duration
					if len(noteslist)>0 and note.startTime==noteslist[-1].startTime:
						if note.duration>noteslist[-1].duration:
							noteslist[-1]=note
					# otherwise add the note to the list
					else:
						noteslist.append(note)
					#found the end of the note so break out of the local loop
					break
				localindex = localindex+1

	return noteslist










def get_note_events(midiFile, trackNumber = None):
	"""
	Gets all note on and note off events from a midifile.

	If trackNumber is not specified, the function will check the file format
	and pick either track 0 for a type 0 (single track format) or track 1 
	for a type 1 or 2 (multi-track) midi file.

	"""

	if trackNumber==None:
		if midiFile.format==0:
			trackNumber=0
		else:
			trackNumber=1

	return get_events_of_type(midiFile, trackNumber, lambda e: (e.type == 'NOTE_ON') | (e.type == "NOTE_OFF") )
	


def get_time_events(midiFile):
	"""
	Gets time signature and tempo events from a MIDI file (MIDI format 0 
	or format 1) and returns a list of those events and their associated 
	absolute start times.  If no time signature or tempo are specified then
	defaults of 4/4 and 120QPM are assumed.

	From the MIDI file specification:

	"All MIDI Files should specify tempo and time signature. If they don't, 
	the time signature is assumed to be 4/4, and the tempo 120 beats per 
	minute. In format 0, these meta-events should occur at least at the 
	beginning of the single multi-channel track. In format 1, these meta-events
	should be contained in the first track. In format 2, each of the temporally
	independent patterns should contain at least initial time signature and 
	tempo information."

	"""
	return get_events_of_type(midiFile, 0, lambda e: (e.type == 'SET_TEMPO') | (e.type == "TIME_SIGNATURE") )
	

def get_events_of_type(midiFile, trackIndex, lambdaEventType):
	"""
	Filters the events in a midi track that are selected by the 
	function object lambdaEventType e.g. lambda e: (e.type == 'NOTE_ON')
	Return a list containing the relevant events with appropriate 
	delta times between them 
	"""
	
	track = midiFile.tracks[trackIndex] 
	eventIndex = 0
	#	numTimeEvents = 0

	localEventList  = []
	localEventFound = True
	#accumulatedTime = 0

	while localEventFound==True:
		#find the next time event from the track:
		(localEventIndex, localEventDelta, localEventFound) = find_event(track, eventIndex, lambdaEventType)

		if localEventFound==True:
			#get the time event object out of the track
			localEvent = track.events[localEventIndex]

			#update the start event to search from
			eventIndex = localEventIndex + 1

			#calculate the absolute start time of the time event
			#accumulatedTime = accumulatedTime + localEventDelta

			localEventList.append(localEvent)

	return localEventList


def midi_event_to_time_signature(midiTimeSignatureEvent):
	"""
	Extract the numerator and denominator from a midi time signature
	event and return a TimeSignature music object.  Ignore clocks per
	quarternote and  32nds per quarternote elements since these are
	only for sequencer metronome settings which we won't use here.
	"""
	if midiTimeSignatureEvent.type!="TIME_SIGNATURE":
		print("Error in midi_event_to_time_signature(),  event must be a midi time signature type")
		return None
	else:
		num = ord(midiTimeSignatureEvent.data[0])
		denom = 2**ord(midiTimeSignatureEvent.data[1])
		return TimeSignature("%d/%d" % (num, denom))
	

def midi_event_to_qpm_tempo(midiTempoEvent):
	"""
	Extract the tempo in QPM from a midi SET_TEMPO event
	"""
	if midiTempoEvent.type!="SET_TEMPO":
		print("Error in midi_event_to_qpm_tempo(),  event must be a midi tempo event")
		return None
	else:
		# tempo is stored as microseconds per quarter note
		# in three bytes which we can extract as three ints:
		values = list(map(ord, midiTempoEvent.data))
		# first byte multiplied by 2^16, second 2^8 and third is normal units
		# giving microseconds per quarter
		microsecondsPerQuarter = values[0]*2**16 + values[1]*2**8 + values[2]

		# to calculate QPM, 1 minute = 60million microseconds
		# so divide 60million by micros per quarter:
		return 60000000/microsecondsPerQuarter

def find_event(track, eventStartIndex, lambdaExpr):
	'''
	From code by Csaba Sulyok:
	Finds MIDI event based on lambda expression, starting from a given index.
	Returns a tuple of the following 3 elements:
	1. event index where the lambda expression is true
	2. aggregate delta time from event start index until the found event
	3. flag whether or not any value was found, or we've reached the end of the event queue
	'''

	eventIndex = eventStartIndex
	deltaTime = 0
	while eventIndex < len(track.events) and not lambdaExpr(track.events[eventIndex]):
	    if track.events[eventIndex].type == 'DeltaTime':
	        deltaTime += track.events[eventIndex].time
	    eventIndex += 1

	success = eventIndex < len(track.events)
	return (eventIndex, deltaTime, success)


