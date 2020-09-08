'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''

from .basic_functions import ceiling, find_divisor, is_prime, velocity_sequence_to_min_timespan

def get_syncopation(bar, parameters = None):
	binarySequence = velocity_sequence_to_min_timespan(bar.get_binary_sequence())
	sequenceLength = len(binarySequence)

	syncopation = 0

	# if the length of b_sequence is 1 or a prime number, syncopation is 0;
	# otherwise the syncopation is calculated by adding up the number of off-beat notes
	if not ( (sequenceLength == 1) or (is_prime(sequenceLength)) ):
		# find all the divisors other than 1 and the length of this sequence
		divisors = find_divisor(sequenceLength)		
		del divisors[0]
		del divisors[-1]

		# the on-beat/off-beat positions are the ones that can/cannot be subdivided by the sequenceLength;
		# the on-beat positions are set to be 0, off-beat positions are set to be 1
		offbeatness = [1]*sequenceLength			
		for index in range(sequenceLength):
			for d in divisors:
				if index % d == 0:
					offbeatness[index] = 0
					break
			#print 'offbeatness', offbeatness
			# syncopation is the sum of the hadamard-product of the rhythm binary-sequence and the off-beatness 
			syncopation += binarySequence[index]*offbeatness[index]
	
	return syncopation
