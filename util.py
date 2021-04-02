
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
    #print(parsed_arg_list)
    #print("NUM INPUTS = %d" % num_inputs)
    return num_inputs