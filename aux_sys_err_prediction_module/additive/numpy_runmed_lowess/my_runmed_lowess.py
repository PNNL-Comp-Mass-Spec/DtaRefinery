from aux_sys_err_prediction_module.additive.numpy_runmed_lowess.my_lowess import lowess
from numpy import array, lexsort, where, vstack, ceil, average, median
from aux_sys_err_prediction_module.additive.numpy_runmed_spline.my_runmed import runmed
from scipy.interpolate import splev, splrep
##import time
##import psyco
##psyco.full()



def runmed_lowess_model(x, y, xFit, **params):
    """
    mult is multiplier from 0 to 1
    0 interpolation
    1 the smoothest fit possible
    """

    #removing redundant entries
    tA = zip(x,y)
    utA = dict.fromkeys(tA).keys()
    uA = array(utA)
    
    #sorting by (1) parameter and (2) responce
    iuA = lexsort(keys=(uA[:,1],uA[:,0]))
    uA = uA[iuA,:]

    #clean up. since I need uA only
    del tA, utA, iuA

    #running median
    runMedSpan = float(params['runMedSpan'])
    NN = int(ceil(float(uA.shape[0])*runMedSpan))
    if NN%2 == 0:
        NN += 1

    yRunMed = runmed(uA[:,1],NN)
   
    #lowess
    f = float(params['lowess span'])
    itr = int(params['lowess robust iters'])
    yFit = lowess(uA[:,0], yRunMed, xFit, f=f, itr=itr)
    
    return yFit, (uA[:,0], yRunMed)

    








if __name__ == '__main__':
    import csv
    import time
    import psyco
    from numpy import log
    from pylab import plot, grid, axhline,\
                     ylim, show, subplot

    psyco.full()

    
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

    a = array([[float(y) for y in x] for x in xTandemInput[1:]])
    aColumns = xTandemInput[0]
    #('parent_scan', 'mz', 'intensity', 'ppm')

    A = a[:,(0,3)] #is the input for 1D fitting

    tic = time.clock()
    newY, runMed = runmed_lowess_model(A[:,0], A[:,1], A[:,0], runMedSpan=0.5, f=0.1, itr=3)
    toc = time.clock()
    print('done in %s seconds' % (toc-tic))
    yRes = A[:,1] - newY

    plot(A[:,0],A[:,1],'bo')
    plot(runMed[0],runMed[1],'y^')
    plot(A[:,0],newY,'r+')
    axhline(0,color='r')
    grid()
    ylim((-40,+40))
    show()




