'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''

from .basic_functions import get_H, velocity_sequence_to_min_timespan, get_rhythm_category, upsample_velocity_sequence,  find_rhythm_Lmax
from .parameter_setter import are_parameters_valid

def get_syncopation(bar, parameters = None):
	syncopation = None
	velocitySequence = bar.get_velocity_sequence()
	subdivisionSequence = bar.get_subdivision_sequence()

	if get_rhythm_category(velocitySequence, subdivisionSequence) == 'poly':
		print('Warning: SG model detects polyrhythms so returning None.')
	elif bar.is_empty():
		print('Warning: SG model detects empty bar so returning None.')
	else:
		velocitySequence = velocity_sequence_to_min_timespan(velocitySequence)	# converting to the minimum time-span format

		# set the defaults
		Lmax  = 10
		weightSequence = list(range(Lmax+1)) # i.e. [0,1,2,3,4,5]
		if parameters!= None:
			if 'Lmax' in parameters:
				Lmax = parameters['Lmax']				
			if 'W' in parameters:
				weightSequence = parameters['W']

		if not are_parameters_valid(Lmax, weightSequence, subdivisionSequence):
			print('Error: the given parameters are not valid.')
		else:
			Lmax = find_rhythm_Lmax(velocitySequence, Lmax, weightSequence, subdivisionSequence) 
			if Lmax != None:
				# generate the metrical weights of level Lmax, and upsample(stretch) the velocity sequence to match the length of H
				H = get_H(weightSequence,subdivisionSequence, Lmax)
				#print len(velocitySequence)
				#velocitySequence = upsample_velocity_sequence(velocitySequence, len(H))
				#print len(velocitySequence)
				
				# The ave_dif_neighbours function calculates the (weighted) average of the difference between the note at a certain index and its neighbours in a certain metrical level
				def ave_dif_neighbours(index, level):

					averages = []
					parameterGarma = 0.8
					
					# The findPre function is to calculate the index of the previous neighbour at a certain metrical level.
					def find_pre(index, level):
						preIndex = (index - 1)%len(H)	# using % is to restrict the index varies within range(0, len(H))
						while(H[preIndex] > level):
							preIndex = (preIndex - 1)%len(H)
						#print 'preIndex', preIndex
						return preIndex

					# The findPost function is to calculate the index of the next neighbour at a certain metrical level.
					def find_post(index, level):
						postIndex = (index + 1)%len(H)
						while(H[postIndex] > level):
							postIndex = (postIndex + 1)%len(H)
						#print 'postIndex', postIndex
						return postIndex
					
					# The dif function is to calculate a difference level factor between two notes (at note position index1 and index 2) in velocity sequence
					def dif(index1,index2):
						parameterBeta = 0.5
						dif_v = velocitySequence[index1]-velocitySequence[index2]
						dif_h = abs(H[index1]-H[index2])
						diffactor = (parameterBeta*dif_h/4+1-parameterBeta)
						if diffactor>1:
							return dif_v
						else:
							return dif_v*diffactor


					# From the highest to the lowest metrical levels where the current note resides, calculate the difference between the note and its neighbours at that level
					for l in range(level, max(H)+1):
						ave = (parameterGarma*dif(index,find_pre(index,l))+dif(index,find_post(index,l)) )/(1+parameterGarma)
						averages.append(ave)
					return averages

				# if the upsampling was successfully done
				if velocitySequence != None:
					syncopation = 0			
					# Calculate the syncopation value for each note
					for index in range(len(velocitySequence)):
						if velocitySequence[index] != 0: # Onset detected
							h = H[index] 
							# Syncopation potential according to its metrical level, which is equal to the metrical weight
							potential = 1 - pow(0.5,h)
							level = h 		# Metrical weight is equal to its metrical level
							syncopation += min(ave_dif_neighbours(index, level))*potential
				else:
					print('Try giving a bigger Lmax so that the rhythm sequence can be measured by the matching metrical weights sequence (H).')
	return syncopation
