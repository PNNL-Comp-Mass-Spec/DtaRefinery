
from aux_sys_err_prediction_module.additive.my_additive_regression_analysis import do_additive_regression_analysis as additive_approach
from aux_sys_err_prediction_module.simple_shift.my_simple_shift import do_simple_shift as simple_shift
#

from pprint import pprint as p

from numpy import log, array, median, zeros
from pylab import plot, grid, axhline,\
                 ylim, show, subplot, clf,\
                 savefig, hist, xlabel, ylabel,\
                 title, text, xlim, subplots_adjust



def bypass_refining( Controller, xTandemInput, dtaEntries):
    
    xtColumns = list(xTandemInput[0])
    massErrorPpmIndex = xtColumns.index('massErrorPpm')    
    xtPpm = array([x[massErrorPpmIndex] for x in xTandemInput[1:]])
    
    return xtPpm, zeros(len(dtaEntries[1:]),'d')



def do_predict_systematic_errors( Controller, xTandemInput, dtaEntries):

    #get the approach function
    approachToUse = {'additiveRegression':    additive_approach,
                     'simpleShift':          simple_shift,
                     'bypassRefining':            bypass_refining
                     }[Controller.updatedSettings['refiningPars']['choices']['refining method']]

    #run the function and get the data (new ppms)
    #TODO: not sure this is the best way to return results
    xtPpm, dtaPpm = approachToUse(Controller, xTandemInput, dtaEntries)

    #returns just systematic ppms
    return xtPpm, dtaPpm
    # WARNING!! the order of ppm errors has to be the same as in INPUTS


    



