from numpy import array, lexsort, where, vstack, ceil, average, median
from aux_sys_err_prediction_module.additive.numpy_runmed_spline.my_runmed import runmed
from scipy.interpolate import splev, splrep

def runmed_spline_model(x, y, xFit, **kwargs):
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

    #running median
    runMedSpan = float(kwargs['runMedSpan'])
    NN = int(ceil(float(uA.shape[0])*runMedSpan))
    if NN%2 == 0:
        NN += 1

    yRunMed = runmed(uA[:,1],NN)

    #runmed may result in non-uniques
    #So group Scans and take averages along yRunMed
    unqScans = array(dict.fromkeys(uA[:,0]).keys())

    avgErr = array([median(yRunMed[where(uA[:,0] == i)].T) for i in unqScans])

    #ordering
    ind = lexsort(keys=(avgErr,unqScans))
    urmA = vstack((unqScans[ind],avgErr[ind])).T

    multiplier = kwargs['multiplier']
    sLim = sum(urmA[:,1]**2) * multiplier
    tck = splrep(urmA[:,0], urmA[:,1], s=sLim)
    yFit = splev(xFit, tck)

    return yFit, (uA[:,0], yRunMed)

    
if __name__ == '__main__':
    import csv
    from numpy import log
    from pylab import plot, grid, axhline,\
                     ylim, show, subplot
    
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

    newY, runMed = runmed_spline_model(A[:,0], A[:,1], A[:,0], runMedSpan = 0.3, mult = 1e-2)
    yRes = A[:,1] - newY

    plot(A[:,0],A[:,1],'bo')
    plot(runMed[0],runMed[1],'y^')
    plot(A[:,0],newY,'r+')
    axhline(0,color='r')
    grid()
    ylim((-40,+40))
    show()
