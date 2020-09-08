'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''
from .basic_functions import repeat, get_note_indices

# To find the product of multiple numbers
def cumu_multiply(numbers):
	product = 1
	for n in numbers:
		product = product*n
	return product

def get_syncopation(bar, parameters = None):
	syncopation = None
	
	noteSequence = bar.get_note_sequence()
	barTicks = bar.get_bar_ticks()
	subdivisionSequence = bar.get_subdivision_sequence()
	strongBeatLevel = bar.get_beat_level()
	
	nextbarNoteSequence = None
	if bar.get_next_bar() != None:
		nextbarNoteSequence = bar.get_next_bar().get_note_sequence()

	# calculate each strong beat ticks
	numberOfBeats = cumu_multiply(subdivisionSequence[:strongBeatLevel+1])
	beatIntervalTicks = barTicks/numberOfBeats
	# beatsTicks represents the ticks for all the beats in the current bar and the first two beats in the next bar
	beatsTicks = [i*beatIntervalTicks for i in range(numberOfBeats+2)] 
	#print beatsTicks
	totalSyncopation = 0
	for note in noteSequence:
	#	print note.to_string()
		# find such beatIndex such that note.startTime is located between (including) beatsTicks[beatIndex] and (not including) beatsTicks[beatIndex+1]
		beatIndex = 0
		while note.startTime < beatsTicks[beatIndex] or note.startTime >= beatsTicks[beatIndex+1]:
			beatIndex += 1

	#	print beatIndex
		# calculate the distance of this note to its nearest beat
		distanceToBeatOnLeft = abs(note.startTime - beatsTicks[beatIndex])/float(beatIntervalTicks)
		distanceToBeatOnRight = abs(note.startTime - beatsTicks[beatIndex+1])/float(beatIntervalTicks)
		distanceToNearestBeat = min(distanceToBeatOnLeft,distanceToBeatOnRight)
	#	print distanceToNearestBeat

		# calculate the WNBD measure for this note, and add to total syncopation value for this bar
		if distanceToNearestBeat == 0:	
			totalSyncopation += 0
		# or if this note is held on past the following beat, but ends on or before the later beat  
		elif beatsTicks[beatIndex+1] < note.startTime+note.duration <= beatsTicks[beatIndex+2]:
			totalSyncopation += float(2)/distanceToNearestBeat
		else:
			totalSyncopation += float(1)/distanceToNearestBeat
	#	print totalSyncopation

	return totalSyncopation

#def get_syncopation(seq, subdivision_seq, strong_beat_level, postbar_seq):
# def get_syncopation(bar, parameters = None):
# 	syncopation = None
	
# 	binarySequence = bar.get_binary_sequence()
# 	sequenceLength = len(binarySequence)
# 	subdivisionSequence = bar.get_subdivision_sequence()
# 	strongBeatLevel = bar.get_beat_level()
# 	nextbarBinarySequence = None

# 	if bar.get_next_bar() != None:
# 		nextbarBinarySequence = bar.get_next_bar().get_binary_sequence()

# 	numberOfBeats = cumu_multiply(subdivisionSequence[0:strongBeatLevel+1])	# numberOfBeats is the number of strong beats
	
# 	if sequenceLength % numberOfBeats != 0:
# 		print 'Error: the length of sequence is not subdivable by the subdivision factor in subdivision sequence.'
# 	else:
# 		# Find the indices of all the strong-beats
# 		beatIndices = []
# 		beatInterval = sequenceLength / numberOfBeats
# 		for i in range(numberOfBeats+1):
# 			beatIndices.append(i*beatInterval)
# 		if nextbarBinarySequence != None:		# if there is a postbar_seq, add another two beats index for later calculation
# 			beatIndices += [sequenceLength+beatInterval, sequenceLength+ 2* beatInterval]

# 		noteIndices = get_note_indices(binarySequence)	# all the notes

# 		# Calculate the WNBD measure for each note
# 		def measure_pernote(noteIndices, nextNoteIndex):
# 			# Find the nearest beats where this note locates - in [beat_indices[j], beat_indices[j+1]) 
# 			j = 0
# 			while noteIndices < beatIndices[j] or noteIndices >= beatIndices[j+1]:
# 				j = j + 1
			
# 			# The distance of note to nearest beat normalised by the beat interval
# 			distanceToNearestBeat = min(abs(noteIndices - beatIndices[j]), abs(noteIndices - beatIndices[j+1]))/float(beatInterval)

# 			# if this note is on-beat
# 			if distanceToNearestBeat == 0:	
# 				measure = 0
# 			# or if this note is held on past the following beat, but ends on or before the later beat  
# 			elif beatIndices[j+1] < nextNoteIndex <= beatIndices[j+2]:
# 				measure = float(2)/distanceToNearestBeat
# 			else:
# 				measure = float(1)/distanceToNearestBeat
# 			return measure

# 		total = 0
# 		for i in range(len(noteIndices)):
# 			# if this is the last note, end_time is the index of the following note in the next bar
# 			if i == len(noteIndices)-1:
# 				# if the next bar is not none or a bar of full rest, 
# 				# the nextNoteIndex is the sum of sequence length in the current bar and the noteIndex in the next bar
# 				if nextbarBinarySequence != None and nextbarBinarySequence != repeat([0],len(nextbarBinarySequence)):
# 					nextNoteIndex = get_note_indices(nextbarBinarySequence)[0]+sequenceLength
# 				# else when the next bar is none or full rest, end_time is the end of this sequence.
# 				else:
# 					nextNoteIndex = sequenceLength
# 			# else this is not the last note, the nextNoteIndex is the following element in the noteIndices list
# 			else:
# 				nextNoteIndex = noteIndices[i+1]
# 			# sum up the syncopation value for individual note at noteIndices[i]
# 			total += measure_pernote(noteIndices[i],nextNoteIndex)

# 		#syncopation = float(total) / len(note_indices)

# 	# return the total value, leave the normalisation done in the end
# 	return total
