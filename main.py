# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: main.py
# Description:  Main algorithm of the tool.  Steps:
#               1) Extract the inputs from the command line
#               2) Run the InputProcessor module, extracting records from the
#                  input files
#               3) For each potential signal, execute a Cello query.
#               4) Following the Cello query, execute the NetlistParser scoring.
#               5) Perform the simulated annealing routine, optimizing the score
#                  of the design produced from Cello.
#               6) If a new best score has been identified, update the state
#                  variables with the best score, inputs, and circuit design.
#               7) Repeat for each potential signal.
#               8) When the algorithm is finished, save the best results to the
#                  working chassis.UCF.json file, and print the location of
#                  said file to the terminal.
# Status:   Mostly operational.  The simulated annealing algorithm is a little
#           artificial (by that, I mean I'm not sure how physically meaningful
#           the results of the optimization are), and we could definitely use
#           some help in defining physically meaningful constraints on the 
#           types of circuits generated and optimized in the tool.  However, we
#           believe we have developed a solid proof-of-concept for optimizing
#           genetic circuits using Cello as a base module.
# ------------------------------------------------------------------------------

# Imports
from record import Input_Signal_Record, Repressor_Record
from input_processor import Input_Processor
from circuit_netlist_parser import Netlist_Parser
from celloapi2 import CelloQuery, CelloResult
from itertools import combinations
from shutil import copyfile
from util import parse_verilog
import time
import os
import sys
import numpy as np
import copy

def main():

    # Process the command line arguments
    if len(sys.argv) >= 2:
        path_to_chassis = sys.argv[1]
        chassis_name = sys.argv[2]
        path_to_verilog = sys.argv[3]
        verilog_name = os.path.split(sys.argv[3])[1]
        working_directory = sys.argv[4]

    if not path_to_chassis or not chassis_name or not path_to_verilog or not verilog_name or not working_directory:
        print("[ERROR]: INVALID ARGUMENTS IN <run.sh> SCRIPT, PLEASE ADJUST")
    
    print(path_to_chassis)
    print(chassis_name)
    print(path_to_verilog)
    print(verilog_name)
    print(working_directory)

    # Create two folders within the working directory - cello_in, where the
    # chassis files will be moved, and cello_out, where Cello will dump results
    IN_DIR = working_directory + "cello_in\\"
    OUT_DIR = working_directory + "cello_out\\"

    # Step 1: Parse the input files of the specified chassis
    file_parser = Input_Processor(path_to_chassis, chassis_name, working_directory = IN_DIR)
    file_parser.parse_input()
    file_parser.parse_ucf()
    file_parser.parse_output()
    #file_parser.print()
    #file_parser.modify_inputs()
    #file_parser.modify_constraint()
    #file_parser.save_input()
    #file_parser.save_ucf()

    # Step 2: Calculate the number of input signals from the input Verilog file
    signal_input = parse_verilog(path_to_verilog)
    copyfile(path_to_verilog, IN_DIR + verilog_name)

    print(file_parser.options_filename)
    print(file_parser.circuit_constraint_filename)
    print(file_parser.circuit_input_filename)
    print(file_parser.circuit_output_filename)

    # Step 3: Run Cello to get a baseline view of valid designs
    q = CelloQuery(
            input_directory = IN_DIR, 
            output_directory = OUT_DIR, 
            verilog_file = verilog_name, 
            compiler_options = file_parser.options_filename, 
            input_ucf = file_parser.circuit_constraint_filename, 
            input_sensors = file_parser.circuit_input_filename, 
            output_device = file_parser.circuit_output_filename)
   
    # Create the input pairing over all potential input signals
    signals = q.get_input_signals()
    signal_pairing = list(combinations(signals, signal_input))

    print("SIGNALS: " + str(signals))
    print("SIGNAL PAIRING: " + str(signal_pairing))

    best_cello_score = 0
    best_cello_design = None
    best_cello_inputs = None

    best_annealing_score = 0
    best_annealing_design = None
    best_annealing_inputs = None

    # For each set of input signals
    for signal_set in signal_pairing:

        signal_set = list(signal_set)
        print("SIGNAL SET: " + str(signal_set))

        q.set_input_signals(signal_set)

        # Generate a design using Cello!
        start_time = time.time()
        q.get_results()
        stop_time = time.time()
        print("GET RESULTS TOTAL TIME = %lf" % (stop_time - start_time))

        try:
            # Get results of the Cello query (most important: Scoring and Netlist)
            res = CelloResult(results_dir = OUT_DIR)
           
            cello_circuit = res.part_names
            cello_score = res.circuit_score

            # Step 4: Run the netlist scoring which should be the same results 
            # as the Cello scoring.

            # Get the output circuit netlist
            circuit_netlist_json = OUT_DIR + verilog_name.replace(".v", "") + "_outputNetlist.json"
            
            # Create the parser module
            netlist_parser = Netlist_Parser(circuit_netlist_json)
  
            # Cleanup the netlist JSON (Not needed if the _outputNetlist.json 
            # file is correctly formatted)
            netlist_parser.parse_netlist(cleanup = True)

            # Populate the reconstructed circuit with the parameters 
            # from the input JSONs (input, UCF, output)
            netlist_parser.populate_input_values(file_parser.input_records)
            netlist_parser.populate_response_functions(file_parser.gate_records)
            netlist_parser.populate_output_converters(file_parser.output_records)
    
            #netlist_parser.print()

            # Now run the logic generator and the genetic generator - first 
            # assume it is digital circuit, compute what the outputs should be.  
            # Next run as genetic circuit w/ response functions for each gate.
            netlist_parser.run_circuit_logical()
            netlist_parser.run_circuit_genetic()

            # Calculate the score
            netlist_parser.calculate_score()
            netlist_parser.print_genetric_truth_table()
            netlist_score = netlist_parser.circuit_score

            #print("NETLIST SCORE = %lf" % netlist_score)

            # Step 5: begin the simulated annealing on the gates in the circuit

            # Set the starting temperature to 20% of the starting score
            temperature = 0.20 * netlist_score
            count = 0
            num_iterations = 1000
            
            best_gates = {}

            # Copy the records to a working space
            scratch_records = {}
            original_records = {}

            for node in netlist_parser.gates:
                new_record = Repressor_Record()
                new_record.name = node.name
                new_record.populate_params(ymax = node.resfunc.ymax, ymin = node.resfunc.ymin, K = node.resfunc.K, n = node.resfunc.n)
                scratch_records[new_record.name] = new_record

            original_records = copy.deepcopy(scratch_records)
            #print(scratch_records)
            #print(original_records)

            # Begin the simulated annealing
            for it in range(0, num_iterations):

                # Every 10% of iterations, reduce the temperature in half, 
                # reducing the probability of selecting new input parameters
                if it > 0 and count % (num_iterations / 10) == 0:
                    temperature /= 2

                # For each gate in the circuit

                pre_modified_records = copy.deepcopy(scratch_records)
                valid_state_generated_list = []

                # Randomly generate a new "input vector" by modifying each of the gates in the circuit
                for gate in netlist_parser.gates:
                    
                    current_name = gate.name
                    current_record = scratch_records[current_name]
                    
                    # Attempt to generate the input vector - will retry up to the specified number of times before moving on
                    current_state_valid_flag = current_record.modify_repressor(num_retries = 10)
                    valid_state_generated_list.append(current_state_valid_flag)

                num_valid = 0
                for entry in valid_state_generated_list:
                    if entry:
                        num_valid += 1

                # If all input vectors are valid
                if num_valid == len(scratch_records):

                    # Repopulate the circuit with the new function parameters
                    netlist_parser.populate_response_functions(scratch_records)

                    # Rerun the circuit at the genetic level
                    netlist_parser.run_circuit_genetic()

                    # Calculate the updated score
                    netlist_parser.calculate_score()
                    updated_netlist_score = netlist_parser.circuit_score

                    # Make sure that the values are physically meaningful...
                    # not sure what exactly this means, but OFF_MAX ~ 1e-10 and ON_MIN ~ 1e5 does NOT seem realistic...
                    # So just check to see if OFF_MAX and ON_MIN are in reasonable values before accepting the change.  Otherwise
                    # We will reject automatically.

                    ON_MIN_UPPER_BOUND = 5
                    OFF_MAX_LOWER_BOUND = 1e-3

                    # If within the range, then we can evaluate the change using simulated annealing algorithm
                    if netlist_parser.ON_MIN < ON_MIN_UPPER_BOUND and netlist_parser.OFF_MAX > OFF_MAX_LOWER_BOUND:

                        # If the updated score was an improvement, accepted the parameter change
                        if updated_netlist_score > netlist_score:
                            netlist_score = updated_netlist_score
                            best_gates = copy.deepcopy(scratch_records)

                        # Else we will accept with certain probability
                        else:
                            cost_diff = netlist_score - updated_netlist_score
                            accept_prob = np.random.uniform(low = 0.0, high = 1.0)
                    
                            if np.exp(-1 * cost_diff / temperature) > accept_prob:
                                netlist_score = updated_netlist_score
                            # Else we need to undo the changes to the scratch records
                            else:
                                best_gates = copy.deepcopy(scratch_records)
                                scratch_records = copy.deepcopy(pre_modified_records)
                                netlist_parser.populate_response_functions(scratch_records)
                                netlist_parser.run_circuit_genetic()
                                netlist_parser.calculate_score()
                        count += 1
                    # Else undo the changes to the scratch records because the changes were not physically meaningful
                    else:
                        scratch_records = copy.deepcopy(pre_modified_records)
                        netlist_parser.populate_response_functions(scratch_records)
                        netlist_parser.run_circuit_genetic()
                        netlist_parser.calculate_score()
                # Else undo the changes to the scratch records because the changes were not physically meaningful
                else:
                    scratch_records = copy.deepcopy(pre_modified_records)
                    netlist_parser.populate_response_functions(scratch_records)
                    netlist_parser.run_circuit_genetic()
                    netlist_parser.calculate_score()
            
            print("CELLO SCORE: %lf" % cello_score)
            print("ANNEALING SCORE: %lf" % netlist_score)

            print("BEST GATES: ")
            for gate_name, record_obj in best_gates.items():
                print("GATE NAME = " + gate_name)
                record_obj.print()

            if cello_score > best_cello_score:
                best_cello_score = cello_score
                best_cello_inputs = signal_set
                best_cello_design = cello_circuit

            if netlist_score > best_annealing_score:
                best_annealing_score = netlist_score
                best_annealing_inputs = signal_set
                best_annealing_design = best_gates

        except:
            pass
        q.reset_input_signals()
                    
    print("BEST CELLO SCORE = %lf" % best_cello_score)
    print("BEST CELLO INPUTS = " + str(best_cello_inputs))
    print("BEST CELLO DESIGN = " + str(best_cello_design))

    print("BEST ANNEALING SCORE = %lf" % best_annealing_score)
    print("BEST ANNEALING INPUTS = " + str(best_annealing_inputs))
    print("BEST ANNEALING DESING = ")
    for gate_name, record_obj in best_annealing_design.items():
        print("GATE NAME = " + gate_name)
        record_obj.print()

    # Step 6: Save the best parameters to the UCF file

    # Overwrite the parameters in the file processor
    for gate_name, gate_obj in best_annealing_design.items():
        #gate_obj.print()
        file_parser.gate_records[gate_name].populate_params(ymax = gate_obj.ymax, ymin = gate_obj.ymin, K = gate_obj.K, n = gate_obj.n)

    # Save the parameters to the UCF
    file_parser.save_ucf()

    # And print the path to the modified file!
    print("YOUR FILE IS " + file_parser.working_circuit_constraint_file)

if __name__ == '__main__':
    main()