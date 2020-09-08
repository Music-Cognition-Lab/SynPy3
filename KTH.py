'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''

from .basic_functions import get_note_indices, repeat, velocity_sequence_to_min_timespan

# To find the nearest power of 2 equal to or less than the given number
def round_down_power_2(number):
	i = 0
	if number > 0:
		while pow(2,i) > number or number >= pow(2,i+1):
			i = i+1
		power2 = pow(2,i)
	else:
		print('Error: numbers that are less than 1 cannot be rounded down to its nearest power of two.')
		power2 = None
	return power2

# To find the nearest power of 2 equal to or more than the given number
def round_up_power_2(number):
	i = 0
	while pow(2,i) < number:
		i = i + 1
	return pow(2,i)

# To examine whether start_time is 'off-beat'
def start_time_offbeat_measure(startTime, c_n):
	measure = 0
	if startTime % c_n != 0:
		measure = 2
	return measure

# To examine whether end_time is 'off-beat'
def end_time_offbeat_measure(endTime, c_n):
	measure = 0
	if endTime % c_n != 0:
		measure = 1
	return measure

def get_syncopation(bar, parameters = None):
	syncopation = None

	# KTH only deals with simple-duple meter where the number of beats per bar is a power of two.
	numerator = bar.get_time_signature().get_numerator()
	if numerator != round_down_power_2(numerator):
		print('Warning: KTH model detects non simple-duple meter so returning None.')
	else:
		# retrieve note-sequence and next bar's note-sequence
		noteSequence = bar.get_note_sequence()
		#for note in noteSequence:
		#	print note.to_string()
		#print 'barlength',bar.get_bar_ticks()

		nextbarNoteSequence = None
		if bar.get_next_bar() != None:
			nextbarNoteSequence = bar.get_next_bar().get_note_sequence()

		# convert note sequence to its minimum time-span representation so that the later calculation can be faster
		# noteSequence = note_sequence_to_min_timespan(noteSequence)
		# find delta_t 
		Tmin = len(velocity_sequence_to_min_timespan(bar.get_velocity_sequence()))
		#print 'Tmin',Tmin
		T = round_up_power_2(Tmin)
		#print 'T',T
		deltaT = float(bar.get_bar_ticks())/T
		#print 'delta',deltaT


		# calculate syncopation note by note
		syncopation = 0

		for note in noteSequence:
			c_n = round_down_power_2(note.duration/deltaT)
			#print 'd', note.duration
			#print 'c_n', c_n
			endTime = note.startTime + note.duration
			#print float(note.startTime)/deltaT, float(endTime)/deltaT
			syncopation = syncopation + start_time_offbeat_measure(float(note.startTime)/deltaT,c_n) + end_time_offbeat_measure(float(endTime)/deltaT,c_n)


	return syncopation

# # To calculate syncopation value of the sequence in the given time-signature.
# def get_syncopation(seq, timesig, postbar_seq):
# 	syncopation = 0

# 	numerator = int(timesig.split("/")[0])
# 	if numerator == round_down_power_2(numerator):	# if is a binary time-signature
# 		# converting to minimum time-span format
# 		seq = get_min_timeSpan(seq)	
# 		if postbar_seq != None:
# 			postbar_seq = get_min_timeSpan(postbar_seq)

# 		# sf is a stretching factor matching rhythm sequence and meter, as Keith defines the note duration as a multiple of 1/(2^d) beats where d is number of metrical level
# 		sf = round_up_power_2(len(seq))
		
# 		# retrieve all the indices of all the notes in this sequence
# 		note_indices = get_note_indices(seq)

# 		for i in range(len(note_indices)):
# 			# Assuming start_time is the index of this note, end_time is the index of the following note
# 			start_time = note_indices[i]*sf/float(len(seq))

# 			if i == len(note_indices)-1:	# if this is the last note, end_time is the index of the following note in the next bar
# 				if postbar_seq != None and postbar_seq != repeat([0],len(postbar_seq)):
# 					next_index = get_note_indices(postbar_seq)[0]+len(seq)
# 					end_time = next_index*sf/float(len(seq))
# 				else:	# or if the next bar is none or full rest, end_time is the end of this sequence.
# 					end_time = sf
# 			else:
# 				end_time = note_indices[i+1]*sf/float(len(seq))

# 			duration = end_time - start_time
# 			c_n = round_down_power_2(duration)
# 			syncopation = syncopation + start(start_time,c_n) + end(end_time,c_n)
# 	else: 
# 		print 'Error: KTH model can only deal with binary time-signature, e.g. 2/4 and 4/4. '
# 		syncopation = None

# 	return syncopation
