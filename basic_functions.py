# This python file is a collection of basic functions that are used in the syncopation models. 

import math

# The concatenation function is used to concatenate two sequences.
def concatenate(seq1,seq2):
	return seq1+seq2

# The repetition function is to concatenate a sequence to itself for 'times' number of times.
def repeat(seq,times):
	new_seq = list(seq)
	if times >= 1:
		for i in range(times-1):
			new_seq = concatenate(new_seq,seq)
	else:
		#print 'Error: repetition times needs to be no less than 1.'
		new_seq = []
	return new_seq

# The subdivision function is to equally subdivide a sequence into 'divisor' number of segments.
def subdivide(seq,divisor):
	subSeq = []
	if len(seq) % divisor != 0:
		print('Error: rhythmic sequence cannot be equally subdivided.')
	else:
		n = len(seq) // divisor
		start , end = 0, n
		for i in range(divisor):
			subSeq.append(seq[start : end])
			start = end
			end = end + n	
	return subSeq


# The ceiling function is to round each number inside a sequence up to its nearest integer.
def ceiling(seq):
	seq_ceil = []
	for s in seq:
		seq_ceil.append(int(math.ceil(s)))
	return seq_ceil

# The find_divisor function returns a list of all possible divisors for a length of sequence.
def find_divisor(number):
	divisors = [1]
	for i in range(2,number+1):
		if number%i ==0:
			divisors.append(i)
	return divisors

# The find_divisor function returns a list of all possible divisors for a length of sequence.
def find_prime_factors(number):
	primeFactors = find_divisor(number)
	
	# remove 1 because 1 is not prime number
	del primeFactors[0]

	# reversely traverse all the divisors list and once find a non-prime then delete
	for i in range(len(primeFactors)-1,0,-1):
	#	print primeFactors[i], is_prime(primeFactors[i])
		if not is_prime(primeFactors[i]):
			del primeFactors[i]

	return primeFactors

def is_prime(number):
	isPrime = True
	# 0 or 1 is not prime numbers
	if number < 2:
		isPrime = False
	# 2 is the only even prime number
	elif number == 2:
		pass
	# all the other even numbers are non-prime
	elif number % 2 == 0:
		isPrime = False
	else:
		for odd in range(3, int(math.sqrt(number) + 1), 2):
			if number % odd == 0:
				isPrime = False
	return isPrime

# upsample a velocity sequence to certain length, e.g. [1,1] to [1,0,0,0,1,0,0,0]
def upsample_velocity_sequence(velocitySequence, length):
	upsampledVelocitySequence = None
	if length < len(velocitySequence):
		print('Error: the requested upsampling length needs to be longer than velocity sequence.')
	elif length % len(velocitySequence) != 0:
		print('Error: velocity sequence can only be upsampled to a interger times of its own length.')
	else:
		upsampledVelocitySequence = [0]*length
		scalingFactor = length/len(velocitySequence)
		for index in range(len(velocitySequence)):
			upsampledVelocitySequence[index*scalingFactor] = velocitySequence[index]
	return upsampledVelocitySequence


# convert a velocity sequence to its minimum time-span representation
def velocity_sequence_to_min_timespan(velocitySequence):
	from music_objects import VelocitySequence
	minTimeSpanVelocitySeq = [1]
	for divisors in find_divisor(len(velocitySequence)):
		segments = subdivide(velocitySequence,divisors)
		if len(segments)!=0:
			del minTimeSpanVelocitySeq[:]
			for s in segments:
				minTimeSpanVelocitySeq.append(s[0])
			if sum(minTimeSpanVelocitySeq) == sum(velocitySequence):
				break
	return VelocitySequence(minTimeSpanVelocitySeq)

"""
# convert a note sequence to its minimum time-span representation
def note_sequence_to_min_timespan(noteSequence):
	from music_objects import note_sequence_to_velocity_sequence
	timeSpanTicks = len(note_sequence_to_velocity_sequence(noteSequence))
#	print timeSpanTicks

	barBinaryArray = [0]*(timeSpanTicks+1)
	for note in noteSequence:
		# mark note_on event (i.e. startTime) and note_off event (i.e. endTime = startTime + duration) as 1 in the barBinaryArray
		barBinaryArray[note.startTime] = 1
		barBinaryArray[note.startTime + note.duration] = 1

	# convert the barBinaryArray to its minimum time-span representation
	minBarBinaryArray = velocity_sequence_to_min_timetpan(barBinaryArray[:-1])
	print barBinaryArray
	print minBarBinaryArray
	delta_t = len(barBinaryArray)/len(minBarBinaryArray)

	# scale the startTime and duration of each note by delta_t
	for note in noteSequence:
		note.startTime = note.startTime/delta_t
		note.duration = note.duration/delta_t

	return noteSequence
"""

# get_note_indices returns all the indices of all the notes in this velocity_sequence
def get_note_indices(velocitySequence):
	noteIndices = []

	for index in range(len(velocitySequence)):
		if velocitySequence[index] != 0:
			noteIndices.append(index)

	return noteIndices


# The get_H returns a sequence of metrical weight for a certain metrical level (horizontal),
# given the sequence of metrical weights in a hierarchy (vertical) and a sequence of subdivisions.
def get_H(weightSequence,subdivisionSequence, level):
	H = []
	#print len(weight_seq), len(subdivision_seq), level
	if (level <= len(subdivisionSequence)-1) and (level <= len(weightSequence)-1):
		if level == 0:
			H = repeat([weightSequence[0]],subdivisionSequence[0])
		else:
			H_pre = get_H(weightSequence,subdivisionSequence,level-1)
			for h in H_pre:
				H = concatenate(H, concatenate([h], repeat([weightSequence[level]],subdivisionSequence[level]-1)))
	else:
		print('Error: a subdivision factor or metrical weight is not defined for the request metrical level.')
	return H


def calculate_bar_ticks(numerator, denominator, ticksPerQuarter):
	return (numerator * ticksPerQuarter *4) / denominator


def get_rhythm_category(velocitySequence, subdivisionSequence):
	'''
	The get_rhythm_category function is used to detect rhythm category: monorhythm or polyrhythm.
	For monorhythms, all prime factors of the length of minimum time-span representation of this sequence are
	elements of its subdivision_seq, otherwise it is polyrhythm; 
	e.g. prime_factors of polyrhythm 100100101010 in 4/4 is [2,3] but subdivision_seq = [1,2,2] for 4/4 
	'''
	rhythmCategory = 'mono'
	for f in find_prime_factors(len(velocity_sequence_to_min_timespan(velocitySequence))):
		if not (f in subdivisionSequence): 
			rhythmCategory = 'poly'
			break
	return rhythmCategory


def string_to_sequence(inputString,typeFunction=float):
	return list(map(typeFunction, inputString.split(',')))

# find the metrical level L that contains the same number of metrical positions as the length of the binary sequence
# if the given Lmax is not big enough to analyse the given sequence, request a bigger Lmax
def find_rhythm_Lmax(rhythmSequence, Lmax, weightSequence, subdivisionSequence):
	L = Lmax

	# initially assuming the Lmax is not big enough
	needBiggerLmax = True 
	
	# from the lowest metrical level (Lmax) to the highest, find the matching metrical level that 
	# has the same length as the length of binary sequence  
	while L >= 0:
		if len(get_H(weightSequence,subdivisionSequence, L)) == len(rhythmSequence):
			needBiggerLmax = False
			break
		else:
			L = L - 1

	# if need a bigger Lmax, print error message and return None; otherwise return the matching metrical level L
	if needBiggerLmax:
		print('Error: needs a bigger L_max (i.e. the lowest metrical level) to match the given rhythm sequence.')
		L = None
	
	return L


# # The get_subdivision_seq function returns the subdivision sequence of several common time-signatures defined by GTTM, 
# # or ask for the top three level of subdivision_seq manually set by the user.
# def get_subdivision_seq(timesig, L_max):
# 	subdivision_seq = []

# 	if timesig == '2/4' or timesig == '4/4':
# 		subdivision_seq = [1,2,2]
# 	elif timesig == '3/4' or timesig == '3/8':
# 		subdivision_seq = [1,3,2]
# 	elif timesig == '6/8':
# 		subdivision_seq = [1,2,3]
# 	elif timesig == '9/8':
# 		subdivision_seq = [1,3,3]
# 	elif timesig == '12/8':
# 		subdivision_seq = [1,4,3]
# 	elif timesig == '5/4' or timesig == '5/8':
# 		subdivision_seq = [1,5,2]
# 	elif timesig == '7/4' or timesig == '7/8':
# 		subdivision_seq = [1,7,2]
# 	elif timesig == '11/4' or timesig == '11/8':
# 		subdivision_seq = [1,11,2]
# 	else:
# 		print 'Time-signature',timesig,'is undefined. Please indicate subdivision sequence for this requested time-signature, e.g. [1,2,2] for 4/4 meter.'
# 		for i in range(3):
# 			s = int(input('Enter the subdivision factor at metrical level '+str(i)+':'))
# 			subdivision_seq.append(s)

# 	if L_max > 2:
# 		subdivision_seq = subdivision_seq + [2]*(L_max-2)
# 	else:
# 		subdivision_seq = subdivision_seq[0:L_max+1]
	
# 	return subdivision_seq

