'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London
'''

from .basic_functions import repeat, subdivide, ceiling, velocity_sequence_to_min_timespan, get_rhythm_category

def get_cost(sequence,nextSequence):
	sequence = velocity_sequence_to_min_timespan(sequence)					# converting to the minimum time-span format
	
	if sequence[1:] == repeat([0],len(sequence)-1):		# null prototype
		cost = 0
	elif sequence == repeat([1],len(sequence)):			# filled prototype
		cost = 1
	elif sequence[0] == 1 and sequence[-1] == 0:			# run1 prototype
		cost = 2
	elif sequence[0] == 1 and (nextSequence == None or nextSequence[0] == 0):	# run2 prototype
		cost = 2
	elif sequence[-1] == 1 and nextSequence != None and nextSequence[0] == 1:		# upbeat prototype
		cost = 3
	elif sequence[0] == 0:							# syncopated prototype
		cost = 5

	return cost

# This function calculates the syncopation value (cost) for the sequence with the postbar_seq for a certain level. 
def syncopation_perlevel(subSequences):
	#print 'subSequences', subSequences
	total = 0
	for l in range(len(subSequences)-1):
		#print 'cost', get_cost(subSequences[l], subSequences[l+1])
		total = total + get_cost(subSequences[l], subSequences[l+1])
	#print 'total this level', total
	normalised = float(total)/(len(subSequences)-1)
	
	return normalised

def get_syncopation(bar, parameters = None):
	syncopation = None

	binarySequence = velocity_sequence_to_min_timespan(bar.get_binary_sequence())
	subdivisionSequence = bar.get_subdivision_sequence()

	# PRS does not handle polyrhythms
	if get_rhythm_category(binarySequence, subdivisionSequence) == 'poly':
		print('Warning: PRS model detects polyrhythms so returning None.')
	elif bar.is_empty():
		print('Warning: PRS model detects empty bar so returning None.')
	else:
		syncopation = 0

		# retrieve the binary sequence in the next bar
		if bar.get_next_bar() != None:
			nextbarBinarySequence = bar.get_next_bar().get_binary_sequence()
		else:
			nextbarBinarySequence = None

		# numberOfSubSeqs is the number of sub-sequences at a certain metrical level, initialised to be 1 (at the bar level)
		numberOfSubSeqs = 1	
		for subdivisor in subdivisionSequence:
			# numberOfSubSeqs is product of all the subdivisors up to the current level
			numberOfSubSeqs = numberOfSubSeqs * subdivisor
			
			# recursion stops when the length of sub-sequence is less than 2
			if len(binarySequence)/numberOfSubSeqs >= 2:		
				# generate sub-sequences and append the next bar sequence
				subSequences = subdivide(ceiling(binarySequence), numberOfSubSeqs)	
				subSequences.append(nextbarBinarySequence)
				# adding syncopation at each metrical level to the total syncopation
				#print 'per level', syncopation_perlevel(subSequences)
				syncopation += syncopation_perlevel(subSequences)	
			else:
				break

	return syncopation
