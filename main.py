
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

def pause_program(flag):
    if flag:
        input("Press Enter to continue...")

PAUSE_FLAG = True
        
def main():

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

    IN_DIR = working_directory + "cello_in\\"
    OUT_DIR = working_directory + "cello_out\\"

    best_score = 0
    best_chassis = None
    best_input_signals = None

    # Step 1: Parse the input files of the specified chassis
'''
    file_parser = Input_Processor(path_to_chassis, chassis_name, working_directory = IN_DIR)
    file_parser.parse_input()
    file_parser.parse_ucf()
    file_parser.parse_output()
    #file_parser.modify_inputs()
    #file_parser.modify_constraint()
    #file_parser.save_input()
    #file_parser.save_ucf()

    print(file_parser.working_circuit_constraint_file)
    print(file_parser.working_circuit_input_file)
    print(file_parser.working_circuit_output_file)
    print(file_parser.working_options_file)

    print(file_parser.options_filename)
    print(file_parser.circuit_constraint_filename)
    print(file_parser.circuit_input_filename)
    print(file_parser.circuit_output_filename)

    print(IN_DIR)
    print(OUT_DIR)


    # Step 2: Calculate the number of input signals from the input Verilog file
    signal_input = parse_verilog(VERILOG_FILE)
    copyfile(path_to_verilog, IN_DIR + verilog_name)

    print(VERILOG_FILE)

    # Step 3: Run Cello once to get a baseline
    #start_time = time.time()
    #q = CelloQuery(
    #        input_directory = IN_DIR, 
    #        output_directory = OUT_DIR, 
    #        verilog_file = verilog_name, 
    #        compiler_options = file_parser.options_filename, 
    #        input_ucf = file_parser.circuit_constraint_filename, 
    #        input_sensors = file_parser.circuit_input_filename, 
    #        output_device = file_parser.circuit_output_filename)
    #stop_time = time.time()
    #print("TOTAL TIME = %lf" % (stop_time - start_time))

    #signals = q.get_input_signals()
    #signal_pairing = list(combinations(signals, signal_input))

    #print("SIGNALS: " + str(signals))
    #print("SIGNAL PAIRING: " + str(signal_pairing))

    circuit_netlist_json = OUT_DIR + verilog_name.replace(".v", "") + "_outputNetlist.json"
    
    
    netlist_parser = Netlist_Parser(circuit_netlist_json)
    netlist_parser.print()

    # Cleanup the netlist JSON (Not needed if the _outputNetlist.json file is correctly formatted)
    netlist_parser.parse_netlist(cleanup = True)

    # Populate the reconstructed circuit with the parameters from the input JSONs (input, UCF, output)
    netlist_parser.populate_input_values(file_parser.input_records)
    netlist_parser.populate_response_functions(file_parser.gate_records)
    netlist_parser.populate_output_converters(file_parser.output_records)

    # Now run the logic generator and the genetic generator - first assume it is digital circuit,
    # compute what the outputs should be.  Next run it like actual genetic circuit using response 
    # functions for each gate.
    netlist_parser.run_circuit_logical()
    netlist_parser.run_circuit_genetic()

    # Calculate the score
    netlist_parser.calculate_score()
    netlist_score = netlist_parser.circuit_score

    print("STARTING SCORE = %lf" % netlist_score)

    # Now, begin the simulated annealing on the gates in the circuit

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
    print(scratch_records)
    print(original_records)

    num_retries = 100

    for it in range(0, num_iterations):

        if it % 10 == 0:
            print("SCORE: %lf" % netlist_score)
            netlist_parser.print_genetric_truth_table()
            #for rec, rec_Obj in scratch_records.items():
            #    rec_Obj.print()
        # Every 10% of iterations, reduce the temperature in half, reducing the probability of selecting new spaces
        #if it > 0 and count % (num_iterations / 10) == 0:
        #    temperature /= 2

        # Randomly generate a new "input vector" by modifying each of the gates in the circuit

        # For each gate in the circuit

        pre_modified_records = copy.deepcopy(scratch_records)
        
        valid_state_generated_list = []

        for gate in netlist_parser.gates:
            
            current_name = gate.name
            current_record = scratch_records[current_name]
            
            current_state_valid_flag = current_record.modify_repressor(num_retries = 10)
            valid_state_generated_list.append(current_state_valid_flag)

        num_valid = 0
        for entry in valid_state_generated_list:
            if entry:
                num_valid += 1

        if num_valid == len(scratch_records):
            # Repopulate the circuit
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

            # If within the range, that's good
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
            # Else undo the changes to the scratch records
            else:
                scratch_records = copy.deepcopy(pre_modified_records)
                netlist_parser.populate_response_functions(scratch_records)
                netlist_parser.run_circuit_genetic()
                netlist_parser.calculate_score()

    #cello_score = res.circuit_score
    
    #print("CELLO SCORE: %lf" % cello_score)
    print("ANNEALING SCORE: %lf" % netlist_score)

    print("BEST GATES: ")
    for gate_name, record_obj in best_gates.items():
        print("GATE NAME = " + gate_name)
        record_obj.print()
'''
'''
    for signal_set in signal_pairing:
        signal_set = list(signal_set)

        print("SIGNAL SET: " + str(signal_set))

        #q.set_input_signals(signal_set)

        start_time = time.time()
        #q.get_results()
        stop_time = time.time()
        print("GET RESULTS TOTAL TIME = %lf" % (stop_time - start_time))

        try:
            # Get results of the Cello query (most important: Scoring and Netlist)
            #res = CelloResult(results_dir = OUT_DIR)
            #print("PART NAMES: " + str(res.part_names))
            #print("REPRESSOR SCORES: " + str(res.repressor_scores))
            #print("CIRCUIT SCORES: " + str(res.circuit_score))

            # Select the output netlist
            circuit_netlist_json = OUT_DIR + verilog_name.replace(".v", "") + "_outputNetlist.json"

            # Create the parser module
            netlist_parser = Netlist_Parser(circuit_netlist_json)
            netlist_parser.print()

            # Cleanup the netlist JSON (Not needed if the _outputNetlist.json file is correctly formatted)
            netlist_parser.parse_netlist(cleanup = True)

            # Populate the reconstructed circuit with the parameters from the input JSONs (input, UCF, output)
            netlist_parser.populate_input_values(file_parser.input_records)
            netlist_parser.populate_response_functions(file_parser.gate_records)
            netlist_parser.populate_output_converters(file_parser.output_records)
    
            # Now run the logic generator and the genetic generator - first assume it is digital circuit,
            # compute what the outputs should be.  Next run it like actual genetic circuit using response 
            # functions for each gate.
            netlist_parser.run_circuit_logical()
            netlist_parser.run_circuit_genetic()
    
            # Calculate the score
            netlist_parser.calculate_score()
            netlist_score = netlist_parser.circuit_score

            # Now, begin the simulated annealing on the gates in the circuit

            temperature = 20.0
            count = 0
            num_iterations = 1000

            for it in range(0, num_iterations):

                if it % 10 == 0:
                    print("SCORE: %lf" % netlist_score)
                if it > 0 and count % (num_iterations / 10) == 0:
                    temperature /= 2

                # Randomly generate a new "input vector" by modifying each of the gates in the circuit

                # For each gate in the circuit
                for gate in netlist_parser.gates:
                    
                    current_name = gate.name
                    current_record = file_parser.gate_records[current_name]
                    
                    # Choose the Protein or DNA operation to apply to the gate
                    selected_operation = np.random.randint(low = 0, high = 54)

                    if 0 <= selected_operation <= 5:
                        stretch_factor = np.random.uniform(low = 0.05, high = 1.5)
                        current_record.stretch(stretch_factor)

                    elif 6 <= selected_operation <= 11:
                        slope_increase_factor = np.random.uniform(low = 0.05, high = 1.05)
                        current_record.increase_slope(slope_increase_factor)

                    elif 12 <= selected_operation <= 17:
                        slope_decrease_factor = np.random.uniform(low = 0.05, high = 1.05)
                        current_record.decrease_slope(slope_decrease_factor)

                    elif 18 <= selected_operation <= 26:
                        promoter_strength_increase = np.random.uniform(low = 1.0, high = 2.0)
                        current_record.stronger_promoter(promoter_strength_increase)
                    
                    elif 27 <= selected_operation <= 35:
                        promoter_strength_decrease = np.random.uniform(low = 1.0, high = 2.0)
                        current_record.weaker_promoter(promoter_strength_decrease)

                    elif 36 <= selected_operation <= 44:
                        rbs_strength_increase = np.random.uniform(low = 1.0, high = 2.0)
                        current_record.strong_rbs(rbs_strength_increase)

                    elif 45 <= selected_operation <= 53:
                        rbs_strength_decrease = np.random.uniform(low = 1.0, high = 2.0)
                        current_record.weaker_rbs(rbs_strength_decrease)

                # Repopulate the circuit
                netlist_parser.populate_response_functions(file_parser.gate_records)

                # Rerun the circuit at the genetic level
                netlist_parser.run_circuit_genetic()
    
                # Calculate the updated score
                netlist_parser.calculate_score()
                updated_netlist_score = netlist_parser.circuit_score

                # If the updated score was an improvement, accepted the parameter change
                if updated_netlist_score > netlist_score:
                    netlist_score = updated_netlist_score
                    best_gates = netlist_parser.gates

                # Else we will accept with certain probability
                else:
                    cost_diff = netlist_score - updated_netlist_score
                    accept_prob = np.random.uniform(low = 0.0, high = 1.0)
                
                if np.exp(-1 * cost_diff / temperature) > accept_prob:
                    netlist_score = updated_netlist_score
                    best_gates = netlist_parser.gates
                count += 1

            cello_score = res.circuit_score
            
            print("CELLO SCORE: %lf" % cello_score)
            print("ANNEALING SCORE: %lf" % netlist_score)

            print("BEST GATES: ")
            print(type(best_gates[0]))
            #for gate in best_gates:
            #    gate.

            if res.circuit_score > best_score:
                best_score = res.circuit_score
                best_chassis = chassis_name
                best_input_signals = signal_set
        except:
            pass
        q.reset_input_signals()

    print('-----')
    print(f'Best Score: {best_score}')
    print(f'Best Chassis: {best_chassis}')
    print(f'Best Input Signals: {best_input_signals}')

    # Step 4: Run optimization algorithm

    # OPTIMIZATION GOES HERE
    

    # Step 5: Run Cello again
'''

if __name__ == '__main__':
    main()