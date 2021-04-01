
import json
import record as rec
from shutil import copyfile

FILEPATH = "D:\\CSBE\\DEVICE_FS\\input\\"

class Input_Processor():

    def __init__(self, input_folder_path = None, chassis_name = None, input_file = None, output_file = None, constraint_file = None, options_file = None, WORK_DIR = None):

        # If the user just provides a folder path and the name of the chassis
        if input_folder_path is not None and chassis_name is not None:

            self.input_folder_path = input_folder_path + "\\" + chassis_name + "\\"
            self.chassis_name = chassis_name

            self.circuit_input_file = self.input_folder_path + self.chassis_name + ".input.json"
            self.circuit_output_file = self.input_folder_path + self.chassis_name + ".output.json"
            self.circuit_constraint_file = self.input_folder_path + self.chassis_name + ".UCF.json"
            self.options_file = self.input_folder_path + "\\options.csv"

        # Else the user specified ALL the paths
        elif input_file is not None and output_file is not None and constraint_file is not None and options_file is not None:
            self.circuit_input_file = input_file
            self.circuit_output_file = output_file
            self.circuit_constraint_file = constraint_file
            self.options_file = options_file

            self.input_folder_path = input_folder_path
            self.chassis_name = "ORGANISM"

        # Now make copies of all the files for modification processes
        self.circuit_input_file_COPY = self.input_folder_path + self.chassis_name + "_TEMP" + ".input.json"
        self.circuit_output_file_COPY  = self.input_folder_path + self.chassis_name + "_TEMP" + ".output.json"
        self.circuit_constraint_file_COPY  = self.input_folder_path + self.chassis_name + "_TEMP" + ".UCF.json"

        copyfile(self.circuit_input_file, self.circuit_input_file_COPY)
        copyfile(self.circuit_output_file, self.circuit_output_file_COPY)
        copyfile(self.circuit_constraint_file, self.circuit_constraint_file_COPY)

        # Turns out we also need just the file name without the path...
        self.circuit_input_filename = self.chassis_name + ".input.json"
        self.circuit_output_filename = self.chassis_name + ".output.json"
        self.circuit_constraint_filename = self.chassis_name + ".UCF.json"
        self.options_filename = "options.csv"

        self.work_dir = WORK_DIR

        # Copy all the files to the working directory
        copyfile(self.circuit_input_file, self.work_dir + self.circuit_input_filename)
        copyfile(self.circuit_output_file, self.work_dir + self.circuit_output_filename)
        copyfile(self.circuit_constraint_file, self.work_dir + self.circuit_constraint_filename)
        copyfile(self.options_file, self.work_dir + self.options_filename)

        self.input_records = {}
        self.output_records = {}
        self.gate_records = {}

    def print(self):

        print("Chassis name: \t\t\t\t" + self.chassis_name)
        print("Input Folder: \t\t\t\t" + self.input_folder_path)
        print("Circuit input JSON file: \t\t" + self.circuit_input_file)
        print("Circuit output JSON file: \t\t" + self.circuit_output_file)
        print("Circuit constraint JSON file: \t\t" + self.circuit_constraint_file)
        print("Options file: \t\t\t\t" + self.options_file)

    def parse_input(self):

        f = open(self.circuit_input_file)
        data = json.load(f)
        f.close()

        input_records = {}

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
                
        self.input_records = input_records

    def parse_ucf(self):

        f = open(self.circuit_constraint_file)
        data = json.load(f)
        f.close()

        gate_records = {}

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

        self.gate_records = gate_records

    def parse_output(self):

        f = open(self.circuit_output_file)
        data = json.load(f)
        f.close()

        for entry in data:
            
            if entry['collection'] == 'models':
                record = rec.Output_Signal_Record()
                record.name = entry['name'].replace("_model", "")
                record.unit_conversion = entry['parameters'][0]['value']
                if record not in self.output_records:
                    self.output_records[record.name] = record
    

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