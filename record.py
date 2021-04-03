# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: record.py
# Description:  In-memory "records" corresponding to named fields of parameters
#               from required JSON (chassis.input, chassis.ucf, chassis.output)
#               files.  Three types of records - Input_Signal_Record, 
#               corresponding to the parameters of the input sensors in the
#               chassis.input file, Repressor_Record, corresponding to the
#               parameters of the gates in the chassis.ucf file, and 
#               Output_Signal_Record, corresponding to the parameters of the 
#               output reporter in the chassis.output file.
# Status:   Fully operational.  Could probably use more abstraction and 
#           hierarchy, as there is a lot of duplicate code here, but it works
#           for now.  The DNA/Protein operations are here as well, it might be
#           better if they were moved to another module, but again, it works.
# ------------------------------------------------------------------------------

# Imports
import numpy as np

''' 
Class:          Input_Signal_Record
Description:    Basic record of input sensors.  Contains fields for name, output
                protein(?) if any, and parameters ymax, ymin, alpha, beta.
'''
class Input_Signal_Record():

    def __init__(self):
        self.name = ""
        self.ymax = 0.0
        self.ymin = 0.0
        self.alpha = 0.0
        self.beta = 0.0
        self.output = []
        self.param_list = []

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Print the parameters of the record
    '''
    def print(self):

        print("Name: " + self.name)
        print("ymax = %lf" % (self.ymax))
        print("ymin = %lf" % (self.ymin))
        print("alpha = %lf" % (self.alpha))
        print("beta = %lf" % (self.beta))
        print("Outputs: ")
        for output in self.output:
            print(output)

    '''
    Function:       print_name
    Args:           None
    Return:         None
    Description:    Print the name of the record
    '''
    def print_name(self):
        print(self.name)

    '''
    Function:       get_parameters
    Args:           in_params: Original list of parameters
    Return:         modified_params: Modified list of parameters populated from
                    the contents of the updated record
    Description:    Return a formatted version of the record's parameters.  This
                    function is used in formatting and saving the data to the
                    JSON files.
    '''
    def get_parameters(self, in_params):

        modified_params = in_params

        # For each entry in the input parameters, look for the corresponding
        # parameter (ymax, ymin, alpha, beta).  If found, overwrite with the
        # contents of the record.
        for entry in modified_params:

            if entry['name'] == 'ymax':
                entry['value'] = self.ymax
            elif entry['name'] == 'ymin':
                entry['value'] = self.ymin
            elif entry['name'] == 'alpha':
                entry['value'] = self.alpha
            elif entry['name'] == 'beta':
                entry['value'] = self.beta

        # Return the list of formatted parameters
        return modified_params

    '''
    Function:       set_parameters
    Args:           in_params: List of parameters to load into the record
    Return:         None
    Description:    CODE ONLY.  Sets the parameters of the input signal record
                    from a dictionary of parameters directly parsed from the
                    input JSON file.
    '''
    def set_params(self, in_params):
        self.param_list = in_params

        for param in self.param_list:
            if param['name'] == 'ymax':
                self.ymax = param['value']
            elif param['name'] == 'ymin':
                self.ymin = param['value']
            elif param['name'] == 'alpha':
                self.alpha = param['value']
            elif param['name'] == 'beta':
                self.beta = param['value']

    '''
    Function:       load_parameters
    Args:           in_params: List of parameters to load into the record
    Return:         None
    Description:    GUI ONLY.  Loads in input signal record parameters through
                    the accompanying GUI application.
    '''
    def load_params(self, in_params):

        self.ymax = in_params['ymax']
        self.ymin = in_params['ymin']
        self.alpha = in_params['alpha']
        self.beta = in_params['beta']

    # --------------------- PROTEIN ENGINEERING OPERATIONS ---------------------

    def stretch(self, x):
        if abs(x) <= 1.5:
            self.ymax *= x
            if x != 0:
                self.ymin /= x

    def increase_slope(self, x):
        if abs(x) <= 1.05:
            self.alpha *= x

    def decrease_slope(self, x):
        if abs(x) <= 1.05 and x != 0:
            self.alpha /= x
    # --------------------------------------------------------------------------
    # ----------------------- DNA ENGINEERING OPERATIONS -----------------------

    def stronger_promoter(self, x):
        self.ymax *= x
        self.ymin *= x

    def weaker_promoter(self, x):
        if x != 0:
            self.ymax /= x
            self.ymin /= x

    def strong_rbs(self, x):
        if x != 0:
            self.beta /= x

    def weaker_rbs(self, x):
        self.beta *= x
    # --------------------------------------------------------------------------
    
''' 
Class:          Output_Signal_Record
Description:    Basic record of output reporter.  Contains fields for name and 
                conversion parameter.
'''
class Output_Signal_Record():
    
    def __init__(self):
        self.name = ""
        self.unit_conversion = 0.0

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Print the parameters of the record
    '''
    def print(self):
        print("Name: " + self.name)
        print("Unit Conversion = %lf" % self.unit_conversion)

    '''
    Function:       print_name
    Args:           None
    Return:         None
    Description:    Print the name of the record
    '''
    def print_name(self):
        print(self.name)

    '''
    Function:       load_params
    Args:           in_params: List of parameters to load into the record
    Return:         None
    Description:    CODE ONLY.  Sets the parameters of the output signal record
                    from a dictionary of parameters directly parsed from the
                    input JSON file.
    '''
    def load_params(self, in_params):
        self.unit_conversion = in_params['unit_conversion']


''' 
Class:          Repressor_Record
Description:    Basic record of output reporter.  Contains fields for name and 
                parameters ymax, ymin, K, n, alpha, beta.
'''
class Repressor_Record():

    def __init__(self):
        self.name = ""
        self.ymax = np.float64(0.0)
        self.ymin = np.float64(0.0)
        self.K = np.float64(0.0)
        self.n = np.float64(0.0)
        self.alpha = np.float64(0.0)
        self.beta = np.float64(0.0)
        self.output = []
        self.gate_type = ""
        self.param_list = []

    '''
    Function:       print
    Args:           None
    Return:         None
    Description:    Print the parameters of the record
    '''
    def print(self):

        print("Name: " + self.name)
        print("Gate type: " + self.gate_type)
        print("ymax = %lf" % (self.ymax))
        print("ymin = %lf" % (self.ymin))
        print("K = %lf" % (self.K))
        print("n = %lf" % (self.n))
        print("alpha = %lf" % (self.alpha))
        print("beta = %lf" % (self.beta))
        print("Outputs: ")
        for output in self.output:
            print(output)

    '''
    Function:       get_parameters
    Args:           in_params: Original list of parameters
    Return:         modified_params: Modified list of parameters populated from
                    the contents of the updated record
    Description:    Return a formatted version of the record's parameters.  This
                    function is used in formatting and saving the data to the
                    JSON files.
    '''
    def get_parameters(self, in_params):

        modified_params = in_params

        # For each entry in the gate parameters, look for the corresponding
        # parameter (ymax, ymin, K, n, alpha, beta).  If found, overwrite with 
        # the contents of the record.
        for entry in modified_params:

            if entry['name'] == 'ymax':
                entry['value'] = self.ymax
            elif entry['name'] == 'ymin':
                entry['value'] = self.ymin

            elif entry['name'] == 'K':
                entry['value'] = self.K
            elif entry['name'] == 'n':
                entry['value'] = self.n

            elif entry['name'] == 'alpha':
                entry['value'] = self.alpha
            elif entry['name'] == 'beta':
                entry['value'] = self.beta
        
        # Return the list of formatted parameters
        return modified_params

    '''
    Function:       set_parameters
    Args:           in_params: List of parameters to load into the record
    Return:         None
    Description:    CODE ONLY.  Sets the parameters of the repressor record
                    from a dictionary of parameters directly parsed from the
                    input JSON file.
    '''
    def set_params(self, in_params):
        self.param_list = in_params

        for param in self.param_list:
            if param['name'] == 'ymax':
                self.ymax = param['value']
            elif param['name'] == 'ymin':
                self.ymin = param['value']
            elif param['name'] == 'K':
                self.K = param['value']
            elif param['name'] == 'n':
                self.n = param['value']
            elif param['name'] == 'alpha':
                self.alpha = param['value']
            elif param['name'] == 'beta':
                self.beta = param['value']

    '''
    Function:       load_parameters
    Args:           in_params: List of parameters to load into the record
    Return:         None
    Description:    GUI ONLY.  Loads in repressor record parameters through
                    the accompanying GUI application.
    '''
    def load_params(self, in_params):

        self.ymax = in_params['ymax']
        self.ymin = in_params['ymin']
        self.alpha = in_params['alpha']
        self.beta = in_params['beta']
        self.K = in_params['K']
        self.n = in_params['n']

    '''
    Function:       populate_parameters
    Args:           ymax: Target setting of ymax
                    ymin: Target setting of ymin
                    K: Target setting of K
                    n: Target setting of n
    Return:         None
    Description:    Explicitly sets record's parameters using function arguments
    '''
    def populate_params(self, ymax, ymin, K, n):
        self.ymax = ymax
        self.ymin = ymin
        self.K = K
        self.n = n

    # --------------------- PROTEIN ENGINEERING OPERATIONS ---------------------

    def stretch(self, x):
        if abs(x) <= 1.5:
            self.ymax *= x
            if x != 0:
                self.ymin /= x

    def increase_slope(self, x):
        if abs(x) <= 1.05:
            self.n *= x

    def decrease_slope(self, x):
        if abs(x) <= 1.05 and x != 0:
            self.n /= x

    # --------------------------------------------------------------------------
    # ----------------------- DNA ENGINEERING OPERATIONS -----------------------

    def stronger_promoter(self, x):
        self.ymax *= x
        self.ymin *= x

    def weaker_promoter(self, x):
        if x != 0:
            self.ymax /= x
            self.ymin /= x

    def strong_rbs(self, x):
        if x != 0:
            self.K /= x

    def weaker_rbs(self, x):
        self.K *= x
    # --------------------------------------------------------------------------

    '''
    Function:       modify_repressor
    Args:           num_retries: Number of times the function should attempt
                    to generate a set of valid input parameters
    Return:         None
    Description:    Applies a random protein or DNA operation to the current
                    repressor.  This function is extremely arbitrary and
                    should be the first target for optimization by someone
                    with high levels of expertise w/ Cello and genetic circuits.
                    Essentially, there are two categories of operations -
                    protein operations, which are powerful, but not readily
                    achievable, and DNA operations, which are weaker but more
                    physically meaningful.  This module will randomly choose
                    one of the supported protein operations or DNA operations
                    to apply to the gate.  A protein operation will be selected
                    with probability 1/9, and a DNA operation will be selected
                    with probability 1/6.  There is no good reason why we picked
                    these values - they just seemed like reasonable heuristics
                    to use to demonstrate the overall optimization algorithm
                    functions correctly.  We also restrict the range of valid
                    parameters - again, there is no good reason why we picked 
                    the range of values, other than they seemed to be within the
                    scope of the parameters found in the UCF.json file - it 
                    would absolutely be worth it to determine physically 
                    meaningful parameter ranges to improve the accuracy of this
                    algorithm.  Finally, this algorithm will attempt to modify
                    the repressor until valid parameters are generated - if it
                    cannot generate a valid parameter input, then it will just
                    give up and return control back to the simulated annealing
                    algorithm.  It would be worth spending some time to ensure
                    that valid repressor parameters are generated each time,
                    which could improve the both the accuracy and the speed
                    of the overall simulated annealing algorithm.
    '''
    def modify_repressor(self, num_retries):
        

        valid_state_generated = False

        # These are the acceptable bounds on the parameters, largely found from
        # looking at the values found in the original UCF.json file.  Not sure
        # how meaningful this is, as it seems very artificial.
        YMAX_UPPER_BOUND = 5
        YMIN_LOWER_BOUND = 1e-3
        K_LOWER_BOUND = 1e-3
        K_UPPER_BOUND = 15
        n_UPPER_BOUND = 10

        # Save the original parameters - will need to reload several times
        orig_ymax = self.ymax
        orig_ymin = self.ymin
        orig_K = self.K
        orig_n = self.n

        # For each retry
        for _ in range(0, num_retries):

            # Generate a uniform random integer corresponding to the selected operation
            selected_operation = np.random.randint(low = 0, high = 54)

            if 0 <= selected_operation <= 5:
                stretch_factor = np.random.uniform(low = 1.0, high = 1.5)
                self.stretch(stretch_factor)

            elif 6 <= selected_operation <= 11:
                slope_increase_factor = np.random.uniform(low = 1.0, high = 1.05)
                self.increase_slope(slope_increase_factor)

            elif 12 <= selected_operation <= 17:
                slope_decrease_factor = np.random.uniform(low = 1.0, high = 2.0)
                self.decrease_slope(slope_decrease_factor)

            elif 18 <= selected_operation <= 26:
                promoter_strength_increase = np.random.uniform(low = 1.0, high = 2.0)
                self.stronger_promoter(promoter_strength_increase)
            
            elif 27 <= selected_operation <= 35:
                promoter_strength_decrease = np.random.uniform(low = 1.0, high = 2.0)
                self.weaker_promoter(promoter_strength_decrease)

            elif 36 <= selected_operation <= 44:
                rbs_strength_increase = np.random.uniform(low = 1.0, high = 5.0)
                self.strong_rbs(rbs_strength_increase)

            elif 45 <= selected_operation <= 53:
                rbs_strength_decrease = np.random.uniform(low = 1.0, high = 2.0)
                self.weaker_rbs(rbs_strength_decrease)

            # If any of the gate parameters exceed the limits we set, try to generate another input state
            if self.ymax > YMAX_UPPER_BOUND or self.ymin < YMIN_LOWER_BOUND or self.K < K_LOWER_BOUND or self.K > K_UPPER_BOUND or self.n > n_UPPER_BOUND:
                
                # Make sure to reset the parameters if invalid gate parameters 
                # are produced as a result of the modifcation!
                self.ymax = orig_ymax
                self.ymin = orig_ymin
                self.K = orig_K
                self.n = orig_n
                continue
            # Else a valid parameter state was generated!  Break out and return!
            else:
                valid_state_generated = True
                break

        # Return whether a valid state was generated - this will help simulated 
        # annealing algorithm determine whether or not to accept parameter state
        return valid_state_generated