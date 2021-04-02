
import numpy as np

class Input_Signal_Record():

    def __init__(self):
        self.name = ""
        self.ymax = 0.0
        self.ymin = 0.0
        self.alpha = 0.0
        self.beta = 0.0
        #self.resfunc = None
        self.output = []
        self.param_list = []

    def print(self):

        print("Name: " + self.name)
        print("ymax = %lf" % (self.ymax))
        print("ymin = %lf" % (self.ymin))
        print("alpha = %lf" % (self.alpha))
        print("beta = %lf" % (self.beta))
        print("Outputs: ")
        for output in self.output:
            print(output)

    def print_name(self):
        print(self.name)

    # PROTEIN ENGINEERING OPERATIONS

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

    # DNA ENGINEERING OPERATIONS

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

    def get_parameters(self, in_params):

        modified_params = in_params

        for entry in modified_params:

            if entry['name'] == 'ymax':
                entry['value'] = self.ymax
            elif entry['name'] == 'ymin':
                entry['value'] = self.ymin
            elif entry['name'] == 'alpha':
                entry['value'] = self.alpha
            elif entry['name'] == 'beta':
                entry['value'] = self.beta

        return modified_params

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

        #self.resfunc = rf.ResponseFunction(ymax = self.ymax, ymin = self.ymin, K = self.alpha, n = self.n)

    def load_params(self, in_params):

        self.ymax = in_params['ymax']
        self.ymin = in_params['ymin']
        self.alpha = in_params['alpha']
        self.beta = in_params['beta']

class Output_Signal_Record():
    
    def __init__(self):
        self.name = ""
        self.unit_conversion = 0.0

    def print(self):
        print("Name: " + self.name)
        print("Unit Conversion = %lf" % self.unit_conversion)

    def print_name(self):
        print(self.name)

    def load_params(self, in_params):
        self.unit_conversion = in_params['unit_conversion']


class Repressor_Record():

    def __init__(self):
        self.name = ""
        self.ymax = np.float64(0.0)
        self.ymin = np.float64(0.0)
        self.K = np.float64(0.0)
        self.n = np.float64(0.0)
        self.alpha = np.float64(0.0)
        self.beta = np.float64(0.0)
        #self.resfunc = None
        self.output = []
        self.gate_type = ""
        self.param_list = []

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

     # PROTEIN ENGINEERING OPERATIONS

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

    # DNA ENGINEERING OPERATIONS

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

    def modify_repressor(self, num_retries):
        # Choose the Protein or DNA operation to apply to the gate

        valid_state_generated = False
        YMAX_UPPER_BOUND = 5
        YMIN_LOWER_BOUND = 1e-3
        K_LOWER_BOUND = 1e-3
        K_UPPER_BOUND = 15
        n_UPPER_BOUND = 10

        orig_ymax = self.ymax
        orig_ymin = self.ymin
        orig_K = self.K
        orig_n = self.n

        for _ in range(0, num_retries):

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
                # Reset the parameters you fool!
                self.ymax = orig_ymax
                self.ymin = orig_ymin
                self.K = orig_K
                self.n = orig_n
                continue
            # Else a valid parameter state was generated!  Break out and return!
            else:
                valid_state_generated = True
                break
        # Return whether or not a valid state was generated - this will help simulated annealing algorithm determine whether or not to accept a parameter state
        return valid_state_generated

    def get_parameters(self, in_params):

        modified_params = in_params

        for entry in modified_params:

            if entry['name'] == 'ymax':
                entry['value'] = self.ymax
            elif entry['name'] == 'ymin':
                entry['value'] = self.ymin

            elif entry['name'] == 'K':
                entry['value'] == self.K
            elif entry['name'] == 'n':
                entry['value'] == self.n

            elif entry['name'] == 'alpha':
                entry['value'] = self.alpha
            elif entry['name'] == 'beta':
                entry['value'] = self.beta
            

        return modified_params

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

        #self.resfunc = rf.ResponseFunction(ymax = self.ymax, ymin = self.ymin, K = self.K, n = self.n)

    def load_params(self, in_params):

        self.ymax = in_params['ymax']
        self.ymin = in_params['ymin']
        self.alpha = in_params['alpha']
        self.beta = in_params['beta']
        self.K = in_params['K']
        self.n = in_params['n']

        #self.resfunc = rf.ResponseFunction(ymax = self.ymax, ymin = self.ymin, K = self.K, n = self.n)

    def populate_params(self, ymax, ymin, K, n):
        self.ymax = ymax
        self.ymin = ymin
        self.K = K
        self.n = n