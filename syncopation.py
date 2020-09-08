'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''
from .rhythm_parser import *
from .music_objects import *


def sync_perbar_permodel (model, bar, parameters=None):
	return model.get_syncopation(bar, parameters)

def calculate_syncopation(model, source, parameters=None, outfile=None, barRange=None):
 	total = 0.0
 	barResults = []
 	numberOfNotes = 0

	barlist = None

 	if isinstance(source, BarList):
 		barlist = source
 		sourceType = "bar list"
 	elif isinstance(source, Bar):
 		barlist = BarList()
 		barlist.append(source)
 		print(barlist)
 		sourceType = "single bar"
	elif isinstance(source, str):
		#treat source as a filename
		sourceType = source
		if source[-4:]==".mid":
			from . import readmidi
			midiFile = readmidi.read_midi_file(source)
			barlist = readmidi.get_bars_from_midi(midiFile)

		elif source[-4:]==".rhy":
			#import rhythm_parser 
			barlist = read_rhythm(source)
		else:
			print("Error in syncopation_barlist_permodel(): Unrecognised file type.")
	else:
		print("Error in syncopation_barlist_permodel(): unrecognised source type.")
	
	barsDiscarded=0
	discardedlist = []
	includedlist = []


	if barlist!=None:

	 	if barRange==None:
	 		barstart=0
 			barend=len(barlist)
 		else:
 			barstart = barRange[0]
 			barend = barRange[1]


		for bar in barlist[barstart:barend]:
			print('processing bar %d' % (barlist.index(bar)+1))

			barSyncopation = sync_perbar_permodel(model, bar, parameters)
			

			# if not bar.is_empty():
			# 	barSyncopation = sync_perbar_permodel(model, bar, parameters)
			# else:
			# 	barSyncopation = None
			# 	print 'Bar %d cannot be measured because it is empty, returning None.' % barlist.index(bar)
			
			barResults.append(barSyncopation)
			if barSyncopation != None:
				total += barSyncopation
				numberOfNotes += sum(bar.get_binary_sequence())
				includedlist.append(barlist.index(bar))
			else:
				barsDiscarded += 1
				discardedlist.append(barlist.index(bar))
				print('Model could not measure bar %d, returning None.' % (barlist.index(bar)+1))

		from . import WNBD
		if model is WNBD:
			total =  total / numberOfNotes
		
		if len(barResults)>barsDiscarded:
			average = total / (len(barResults)-barsDiscarded)
		else:
			average = total

	output = {
 			"model_name":model.__name__ , 
 			"summed_syncopation":total, 
 			"mean_syncopation_per_bar":average, 
 			"source":sourceType, 
 			"number_of_bars":len(barResults), 
 			"number_of_bars_not_measured":barsDiscarded, 
 			"bars_with_valid_output":includedlist, 
 			"bars_without_valid_output":discardedlist, 
 			"syncopation_by_bar":barResults
 			}

 	if outfile!=None:
 		
 		if ".xml" in outfile:
 			results_to_xml(output,outfile)
 		elif ".json" in outfile:
 			results_to_json(output,outfile)
 		else:
 			print("Error in syncopation.py: Unrecognised output file type: ", outfile)

 	return output



def results_to_xml(results, outputFilename):
	from xml.etree.ElementTree import Element, ElementTree

	elem = Element("syncopation_results")

	for key, val in list(results.items()):
		child = Element(key)
		child.text = str(val)
		elem.append(child)

	ElementTree(elem).write(outputFilename)

def results_to_json(results, outputFilename):
	import json

	fileHandle = open(outputFilename, 'w')
	json.dump(results, fileHandle, sort_keys=True, indent=4, separators=(',', ': '))
	fileHandle.flush()

