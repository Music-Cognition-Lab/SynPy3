'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''

from .basic_functions import get_H, ceiling, velocity_sequence_to_min_timespan, get_rhythm_category,  find_rhythm_Lmax
from .parameter_setter import are_parameters_valid

# The get_metricity function calculates the metricity for a binary sequence with given sequence of metrical weights in a certain metrical level.
def get_metricity(binarySequence, H):
	metricity = 0
	for m in range(len(binarySequence)):
		metricity = metricity + binarySequence[m]*H[m]
	return metricity

# The get_max_metricity function calculates the maximum metricity for the same number of notes in a binary sequence.
def get_max_metricity(binarySequence, H):
	maxMetricity = 0
	H.sort(reverse=True) # Sort the metrical weight sequence from large to small
	for i in range(sum(binarySequence)):
		maxMetricity = maxMetricity+H[i]
	return maxMetricity



# The get_syncopation function calculates the syncopation value of the given sequence for TMC model. 
#def get_syncopation(seq, subdivision_seq, weight_seq, L_max, rhythm_category):
def get_syncopation(bar, parameters = None):
	syncopation = None
	binarySequence = bar.get_binary_sequence()
	subdivisionSequence = bar.get_subdivision_sequence()

	if get_rhythm_category(binarySequence, subdivisionSequence) == 'poly':
		print('Warning: TMC model detects polyrhythms so returning None.')
	else:
		
		# set the defaults
		Lmax  = 5
		weightSequence = list(range(Lmax+1,0,-1)) # i.e. [6,5,4,3,2,1]
		
		if parameters!= None:
			if 'Lmax' in parameters:
				Lmax = parameters['Lmax']				
			if 'W' in parameters:
				weightSequence = parameters['W']

		if not are_parameters_valid(Lmax, weightSequence, subdivisionSequence):
			print('Error: the given parameters are not valid.')
		else:
			binarySequence = velocity_sequence_to_min_timespan(binarySequence)	# converting to the minimum time-span format
			L = find_rhythm_Lmax(binarySequence, Lmax, weightSequence, subdivisionSequence) 
			if L != None:
				#? generate the metrical weights of the lowest level, 
				#? using the last matching_level number of elements in the weightSequence, to make sure the last element is 1
				H = get_H (weightSequence[-(L+1):], subdivisionSequence, L)
				metricity = get_metricity(binarySequence, H)	# converting to binary sequence then calculate metricity
				maxMetricity = get_max_metricity(binarySequence, H)

				syncopation = maxMetricity - metricity
				
	return syncopation

