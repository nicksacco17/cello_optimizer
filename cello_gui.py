import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import copy
import time
from circuit_netlist_parser import Netlist_Parser
from itertools import combinations
from util import parse_verilog
from shutil import copyfile
from PIL import ImageTk, Image
import os

# This is our custom module for parsing JSONs related to Cello
from input_processor import Input_Processor
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

    def parse_files(self):
        self.file_processor = Input_Processor(input_folder_path = self.input_path, chassis_name = self.chassis, working_directory = self.IN_DIR)
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

    def approve_params(self):
        self.mod_path = tk.filedialog.askopenfilename(initialdir = self.input_folder_path, title = "Select file", filetypes = (("json files", "*.JSON"), ("all files", "*.*")))
        self.approve_entry.delete(0, tk.END)
        self.approve_entry.insert(0, self.mod_path)

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

        num_signal_combinations = len(signal_pairing)
        local_progress = 0

        for signal_set in signal_pairing:
            signal_set = list(signal_set)

            print("SIGNAL SET: " + str(signal_set))

            q.set_input_signals(signal_set)

            start_time = time.time()
            q.get_results()
            stop_time = time.time()
            print("GET RESULTS TOTAL TIME = %lf" % (stop_time - start_time))

            try:
                # Get results of the Cello query (most important: Scoring and Netlist)
                res = CelloResult(results_dir = self.OUT_DIR)
                local_progress += int(100 / num_signal_combinations)
                self.cello_progress_num.set(local_progress)
                self.update_idletasks()
                print("PART NAMES: " + str(res.part_names))
                #print("REPRESSOR SCORES: " + str(res.repressor_scores))
                print("CIRCUIT SCORES: " + str(res.circuit_score))

                # Select the output netlist
                circuit_netlist_json = self.OUT_DIR + verilog_name.replace(".v", "") + "_outputNetlist.json"
                #circuit_netlist_png = self.OUT_DIR + verilog_name.replace(".v", "") + "_gate_export.png"

                # Canvas

                #self.schematic.img = tk.PhotoImage(file = circuit_netlist_png)

                #self.circuit_schematic = ImageTk.PhotoImage(Image.open(circuit_netlist_png))
                #self.circuit_schematic_label = tk.Label(self.circuit_schematic)
                #self.circuit_schematic_label.grid(row = 0, column = 10)

                #self.circuit_schematic_canvas = tk.Canvas(self, bg = 'white', width = 300, height = 300)
                #schematic = self.circuit_schematic_canvas.create_image(150, 150, image = circuit_netlist_png)

                #self.circuit_schematic_canvas.grid(row = 0, column = 10)
                #self.update_idletasks()

                # Create the parser module
                netlist_parser = Netlist_Parser(circuit_netlist_json)
                netlist_parser.print()

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
                print("NETLIST SCORE = %lf" % netlist_score)

                if res.circuit_score > best_score:
                    best_score = res.circuit_score
                    best_chassis = self.chassis
                    best_input_signals = signal_set
            except:
                pass
            q.reset_input_signals()
            
        print('-----')
        print(f'Best Score: {best_score}')
        print(f'Best Chassis: {best_chassis}')
        print(f'Best Input Signals: {best_input_signals}')

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
        self.approve_changes_button = tk.Button(self, text = "APPROVE CHANGES", padx = 5, pady = 5, command = self.approve_params)
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
        self.run_button.grid(row = 6, column = 0)
        self.print_param_button.grid(row = 7, column = 3)
        self.submit_param_button.grid(row = 7, column = 4)
        self.approve_changes_button.grid(row = 8, column = 0)
        self.working_dir_button.grid(row = 9, column = 0)
        self.submit_chassis_button.grid(row = 10, column = 0)
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
        self.approve_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.workdir_entry = tk.Entry(self, width = 75, borderwidth = 5)
        self.chassis_entry = tk.Entry(self, width = 75, borderwidth = 5)

        # Entry Positioning
        self.folder_entry.grid(row = 0, column = 1, padx = 10, pady = 10)
        self.input_entry.grid(row = 1, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.output_entry.grid(row = 2, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.ucf_entry.grid(row = 3, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.options_entry.grid(row = 4, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.verilog_entry.grid(row = 5, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.approve_entry.grid(row = 8, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.workdir_entry.grid(row = 9, column = 1, columnspan = 3, padx = 10, pady = 10)
        self.chassis_entry.grid(row = 10, column = 1, columnspan = 3, padx = 10, pady = 10)

        options_input = ["Input signals will go here..."]
        options_gate = ["Gates will go here..."]

        self.clicked_input = tk.StringVar(self)
        self.clicked_input.set("Input signals will go here...")
        self.clicked_gate = tk.StringVar(self)
        self.clicked_gate.set("Gates will go here...")

        self.possible_inputs = tk.OptionMenu(self, self.clicked_input, *options_input)
        self.possible_inputs.grid(row = 6, column = 1)

        self.possible_gates = tk.OptionMenu(self, self.clicked_gate, *options_gate)
        self.possible_gates.grid(row = 6, column = 2)

        self.input_param_textbox = tk.Text(self, width = 30, height = 20)
        self.input_param_textbox.grid(row = 6, column = 3)

        self.gate_param_textbox = tk.Text(self, width = 30, height = 20)
        self.gate_param_textbox.grid(row = 6, column = 4)

        #self.schematic = tk.Label(self)
        #self.schematic.grid(row = 0, column = 5, columnspan = 3, padx = 10, pady = 10)

        self.optimization_flag = tk.IntVar()
        self.optimize_checkbox = tk.Checkbutton(self, text = "Enable Optimization via Simulated Annealing?", variable = self.optimization_flag, onvalue = 1, offvalue = 0, height = 5, width = 75)
        self.optimize_checkbox.grid(row = 11, column = 1, columnspan = 1, padx = 10, pady = 10)

if __name__ == '__main__':
    root = tk.Tk()
    app = CelloGUI(master = root, load = "DEFAULT")
    app.master.title("Genetic Circuit GUI")
    app.master.maxsize(1750, 1000)
    app.master.geometry("1750x1000")
    app.mainloop()
