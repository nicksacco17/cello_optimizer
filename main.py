
from input_processor import Input_Processor
from circuit_netlist_parser import Netlist_Parser
from celloapi2 import CelloQuery, CelloResult
from itertools import combinations
from shutil import copyfile
import time

WORKING_DIR = "D:\\CSBE\\"
IN_DIR = WORKING_DIR + "cello_in\\"
OUT_DIR = WORKING_DIR + "cello_out\\"

FILEPATH = "D:\\CSBE\\DEVICE_FS\\input\\"

VERILOG_FILEPATH = "D:\\CSBE\\DEVICE_FS\\input\\verilog_files\\"
VERILOG_FILENAME = "and.v"

VERILOG_FILE = VERILOG_FILEPATH + VERILOG_FILENAME

#OUTPUT_DIR = "D:\\CSBE\\DEVICE_FS\\input\\OUTDIR\\"

def pause_program(flag):
    if flag:
        input("Press Enter to continue...")

PAUSE_FLAG = True

def parse_verilog(input_file):

    f = open(input_file)
    data = f.readlines()
    f.close()
    
    arg_found = False

    arg_list = []
    for line in data:
        if "(" in line:
            arg_found = True
            arg_list.append(line)
        if arg_found and line not in arg_list:
            arg_list.append(line)
        if ")" in line:
            arg_found = False
            break

    parsed_arg_list = []

    if len(arg_list) == 1:
        arg_string = arg_list[0]
        arg_list = arg_string.split()
        
        for token in arg_list:
            if "module" in token:
                continue
            if "input" in token or "output" in token:
                continue
            else:
                new_token = token.replace(",", "")
                new_token = new_token.replace("(", "")
                new_token = new_token.replace(")", "")
                new_token = new_token.replace(";", "")
                parsed_arg_list.append(new_token)

    else:
        for token in arg_list:
            if "(" in token or ")" in token:
                continue
            else:
                new_token = token.replace(",", "")
                new_token = new_token.replace(" ", "")
                new_token = new_token.replace("\n", "")
                parsed_arg_list.append(new_token)

    num_inputs = len(parsed_arg_list) - 1
    print(parsed_arg_list)
    print("NUM INPUTS = %d" % num_inputs)
    return num_inputs
        
def main():

    best_score = 0
    best_chassis = None
    best_input_signals = None

    chassis = "Eco1C2G2T2"

    # Step 1: Parse the input files of the specified chassis
    #print(FILEPATH)
    file_parser = Input_Processor(FILEPATH, chassis, WORK_DIR = IN_DIR)
    file_parser.parse_input()
    file_parser.parse_ucf()
    file_parser.parse_output()

    # Step 2: Calculate the number of input signals from the input Verilog file
    signal_input = parse_verilog(VERILOG_FILE)
    copyfile(VERILOG_FILE, IN_DIR + VERILOG_FILENAME)

    #print(file_parser.circuit_input_filename)
    #print(file_parser.circuit_output_filename)
    #print(file_parser.circuit_constraint_filename)
    #print(file_parser.input_folder_path)
    #print(file_parser.options_filename)

    # Step 3: Run Cello once to get a baseline
    #start_time = time.time()
    #q = CelloQuery(
    #        input_directory = IN_DIR, 
    #        output_directory = OUT_DIR, 
    #        verilog_file = VERILOG_FILENAME, 
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

    #for signal_set in signal_pairing:
    #    signal_set = list(signal_set)

    #    print("SIGNAL SET: " + str(signal_set))

    #    q.set_input_signals(signal_set)

    #    start_time = time.time()
    #    q.get_results()
    #    stop_time = time.time()
    #    print("TOTAL TIME = %lf" % (stop_time - start_time))

    #    try:
    #        res = CelloResult(results_dir = OUT_DIR)
    #        print("PART NAMES: " + str(res.part_names))
            #print("REPRESSOR SCORES: " + str(res.repressor_scores))
    #        print("CIRCUIT SCORES: " + str(res.circuit_score))

    #        circuit_netlist_json = OUT_DIR + VERILOG_FILENAME.replace(".v", "") + "_outputNetlist.json"

    #        netlist_parser = Netlist_Parser(circuit_netlist_json)
    #        netlist_parser.print()
    #        netlist_parser.parse_netlist(cleanup = True)
    #        netlist_parser.populate_input_values(file_parser.input_records)
    #        netlist_parser.populate_response_functions(file_parser.gate_records)
    #        netlist_parser.populate_output_converters(file_parser.output_records)
    
    #        netlist_parser.run_circuit_logical()
    #        netlist_parser.run_circuit_genetic()
    #        netlist_parser.print_names()
    #        netlist_parser.calculate_score()

    #        if res.circuit_score > best_score:
    #            best_score = res.circuit_score
    #            best_chassis = chassis
    #            best_input_signals = signal_set
    #    except:
    #        pass
    #    q.reset_input_signals()
    #print('-----')
    #print(f'Best Score: {best_score}')
    #print(f'Best Chassis: {best_chassis}')
    #print(f'Best Input Signals: {best_input_signals}')

    # Step 4: Run optimization algorithm

    # OPTIMIZATION GOES HERE
    

    # Step 5: Run Cello again


if __name__ == '__main__':
    main()