# ------------------------------------------------------------------------------
# Project: Genetic Circuit Optimization with Cello and Simulated Annealing
# EC/BE552 Computational Synthetic Biology for Engineers
# Homework 1
# Date: April 2, 2021
# Authors: N. Sacco, N. Villareal
#
# Module: response_function.py
# Description:  Sigmoidal response function.  Contains the actual response 
#               function that can return a useful output based on specified
#               parameters.  Really just a wrapper module around the function.
# Status:   Fully operational, but not sure how useful.  The protein and DNA
#           operations are not in this module, but maybe they should be - look
#           into that.  The major task of this module - creating the actual
#           mathematical relationship using the parameters is accomplished,
#           which is good, but more functionality could be added here.
# ------------------------------------------------------------------------------

# Imports
import numpy as np

''' 
Class:          ResponseFunction
Description:    Sigmoial response function of the form described in the HW1
                technical document.  Currently just a wrapper around creation &
                access of the mathematical object used to calculate res_func(x).
'''
class ResponseFunction():

    def __init__(self, ymax, ymin, K, n):

        self.x = np.logspace(-3, 3)
        
        # Sigmoidal parameters
        self.ymax = np.float64(ymax)
        self.ymin = np.float64(ymin)
        self.K = np.float64(K)
        self.n = np.float64(n)

        # Create the sigmoidal object
        self.create_sigmoid()
    
    '''
    Function:       create_sigmoid
    Args:           None
    Return:         None
    Description:    Populates the output array self.y with values according to 
                    the sigmoidal response function.  Currently not used.
    '''
    def create_sigmoid(self):
        self.y = self.ymin + ((self.ymax - self.ymin) / (1.0 + (self.x/self.K)**self.n))

    '''
    Function:       f
    Args:           x: Input value x
    Return:         f(x), aka output of sigmoidal response function for input x
    Description:    Returns the y value corresponding to input x value.  This is 
                    how we actually access res_func(x) - just call f(x) on 
                    the desired input x.
    '''
    def f(self, x):
        return self.ymin + ((self.ymax - self.ymin) / (1.0 + (x/self.K)**self.n))

if __name__ == '__main__':
    print("Response Function!")
    


    

   
