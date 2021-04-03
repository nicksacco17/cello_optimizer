
# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: circuit_netlist_parser.py
# Description:  Builds a genetic circuit from a Netlist JSON file produced from
#               Cello.  Scores the circuit based on an aggregate of computations 
#               using the response functions for each gate in the circuit.
# Status:   Fully operational for basic genetic circuit models where the input 
#           signals are solely described by high and low values, the gates are
#           solely described by sigmoidal response functions, and any input 
#           design that is properly formatted is considered valid, regardless
#           of physical realizability.
# ------------------------------------------------------------------------------

# Imports
import json
import itertools
import record as rec
from response_function import ResponseFunction
import numpy as np
from typing import (Any, Dict, List, Union,)
import yaml

# ------------------------------ HELPER FUNCTIONS ------------------------------

''' 
Function:       f_not
Arg:            x: Input signal to the simulated digital NOT gate
Return:         NOT x
Description:    Logical NOT operation.  Valid inputs are processed, invalid 
                inputs are just passed through.
'''
def f_not(x):
    if x == 0:
        return 1
    elif x == 1:
        return 0
    elif x == -1:
        return -1

''' 
Function:       f_nor
Args:           x: Input signal to the simulated digital NOR gate
                y: Input signal to the simulated digital NOR gate
Return:         x NOR y
Description:    Logical NOR operation.  Valid inputs are processed, invalid 
                inputs are just passed through.
'''
def f_nor(x, y):
    if x == 0 and y == 0:
        return 1
    elif x == 0 and y == 1:
        return 0
    elif x == 1 and y == 0:
        return 0
    elif x == 1 and y == 1:
        return 0
    elif x == -1 or y == -1:
        return -1


'''
Function:       _fix_input_json
Args:           input_fp: File pointer to the target JSON
                final_trailing_comma: Flag to indicate cleanup
Description:    Clean up of netlist JSONs produced during Cello queries.
                This is from cello api, just pulled the code here to make it 
                easier to use, but all credit goes to WR Jackson.
'''
def _fix_input_json(input_fp: str, final_trailing_comma: bool = False,) -> Union[List[Dict], Dict]:
    """
    Fixes some of the weird data output from Cello2 when it comes to marshalling
    resources back and forth.

    Args:
        input_fp: Absolute path to the file
        final_trailing_comma: Whether or not the JSON in question has a final
            trailing comma.

    Returns:
        List of Dictionaries, typically.

    """
    with open(input_fp) as input_file:
        # TODO: Tim outputs invalid JSON in a number of very special ways
        #  that needs to be resolved. Quick and dirty hack for now.
        dirty_data = input_file.read()
        # It's tab-delineated!
        dirty_data = dirty_data.replace("\t", "")
        # There is (only sometimes!) a final trailing comma on the outside of
        # the entire JSON structure that can't be handled by the YAML superset!
        # Depends on the file for some reason!
        if final_trailing_comma:
            idx = dirty_data.rfind(",")
            dirty_data = dirty_data[:idx]
        data = yaml.load(dirty_data, Loader=yaml.FullLoader)
        # Generally, these kind of things are structured dictionaries but the
        # input JSONs are mangled so it's a coin flip.
        return data

# ------------------------------- NODE DEFINITION ------------------------------

''' 
Class:          Node
Description:    Basic circuit element.  All components of the target netlist
                JSON are treated as nodes in a linked-list type data structure.
'''
class Node():

    def __init__(self, nodeType, name, tag):

        self.type = nodeType            # Type of node (Input, Gate, Output)
        self.name = name                # Name of node (i.e. S4_SrpR)         
        self.tag = tag                  # Numerical ID of node, used for 
                                        # keeping track of next/prev nodes)

        self.func = None                # Boolean function implemented in node
        self.resfunc = None             # Sigmoidal response function 
                                        # implemented in node
        self.func_out = -1              # Node output calculated using either
                                        # the digital or genetic behavior
        
        self.prev_nodes = []            # List of input nodes to this node
        self.next_nodes = []            # List of nodes where this node is input
        self.high = -1                  # High value of an Input node
        self.low = -1                   # Low value of an Input node
        self.unit_conversion = None     # Unit scaling factor of output node

        # If node is gate (i.e. NOR or NOT) assign corresponding digital output
        if self.type == "NOR":
            self.func = f_nor
        elif self.type == "NOT":
            self.func = f_not

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Print parameters and properties of all nodes in the circuit
    '''
    def print(self):

        print("--------------------")
        print("NAME: " + self.name)
        print("ID: " + self.tag)
        print("TYPE: " + self.type)
        print("NEXT NODES: ", end = '')
        if self.next_nodes:
            for node in self.next_nodes:
                print(str(node.tag) + ", ", end = '')
        print()
        print("PREVIOUS NODE: ", end = '')
        if self.prev_nodes:
            for node in self.prev_nodes:
                print(str(node.tag) + ", ", end = '')
        print()
        print("--------------------")
        if self.type == "PRIMARY_INPUT":
            print("LOW = %lf, HIGH = %lf" % (self.low, self.high))
        elif self.type == "NOR" or self.type == "NOT" and self.resfunc is not None:
            print("YMAX = %lf, YMIN = %lf, K = %lf, n = %lf" % (self.resfunc.ymax, self.resfunc.ymin, self.resfunc.K, self.resfunc.n))
        print("--------------------")

    '''
    Function:       update_node_output
    Args:           circuit_type:   Current mode of operation (i.e. Digital or
                                    Genetic) of the circuit
    Return:         None
    Description:    Update output of node by applying the digital function to 
                    the inputs (i.e. OUT = x NOR y) OR the genetic function
                    (i.e. OUT = f(x), f is the sigmoidal response function) to
                    the inputs.  The inputs to any node are found in the 
                    self.prev_nodes list.  For a node behaving as a logical
                    NOT, there is 1 node in the list.  For a node behaving as a
                    logical NOR, there are 2 nodes in the list.  While there
                    is a scaling factor, the Output node is essentially a 
                    reporter and will just take on the value of the last
                    gate node in the circuit - the Output node should have only
                    1 previous node, so just get that output & pass it through. 
    '''
    def update_node_output(self, circuit_type):

        if circuit_type == "DIGITAL":

            if self.type == "NOT":
                self.func_out = self.func(self.prev_nodes[0].func_out)
            elif self.type == "NOR":
                self.func_out = self.func(self.prev_nodes[0].func_out, self.prev_nodes[1].func_out)
            elif self.type == "PRIMARY_OUTPUT":
                self.func_out = self.prev_nodes[0].func_out

        elif circuit_type == "GENETIC":

            if self.type == "NOT":
                self.func_out = self.resfunc.f(self.prev_nodes[0].func_out)
            elif self.type == "NOR":
                self.func_out = self.resfunc.f(self.prev_nodes[0].func_out + self.prev_nodes[1].func_out)
            elif self.type == "PRIMARY_OUTPUT":
                self.func_out = self.prev_nodes[0].func_out
 
    '''
    Function:       get_node_output
    Args:           None
    Return:         Logical output of the node
    Description:    Wrapper function that just returns the output of any node.
                    Return value based on type of node. 
    '''
    def get_node_output(self):

        if self.type == "NOT":
            return self.func(self.prev_nodes[0].func_out)
        elif self.type == "NOR":
            return self.func(self.prev_nodes[0].func_out, self.prev_nodes[1].func_out)
        elif self.type == "PRIMARY_OUTPUT":
            return self.prev_nodes[0].func_out
        elif self.type == "PRIMARY_INPUT":
            return self.func_out

# ------------------------------- NODE DEFINITION ------------------------------

# ------------------------- NETLIST_PARSER DEFINITION --------------------------

''' 
Class:          Netlist_Parser
Description:    Builds a linked-list data structure to represent digital/genetic
                circuits generated using the Cello tool.  Represents each
                item in the circuit as a node.  Performs two evaluations - a
                logical evaluation, where all components and signals are treated
                as digital components and Boolean values accordingly, and a
                genetic evaluation, where all components are modeled with a
                response function and the inputs and outputs are measured as 
                high and low values.  A score is produced which also measures
                how well the genetic circuit models the I/O behavior of the
                corresponding digital circuit.
''' 
class Netlist_Parser():

    def __init__(self, filepath):
        self.filepath = filepath            # Path to the input netlist JSON

        self.node_list = []                 # List of Nodes in the circuit
        self.inputs = []                    # List of Input Nodes
        self.output = []                    # List of Output Node(s)
        self.gates = []                     # List of Gates in the Circuit

        self.truth_table = {}               # I/O relationship assuming the 
                                            # circuit is a digital circuit
        self.genetic_truth_table = {}       # I/O relationship using the fact 
                                            # the circuit is genetic circuit

        self.circuit_score = 0              # Score of the circuit.  Defined as
                                            # ON_MIN/OFF_MAX - ratio of
                                            # smallest output value of genetic
                                            # circuit corresponding to logical 1 
                                            # output OVER largest output value 
                                            # of genetic circuit corresponding 
                                            # to logical 0 output
        self.log_circuit_score = 0          # log10 of the score

    '''
    Function:       check_initialized
    Args:           None
    Return:         The number of uninitialized gates in the circuit
    Description:    Calculate the number of unitialized nodes in the circuit.
                    An uninitalized node is defined as a node w/ output -1,
                    indicating that it has not yet applied its function (digital 
                    or genetic) to its input signal(s).  A circuit is fully
                    initialized all nodes output a valid output signal, and thus
                    the number of non-initialized nodes is 0.
    '''
    def check_initalized(self):
        num_non_initialized = 0
        for node in self.gates:
            if node.func_out == -1:
                num_non_initialized += 1
        return num_non_initialized

    '''
    Function:       print_names
    Args:           None
    Return:         None
    Description:    Print the name and ID (i.e. $1) of each node in the circuit.
    '''
    def print_names(self):
        for node in self.node_list:
            print("ID: " + node.tag + ", NAME: " + node.name)

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Prints the entire contents of each node in the circuit
    '''
    def print(self):
        for node in self.node_list:
            node.print()

    '''
    Function:       get_node
    Args:           tag: ID of requested node
    Return:         Node with matching ID
    Description:    Return the node in circuit with the requested ID (i.e. $1).
    '''
    def get_node(self, tag):

        for node in self.node_list:
            if node.tag == tag:
                return node

    '''
    Function:       parse_netlist
    Args:           cleanup:    Flag indicating input JSON needs to be fixed 
                                before processing
    Return:         None
    Description:    Processes the input netlist JSON, extracting the node info
                    from the JSON and building the linked list data structure.
    '''
    def parse_netlist(self, cleanup = False):

        # If no clean-up of the input JSON is necessary, just get the data
        if cleanup == False:

            f = open(self.filepath)
            data = json.load(f)
            f.close()

        # Else get the data and clean up the code by removing trailing commas
        elif cleanup == True:
            data = _fix_input_json(self.filepath, final_trailing_comma = True)
  
        # Look for the JSON field labeled nodes - for each entry in this field:
        for entry in data['nodes']:
            # Create a new node and extract the required parameters
            new_node = Node(nodeType = entry['nodeType'], name = entry['deviceName'], tag = entry['name'])
            # Append the node to the list of all circuit nodes
            self.node_list.append(new_node)

        # Look for the JSON field labeled edges - for each entry in this field:
        for entry in data['edges']:
            
            # Get the source node - starting point of the edge
            source_tag = entry['src']
            source_node = self.get_node(source_tag)

            # Get the destination node - stopping point of the edge
            dest_tag = entry['dst']
            dest_node = self.get_node(dest_tag)

            # Perform linking - dest_node is in next_nodes list of source_node,
            # and source_node is in prev_nodes list of dest_node.  This linking
            # is crucial towards "populating" the circuit with function values.
            source_node.next_nodes.append(dest_node)
            dest_node.prev_nodes.append(source_node)

        # For completeness, categorize each node by type - this will be helpful
        # in populating the circuit later.
        for node in self.node_list:

            if node.type == "PRIMARY_INPUT":
                self.inputs.append(node)
            elif node.type == "PRIMARY_OUTPUT":
                self.output.append(node)
            elif node.type == "NOT" or node.type == "NOR":
                self.gates.append(node)

    '''
    Function:       populate_input_values
    Args:           input_records:  Input signal records from Input_Processor
                                    module that extracted info from chassis JSON
    Return:         None
    Description:    Populates all Input nodes with parameters from chassis JSON
    '''
    def populate_input_values(self, input_records):

        # For each input node in circuit, look to see if it appears in the input
        # records - if it does, get the required parameters
        for node in self.inputs:
            if node.name in input_records:
                current_record = input_records[node.name]
                node.high = current_record.ymax
                node.low = current_record.ymin

    '''
    Function:       populate_response_functions
    Args:           gate_records:   Repressor records from Input_Processor
                                    module that extracted info from chassis JSON
    Return:         None
    Description:    Populates all Gate nodes with parameters from chassis JSON
    '''
    def populate_response_functions(self, gate_records):

        # For each gate in the circuit, look to see if it appears in the gate
        # records - if it does, get the required parameters
        for node in self.gates:
            if node.name in gate_records:
                current_record = gate_records[node.name]
                # Populate the node's response function with the parameters
                node.resfunc = ResponseFunction(ymax = current_record.ymax, ymin = current_record.ymin, K = current_record.K, n = current_record.n)

    '''
    Function:       populate_output_converters
    Args:           output_records: Output reporter records from Input_Processor
                                    module that extracted info from chassis JSON
    Return:         None
    Description:    Populates all Output nodes with parameters from chassis JSON
    '''
    def populate_output_converters(self, output_records):

        # For each output (should only be 1) in the circuit, look to see if it 
        # appears in the output records - if it does, get required parameters
        for node in self.output:
            if node.name in output_records:
                current_record = output_records[node.name]
                node.unit_conversion = current_record.unit_conversion

    '''
    Function:       run_circuit_logical
    Args:           None
    Return:         None
    Description:    Simulates the digital model of the circuit.  The underlying
                    algorithm is definitely not efficient, but due to the small
                    # of gates in the circuit, meets performance expecations.
                    Essentially, the algorithm is a three-step algorithm:
                    1) Assign a signal value to each input signal.
                    2) Update each single-input gate (i.e. NOT gate) that is 
                    directly tied to a circuit input signal - essentially 
                    "propagate" the circuit values upward.
                    3) Iterate over all remaining gates, attempting to generate
                    an output signal if the input signal(s) to the current gate
                    are valid.  In principle, this is the most expensive part of
                    the algorithm: O(n^2) if there are n gates remaining after
                    the first two steps.  In practice, given that n is small
                    and sometimes the ordering of the gates in the gate list
                    is conducive towards fast computation (i.e. gates that can
                    be updated appear earlier in the list!), the cost is very
                    small - it would be worth exploring more efficient
                    algorithms here, especially for more advanced circuits.
    '''
    def run_circuit_logical(self):

        num_inputs = 0
        circuit_output = 0

        # Determine the number of input signals
        for node in self.node_list:
            if node.type == "PRIMARY_INPUT":
                num_inputs += 1
   
        # Generate all possible combinations of logical inputs: 2^num_inputs
        inputs = list(itertools.product([0, 1], repeat = num_inputs))

        # For each potential logical input
        for current_input in inputs:

            # Make sure to reset the output of each node after each iteration!
            for node in self.node_list:
                node.func_out = -1

            # First assign values to each of the input signals
            for i in range(0, num_inputs):
                self.inputs[i].func_out = current_input[i]

            # Second, populate all gates that are directly tied to the inputs
            for input_node in self.inputs:

                # For each of the next gates
                for next_node in input_node.next_nodes:
                    # If the next gate is a NOT gate, directly populate output
                    if next_node.type == "NOT":
                        next_node.update_node_output("DIGITAL")

                    # Else if the next gate is a NOR gate can only populate the
                    # output if both of its predecessors are primary inputs
                    elif next_node.type == "NOR" and next_node.prev_nodes[0].type == "PRIMARY_INPUT" and next_node.prev_nodes[1].type == "PRIMARY_INPUT":
                        next_node.update_node_output("DIGITAL")
            
            #for node in self.node_list:
            #    print("NODE TAG = " + node.tag + " OUTPUT = " + str(node.func_out))

            # Third, "flow upwards" until all gates are populated - 
            # While there are still unitialized nodes:
            while self.check_initalized() != 0:
                # For each node in the gate list
                for node in self.gates:
                    # If NOT gate was identified & has a valid input, update
                    if node.func_out == -1 and node.type == "NOT" and node.prev_nodes[0].func_out != -1:
                        node.update_node_output("DIGITAL")
                    # Else if NOR gate was identified & has valid inputs, update
                    elif node.func_out == -1 and node.type == "NOR" and node.prev_nodes[0].func_out != -1 and node.prev_nodes[1].func_out != -1:
                        node.update_node_output("DIGITAL")

            # Caluclate the circuit output and populate the Boolean truth table
            circuit_output = self.output[0].get_node_output()
            self.truth_table[current_input] = circuit_output

    '''
    Function:       run_circuit_genetic
    Args:           None
    Return:         None
    Description:    Simulates the genetic model of the circuit.  The underlying
                    algorithm is identical to the algorithm used in the
                    run_circuit_logical function, but the functions used are
                    sigmoidal response functions, not the Boolean functions.
    '''
    def run_circuit_genetic(self):

        num_inputs = 0
        circuit_output = 0.0

        # Determine the number of input signals
        for node in self.node_list:
            if node.type == "PRIMARY_INPUT":
                num_inputs += 1

        # Generate all possible combinations of logical inputs: 2^num_inputs
        inputs = list(itertools.product([0, 1], repeat = num_inputs))
        
        # For each potential genetic input
        for current_input in inputs:

            # Make sure to reset the output of each node after each iteration!
            for node in self.node_list:
                node.func_out = -1

            # First assign values to each of the input signals
            # Need to map the Boolen values to genetic high/low values
            for i in range(0, num_inputs):
                if current_input[i] == 0:
                    self.inputs[i].func_out = self.inputs[i].low
                elif current_input[i] == 1:
                    self.inputs[i].func_out = self.inputs[i].high

            inputs_genetic = tuple([node.func_out for node in self.inputs])

            # Second, populate all gates that are directly tied to the inputs
            for input_node in self.inputs:

                # For each of the next gates
                for next_node in input_node.next_nodes:
                    # If the next gate is a NOT gate, directly populate output
                    if next_node.type == "NOT":
                        next_node.update_node_output("GENETIC")
                        
                    # Else if the next gate is a NOR gate can only populate the
                    # output if both of its predecessors are primary inputs
                    elif next_node.type == "NOR" and next_node.prev_nodes[0].type == "PRIMARY_INPUT" and next_node.prev_nodes[1].type == "PRIMARY_INPUT":
                        next_node.update_node_output("GENETIC")
                        
            # Third, "flow upwards" until all gates are populated - 
            # While there are still unitialized nodes:
            while self.check_initalized() != 0:
                
                # For each node in the gate list
                for node in self.gates:
                    # If NOT gate was identified & has a valid input, update
                    if node.func_out == -1 and node.type == "NOT" and node.prev_nodes[0].func_out != -1:
                        node.update_node_output("GENETIC")
                    # Else if NOR gate was identified & has valid inputs, update
                    elif node.func_out == -1 and node.type == "NOR" and node.prev_nodes[0].func_out != -1 and node.prev_nodes[1].func_out != -1:
                        node.update_node_output("GENETIC")
                    
            # Calculate the overall output of the circuit and populate the genetic Truth table
            circuit_output = self.output[0].get_node_output() * self.output[0].unit_conversion
            self.genetic_truth_table[current_input] = [inputs_genetic, circuit_output, self.truth_table[current_input]]
 

    '''
    Function:       calculate_score
    Args:           None
    Return:         None
    Description:    Calculates the score of a genetic circuit - ON_MIN/OFF_MAX
    '''
    def calculate_score(self):

        ON_MIN = 1e9
        OFF_MAX = -1

        # For each entry in the genetic truth table
        for key, value in self.genetic_truth_table.items():

            # Get the logical output and the genetic output
            logic_out = value[2]
            genetic_out = value[1]
            
            # If entry's output corresponds to logical 0, update OFF_MAX as necessary
            if logic_out == 0 and genetic_out > OFF_MAX:
                    OFF_MAX = genetic_out
            # Else if entry's output corresponds to logical 1, update ON_MIN as ncessary
            elif logic_out == 1 and genetic_out < ON_MIN:
                    ON_MIN = genetic_out

        self.ON_MIN = ON_MIN
        self.OFF_MAX = OFF_MAX

        # Calculate the score and log score
        self.circuit_score = self.ON_MIN/self.OFF_MAX
        self.log_circuit_score = np.log10(self.circuit_score)

    '''
    Function:       print_genetic_truth_table
    Args:           None
    Return:         None
    Description:    Prints the contents of the genetic truth table line by line
    '''
    def print_genetric_truth_table(self):

        for key, value in self.genetic_truth_table.items():
            logic_out = value[2]
            genetic_out = value[1]
            print("DI/O = [ (" + ' '.join(('%d' % f) for f in key) + ") --> " + str(logic_out) + " ] || GI/O = [ (" + ' '.join(('%.3e' % f) for f in value[0]) + ") --> %.5e" % value[1] + " ]")

if __name__ == '__main__':

    mParser = Netlist_Parser(NETLIST_JSON)
    mParser.parse_netlist()
    mParser.print()
    mParser.run_circuit_logical()
    