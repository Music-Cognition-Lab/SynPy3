'''
Author: Chunyang Song
Institution: Centre for Digital Music, Queen Mary University of London
'''

from basic_functions import concatenate, repeat, subdivide, ceiling, get_rhythm_category
from parameter_setter import are_parameters_valid


# Each terminal node contains two properties: its node type (note or rest) and its metrical weight.
class Node:
    def __init__(self,nodeType,metricalWeight):
        self.nodeType = nodeType
        self.metricalWeight = metricalWeight

# This function will recurse the tree for a binary sequence and return a sequence containing the terminal nodes in time order.
def recursive_tree(binarySequence, subdivisionSequence, weightSequence, metricalWeight, level, Lmax):
    # If matching to a Note type, add to terminal nodes
    output = []
    if binarySequence == concatenate([1],repeat([0],len(binarySequence)-1)):
        output.append(Node('N',metricalWeight))

    # If matching to a Rest type, add to terminal nodes
    elif binarySequence == repeat([0],len(binarySequence)):                                 
        output.append(Node('R',metricalWeight))

    elif level+1 == Lmax:
        print("""WARNING: LHL tree recursion descended to Lmax, returning a note node but result will
                not be fully accurate.  Check the rhythm pattern under test and/or specify larger Lmax
                to rectify the problem.""")
        output.append(Node('N',metricalWeight))

    # Keep subdividing by the subdivisor of the next level
    else:   
        subBinarySequences = subdivide(binarySequence, subdivisionSequence[level+1])    
        subWeightSequences = concatenate([metricalWeight],repeat([weightSequence[level+1]],subdivisionSequence[level+1]-1))
        for a in range(len(subBinarySequences)):
            rt = recursive_tree(subBinarySequences[a], subdivisionSequence, weightSequence, subWeightSequences[a], level+1, Lmax)
            output = output + rt
        
    return output

def get_syncopation(bar, parameters = None):
    syncopation = None
    naughtyglobal = 0

    binarySequence = bar.get_binary_sequence()
    subdivisionSequence = bar.get_subdivision_sequence()

    # LHL can only measure monorhythms
    if get_rhythm_category(binarySequence, subdivisionSequence) == 'poly':
        print('Warning: LHL model detects polyrhythms so returning None.')
    elif bar.is_empty():
        print('LHL model detects empty bar so returning -1.')
        syncopation = -1
    else:
        # set defaults
        Lmax = 10
        weightSequence = list(range(0,-Lmax-1,-1))
        # if parameters are specified by users, check their validities and update parameters if valid           
        if parameters!= None:
            if 'Lmax' in parameters:
                Lmax = parameters['Lmax']                               
            if 'W' in parameters:
                weightSequence = parameters['W']

        if not are_parameters_valid(Lmax, weightSequence, subdivisionSequence):
            print('Error: the given parameters are not valid.')
        else:
                # For the rhythm in the current bar, process its tree structure and store the terminal nodes 
                terminalNodes = recursive_tree(ceiling(binarySequence), subdivisionSequence, weightSequence, weightSequence[0],0, Lmax)
                
                # save the terminal nodes on the current bar so that 
                # the next bar can access them...
                bar.LHLterminalNodes = terminalNodes

                # If there is rhythm in the previous bar and we've already processed it 
                prevbar =  bar.get_previous_bar()
                if prevbar != None and prevbar.is_empty() != True:
                        # get its LHL tree if it has one
                        try:
                                prevbarNodes = prevbar.LHLterminalNodes
                        except AttributeError:
                                prevbarNodes = []

                        # find the final note node in the previous bar:
                        if len(prevbarNodes)>0:
                                i = len(prevbarNodes) - 1
                                # Only keep the last note-type node
                                while prevbarNodes[i].nodeType != 'N' and i>=0:
                                        i = i-1
                                # prepend the note to the terminal node list for this bar
                                terminalNodes = [ prevbarNodes[i] ] + terminalNodes
                                        
                
                # Search for the NR pairs that contribute to syncopation, then add the weight-difference to the NRpairSyncopation list
                NRpairSyncopation = []
                for i in range(len(terminalNodes)-1,0,-1):
                        if terminalNodes[i].nodeType == 'R':
                                for j in range(i-1, -1, -1):
                                        if (terminalNodes[j].nodeType == 'N') & (terminalNodes[i].metricalWeight >= terminalNodes[j].metricalWeight):
                                                NRpairSyncopation.append(terminalNodes[i].metricalWeight - terminalNodes[j].metricalWeight)
                                                break

                # If there are syncopation, sum all the local syncopation values stored in NRpairSyncopation list       
                if len(NRpairSyncopation) != 0:
                        syncopation = sum(NRpairSyncopation)
                # If no syncopation, the value is -1;   
                elif len(terminalNodes) != 0:
                        syncopation = -1

        return syncopation

def get_syncopation_bitstring(bin_seq, ts, Lmax=4, subdiv_seq=None):
    ''' Simple bitstring LHL utility, avoiding need for any rhythm files or MIDI

    Keyword arguments:
        bin_seq -- binary sequence (list), e.g. [1, 0, 1, 0]
        ts -- time signature (string), e.g. '2/4' or '3/2'
        Lmax -- recursion depth (int, default 4)
        subdiv_seq -- explicit sequence of subdivisions (list), e.g. [1, 4, 2]

    Example:
        > get_syncopation_bitstring([1, 0, 0, 1, 0, 1, 1, 0], '2/4')
        > 2

    '''
    if not subdiv_seq:
        # TODO: Sanity check whether this is a meaningful default
        from parameter_setter import timeSignatureBase
        subdiv_seq = timeSignatureBase[ts][0]

    syncopation = None
    naughtyglobal = 0

    weight_seq = range(0, -Lmax-1, -1)

    # For the rhythm in the current bar, process its tree structure and store the terminal nodes 
    terminal_nodes = recursive_tree(ceiling(bin_seq), subdiv_seq, weight_seq, weight_seq[0], 0, Lmax)
                            
    # Search for the NR pairs that contribute to syncopation, then add the weight-difference to the NRpairSyncopation list
    NR_pair_sync = []
    for i in range(len(terminal_nodes)-1, 0, -1):
        node_i = terminal_nodes[i]
        if node_i.nodeType == 'R':
            for j in range(i-1, -1, -1):
                node_j = terminal_nodes[j]
                if (node_j.nodeType == 'N') & (node_i.metricalWeight >= node_j.metricalWeight):
                    NR_pair_sync.append(node_i.metricalWeight - node_j.metricalWeight)
                    break

    if NR_pair_sync:
        syncopation = sum(NR_pair_sync)
    elif terminal_nodes:
        syncopation = -1
    else:
        syncopation = None
    return syncopation
