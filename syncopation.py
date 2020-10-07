'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London

'''
from rhythm_parser import *
from music_objects import *


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
                        import readmidi
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
                        #print('processing bar %d' % (barlist.index(bar)+1))

                        barSyncopation = sync_perbar_permodel(model, bar, parameters)


                        # if not bar.is_empty():
                        #       barSyncopation = sync_perbar_permodel(model, bar, parameters)
                        # else:
                        #       barSyncopation = None
                        #       print 'Bar %d cannot be measured because it is empty, returning None.' % barlist.index(bar)

                        barResults.append(barSyncopation)
                        if barSyncopation != None:
                                total += barSyncopation
                                numberOfNotes += sum(bar.get_binary_sequence())
                                includedlist.append(barlist.index(bar))
                        else:
                                barsDiscarded += 1
                                discardedlist.append(barlist.index(bar))
                                print('Model could not measure bar %d, returning None.' % (barlist.index(bar)+1))

                import WNBD
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


def calculate_syncopation_inline(model, bits_bars, ts, tpq=None):
    ''' Calculate syncopation of bits without a rhythm file or Barlist/Bar representation

    Constructs a temporary file with minimal meta-information, for running a syncopation
    model over bars defined as lists of bits.

    Keyword arguments:
        model -- syncopation model, e.g. LHL or KTH
        bits_bars -- rhythm as bitstring, as list of bars, e.g. [[1, 0, 1, 0], [1, 0, 1, 0]]
        ts -- time signature (string), e.g. '2/4' or '3/2'
        tpq -- ticks per quarter note, optional (default: none specified)

    Example:
        > import LHL
        > calculate_syncopation_inline(LHL, [[1, 0, 1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1, 0, 1]],
        ...                            '2/4', tpq=2)
        > {'model_name': 'LHL', 'summed_syncopation': 5.0, 'mean_syncopation_per_bar': 2.5,
        ...     'source': '/var/folders/vc/tjp2tnh51rb7vg7zgt2wp9mm0000gn/T/tmpdy_7ocwn.rhy',
        ...     'number_of_bars': 2, 'number_of_bars_not_measured': 0, 'bars_with_valid_output':
        ...     [0, 1], 'bars_without_valid_output': [], 'syncopation_by_bar': [-1, 6],
        ...     'input': [0, 1, 0, 1, 0, 1, 0, 1]}
    '''
    import tempfile

    res = None
    with tempfile.NamedTemporaryFile(suffix='.rhy') as tmp:
        _write_bytes = lambda string: tmp.write(string.encode('utf-8'))
        # Populate the temporary rhythm file
        _write_bytes('T{' + ts + '}\n')
        if tpq:
            _write_bytes('TPQ{' + str(tpq) + '}\n')
        for bits in bits_bars:
            bits = list(bits) # Ensures correct brackets below in temp rhythm file...
            _write_bytes('v' + str(bits).replace('[', '{').replace(']', '}') + '\n')
        # Run model as per normal
        tmp.seek(0)
        res = calculate_syncopation(model, tmp.name)
        res['input'] = bits
    return res
