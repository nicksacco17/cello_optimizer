
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.linalg as la
from scipy import optimize as opt
import scipy as sp

class ResponseFunction():

    def __init__(self, ymax, ymin, K, n):

        self.x = np.logspace(-3, 3)
        self.ymax = ymax
        self.ymin = ymin
        self.K = K
        self.n = n
        self.create_sigmoid()
        self.num_plots = 0

    def add_plot(self):
        plt.loglog(self.x, self.y, linewidth = 1.5)
        self.num_plots += 1
        
    def show_plots(self):
        plt.xlabel("Input")
        plt.ylabel("Output")
        legend_str = []
        for i in range(0, self.num_plots):
            legend_str.append(str(i))
        plt.legend(legend_str)
        plt.show()

    def plot(self):
        plt.loglog(self.x, self.y, '-r', linewidth = 1.5)
        plt.show()

    def create_sigmoid(self):
        self.y = self.ymin + ((self.ymax - self.ymin) / (1.0 + (self.x/self.K)**self.n))

    def f(self, x):
        return self.ymin + ((self.ymax - self.ymin) / (1.0 + (x/self.K)**self.n))

    # Protein Engineering

    def stretch(self, x):
        if abs(x) <= 1.5:
            self.ymax *= x
            if x != 0:
                self.ymin /= x
        self.create_sigmoid()

    def increase_slope(self, x):
        if abs(x) <= 1.05:
            self.n *= x
        self.create_sigmoid()

    def decrease_slope(self, x):
        if abs(x) <= 1.05 and x != 0:
            self.n /= x
        self.create_sigmoid()

    # DNA Engineering

    def stronger_promoter(self, x):
        self.ymax *= x
        self.ymin *= x
        self.create_sigmoid()

    def weaker_promoter(self, x):
        if x != 0:
            self.ymax /= x
            self.ymin /= x
        self.create_sigmoid()

    def strong_rbs(self, x):
        if x != 0:
            self.K /= x
        self.create_sigmoid()

    def weaker_rbs(self, x):
        self.K *= x
        self.create_sigmoid()
    
def test():
    func1 = ResponseFunction(ymax = 3.8, ymin = 0.06, K = 1, n = 1.6)
    func1.add_plot()

    func1.strong_rbs(2)
    func1.add_plot()

    func1.show_plots()

def circuit_func(x, y):

    if x == 0 and y == 0:
        return 0
    elif x == 0 and y == 1:
        return 1
    elif x == 1 and y == 0:
        return 0
    elif x == 1 and y == 1:
        return 0

def naive_optimization():
    ON_MIN = 1e9
    OFF_MAX = 0
    BEST_INPUTS = []
    BEST_SCORE = 0.0

    P1_Ph1F_gate = ResponseFunction(ymax = 3.9, ymin = 0.01, n = 4, K = 0.03)
    S1_SrpR_gate = ResponseFunction(ymax = 1.3, ymin = 0.003, n = 2.9, K = 0.01)

    x = np.linspace(1e-3, 35, 25)
    print(x)
    for i in range(0, len(x)):
        pLuxStar_HIGH = x[i]
    
        print(i)
        for j in range(0, i):
            pLuxStar_LOW = x[j]

            pLuxStar_INPUTS = [pLuxStar_LOW, pLuxStar_HIGH]
            for k in range(0, len(x)):
                pTet_HIGH = x[k]
                for m in range(0, k):
                    pTet_LOW = x[m]

                    pTet_INPUTS = [pTet_LOW, pTet_HIGH]

                    output_logic_results = []

                    for i in range(0, 2):
                        for j in range(0, 2):
                            S1_SrpR_gate_OUT = S1_SrpR_gate.f(pTet_INPUTS[j])
                            P1_Ph1F_gate_OUT = P1_Ph1F_gate.f(pLuxStar_INPUTS[i] + S1_SrpR_gate_OUT)
                            output_logic_map = {circuit_func(i, j) : P1_Ph1F_gate_OUT}
                            output_logic_results.append(output_logic_map)
                            #print("[Logic %d] pLuxStar = %.6lf, [Logic %d] pTet = %.6lf --> [Logic %d] YFP = %0.6lf" % (i, pLuxStar_INPUTS[i], j, pTet_INPUTS[j], circuit_func(i, j), P1_Ph1F_gate_OUT))
                            
                    for entry in output_logic_results:
                        for logic_val, genetic_val in entry.items():
                            if logic_val == 0 and genetic_val > OFF_MAX:
                                OFF_MAX = genetic_val
                            elif logic_val == 1 and genetic_val < ON_MIN:
                                ON_MIN = genetic_val
                    
                    score = np.log10(ON_MIN/OFF_MAX)
                    if score > BEST_SCORE:
                        BEST_SCORE = score
                        BEST_INPUTS = [pLuxStar_INPUTS, pTet_INPUTS]

    print("BEST INPUTS: ")
    print(BEST_INPUTS)
    print("BEST SCORE: %lf" % BEST_SCORE)


    pLuxStar_LOW = 0.025
    pLuxStar_HIGH = 0.31

    pLuxStar_INPUTS = [pLuxStar_LOW, pLuxStar_HIGH]

    pTet_LOW = 0.0013
    pTet_HIGH = 4.4

    pTet_INPUTS = [pTet_LOW, pTet_HIGH]

    output_logic_results = []

    for i in range(0, 2):
        for j in range(0, 2):
            S1_SrpR_gate_OUT = S1_SrpR_gate.f(pTet_INPUTS[j])
            P1_Ph1F_gate_OUT = P1_Ph1F_gate.f(pLuxStar_INPUTS[i] + S1_SrpR_gate_OUT)
            output_logic_map = {circuit_func(i, j) : P1_Ph1F_gate_OUT}
            print("[Logic %d] pLuxStar = %.6lf, [Logic %d] pTet = %.6lf --> [Logic %d] YFP = %0.6lf" % (i, pLuxStar_INPUTS[i], j, pTet_INPUTS[j], circuit_func(i, j), P1_Ph1F_gate_OUT))
            output_logic_results.append(output_logic_map)

    ON_MIN = 1e9
    OFF_MAX = 0

    for entry in output_logic_results:
        for logic_val, genetic_val in entry.items():
            if logic_val == 0:
                if genetic_val > OFF_MAX:
                    OFF_MAX = genetic_val
            elif logic_val == 1:
                if genetic_val < ON_MIN:
                    ON_MIN = genetic_val

    print("ON_MIN = %lf, OFF_MAX = %lf" %(ON_MIN, OFF_MAX))
    score = np.log10(ON_MIN/OFF_MAX)
    print(score)


def f(x):
    return 0.003 + ((1.3 - 0.003) / (1.0 + (x/0.01) ** 2.9))

def g_act(x, y):
    return 0.01 + ((3.9 - 0.01) / (1.0 + ((y + f(x))/0.03) ** 4))

def g(params):
    x, y = params
    return 0.01 + ((3.9 - 0.01) / (1.0 + ((y + f(x))/0.03) ** 4))

def neg_g(params):
    return -1 * g(params)

#def f(x):
#    return x**4 + 3*(x-2)**3 - 15*(x)**2 + 1


if __name__ == '__main__':
    #naive_optimization()
    #x = np.linspace(1e-3, 5, 1000)
    #y = np.linspace(1e-3, 0.5, 1000)

    #output = g(x, y)
    #print(np.max(output))
    #print(g(0.0013, 0.025))
    #print(f(4.4))
    #print(g(4.4, 0.025))

    #X, Y = np.meshgrid(x, y)
    #Z = g_act(X, Y)

    #print(np.max(Z))
    maxZ = sp.optimize.fmin(neg_g, [1, 1])
    minZ = sp.optimize.fmin(g, [1, 1])
    #minZ = sp.optimize.fmin(g, [1, 1])
    #minZ = sp.optimize.minimize(g, x0 = [1, 1], bounds = ((0, 1000), (0, 1000)), method='SLSQP', tol = 1e-6)
    #maxZ = sp.optimize.minimize(neg_g, x0 = [1e-3, 1e-3], bounds = ((0, 1000), (0, 1000)), method='SLSQP', tol = 1e-6)
    #maxZ = sp.optimize.minimize(neg_g, x0 = [1e-3, 1e-3], bounds = ((0, None), (0, None)))
    print(maxZ)
    print(minZ)
    #print(minZ)
    print(g_act(maxZ[0], -1*maxZ[1]))
    print(g_act(minZ[0], minZ[1]))
    #plt.contourf(X, Y, Z)
    #plt.colorbar()
    #plt.show()

    #fig = plt.figure()
    #ax = Axes3D(fig)
    #ax.plot_surface(X, Y, Z)
    #plt.xlabel('x')
    #plt.ylabel('y')
    #plt.show()

    #plt.plot(x, output)
    #plt.plot(y, output)
    #plt.show()


    #print(opt.minimize_scalar(f, method = 'bounded', bounds = [0, 6]))
    


    

   
