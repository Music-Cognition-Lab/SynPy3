'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London
'''

# Set the parameters: time-signature, subdivision-sequence, strong-beat-level; Lmax; weight-sequence
# Important condition: Lmax needs to be no less than the length of subdivision-sequence and the length of weight-sequence

def getScriptPath():
	import os
	return os.path.dirname(os.path.realpath(__file__))

# {'key': time-signature} :  
# {'value': [subdivision-sequence, theoretical beat-level represented by index in the subdivision-sequence list]}
timeSignatureBase = {
	'2/2': [[1,2,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'3/2': [[1,3,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'4/2': [[1,2,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'2/4': [[1,2,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'3/4': [[1,3,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'4/4': [[1,2,2,2,2,2,2,2,2,2,2,2,2,2],2],
	'5/4': [[1,5,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'7/4': [[1,7,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'3/8': [[1,3,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'5/8': [[1,5,2,2,2,2,2,2,2,2,2,2,2,2],1],
	'6/8': [[1,2,3,2,2,2,2,2,2,2,2,2,2,2],1],
	'9/8': [[1,3,3,2,2,2,2,2,2,2,2,2,2,2],1],
	'12/8':[[1,2,2,3,2,2,2,2,2,2,2,2,2,2],2],	
}


def add_time_signature(timeSignature, subdivisionSequence, beatLevel):
	if is_time_signature_valid(timeSignature,subdivisionSequence,beatLevel):
		if timeSignature in timesigBase:
			print('This time-signature is existed already.')
		else:
			timeSignatureBase[timeSignature] = [subdivisionSequence, beatLevel]
			write_time_signature()

def update_time_signature(timeSignature, subdivisionSequence, beatLevel):
	if is_time_signature_valid(timeSignature,subdivisionSequence,beatLevel):
		if timeSignature in timeSignatureBase:
			print(('Original settings for ', timeSignature, ':',timeSignatureBase[timeSignature] ))
			timeSignatureBase[timeSignature] = [subdivisionSequence, beatLevel]
			print(('Changed into:',timeSignatureBase[timeSignature]))
			write_time_signature()

def is_time_signature_valid(timeSignature, subdivisionSequence, beatLevel):
	isValid = False
	if ('/' not in timeSignature) or (not timeSignature.split('/')[0].isdigit()) or (not timeSignature.split('/')[1].isdigit()):
		print('Error: invalid time-signature. Please indicate in the form of fraction, e.g. 4/4, 6/8 or 3/4.')
	elif subdivisionSequence != [s for s in subdivisionSequence if isinstance(s,int)]:
		print('Error: invalid subdivision sequence. Please indicate in the form of list of numbers, e.g [1,2,2,2,2].')
	elif beatLevel >= len(subdivisionSequence):
		print('Error: beat-level exceeds the range of subdivision sequence list.')
	else:
		isValid = True
	return isValid

def write_time_signature():
	import pickle as pickle
	timeSigFile = open(getScriptPath()+'/TimeSignature.pkl', 'wb')
	pickle.dump(timeSignatureBase, timeSigFile)
	timeSigFile.close()

def read_time_signature():
	import pickle as pickle
	timeSigFile = open(getScriptPath()+'/TimeSignature.pkl','rb')
	data = pickle.load(timeSigFile)
	return data
	timeSigFile.close()

def print_time_signature_base():
	data = read_time_signature()
	for timeSignature, settings in list(data.items()):
		print((timeSignature, settings))


def are_parameters_valid(Lmax, weightSequence, subdivisionSequence):

	# is_Lmax_valid() checks:
	# 1. if Lmax is a non-negative integer
	# 2. if Lmax is higher than the length of weightSequence and subdivisionSequence 
	def is_Lmax_valid():
		isValid = False
		if isinstance(Lmax,int) and Lmax > 0:
			if Lmax <= len(subdivisionSequence)-1:
				if Lmax <= len(weightSequence)-1:
					isValid = True
				else:
					print('Error: Lmax exceeds the length of weight-sequence. Either reduce Lmax, or provide a new weight-sequence whose length is greater or equal to Lmax.')
			else:
				print('Error: Lmax exceeds the length of subdivision-sequence. Either reduce Lmax, or extend subdivision-sequence through updating time-signature (refer to update_time_signature function).')
		else:	
			print('Error: Lmax needs to be a positive integer.')
		return isValid

	# is_weight_sequence_valid() checks:
	# 1. weightSequence is a list of numbers
	# 2. the length of weightSequence is no less than Lmax
	def is_weight_sequence_valid():
		isValid = False
		if isinstance(weightSequence,list) and weightSequence == [i for i in weightSequence if isinstance(i,int)]:
			if len(weightSequence) >= Lmax:
				isValid = True
			else:
				print('Error: the length of weight-sequence needs to be greater or equal to Lmax.')
		else:
			print('Error: the weight-sequence needs to be a list of integers.')
		return isValid


	if is_weight_sequence_valid() and is_Lmax_valid():
		return True
	else:
		return False
