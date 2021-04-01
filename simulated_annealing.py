
import numpy as np
import random as rand
import matplotlib.pyplot as plt

def f1(x):
    return (-1 * x**2) + 5

class Simulated_Annealer():

    def __init__(self, func, num_iterations):
        self.func = func
        self.num_iterations = num_iterations
        self.T = 20
        self.maximum = np.NINF

    def run_algo(self, x0):

        self.maximum = self.func(x0)

        count = 0

        for i in range(0, self.num_iterations):

            if i > 0 and count % (self.num_iterations / 10) == 0:
                self.T /= 2
            new_x = np.random.uniform(low = -5, high = 5)
            new_max = self.func(new_x)
            if new_max >= self.maximum:
                self.maximum = new_max
            else:
                cost_diff = self.maximum - new_max
                #print("CURRENT MAX = %lf, NEW MAX = %lf, COST DIFFERENCE = %lf" % (self.maximum, new_max, cost_diff))
                accept_prob = np.random.uniform(low = 0.0, high = 1.0)
                #print("PROB COST = %e, ACCEPT PROB = %lf" % (np.exp(-1 * cost_diff / self.T), accept_prob))
                if np.exp(-1 * cost_diff / self.T) > accept_prob:
                    self.maximum = new_max
            count += 1
        print("MAXIMUM = %lf" % self.maximum)

if __name__ == '__main__':

    x0 = np.random.uniform(low = -10, high = 10)
    annealer = Simulated_Annealer(np.sinc, 10000)
    annealer.run_algo(x0)

    x = np.linspace(-5, 5, num = 1000)
    plt.plot(x, np.sinc(x))
    plt.show()

