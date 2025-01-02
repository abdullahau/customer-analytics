import polars as pl
import numpy as np

from scipy.optimize import minimize
from scipy.special import gammaln, comb, hyp2f1
from scipy.special import beta as beta_fn
from scipy.stats import beta as beta_dist
from scipy.integrate import quad

class BGBB(object):
    def __init__(self, data):
        self.data = data
        self.alpha, self.beta, self.gamma, self.delta = None
        
    def log_likelihood(self):
        pass
        
    def parameter_estimate():
        pass
    
    def sample_model_fit():
        pass
    
    def calibration_model_fit():
        pass
    
    def p_alive(self):
        pass
    
    def conditiona_expectation(self):
        pass

    def p_active(self):
        pass     
    
    
    def dert(self):
        pass   
    
    