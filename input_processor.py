# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: input_processor.py
# Description:  Parses input JSONs (chassis.input, chassis.UCF, chassis.output)
#               for the chassis under study.  Loads all of the pertinent info
#               and parameters into a <Type>_Record object and stores in a list.
#               Much more user-friendly and efficient than repetitive calls to
#               the JSON file.  Supports writing back to files.
# Status:   Fully operational.  Could probably be more efficient with pathing,
#           but that's not the most important part of the module.
# ------------------------------------------------------------------------------

# Imports
import json
import record as rec
from shutil import copyfile

''' 
Class:          Input_Processor
Description:    Basic file processor.  Reads in data from JSON files, builds
                "records" that contain names and parameters of the objects in
                the genetic circuit.  Writes data back to the same JSON files.
'''
class Input_Processor():

    # There are a few different ways of initializing this class, depending on
    # whether or not the GUI application is used.
    def __init__(self, input_folder_path = None, 
                        chassis_name = None, input_file = None, 
                        output_file = None, constraint_file = None, 
                        options_file = None, working_directory = None):

        # If user just provides folder path & name of the chassis (COMMAND LINE)
        if not input_file and not output_file and not constraint_file and not options_file:

            # Get the folder and chassis name
            self.input_folder_path = input_folder_path
            self.chassis_name = chassis_name

            # And build paths to each of the required files in chassis directory
            self.circuit_input_file = self.input_folder_path + self.chassis_name + ".input.json"
            self.circuit_output_file = self.input_folder_path + self.chassis_name + ".output.json"
            self.circuit_constraint_file = self.input_folder_path + self.chassis_name + ".UCF.json"
            self.options_file = self.input_folder_path + "\\options.csv"

        # Else the user specified ALL the paths (GUI APP)
        else:
            self.circuit_input_file = input_file
            self.circuit_output_file = output_file
            self.circuit_constraint_file = constraint_file
            self.options_file = options_file

            self.input_folder_path = input_folder_path
            self.chassis_name = chassis_name

        # We also need just the file name without the path
        self.circuit_input_filename = self.chassis_name + ".input.json"
        self.circuit_output_filename = self.chassis_name + ".output.json"
        self.circuit_constraint_filename = self.chassis_name + ".UCF.json"
        self.options_filename = "options.csv"

        # The working directory is where Cello will read from and store results.
        self.work_dir = working_directory

        # Working Files - Essentially the same files in the chassis directory,
        # but moved to the working directory to preserve the original file
        self.working_circuit_input_file = self.work_dir + self.circuit_input_filename
        self.working_circuit_output_file = self.work_dir + self.circuit_output_filename
        self.working_circuit_constraint_file = self.work_dir + self.circuit_constraint_filename
        self.working_options_file = self.work_dir + self.options_filename

        # Copy all the original files to the working directory - Cello will
        # operate on these entirely NEW files, not the original ones in the
        # chassis directory.
        copyfile(self.circuit_input_file, self.working_circuit_input_file)
        copyfile(self.circuit_output_file, self.working_circuit_output_file)
        copyfile(self.circuit_constraint_file, self.working_circuit_constraint_file)
        copyfile(self.options_file, self.working_options_file)

        # Initialize the empty dictionaries for each record type: Each record
        # will be indexed by name.  EX: self.input_records[gate_name] = gate_obj
        self.input_records = {}
        self.output_records = {}
        self.gate_records = {}

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Print all of the file path information of the parser object
    '''
    def print(self):

        print("Chassis name: \t\t\t\t" + self.chassis_name)
        print("Input Folder: \t\t\t\t" + self.input_folder_path)
        print("Circuit input JSON file: \t\t" + self.circuit_input_file)
        print("Circuit output JSON file: \t\t" + self.circuit_output_file)
        print("Circuit constraint JSON file: \t\t" + self.circuit_constraint_file)
        print("Options file: \t\t\t\t" + self.options_file)
        print("Working Directory: " + self.work_dir)

    '''
    Function:       parse_input
    Args:           None
    Return:         None
    Description:    Process the chassis.input.json file, extracting input sensor
                    records.  Utilizes the Input_Signal_Record class.
    '''
    def parse_input(self):

        # Open the JSON and read in the data - assume it is valid
        f = open(self.circuit_input_file)
        data = json.load(f)
        f.close()

        input_records = {}

        # For each field of JSON data, extract the relevant parameters
        for entry in data:

            if entry['collection'] == 'input_sensors':
                record = rec.Input_Signal_Record()
                record.name = entry['name']
                if record not in input_records:
                    input_records[record.name] = record

            elif entry['collection'] == 'models':
                model_name = entry['name'].replace("_model", "")

                if model_name not in input_records.keys():
                    print("[ERROR]: NOT SURE WHY WE'RE HERE")

                current_record = input_records[model_name]
                current_record.set_params(entry['parameters'])

            elif entry['collection'] == 'structures':
                structure_name = entry['name'].replace("_structure", "")

                if structure_name not in input_records.keys():
                    print("[ERROR]: NOT SURE WHY WE'RE HERE")

                current_record = input_records[structure_name]
                current_record.output = entry['outputs']
        
        # Done - InputProcessor now has all of the input signal records
        self.input_records = input_records

    '''
    Function:       parse_ucf
    Args:           None
    Return:         None
    Description:    Process the chassis.ucf.json file, extracting gate/repressor
                    records.  Utilizes the Repressor_Record class.
    '''
    def parse_ucf(self):

        # Open the JSON and read in the data - assume it is valid
        f = open(self.circuit_constraint_file)
        data = json.load(f)
        f.close()

        gate_records = {}

        # For each field of JSON data, extract the relevant parameters
        for entry in data:

            if entry['collection'] == 'gates':
                record = rec.Repressor_Record()
                record.name = entry['name']
                record.gate_type = entry['gate_type']
                if record not in gate_records:
                    gate_records[record.name] = record

            if entry['collection'] == 'models':
                model_name = entry['name'].replace("_model", "")

                if model_name not in gate_records.keys():
                    print("[ERROR]: NOT SURE WHY WE'RE HERE")

                current_record = gate_records[model_name]
                current_record.set_params(entry['parameters'])

        # Done - InputProcessor now has all of the gate records
        self.gate_records = gate_records

    '''
    Function:       parse_output
    Args:           None
    Return:         None
    Description:    Process the chassis.output.json file, extracting output
                    report records.  Utilizes the Output_Signal_Record class.
    '''
    def parse_output(self):

        # Open the JSON and read in the data - assume it is valid
        f = open(self.circuit_output_file)
        data = json.load(f)
        f.close()

        # For each field of JSON data, extract the relevant parameters
        for entry in data:
            
            if entry['collection'] == 'models':
                record = rec.Output_Signal_Record()
                record.name = entry['name'].replace("_model", "")
                record.unit_conversion = entry['parameters'][0]['value']
                if record not in self.output_records:
                    self.output_records[record.name] = record
    
    '''
    Function:       save_input
    Args:           None
    Return:         None
    Description:    Saves all of the current Input_Signal_Records of the 
                    Input_Processor module to working chassis.input.json file.
    '''
    def save_input(self):
        
        # First, load in the contents of the working input JSON to memory
        f = open(self.working_circuit_input_file)
        data = json.load(f)
        f.close()

        # Then, for each entry in the data array:
        for entry in data:
            
            # If we found a field that corresponds to the input signal info
            if entry['collection'] == 'models':

                model_name = entry['name'].replace("_model", "")

                # Look up the corrsponding record in this module's record list
                current_record = self.input_records[model_name]

                # Get the JSON-formatted parameters of the selected record
                new_formatted_parameters = current_record.get_parameters(entry['parameters'])

                # And write the new parameters to the data array
                entry['parameters'] = new_formatted_parameters

        # Finally, once all parameters have been written to the formatted data
        # array, write the contents of the array BACK to the working input JSON
        f = open(self.working_circuit_input_file, 'w')
        json.dump(data, f, indent = 4)
        f.close()

    '''
    Function:       save_ucf
    Args:           None
    Return:         None
    Description:    Saves all of the current Repressor_Records of the 
                    Input_Processor module to working chassis.ucf.json file.
    '''
    def save_ucf(self):
       
        # First, load in the contents of the working UCF JSON to memory
        f = open(self.working_circuit_constraint_file)
        data = json.load(f)
        f.close()

        # Then, for each entry in the data array:
        for entry in data:

            # If we found a field that corresponds to the gate information
            if entry['collection'] == 'models':

                model_name = entry['name'].replace("_model", "")

                # Look up the corrsponding record in this module's record list
                current_record = self.gate_records[model_name]

                # Get the JSON-formatted parameters of the selected record
                new_formatted_parameters = current_record.get_parameters(entry['parameters'])

                # And write the new parameters to the data array
                entry['parameters'] = new_formatted_parameters

        # Finally, once all parameters have been written to the formatted data
        # array, write the contents of the array BACK to the working UCF JSON
        f = open(self.working_circuit_constraint_file, 'w')
        json.dump(data, f, indent = 4)
        f.close()

def main():
    file_parser = Input_Processor(FILEPATH, "Eco1C1G1T1")
    file_parser.print()
    file_parser.parse_input()
    file_parser.parse_ucf()
    file_parser.parse_output()

    #for record in file_parser.input_records.values():
    #    record.print()

    #for record in file_parser.input_records.keys():
    #    print(record)

    #for record in file_parser.gate_records.keys():
    #    print(record)

if __name__ == '__main__':
    main()