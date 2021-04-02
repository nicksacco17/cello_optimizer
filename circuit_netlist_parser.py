
import json
import itertools
import record as rec
import response_function as rf
import numpy as np
from typing import (
    Any,
    Dict,
    List,
    Union,
)
import yaml


NETLIST_JSON = "D:\\CSBE\\HW1\\and_outputNetlist.json"

def f_not(x):
    if x == 0:
        return 1
    elif x == 1:
        return 0
    elif x == -1:
        return -1

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

# This is from cello api, just pulled the code here to make it easier to use, but all credit goes to WR Jackson who
# wrote the cello api
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

class Node():

    def __init__(self, nodeType, name, tag):
        self.type = nodeType
        self.name = name
        self.tag = tag
        self.func = None
        self.resfunc = None
        self.func_out = -1
        self.prev_nodes = []
        self.next_nodes = []
        self.high = -1
        self.low = -1
        self.unit_conversion = None

        if self.type == "NOR":
            self.num_outputs = 1
            self.num_inputs = 2
            self.func = f_nor
        elif self.type == "NOT":
            self.num_outputs = 1
            self.num_inputs = 1
            self.func = f_not
        elif self.type == "PRIMARY_OUTPUT":
            self.num_outputs = 0
            self.num_inputs = -9999
        elif self.type == "PRIMARY_INPUT":
            self.num_outputs = -9999
            self.num_inputs = 0

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
        elif self.type == "NOR" or self.type == "NOT":
            print("YMAX = %lf, YMIN = %lf, K = %lf, n = %lf" % (self.resfunc.ymax, self.resfunc.ymin, self.resfunc.K, self.resfunc.n))
        print("--------------------")

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
    def update_node_output(self):

        if self.type == "NOT":
            self.func_out = self.func(self.prev_nodes[0].func_out)
        elif self.type == "NOR":
            self.func_out = self.func(self.prev_nodes[0].func_out, self.prev_nodes[1].func_out)
        elif self.type == "PRIMARY_OUTPUT":
            self.func_out = self.prev_nodes[0].func_out

    def update_node_genetic_output(self):

        if self.type == "NOT":
            self.func_out = self.resfunc.f(self.prev_nodes[0].func_out)
        elif self.type == "NOR":
            self.func_out = self.resfunc.f(self.prev_nodes[0].func_out + self.prev_nodes[1].func_out)
        elif self.type == "PRIMARY_OUTPUT":
            self.func_out = self.prev_nodes[0].func_out
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

class Netlist_Parser():

    def __init__(self, filepath):
        self.filepath = filepath
        self.node_list = []
        self.inputs = []
        self.output = []
        self.gates = []
        self.truth_table = {}
        self.genetic_truth_table = {}
        self.circuit_score = 0
        self.log_circuit_score = 0

    def check_initalized(self):

        num_non_initialized = 0
        for node in self.gates:
            if node.func_out == -1:
                num_non_initialized += 1
        return num_non_initialized

    def print_names(self):
        for node in self.node_list:
            print("ID: " + node.tag + ", NAME: " + node.name)

    def get_node(self, tag):

        for node in self.node_list:
            if node.tag == tag:
                return node

    def parse_netlist(self, cleanup = False):

        if cleanup == False:

            f = open(self.filepath)
            data = json.load(f)
            f.close()

        elif cleanup == True:
            data = _fix_input_json(self.filepath, final_trailing_comma = True)
  
        for entry in data['nodes']:
            new_node = Node(nodeType = entry['nodeType'], name = entry['deviceName'], tag = entry['name'])
            self.node_list.append(new_node)

        for entry in data['edges']:
            
            source_tag = entry['src']
            source_node = self.get_node(source_tag)

            dest_tag = entry['dst']
            dest_node = self.get_node(dest_tag)

            source_node.next_nodes.append(dest_node)
            dest_node.prev_nodes.append(source_node)

        for node in self.node_list:

            if node.type == "PRIMARY_INPUT":
                self.inputs.append(node)
            elif node.type == "PRIMARY_OUTPUT":
                self.output.append(node)
            elif node.type == "NOT" or node.type == "NOR":
                self.gates.append(node)

        #temp_array = self.inputs

        #for i in range(0, len(temp_array) - 1):
        #    for j in range(i, len(temp_array) - 1):
        #        if temp_array[j].tag > temp_array[j+1].tag:
        #            temp = temp_array[j+1]
        #            temp_array[j+1] = temp_array[j]
        #            temp_array[j] = temp

        #temp_array.reverse()
        #self.inputs = temp_array

            # For each node in the list
            #for node in self.node_list:

                # If the source has been found
            #    if node.tag == source:

                    # Append the destination node
            #        node.next_nodes.append(dest)

                    # Now do the reverse - for each node in the list, look for the destination
            #        for node2 in self.node_list:

                        # If the destination has been found, append the source node
            #            if node2.tag == dest:
            #                node2.prev_nodes.append(source)

    def populate_output_converters(self, output_records):

        for node in self.output:
            if node.name in output_records:
                current_record = output_records[node.name]
                node.unit_conversion = current_record.unit_conversion

    def populate_input_values(self, input_records):

        for node in self.inputs:
            if node.name in input_records:
                current_record = input_records[node.name]
                node.high = current_record.ymax
                node.low = current_record.ymin

    def populate_response_functions(self, gate_records):

        for node in self.gates:
            if node.name in gate_records:
                current_record = gate_records[node.name]
                node.resfunc = rf.ResponseFunction(ymax = current_record.ymax, ymin = current_record.ymin, K = current_record.K, n = current_record.n)

    def run_circuit_logical(self):

        num_inputs = 0

        # Determine the number of input signals
        for node in self.node_list:
            if node.type == "PRIMARY_INPUT":
                num_inputs += 1

        # Generate the logical inputs
        inputs = list(itertools.product([0, 1], repeat = num_inputs))
        circuit_output = 0

        # For each potential logical input
        for current_input in inputs:

            # Reset after each iteration!
            for node in self.node_list:
                node.func_out = -1

            # First assign inputs to each of the input signals
            for i in range(0, num_inputs):
                self.inputs[i].func_out = current_input[i]

            # Then, attempt to populate all gates that are directly tied to the inputs
            for input_node in self.inputs:

                # For each of the next gates
                for next_node in input_node.next_nodes:
                    # If the next gate is a NOT gate we can directly populate the output
                    if next_node.type == "NOT":
                        next_node.update_node_output("DIGITAL")
                        #next_node.func_out = next_node.func(next_node.prev_nodes[0].func_out)
                    # Else if the next gate is a NOR gate we can only populate the output if its predecessors are both primary inputs
                    elif next_node.type == "NOR" and next_node.prev_nodes[0].type == "PRIMARY_INPUT" and next_node.prev_nodes[1].type == "PRIMARY_INPUT":
                        next_node.update_node_output("DIGITAL")
                        #next_node.func_out = next_node.func(next_node.prev_nodes[0].func_out, next_node.prev_nodes[1].func_out)
            
            #for node in self.gates:
            #    print("NODE TAG = " + node.tag + " " + "FUNCTION OUT = %d" % node.func_out)

            # Now flow up until all gates are populated
            while self.check_initalized() != 0:
                for node in self.gates:
                    if node.func_out == -1 and node.type == "NOT" and node.prev_nodes[0].func_out != -1:
                        node.update_node_output("DIGITAL")
                        #node.func_out = node.func(node.prev_nodes[0].func_out)
                    elif node.func_out == -1 and node.type == "NOR" and node.prev_nodes[0].func_out != -1 and node.prev_nodes[1].func_out != -1:
                        node.update_node_output("DIGITAL")
                        #node.func_out = node.func(node.prev_nodes[0].func_out, node.prev_nodes[1].func_out)

            circuit_output = self.output[0].get_node_output()
            self.truth_table[current_input] = circuit_output
 

        #print(self.truth_table)

    def run_circuit_genetic(self):

        num_inputs = 0

        # Determine the number of input signals
        for node in self.node_list:
            if node.type == "PRIMARY_INPUT":
                num_inputs += 1

        # Generate the logical inputs
        inputs = list(itertools.product([0, 1], repeat = num_inputs))
        circuit_output = 0.0

        # For each potential genetic input
        for current_input in inputs:

            # Reset after each iteration!
            for node in self.node_list:
                node.func_out = -1

            # First assign inputs to each of the input signals - need to map the boolean values to genetic values
            for i in range(0, num_inputs):
                if current_input[i] == 0:
                    self.inputs[i].func_out = self.inputs[i].low
                elif current_input[i] == 1:
                    self.inputs[i].func_out = self.inputs[i].high
            inputs_genetic = tuple([node.func_out for node in self.inputs])

            # Then, attempt to populate all gates that are directly tied to the inputs
            for input_node in self.inputs:

                # For each of the next gates
                for next_node in input_node.next_nodes:
                    # If the next gate is a NOT gate we can directly populate the output
                    if next_node.type == "NOT":
                        next_node.update_node_output("GENETIC")
                        #next_node.func_out = next_node.func(next_node.prev_nodes[0].func_out)
                    # Else if the next gate is a NOR gate we can only populate the output if its predecessors are both primary inputs
                    elif next_node.type == "NOR" and next_node.prev_nodes[0].type == "PRIMARY_INPUT" and next_node.prev_nodes[1].type == "PRIMARY_INPUT":
                        next_node.update_node_output("GENETIC")
                        #next_node.func_out = next_node.func(next_node.prev_nodes[0].func_out, next_node.prev_nodes[1].func_out)

            # Now flow up until all gates are populated
            while self.check_initalized() != 0:
                for node in self.gates:
                    if node.func_out == -1 and node.type == "NOT" and node.prev_nodes[0].func_out != -1:
                        node.update_node_output("GENETIC")
                        #node.func_out = node.func(node.prev_nodes[0].func_out)
                    elif node.func_out == -1 and node.type == "NOR" and node.prev_nodes[0].func_out != -1 and node.prev_nodes[1].func_out != -1:
                        node.update_node_output("GENETIC")
                        #node.func_out = node.func(node.prev_nodes[0].func_out, node.prev_nodes[1].func_out)

            circuit_output = self.output[0].get_node_output() * self.output[0].unit_conversion
            self.genetic_truth_table[current_input] = [inputs_genetic, circuit_output, self.truth_table[current_input]]
 
    def print(self):
        for node in self.node_list:
            node.print()

    def calculate_score(self):

        input_signals = tuple([node.name for node in self.inputs])
        #print("INPUT TUPLE: " + str(input_signals))

        ON_MIN = 1e9
        OFF_MAX = -1

        for key, value in self.genetic_truth_table.items():
            logic_out = value[2]
            genetic_out = value[1]
            
            if logic_out == 0 and genetic_out > OFF_MAX:
                    OFF_MAX = genetic_out
            elif logic_out == 1 and genetic_out < ON_MIN:
                    ON_MIN = genetic_out

        self.ON_MIN = ON_MIN
        self.OFF_MAX = OFF_MAX
        self.circuit_score = self.ON_MIN/self.OFF_MAX
        self.log_circuit_score = np.log10(self.circuit_score)

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
    