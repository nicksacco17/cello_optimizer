
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
        self.ymax = 0.0
        self.ymin = 0.0
        self.K = 0.0
        self.n = 0.0
        self.alpha = 0.0
        self.beta = 0.0
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