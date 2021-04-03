# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: cello_gui.py
# Description:  Accompanying Cello Genetic Circuit Optimization GUI.  Built
#               using the Tkinter module in Python.  Some good resources that
#               were especially helpful were the tutorial series by Codemy
#               (https://youtu.be/YXPyB4XeYLA) and the tutorial from 
#               (https://coderslegacy.com/python/python-gui/).  Highly recommend
#               these two resources for starting w/ basic GUI development.
# Status:   Mostly operational, provided the user follows the documentation.
#           There could be some edge cases where the program collapses in on
#           itself, but they shouldn't appear during standard operation.  That
#           should be fixed in future iterations of the application.  Also, the
#           code is quite cumbersome, which seems to be par for the course using
#           Tkinter - there are just so many moving parts here, it's a little
#           difficult to encapsulate and modularize.
# ------------------------------------------------------------------------------

import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import copy
import time
import numpy as np
from circuit_netlist_parser import Netlist_Parser
from itertools import combinations
from util import parse_verilog
from shutil import copyfile
import os

# This is our custom module for parsing JSONs related to Cello
from input_processor import Input_Processor
from record import Repressor_Record
from celloapi2 import CelloQuery, CelloResult

class CelloGUI(tk.Frame):

    def __init__(self, master = None, load = None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.input_path = "IN"
        self.output_path = "OUT"
        self.ucf_path = "UCF"
        self.mod_path = "MOD"
        self.mod_file = "MOD"
        self.input_folder_path = "/"

        if load == "DEFAULT":
            self.input_folder_path = "D:\\CSBE\\DEVICE_FS\\"
            self.input_path = "D:\\CSBE\\DEVICE_FS\\input\\Eco1C1G1T1\\"
            #self.input_path = "D:\\CSBE\\DEVICE_FS\\input\\Eco1C1G1T1\\Eco1C1G1T1.input.json"
            self.output_path = "D:\\CSBE\\DEVICE_FS\\input\\Eco1C1G1T1\\Eco1C1G1T1.output.json"
            self.ucf_path = "D:\\CSBE\\DEVICE_FS\\input\\Eco1C1G1T1\\Eco1C1G1T1.ucf.json"
            self.options_path = "D:\\CSBE\\DEVICE_FS\\input\\Eco1C1G1T1\\options.csv"
            self.verilog_path = "D:\\CSBE\\DEVICE_FS\\input\\verilog_files\\and.v"
            self.work_dir = "D:\\CSBE\\"

            self.IN_DIR = self.work_dir + "cello_in\\"
            self.OUT_DIR = self.work_dir + "cello_out\\"

            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.input_folder_path)

            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.input_path)

            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_path)

            self.ucf_entry.delete(0, tk.END)
            self.ucf_entry.insert(0, self.ucf_path)

            self.options_entry.delete(0, tk.END)
            self.options_entry.insert(0, self.options_path)

            self.verilog_entry.delete(0, tk.END)
            self.verilog_entry.insert(0, self.verilog_path)

            self.workdir_entry.delete(0, tk.END)
            self.workdir_entry.insert(0, self.work_dir)

    def get_input_folder(self):
        self.input_folder_path = tk.filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.input_folder_path)

    def get_input_json(self):
        self.input_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("json files", "*.JSON"), ("all files", "*.*")))
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.input_path)
        
    def get_output_json(self):
        self.output_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("json files", "*.JSON"), ("all files", "*.*")))
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output_path)

    def get_ucf_json(self):
        self.ucf_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("json files", "*.JSON"), ("all files", "*.*")))
        self.ucf_entry.delete(0, tk.END)
        self.ucf_entry.insert(0, self.ucf_path)

    def get_options(self):
        self.options_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("csv files", "*.CSV"), ("all files", "*.*")))
        self.options_entry.delete(0, tk.END)
        self.options_entry.insert(0, self.options_path)

    def get_verilog(self):
        self.verilog_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("verilog files", "*.v"), ("all files", "*.*")))
        self.verilog_entry.delete(0, tk.END)
        self.verilog_entry.insert(0, self.verilog_path)

    def get_workdir(self):
        self.work_dir = tk.filedialog.askdirectory()
        self.workdir_entry.delete(0, tk.END)
        self.workdir_entry.insert(0, self.work_dir)
        self.IN_DIR = self.work_dir + "\\cello_in\\"
        self.OUT_DIR = self.work_dir + "\\cello_out\\"

    def parse_files(self):
        self.file_processor = Input_Processor(input_folder_path = self.input_path, chassis_name = self.chassis, 
                                                input_file = self.input_path, output_file = self.output_path, 
                                                constraint_file = self.ucf_path, options_file = self.options_path, 
                                                working_directory = self.IN_DIR)
        self.file_processor.parse_input()
        self.file_processor.parse_ucf()
        self.file_processor.parse_output()

        menu = self.possible_inputs["menu"]
        menu.delete(0, tk.END)
        
        for potential_input_signal in self.file_processor.input_records.keys():
            menu.add_command(label = potential_input_signal, command = lambda value = potential_input_signal: self.clicked_input.set(value))

        menu = self.possible_gates["menu"]
        menu.delete(0, tk.END)

        for potential_gate in self.file_processor.gate_records.keys():
            menu.add_command(label = potential_gate, command = lambda value = potential_gate: self.clicked_gate.set(value))
        
    def print_params(self):
        self.input_param_textbox.delete(1.0, tk.END)
        name = self.clicked_input.get()
        if name != "Input signals will go here...":
            current_record = self.file_processor.input_records[name]
            self.input_param_textbox.insert(1.0, "Name: " + str(current_record.name) + "\n")
            self.input_param_textbox.insert(2.0, "ymax = " + str(current_record.ymax) + "\n")
            self.input_param_textbox.insert(3.0, "ymin = " + str(current_record.ymin) + "\n")
            self.input_param_textbox.insert(4.0, "alpha = " + str(current_record.alpha) + "\n")
            self.input_param_textbox.insert(5.0, "beta = " + str(current_record.beta) + "\n")

            self.input_param_textbox.insert(6.0, "------------------------------\n")
            self.input_param_textbox.insert(7.0, "New ymax = \n")
            self.input_param_textbox.insert(8.0, "New ymin = \n")
            self.input_param_textbox.insert(9.0, "New alpha = \n")
            self.input_param_textbox.insert(10.0, "New beta = \n")

        self.gate_param_textbox.delete(1.0, tk.END)
        name = self.clicked_gate.get()
        if name != "Gates will go here...":
            current_record = self.file_processor.gate_records[name]

            self.gate_param_textbox.insert(1.0, "Name: " + str(current_record.name) + "\n")
            self.gate_param_textbox.insert(2.0, "ymax = " + str(current_record.ymax) + "\n")
            self.gate_param_textbox.insert(3.0, "ymin = " + str(current_record.ymin) + "\n")
            self.gate_param_textbox.insert(4.0, "alpha = " + str(current_record.alpha) + "\n")
            self.gate_param_textbox.insert(5.0, "beta = " + str(current_record.beta) + "\n")
            self.gate_param_textbox.insert(6.0, "K = " + str(current_record.K) + "\n")
            self.gate_param_textbox.insert(7.0, "n = " + str(current_record.n) + "\n")

            self.gate_param_textbox.insert(8.0, "------------------------------\n")
            self.gate_param_textbox.insert(9.0, "New ymax = \n")
            self.gate_param_textbox.insert(10.0, "New ymin = \n")
            self.gate_param_textbox.insert(11.0, "New alpha = \n")
            self.gate_param_textbox.insert(12.0, "New beta = \n")
            self.gate_param_textbox.insert(13.0, "New K = \n")
            self.gate_param_textbox.insert(14.0, "New n = \n")

    def submit_params(self):
        
        new_input_params = [entry.strip("Newyminymaxalphabeta =") for entry in self.input_param_textbox.get(7.0, "end - 1 lines").split('\n')]
        new_input_params = new_input_params[0:-1]
        input_signal_name = (self.input_param_textbox.get(1.0, "1.0 lineend").split('\n'))[0][6:]

        new_gate_params = [entry.strip("NewyminymaxalphabetaKn =") for entry in self.gate_param_textbox.get(9.0, "end - 1 lines").split('\n')]
        new_gate_params = new_gate_params[0:-1]
        gate_name = (self.gate_param_textbox.get(1.0, "1.0 lineend").split('\n'))[0][6:]

        # Update the input signal parameters
        update_flag = True
        for entry in new_input_params:
            if not entry:
                update_flag = False
                break
        if update_flag:
            new_input_param_dict = dict(zip(["ymax", "ymin", "alpha", "beta"], [float(x) for x in new_input_params]))
            self.file_processor.input_records[input_signal_name].load_params(new_input_param_dict)

        # Update the gate parameters
        update_flag = True
        for entry in new_gate_params:
            if not entry:
                update_flag = False
                break
        if update_flag:
            new_gate_param_dict = dict(zip(["ymax", "ymin", "alpha", "beta", "K", "n"], [float(x) for x in new_gate_params]))
            self.file_processor.gate_records[gate_name].load_params(new_gate_param_dict)

        self.file_processor.save_input()
        self.file_processor.save_ucf()

    def approve_params(self):
               
        # Step 6: Save the best parameters to the UCF file

        # Overwrite the parameters in the file processor
        for gate_name, gate_obj in self.best_annealing_design.items():
            self.file_processor.gate_records[gate_name].populate_params(ymax = gate_obj.ymax, ymin = gate_obj.ymin, K = gate_obj.K, n = gate_obj.n)

        # Save the parameters to the UCF
        self.file_processor.save_ucf()

        # And print the path to the modified file!
        self.output_results_textbox.insert(7.0, "YOUR FILE IS " +  self.file_processor.working_circuit_constraint_file + "\n")
    

    def submit_chassis(self):
        self.chassis = self.chassis_entry.get()

    def run_cello(self):

        opt_flag = self.optimization_flag.get()

        verilog_name = os.path.split(self.verilog_path)[1]
        
        signal_input = parse_verilog(self.verilog_path)
        copyfile(self.verilog_path, self.IN_DIR + verilog_name)

        q = CelloQuery(input_directory = self.IN_DIR, 
            output_directory = self.OUT_DIR, 
            verilog_file = verilog_name, 
            compiler_options = self.file_processor.options_filename, 
            input_ucf = self.file_processor.circuit_constraint_filename, 
            input_sensors = self.file_processor.circuit_input_filename, 
            output_device = self.file_processor.circuit_output_filename)

        signals = q.get_input_signals()
        signal_pairing = list(combinations(signals, signal_input))

        print("SIGNALS: " + str(signals))
        print("SIGNAL PAIRING: " + str(signal_pairing))

        self.best_cello_score = 0
        self.best_cello_design = None
        self.best_cello_inputs = None

        self.best_annealing_score = 0
        self.best_annealing_design = None
        self.best_annealing_inputs = None

        num_signal_combinations = len(signal_pairing)
        local_progress = 0

        for signal_set in signal_pairing:
            signal_set = list(signal_set)

            q.set_input_signals(signal_set)

            q.get_results()

            try:
                # Get results of the Cello query (most important: Scoring and Netlist)
                res = CelloResult(results_dir = self.OUT_DIR)

                cello_circuit = res.part_names
                cello_score = res.circuit_score

                local_progress += int(100 / num_signal_combinations)
                self.cello_progress_num.set(local_progress)
                self.update_idletasks()

                # Select the output netlist
                circuit_netlist_json = self.OUT_DIR + verilog_name.replace(".v", "") + "_outputNetlist.json"
               
                # Create the parser module
                netlist_parser = Netlist_Parser(circuit_netlist_json)

                # Cleanup the netlist JSON (Not needed if the _outputNetlist.json file is correctly formatted)
                netlist_parser.parse_netlist(cleanup = True)

                # Populate the reconstructed circuit with the parameters from the input JSONs (input, UCF, output)
                netlist_parser.populate_input_values(self.file_processor.input_records)
                netlist_parser.populate_response_functions(self.file_processor.gate_records)
                netlist_parser.populate_output_converters(self.file_processor.output_records)
        
                # Now run the logic generator and the genetic generator - first assume it is digital circuit,
                # compute what the outputs should be.  Next run it like actual genetic circuit using response 
                # functions for each gate.
                netlist_parser.run_circuit_logical()
                netlist_parser.run_circuit_genetic()
        
                # Calculate the score
                netlist_parser.calculate_score()
                netlist_parser.print_genetric_truth_table()
                netlist_score = netlist_parser.circuit_score
                #print("NETLIST SCORE = %lf" % netlist_score)

                # Step 5: begin the simulated annealing on the gates in the circuit

                # Set the starting temperature to 20% of the starting score
                if opt_flag:
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

                if cello_score > self.best_cello_score:
                    self.best_cello_score = cello_score
                    self.best_cello_inputs = signal_set
                    self.best_cello_design = cello_circuit

                if netlist_score > self.best_annealing_score:
                    self.best_annealing_score = netlist_score
                    self.best_annealing_inputs = signal_set
                    self.best_annealing_design = best_gates

            except:
                pass
            q.reset_input_signals()
                        
    def print_opt_results(self):
        
        self.output_results_textbox.delete(1.0, tk.END)
        self.output_results_textbox.insert(1.0, "BEST CELLO SCORE = %lf\n" % self.best_cello_score)
        self.output_results_textbox.insert(2.0, "BEST CELLO INPUTS = " + str(self.best_cello_inputs) + "\n")
        self.output_results_textbox.insert(3.0, "BEST CELLO DESIGN = " + str(self.best_cello_design) + "\n")
        self.output_results_textbox.insert(4.0, "BEST ANNEALING SCORE = %lf\n" % self.best_annealing_score)
        self.output_results_textbox.insert(5.0, "BEST ANNEALING INPUTS = " + str(self.best_annealing_inputs) + "\n")
        gate_in_circuit_str = ""
        for gate_name, record_obj in self.best_annealing_design.items():
            gate_in_circuit_str += gate_name + ", "
        self.output_results_textbox.insert(6.0, "BEST ANNEALING DESIGN = " + gate_in_circuit_str + "\n")

    def create_widgets(self):

        # Button Declaration
        self.folder_button = tk.Button(self, text = "INPUT FOLDER", padx = 5, pady = 5, command = self.get_input_folder)
        self.input_json_button = tk.Button(self, text = "INPUT JSON", padx = 5, pady = 5, command = self.get_input_json)
        self.output_json_button = tk.Button(self, text = "OUTPUT JSON", padx = 5, pady = 5, command = self.get_output_json)
        self.ucf_json_button = tk.Button(self, text = "UCF JSON", padx = 5, pady = 5, command = self.get_ucf_json)
        self.options_button = tk.Button(self, text = "OPTIONS", padx = 5, pady = 5, command = self.get_options)
        self.verilog_button = tk.Button(self, text = "VERILOG", padx = 5, pady = 5, command = self.get_verilog)
        self.working_dir_button = tk.Button(self, text = "WORKING DIRECTORY", padx = 5, pady = 5, command = self.get_workdir)
        self.run_button = tk.Button(self, text = "Generate Inputs and Gates", padx = 5, pady = 5, command = self.parse_files)
        self.print_param_button = tk.Button(self, text = "Print Parameters", padx = 5, pady = 5, command = self.print_params)
        self.submit_param_button = tk.Button(self, text = "Save Parameters", padx = 5, pady = 5, command = self.submit_params)
        self.print_optimization_output_button = tk.Button(self, text = "Print Opt. Results", padx = 5, pady = 5, command = self.print_opt_results)
        self.approve_changes_button = tk.Button(self, text = "Approve Changes", padx = 5, pady = 5, command = self.approve_params)
        self.submit_chassis_button = tk.Button(self, text = "Submit Chassis", padx = 5, pady = 5, command = self.submit_chassis)
        self.run_cello_button = tk.Button(self, text = "Run Cello!", padx = 5, pady = 5, command = self.run_cello)
        self.cello_progress_num = tk.DoubleVar()
        self.cello_progress_bar = ttk.Progressbar(self, orient = tk.HORIZONTAL, length = 300, mode = 'determinate', variable = self.cello_progress_num, maximum = 100)
        self.quit_button = tk.Button(self, text = "Quit", padx = 5, pady = 5, command = self.quit)
        
        # Button Positioning
        self.folder_button.grid(row = 0, column = 0)
        self.input_json_button.grid(row = 1, column = 0)
        self.output_json_button.grid(row = 2, column = 0)
        self.ucf_json_button.grid(row = 3, column = 0)
        self.options_button.grid(row = 4, column = 0)
        self.verilog_button.grid(row = 5, column = 0)
        self.run_button.grid(row = 0, column = 2)
        self.print_param_button.grid(row = 7, column = 2)
        self.submit_param_button.grid(row = 7, column = 3)
        self.print_optimization_output_button.grid(row = 7, column = 4)
        self.approve_changes_button.grid(row = 8, column = 4)
        self.working_dir_button.grid(row = 6, column = 0)
        self.submit_chassis_button.grid(row = 7, column = 0)
        self.run_cello_button.grid(row = 11, column = 0)
        self.quit_button.grid(row = 12, column = 0)
        self.cello_progress_bar.grid(row = 11, column = 2)

        # Entry Declaration
        self.folder_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.input_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.output_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.ucf_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.options_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.verilog_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.workdir_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.chassis_entry = tk.Entry(self, width = 75, borderwidth = 5)

        # Entry Positioning
        self.folder_entry.grid(row = 0, column = 1, padx = 10, pady = 10)
        self.input_entry.grid(row = 1, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.output_entry.grid(row = 2, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.ucf_entry.grid(row = 3, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.options_entry.grid(row = 4, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.verilog_entry.grid(row = 5, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.workdir_entry.grid(row = 6, column = 1, columnspan = 1, padx = 10, pady = 10)
        self.chassis_entry.grid(row = 7, column = 1, columnspan = 1, padx = 10, pady = 10)

        # Miscellaneous declaration and positioning
        options_input = ["Input signals will go here..."]
        options_gate = ["Gates will go here..."]

        self.clicked_input = tk.StringVar(self)
        self.clicked_input.set("Input signals will go here...")
        self.clicked_gate = tk.StringVar(self)
        self.clicked_gate.set("Gates will go here...")

        self.possible_inputs = tk.OptionMenu(self, self.clicked_input, *options_input)
        self.possible_inputs.grid(row = 1, column = 2)

        self.possible_gates = tk.OptionMenu(self, self.clicked_gate, *options_gate)
        self.possible_gates.grid(row = 1, column = 3)

        self.input_param_textbox = tk.Text(self, width = 30, height = 20)
        self.input_param_textbox.grid(row = 6, column = 2)

        self.gate_param_textbox = tk.Text(self, width = 30, height = 20)
        self.gate_param_textbox.grid(row = 6, column = 3)

        self.output_results_textbox = tk.Text(self, width = 50, height = 20)
        self.output_results_textbox.grid(row = 6, column = 4)

        self.optimization_flag = tk.IntVar()
        self.optimize_checkbox = tk.Checkbutton(self, text = "Enable Optimization via Simulated Annealing?", variable = self.optimization_flag, onvalue = 1, offvalue = 0, height = 5, width = 75)
        self.optimize_checkbox.grid(row = 11, column = 1, columnspan = 1, padx = 10, pady = 10)

if __name__ == '__main__':
    root = tk.Tk()
    app = CelloGUI(master = root)
    app.master.title("Genetic Circuit GUI")
    app.master.maxsize(1750, 1000)
    app.master.geometry("1750x1000")
    app.mainloop()
