# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: util.py
# Description:  Miscellaneous utility function(s).  Currently just the verilog
#               parser function, which counts the number of inputs in a 
#               verilog file.
# Status:   Fully operational for any "well-behaved" verilog file.
# ------------------------------------------------------------------------------

'''
    Function:       parse_verilog
    Args:           input_file: Path to verilog file
    Return:         num_inputs: Number of signal inputs in the verilog module
    Description:    Returns the number of input signals in the verilog module.
                    Looks for the module(...) phrase and counts the number of
                    tokens within the parentheses.  Assumes each input is 1 bit
                    wide, and there is only one output signal.
    '''
def parse_verilog(input_file):

    # Read in the contents of the file
    f = open(input_file)
    data = f.readlines()
    f.close()
    
    arg_found = False
    arg_list = []

    # Build the list of arguments for all tokens within the first ()
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

    # If only one line, tokenize and append valid tokens (i.e. named signals)
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

    # Else there was a multi-line input, still look for only named signals
    else:
        for token in arg_list:
            if "(" in token or ")" in token:
                continue
            else:
                new_token = token.replace(",", "")
                new_token = new_token.replace(" ", "")
                new_token = new_token.replace("\n", "")
                parsed_arg_list.append(new_token)

    # If there is exactly one output signal in the argument list and there are
    # n arguments, then there must be n - 1 input signals.
    num_inputs = len(parsed_arg_list) - 1
    
    return num_inputs