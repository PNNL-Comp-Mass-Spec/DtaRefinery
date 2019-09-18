from numpy import array, median, zeros
from pylab import plot, hist, subplot, show, xlim, axvline
from aux_sys_err_prediction_module.simple_shift.my_em_gfg_function import do_em_norm_n_fixed_norm
from pprint import pprint as p

myName = 'simple shift'

def shift_em_norm_n_fixed_norm( xtPpm, dtaPpm):
    lim = max(abs(xtPpm))
    mean1, stdev1, portion1, mean2, stdev2 = do_em_norm_n_fixed_norm(xtPpm, 100)
    xtPpm = xtPpm - mean1
    dtaPpm = dtaPpm - mean1
    return (xtPpm, dtaPpm)


def shift_median(xtPpm, dtaPpm):
    shift = median(xtPpm)
    xtPpm = xtPpm - shift
    dtaPpm = dtaPpm - shift
    return (xtPpm, dtaPpm)
    

def do_simple_shift( Controller, xTandemInput, dtaInput):

##    correctionPars = Controller.refiningPars
##
##    params = correctionPars[myName]['params']
##    params['other params'] = correctionPars['other params']

    xt = array([[float(y) for y in x[1:]] for x in xTandemInput[1:]])
    xtColumns = list(xTandemInput[0][1:])
    massErrorPpmIndex = xtColumns.index('massErrorPpm')

    dta = array([[float(y) for y in x[3:]] for x in dtaInput[1:]])
    dtaColumns = dtaInput[0][2:]
    #first two columns are string index and entry string itself in the dta file
    
    xtPpm = xt[:,massErrorPpmIndex].copy()
    dtaPpm = zeros(dta.shape[0],'d')

    #choose the approach
##    approaches = [i for i in params.keys() if 'do' in params[i]]
##    approachToUseNameBool = [params[i]['do'] for i in approaches]
##    #---check if there is only one True
##    if sum(approachToUseNameBool) != 1:
##        print("Something wrong in parameter input")
##    approachToUseName = approaches[approachToUseNameBool.index(True)]        
    #---get the approach function
    approachToUseName = Controller.updatedSettings['refiningPars']['choices']['simpleShift']
    approachToUse = {'medianShift':             shift_median,
                     'ExpMax_Norm_n_FixedNorm': shift_em_norm_n_fixed_norm}[approachToUseName]

    #zero center the errors
    xtPpm, dtaPpm = approachToUse(xtPpm, dtaPpm)
    
    return xtPpm, dtaPpm



if __name__ == '__main__':
    import time
    import csv
    from pprint import pprint as p

    #---READING FILES----------------------------------
    xTandemInputFH    = open('xt_log_merg.txt','r')
    csv_reader = csv.reader(xTandemInputFH, delimiter='\t')
    xTandemInput = [tuple(x) for x in csv_reader]
    xTandemInputFH.close()

    dtaEntriesFH      = open('dta_entries.txt','r')
    csv_reader = csv.reader(dtaEntriesFH, delimiter='\t')
    dtaEntries = [x for x in csv_reader]
    dtaEntriesFH.close()
    #--------------------------------------------------    

    a, b = do_simple_shift(xTandemInput, dtaEntries)

    #--plotting----------------------------------------
    ori = array([float(x[3]) for x in xTandemInput[1:]])
    subplot(121)
    hist(ori,100)
    axvline(0,color='green')
    xlim(-50,+50)
    subplot(122)
    hist(a,100)    
    axvline(0,color='green')
    xlim(-50,+50)
    show()
